import { Metadata } from "next"

export const metadata: Metadata = {
  title: "Live Session | Thera VL",
  description: "View real-time updates for this research and brainstorming session"
}

export default async function LiveSessionLayout({
  children
}: {
  children: React.ReactNode
}) {
  return children
} 