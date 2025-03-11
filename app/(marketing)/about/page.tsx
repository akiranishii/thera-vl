/*
<ai_context>
This server page returns a simple "About Page" component as a (marketing) route.
</ai_context>
*/

"use server"

export default async function AboutPage() {
  return (
    <div className="container max-w-4xl py-12">
      <h1 className="mb-8 text-4xl font-bold">Thera</h1>
      <p className="mb-8 text-lg text-muted-foreground">
        We're an applied research lab reimagining scientific innovation. The pace of AI innovation is outstripping our ability to consume new research and act on it. Scientific papers are not easily digestible by AI or by busy humans, and the slow cycle from reading to implementation limits everyone's potential—even as breakthroughs multiply daily. Thera is bridging this gap.
      </p>

      <h2 className="mb-6 mt-12 text-2xl font-semibold">The Challenges We Address</h2>
      
      <div className="mb-8 space-y-8">
        <div>
          <h3 className="mb-2 text-xl font-medium">1. Information Overload</h3>
          <p className="text-muted-foreground">
            AI evolves at a dizzying rate, and we can't keep up with the daily deluge of papers and repos. Thera AI contextualizes research so you can act, rather than get lost in the noise.
          </p>
        </div>

        <div>
          <h3 className="mb-2 text-xl font-medium">2. Non-Deterministic Engineering</h3>
          <p className="text-muted-foreground">
            AI systems are messy. Trial-and-error is the rule, not the exception. Thera AI shortens the feedback loop from days to hours, enabling rapid experiments and more breakthroughs, faster.
          </p>
        </div>

        <div>
          <h3 className="mb-2 text-xl font-medium">3. Human-AI Co-Research</h3>
          <p className="text-muted-foreground">
            We believe in co-scientists—AI agents that partner with human researchers—to spark more flexible, creative work than black-box "fully autonomous" systems. Thera AI orchestrates multi-agent workflows so humans keep the big-picture insights, while repetitive tasks go to specialized AI "assistants."
          </p>
        </div>

        <div>
          <h3 className="mb-2 text-xl font-medium">4. Reimagining How We Share Science</h3>
          <p className="text-muted-foreground">
            Traditional papers show one static snapshot. Yet research is iterative, involving evolving data, new references, and continuous collaboration. Thera AI preserves the process behind the results—so you can share not just the final findings, but how they came to be.
          </p>
        </div>
      </div>

      <h2 className="mb-6 mt-12 text-2xl font-semibold">Join Our Journey</h2>
      <p className="mb-4 text-muted-foreground">
        If you agree that modern research needs a 21st-century upgrade—and that AI can help us not just "read more papers," but transform how we experiment, build, and learn—let's connect. We're creating Thera AI to be the place where scientific breakthroughs can move from idea to reality lightning-fast.
      </p>
      <p className="mb-4 text-muted-foreground">
        Please email your resume and a note on a project you're proud of to <a href="mailto:info@thera-ai.com" className="text-primary hover:underline">info@thera-ai.com</a>.
      </p>
    </div>
  )
}
