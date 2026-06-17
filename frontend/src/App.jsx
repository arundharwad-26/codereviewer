import { BrowserRouter } from "react-router-dom";
import { useEffect } from "react";
import useAuthStore from "./store/authStore";
import AppRoutes from "./routes";
import Navbar from "./components/Navbar";

function App() {
  const initAuth = useAuthStore((state) => state.initAuth);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  // Initialize auth state from localStorage on app load
  useEffect(() => {
    initAuth();
  }, []);

  return (
    <BrowserRouter>
      {isAuthenticated && <Navbar />}
      <AppRoutes />
    </BrowserRouter>
  );
}

export default App;