# tool_agent_file.py

import os
import sys
import re
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# -- Third-Party / External Imports --
from semanticscholar import SemanticScholar
from litellm import completion
from langchain import hub
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain_community.chat_models import ChatLiteLLM
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate

# -- Local Imports (adjust paths if needed) --
from paperscraper.pubmed import get_query_from_keywords_and_date, get_pubmed_papers
from paperscraper.arxiv import get_arxiv_papers_api
from paperscraper.xrxiv.xrxiv_query import XRXivQuery
# from paperscraper.pdf import save_pdf  # only if needed

# =============================================================================
# 1) Load environment variables
# =============================================================================

dotenv_path = Path(__file__).parent / '.env'  # Adjust if your .env is elsewhere
load_dotenv(dotenv_path)

logger = logging.getLogger(__name__)

S2_API_KEY = os.getenv("S2_API_KEY", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Just to confirm in logs (optional):
logger.info(f"S2_API_KEY loaded: {bool(S2_API_KEY)}")
logger.info(f"MISTRAL_API_KEY loaded: {bool(MISTRAL_API_KEY)}")
logger.info(f"OPENAI_API_KEY loaded: {bool(OPENAI_API_KEY)}")
logger.info(f"ANTHROPIC_API_KEY loaded: {bool(ANTHROPIC_API_KEY)}")

# =============================================================================
# 2) Configuration Constants
# =============================================================================

BIOARXIV_FILEPATH = "server_dumps/biorxiv_2025-03-11.jsonl"
MEDARXIV_FILEPATH = "server_dumps/medrxiv_2025-03-11.jsonl"
CHEMARXIV_FILEPATH = "server_dumps/chemrxiv_2025-03-11.jsonl"

PAPER_METADATA_FIELDS = ["title", "authors", "date", "abstract", "doi"]

NUM_KEYWORDS = 2
MAX_PUBMED_RESULTS = 10
MAX_ARXIV_RESULTS = 10
MAX_BIOARXIV_RESULTS = 10
MAX_CHEMARXIV_RESULTS = 10
MAX_S2_RESULTS = 10
MAX_TOKENS = 10000
TEMPERATURE = 0.7
MAX_SOURCES_TO_PRINT = 2

# You can switch model here if you like, e.g. "anthropic/claude-3-5" or "mistral/mistral-small"
MODEL = "openai/gpt-4o"  

ERROR_MESSAGE = "Unable to retrieve information."

# =============================================================================
# 3) Helper functions for queries
# =============================================================================

def query_pubmed(query: str) -> list[dict]:
    """Get papers from PubMed using the paperscraper library."""
    papers = get_pubmed_papers(
        query=query,
        fields=PAPER_METADATA_FIELDS,
        max_results=MAX_PUBMED_RESULTS
    )
    return papers.to_dict(orient="records")


def query_s2(query: str) -> list[dict]:
    """Get papers from Semantic Scholar using the official semanticscholar library."""
    sch = SemanticScholar(api_key=S2_API_KEY)
    results = sch.search_paper(
        query,
        fields=["title", "abstract", "externalIds"], 
        limit=MAX_S2_RESULTS,
        bulk=False
    )
    return results.raw_data


def query_arxiv(query: str) -> list[dict]:
    """Get papers from ArXiv using the paperscraper library."""
    papers = get_arxiv_papers_api(
        query=query,
        fields=PAPER_METADATA_FIELDS,
        max_results=MAX_ARXIV_RESULTS
    )
    return papers.to_dict(orient="records")


def query_bioarxiv(query: str) -> list[dict]:
    """Get papers from local biorxiv dump."""
    querier = XRXivQuery(BIOARXIV_FILEPATH)
    papers = querier.search_keywords(query, fields=PAPER_METADATA_FIELDS)
    return papers.to_dict(orient="records")


def query_medarxiv(query: str) -> list[dict]:
    """Get papers from local medarxiv dump."""
    querier = XRXivQuery(MEDARXIV_FILEPATH)
    papers = querier.search_keywords(query, fields=PAPER_METADATA_FIELDS)
    return papers.to_dict(orient="records")


def query_chemarxiv(query: str) -> list[dict]:
    """Get papers from local chemarxiv dump."""
    querier = XRXivQuery(CHEMARXIV_FILEPATH)
    papers = querier.search_keywords(query, fields=PAPER_METADATA_FIELDS)
    return papers.to_dict(orient="records")

# You can expand your function_to_call dict with more archives if you like
function_to_call = {
    "pubmed": query_pubmed,
    "arxiv": query_arxiv,
    "semanticscholar": query_s2,
    # "bioarxiv": query_bioarxiv,
    # "medarxiv": query_medarxiv,
    # "chemarxiv": query_chemarxiv,
}

# =============================================================================
# 4) Main tool_agent function
# =============================================================================

def tool_agent(conversation: str) -> str:
    """
    The specialized tool agent that:
    1) Reads the conversation so far.
    2) Extracts up to NUM_KEYWORDS from the conversation (using an LLM).
    3) Decides which resource to query (pubmed, arxiv, semanticscholar, etc.).
    4) Retrieves relevant papers from that resource.
    5) Summarizes them with a retrieval QA chain (LangChain).
    6) Returns text with references.

    Args:
        conversation: The entire conversation so far.

    Returns:
        A text response summarizing newly discovered information and sources,
        or an ERROR_MESSAGE if something fails.
    """
    # 1) Use your model to parse the conversation for the resource + keywords
    messages = [
        {
            "role": "system",
            "content": (
                "You are helping a group of researchers obtain additional information from outside sources. "
                "Whenever you receive a conversation transcript, use it to identify up to {NUM_KEYWORDS} keywords "
                "from the last speaker. Then decide which source to obtain additional information from. "
                "The available sources are pubmed for medical, arxiv for comp sci/physics/mathematics, "
                "and semanticscholar for other fields."
            )
        },
        {
            "role": "user",
            "content": (
                f"{conversation}\n\n"
                f"Given the above conversation, give me up to {NUM_KEYWORDS} keywords I should obtain additional "
                "information on AND tell me which resource (pubmed/arxiv/semanticscholar) is best. "
                "Answer as valid JSON with keys `resource` (string) and `keywords` (list of strings)."
            )
        }
    ]

    try:
        # 2) Call an LLM to get a JSON with resource + keywords
        completion_resp = completion(
            model=MODEL,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        json_str = completion_resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"LLM error in tool_agent: {e}")
        return ERROR_MESSAGE

    logger.debug(f"tool_agent JSON from LLM: {json_str}")

    def parse_llm_json_output(llm_output: str):
        """
        Safely extracts and parses JSON from a string that may include
        triple backticks and optional "json" language tags.
        """

        # 1. Use a regex to capture anything between ```json ... ``` or just ``` ... ```.
        #    This handles the case where the LLM might output:
        #
        #    ```json
        #    {
        #      "resource": "arxiv",
        #      "keywords": ["AI", "latest research"]
        #    }
        #    ```
        #
        #    or
        #
        #    ```
        #    {
        #      "resource": "arxiv",
        #      "keywords": ["AI", "latest research"]
        #    }
        #    ```
        
        pattern = r"```(?:json)?\s*(.*?)\s*```"
        match = re.search(pattern, llm_output, re.DOTALL)
        
        if match:
            # Extract just the JSON part inside the code block
            json_str = match.group(1)
        else:
            # If there's no fenced code block, assume the entire string is JSON
            json_str = llm_output.strip()

        try:
            # 2. Attempt to parse the JSON
            json_dict = json.loads(json_str)
            
            # 3. Extract required fields
            resource = json_dict["resource"]
            keywords = json_dict["keywords"]
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Error decoding JSON or missing keys: {e}")
            return ERROR_MESSAGE
        
        # 4. You can now safely use `resource` and `keywords`
        return resource, keywords

    resource, keywords = parse_llm_json_output(json_str)
    # # 3) Parse the JSON to extract "resource" and "keywords"
    # try:
    #     print(json_str)
    #     json_dict = json.loads(json_str)
    #     resource = json_dict["resource"]
    #     keywords = json_dict["keywords"]
    # except (json.JSONDecodeError, KeyError, TypeError) as e:
    #     logger.error(f"Error decoding JSON or missing keys: {e}")
    #     return ERROR_MESSAGE

    # Validate
    if not isinstance(resource, str):
        logger.error("`resource` is not a string.")
        return ERROR_MESSAGE
    if not isinstance(keywords, list) or any(not isinstance(k, str) for k in keywords):
        logger.error("`keywords` must be a list of strings.")
        return ERROR_MESSAGE

    # 4) Formulate a search query from the keywords and query the chosen resource
    def get_papers(resource_name: str, keywords_list: list[str]) -> list[dict]:
        """Helper to get papers from the chosen resource."""
        func = function_to_call.get(resource_name)
        if func is None:
            logger.error(f"Resource not supported by tool_agent: {resource_name}")
            return []
        # Convert the list of keywords to a search string
        query_string = get_query_from_keywords_and_date(
            keywords_list, start_date="None", end_date="None"
        )
        logger.info(f"tool_agent: Querying {resource_name} with: {query_string}")
        papers_list = func(query_string)
        return papers_list

    papers = get_papers(resource, keywords)
    if not papers:
        logger.warning("No relevant papers found for the chosen resource/keywords.")
        return ERROR_MESSAGE

    # 5) Turn the abstracts into a small RAG pipeline for summarization
    docs = []
    for paper in papers:
        abstract = paper.get("abstract", "")
        if not abstract:
            continue
        docs.append(Document(page_content=abstract))

    if not docs:
        logger.warning("All retrieved papers had empty abstracts.")
        return ERROR_MESSAGE

    # Create vector store from docs
    embeddings = OpenAIEmbeddings()  # uses OPENAI_API_KEY under the hood
    vectorstore = FAISS.from_documents(docs, embeddings)
    retriever = vectorstore.as_retriever()

    # Create a retrieval-qa pipeline
    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
    llm = ChatLiteLLM(
        model=MODEL,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS
    )
    combine_docs_chain = create_stuff_documents_chain(llm, retrieval_qa_chat_prompt)
    retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

    # The actual question to pass to the retriever:
    input_str = (
        f"{conversation}\n\n"
        f"Based on the above conversation, provide relevant context for these keywords: {keywords}."
    )

    try:
        response = retrieval_chain.invoke({"input": input_str})
        answer_text = response["answer"]
    except Exception as e:
        logger.error(f"Error in retrieval QA chain: {e}")
        return ERROR_MESSAGE

    # 6) Build a final output with references
    output = f"**[Tool Agent]** Searching *{resource}* for relevant info...\n\n"
    output += answer_text
    output += "\n\n**Sources (sample)**\n"
    for paper in papers[:MAX_SOURCES_TO_PRINT]:
        title = paper.get("title") or "Untitled"
        output += f"- {title}\n"

    return output


# =============================================================================
# 5) (Optional) A simple CLI main() if you want to test locally
# =============================================================================

if __name__ == "__main__":
    # Quick test. Adjust the conversation text below to see how it behaves.
    test_convo = (
        "Researcher: I'm really curious about new immunotherapy approaches, "
        "especially T-cell engineering techniques. Let's see what's new.\n"
        "Another: We also talked about using deep learning to predict response."
    )

    result = tool_agent(test_convo)
    print("\n=== TOOL AGENT RESULT ===\n")
    print(result)
