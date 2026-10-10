import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "@/lib/auth-context";

export function RequireAuth() {
  const { user, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <div className="py-20 text-center text-muted-foreground">Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <Outlet />;
}