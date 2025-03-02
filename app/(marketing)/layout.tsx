/*
<ai_context>
This server layout provides a shared header and basic structure for (marketing) routes.
</ai_context>
*/

import Header from "@/components/header"

export default async function MarketingLayout({
  children
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1">{children}</main>
    </div>
  )
}
