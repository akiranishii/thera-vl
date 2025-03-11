import type { Metadata } from "next"
import { auth } from "@clerk/nextjs/server"
import { SidebarNav } from "@/components/ui/sidebar-nav"
import { Separator } from "@/components/ui/separator"
import Header from "@/components/header"

export const metadata: Metadata = {
  title: "Gallery | Thera VL",
  description: "Browse and discover public sessions"
}

interface GalleryLayoutProps {
  children: React.ReactNode
}

export default async function GalleryLayout({ children }: GalleryLayoutProps) {
  const { userId } = await auth()

  // Sidebar items commented out as not needed
  /* 
  const sidebarNavItems = [
    {
      title: "All Sessions",
      href: "/gallery"
    },
    {
      title: "Popular",
      href: "/gallery?sort=popular"
    },
    {
      title: "Recent",
      href: "/gallery?sort=recent"
    },
    {
      title: "Trending",
      href: "/gallery?sort=trending"
    }
  ]
  */

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1">
        <div className="container relative">
          <div className="flex flex-col space-y-8 lg:flex-row lg:space-y-0">
            {/* Sidebar removed as requested */}
            {/* 
            <aside className="hidden w-[200px] flex-col lg:flex">
              <SidebarNav items={sidebarNavItems} />
            </aside>
            */}
            <div className="flex-1 lg:max-w-7xl">
              <div className="flex items-center justify-between py-4">
                <div className="flex-1">
                  <h1 className="text-3xl font-bold tracking-tight">Gallery</h1>
                  <p className="text-muted-foreground">
                    Browse and discover public sessions
                  </p>
                </div>
              </div>
              <Separator className="my-6" />
              <div className="flex-1">{children}</div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
} 