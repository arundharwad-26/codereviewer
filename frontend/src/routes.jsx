import { Routes, Route, Navigate } from "react-router-dom";
import useAuthStore from "./store/authStore";

// Pages
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import ReviewDetailPage from "./pages/ReviewDetailPage";
import RepositoriesPage from "./pages/RepositoriesPage";

// Auth Guard — protects routes that require login
const AuthGuard = ({ children }) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

const AppRoutes = () => {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<LoginPage />} />

      {/* OAuth callback — handles JWT from backend */}
      <Route
        path="/auth/callback"
        element={<AuthCallbackPage />}
      />

      {/* Protected routes */}
      <Route
        path="/dashboard"
        element={
          <AuthGuard>
            <DashboardPage />
          </AuthGuard>
        }
      />
      <Route
        path="/reviews/:id"
        element={
          <AuthGuard>
            <ReviewDetailPage />
          </AuthGuard>
        }
      />
      <Route
        path="/repos"
        element={
          <AuthGuard>
            <RepositoriesPage />
          </AuthGuard>
        }
      />

      {/* Default redirect */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};

// Auth callback page — reads token from URL and saves it
const AuthCallbackPage = () => {
  const setAuth = useAuthStore((state) => state.setAuth);

  const params = new URLSearchParams(window.location.search);
  const token = params.get("token");
  const username = params.get("username");
  const avatar_url = params.get("avatar_url");

  if (token) {
    setAuth(
      { username, avatar_url },
      token
    );
    window.location.href = "/dashboard";
  } else {
    window.location.href = "/login";
  }

  return <div>Redirecting...</div>;
};

export default AppRoutes;