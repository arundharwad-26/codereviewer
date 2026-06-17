import { useEffect, useState } from "react";
import { getRepos, connectRepo } from "../api/reposApi";

const RepositoriesPage = () => {
  const [repos, setRepos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newRepo, setNewRepo] = useState("");
  const [connecting, setConnecting] = useState(false);
  const [connectError, setConnectError] = useState(null);
  const [connectSuccess, setConnectSuccess] = useState(null);

  useEffect(() => {
    fetchRepos();
  }, []);

  const fetchRepos = async () => {
    setLoading(true);
    try {
      const data = await getRepos();
      setRepos(data.items);
    } catch (err) {
      setError("Failed to load repositories");
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async () => {
    if (!newRepo.trim()) return;
    setConnecting(true);
    setConnectError(null);
    setConnectSuccess(null);
    try {
      await connectRepo(newRepo.trim());
      setConnectSuccess(`${newRepo} connected successfully`);
      setNewRepo("");
      fetchRepos();
    } catch (err) {
      setConnectError(
        err.response?.data?.detail || "Failed to connect repository"
      );
    } finally {
      setConnecting(false);
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Repositories</h1>

      {/* Connect new repo */}
      <div style={styles.connectBox}>
        <h2 style={styles.connectTitle}>Connect a Repository</h2>
        <p style={styles.connectHint}>
          Enter the repository in owner/repo-name format
        </p>
        <div style={styles.inputRow}>
          <input
            type="text"
            value={newRepo}
            onChange={(e) => setNewRepo(e.target.value)}
            placeholder="e.g. facebook/react"
            style={styles.input}
            onKeyDown={(e) => e.key === "Enter" && handleConnect()}
          />
          <button
            onClick={handleConnect}
            disabled={connecting}
            style={styles.connectButton}
          >
            {connecting ? "Connecting..." : "Connect"}
          </button>
        </div>
        {connectError && (
          <p style={styles.connectError}>{connectError}</p>
        )}
        {connectSuccess && (
          <p style={styles.connectSuccess}>✅ {connectSuccess}</p>
        )}
      </div>

      {/* Repository list */}
      {loading && (
        <p style={styles.loading}>Loading repositories...</p>
      )}

      {error && (
        <p style={styles.error}>{error}</p>
      )}

      {!loading && repos.length === 0 && (
        <div style={styles.empty}>
          <p style={styles.emptyText}>No repositories connected yet.</p>
          <p style={styles.emptyHint}>
            Connect a repository above to start reviewing Pull Requests.
          </p>
        </div>
      )}

      {!loading && repos.map((repo) => (
        <div key={repo.id} style={styles.repoCard}>
          <div style={styles.repoHeader}>
            <span style={styles.repoName}>{repo.full_name}</span>
            <span style={styles.repoBadge}>
              {repo.is_private ? "🔒 Private" : "🌐 Public"}
            </span>
          </div>
          <div style={styles.repoMeta}>
            {repo.language && (
              <span style={styles.language}>
                💻 {repo.language}
              </span>
            )}
            <span style={styles.connectedAt}>
              Connected {new Date(repo.created_at).toLocaleDateString()}
            </span>
          </div>
        </div>
      ))}
    </div>
  );
};

const styles = {
  container: {
    maxWidth: "800px",
    margin: "0 auto",
    padding: "32px 24px",
    backgroundColor: "#11111b",
    minHeight: "100vh",
  },
  title: {
    color: "#cdd6f4",
    fontSize: "28px",
    margin: "0 0 32px 0",
  },
  connectBox: {
    backgroundColor: "#1e1e2e",
    border: "1px solid #313244",
    borderRadius: "10px",
    padding: "24px",
    marginBottom: "32px",
  },
  connectTitle: {
    color: "#cba6f7",
    fontSize: "18px",
    margin: "0 0 8px 0",
  },
  connectHint: {
    color: "#a6adc8",
    fontSize: "13px",
    margin: "0 0 16px 0",
  },
  inputRow: {
    display: "flex",
    gap: "12px",
  },
  input: {
    flex: 1,
    backgroundColor: "#11111b",
    border: "1px solid #313244",
    borderRadius: "6px",
    padding: "10px 14px",
    color: "#cdd6f4",
    fontSize: "14px",
    outline: "none",
  },
  connectButton: {
    backgroundColor: "#cba6f7",
    color: "#1e1e2e",
    border: "none",
    padding: "10px 20px",
    borderRadius: "6px",
    fontSize: "14px",
    fontWeight: "bold",
    cursor: "pointer",
  },
  connectError: {
    color: "#f38ba8",
    fontSize: "13px",
    margin: "8px 0 0 0",
  },
  connectSuccess: {
    color: "#a6e3a1",
    fontSize: "13px",
    margin: "8px 0 0 0",
  },
  loading: {
    color: "#89b4fa",
    textAlign: "center",
  },
  error: {
    color: "#f38ba8",
    textAlign: "center",
  },
  empty: {
    textAlign: "center",
    padding: "48px",
    backgroundColor: "#1e1e2e",
    borderRadius: "10px",
    border: "1px solid #313244",
  },
  emptyText: {
    color: "#cdd6f4",
    fontSize: "18px",
    margin: "0 0 8px 0",
  },
  emptyHint: {
    color: "#a6adc8",
    fontSize: "14px",
    margin: "0",
  },
  repoCard: {
    backgroundColor: "#1e1e2e",
    border: "1px solid #313244",
    borderRadius: "10px",
    padding: "16px",
    marginBottom: "12px",
  },
  repoHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "8px",
  },
  repoName: {
    color: "#89b4fa",
    fontSize: "16px",
    fontWeight: "bold",
  },
  repoBadge: {
    color: "#a6adc8",
    fontSize: "12px",
  },
  repoMeta: {
    display: "flex",
    gap: "16px",
  },
  language: {
    color: "#cba6f7",
    fontSize: "13px",
  },
  connectedAt: {
    color: "#6c7086",
    fontSize: "13px",
  },
};

export default RepositoriesPage;