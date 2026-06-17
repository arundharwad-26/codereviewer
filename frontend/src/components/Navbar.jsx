import { Link, useNavigate } from "react-router-dom";
import useAuthStore from "../store/authStore";

const Navbar = () => {
  const user = useAuthStore((state) => state.user);
  const clearAuth = useAuthStore((state) => state.clearAuth);
  const navigate = useNavigate();

  const handleLogout = () => {
    clearAuth();
    navigate("/login");
  };

  return (
    <nav style={styles.nav}>
      <div style={styles.left}>
        <Link to="/dashboard" style={styles.brand}>
          🤖 CodeReviewer
        </Link>
        <Link to="/dashboard" style={styles.link}>
          Dashboard
        </Link>
        <Link to="/repos" style={styles.link}>
          Repositories
        </Link>
      </div>
      <div style={styles.right}>
        {user && (
          <span style={styles.username}>
            👤 {user.username}
          </span>
        )}
        <button onClick={handleLogout} style={styles.button}>
          Logout
        </button>
      </div>
    </nav>
  );
};

const styles = {
  nav: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "12px 24px",
    backgroundColor: "#1e1e2e",
    borderBottom: "1px solid #313244",
  },
  left: {
    display: "flex",
    alignItems: "center",
    gap: "24px",
  },
  brand: {
    color: "#cba6f7",
    textDecoration: "none",
    fontWeight: "bold",
    fontSize: "18px",
  },
  link: {
    color: "#cdd6f4",
    textDecoration: "none",
    fontSize: "14px",
  },
  right: {
    display: "flex",
    alignItems: "center",
    gap: "16px",
  },
  username: {
    color: "#a6e3a1",
    fontSize: "14px",
  },
  button: {
    backgroundColor: "#f38ba8",
    color: "#1e1e2e",
    border: "none",
    padding: "6px 14px",
    borderRadius: "6px",
    cursor: "pointer",
    fontWeight: "bold",
    fontSize: "13px",
  },
};

export default Navbar;