"use client"

import { useState, useTransition } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { Filter, Search, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage
} from "@/components/ui/form"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from "@/components/ui/select"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger
} from "@/components/ui/sheet"

const filterSchema = z.object({
  sort: z.enum(["recent", "popular", "trending"]).default("recent"),
  search: z.string().optional()
})

type FilterValues = z.infer<typeof filterSchema>

interface GalleryFiltersProps {
  initialSort: string
  initialSearch: string
}

export default function GalleryFilters({
  initialSort = "recent",
  initialSearch = ""
}: GalleryFiltersProps) {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [search, setSearch] = useState("")
  const [isPending, startTransition] = useTransition()
  const [isFiltersOpen, setIsFiltersOpen] = useState(false)
  
  // Count active filters
  const activeFilters = [
    initialSearch ? 1 : 0
  ].reduce((sum, count) => sum + count, 0)
  
  const form = useForm<FilterValues>({
    resolver: zodResolver(filterSchema),
    defaultValues: {
      sort: (initialSort as "recent" | "popular" | "trending") || "recent",
      search: initialSearch || ""
    }
  })
  
  function handleSearch(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    
    startTransition(() => {
      const params = new URLSearchParams(searchParams.toString())
      
      if (search) {
        params.set("search", search)
      } else {
        params.delete("search")
      }
      
      // Reset to page 1 when changing search
      params.delete("page")
      
      router.push(`/gallery?${params.toString()}`)
    })
  }
  
  function onFilterSubmit(values: FilterValues) {
    startTransition(() => {
      const params = new URLSearchParams(searchParams.toString())
      
      // Update sort
      if (values.sort) {
        params.set("sort", values.sort)
      } else {
        params.delete("sort")
      }
      
      // Keep search parameter
      if (values.search) {
        params.set("search", values.search)
        setSearch(values.search)
      }
      
      // Reset to page 1 when changing filters
      params.delete("page")
      
      router.push(`/gallery?${params.toString()}`)
      setIsFiltersOpen(false)
    })
  }
  
  function handleSortChange(value: string) {
    startTransition(() => {
      const params = new URLSearchParams(searchParams.toString())
      
      if (value) {
        params.set("sort", value)
      } else {
        params.delete("sort")
      }
      
      // Reset to page 1 when changing sort
      params.delete("page")
      
      router.push(`/gallery?${params.toString()}`)
    })
  }
  
  function clearFilters() {
    startTransition(() => {
      const params = new URLSearchParams()
      
      // Keep sort parameter
      const sort = searchParams.get("sort")
      if (sort) {
        params.set("sort", sort)
      }
      
      router.push(`/gallery?${params.toString()}`)
      form.reset({
        sort: (sort as "recent" | "popular" | "trending") || "recent",
        search: ""
      })
      setSearch("")
    })
  }
  
  return (
    <div className="flex flex-wrap gap-2 items-center">
      <form onSubmit={handleSearch} className="flex flex-1 items-center space-x-2">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Search sessions..."
            className="pl-8"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <Button type="submit" disabled={isPending}>
          Search
        </Button>
      </form>
      
      <Select
        defaultValue={initialSort || "recent"}
        onValueChange={handleSortChange}
      >
        <SelectTrigger className="w-[140px]">
          <SelectValue placeholder="Sort by" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="recent">Recent</SelectItem>
          <SelectItem value="popular">Popular</SelectItem>
          <SelectItem value="trending">Trending</SelectItem>
        </SelectContent>
      </Select>
      
      <Sheet open={isFiltersOpen} onOpenChange={setIsFiltersOpen}>
        <SheetTrigger asChild>
          <Button variant="outline" size="icon" className="relative">
            <Filter className="h-4 w-4" />
            {activeFilters > 0 && (
              <Badge 
                variant="destructive" 
                className="absolute -right-2 -top-2 h-5 w-5 rounded-full p-0 text-[10px]"
              >
                {activeFilters}
              </Badge>
            )}
          </Button>
        </SheetTrigger>
        <SheetContent>
          <SheetHeader>
            <SheetTitle>Filters</SheetTitle>
          </SheetHeader>
          
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onFilterSubmit)} className="space-y-6 pt-6">
              <FormField
                control={form.control}
                name="sort"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Sort By</FormLabel>
                    <Select 
                      onValueChange={field.onChange} 
                      defaultValue={field.value}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select sort order" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="recent">Recent</SelectItem>
                        <SelectItem value="popular">Popular</SelectItem>
                        <SelectItem value="trending">Trending</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="search"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Search</FormLabel>
                    <FormControl>
                      <div className="relative">
                        <Input
                          placeholder="Search by keyword"
                          {...field}
                        />
                        {field.value && (
                          <Button
                            type="button"
                            variant="ghost"
                            size="icon"
                            className="absolute right-0 top-0 h-full"
                            onClick={() => {
                              field.onChange("")
                              setSearch("")
                            }}
                          >
                            <X className="h-4 w-4" />
                            <span className="sr-only">Clear</span>
                          </Button>
                        )}
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <div className="flex flex-col gap-2 pt-4">
                <Button type="submit" disabled={isPending}>
                  Apply Filters
                </Button>
                {activeFilters > 0 && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={clearFilters}
                    disabled={isPending}
                  >
                    Clear Filters
                  </Button>
                )}
              </div>
            </form>
          </Form>
        </SheetContent>
      </Sheet>
    </div>
  )
} 