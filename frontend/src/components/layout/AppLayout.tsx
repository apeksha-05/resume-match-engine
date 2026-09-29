import { Target } from "lucide-react";
import { Link, NavLink, Outlet } from "react-router-dom";
import { cn } from "@/lib/utils";

const navItems = [
  { to: "/analyze", label: "New Analysis" },
  { to: "/jobs", label: "Jobs" },
  { to: "/history", label: "History" },
  { to: "/results/demo", label: "Demo" },
  { to: "/settings", label: "Privacy" },
];

export function AppLayout() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-10 border-b bg-background/95 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center gap-6 px-4 py-3">
          <Link to="/" className="flex items-center gap-2 font-semibold">
            <Target className="size-5" />
            <span>ResumeMatch</span>
          </Link>
          <nav className="flex gap-1 overflow-x-auto">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cn(
                    "whitespace-nowrap rounded-md px-3 py-1.5 text-sm transition-colors hover:bg-muted",
                    isActive
                      ? "bg-muted font-medium text-foreground"
                      : "text-muted-foreground",
                  )
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8">
        <Outlet />
      </main>

      <footer className="border-t py-4 text-center text-xs text-muted-foreground">
        Scores are estimated fit indicators, not hiring probabilities. Sample
        jobs and data are fictional demo data.
      </footer>
    </div>
  );
}