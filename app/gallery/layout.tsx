"use server"

import type { Metadata } from "next"
import { auth } from "@clerk/nextjs/server"
import { SidebarNav } from "@/components/ui/sidebar-nav"
import { Separator } from "@/components/ui/separator"

export const metadata: Metadata = {
  title: "Gallery | Thera VL",
  description: "Browse and discover public sessions"
}

interface GalleryLayoutProps {
  children: React.ReactNode
}

export default async function GalleryLayout({ children }: GalleryLayoutProps) {
  const { userId } = await auth()

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

  return (
    <div className="container relative">
      <div className="flex flex-col space-y-8 lg:flex-row lg:space-x-12 lg:space-y-0">
        <aside className="hidden w-[200px] flex-col lg:flex">
          <SidebarNav items={sidebarNavItems} />
          
          {userId && (
            <div className="mt-6">
              <h3 className="font-medium mb-2">My Sessions</h3>
              <SidebarNav
                items={[
                  {
                    title: "My Public Sessions",
                    href: `/gallery?userId=${userId}&isPublic=true`,
                  },
                  {
                    title: "My Private Sessions",
                    href: `/gallery?userId=${userId}&isPublic=false`,
                  },
                ]}
              />
            </div>
          )}
          
          <div className="mt-6">
            <h3 className="font-medium mb-2">Agent Types</h3>
            <SidebarNav
              items={[
                {
                  title: "Individual Agents",
                  href: "/gallery?agentType=individual",
                },
                {
                  title: "Multi-agent Sessions",
                  href: "/gallery?agentType=multi",
                },
                {
                  title: "Brainstorming",
                  href: "/gallery?agentType=brainstorm",
                },
              ]}
            />
          </div>
        </aside>
        <div className="flex-1 lg:max-w-5xl">
          <div className="flex items-center justify-between py-4">
            <div className="flex-1">
              <h1 className="text-3xl font-bold tracking-tight">Gallery</h1>
              <p className="text-muted-foreground">
                Browse and discover public sessions
              </p>
            </div>
          </div>
          <Separator className="my-6" />
          <div className="flex-1 lg:max-w-5xl">{children}</div>
        </div>
      </div>
    </div>
  )
} 