import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getReview, retryReview } from "../api/reviewsApi";
import AgentResultPanel from "../components/AgentResultPanel";
import ScoreBadge from "../components/ScoreBadge";
import StatusChip from "../components/StatusChip";

const ReviewDetailPage = () => {
  const { id } = useParams();
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retrying, setRetrying] = useState(false);

  useEffect(() => {
    const fetchReview = async () => {
      setLoading(true);
      try {
        const data = await getReview(id);
        setReview(data);
      } catch (err) {
        setError("Failed to load review");
      } finally {
        setLoading(false);
      }
    };

    fetchReview();
  }, [id]);

  const handleRetry = async () => {
    setRetrying(true);
    try {
      await retryReview(id);
      // Refresh review after retry
      const data = await getReview(id);
      setReview(data);
    } catch (err) {
      setError("Failed to retry review");
    } finally {
      setRetrying(false);
    }
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <p style={styles.loading}>Loading review...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.container}>
        <p style={styles.error}>{error}</p>
      </div>
    );
  }

  if (!review) return null;

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerTop}>
          <h1 style={styles.title}>
            PR #{review.pull_request?.pr_number} — {review.pull_request?.title}
          </h1>
          <StatusChip status={review.status} />
        </div>
        <div style={styles.meta}>
          <span style={styles.metaItem}>
            👤 {review.pull_request?.author}
          </span>
          <span style={styles.metaItem}>
            🌿 {review.pull_request?.base_branch}
          </span>
          <span style={styles.metaItem}>
            📅 {new Date(review.triggered_at).toLocaleDateString()}
          </span>
        </div>
      </div>

      {/* Score */}
      {review.overall_score !== null && review.overall_score !== undefined && (
        <div style={styles.scoreSection}>
          <span style={styles.scoreLabel}>Overall Score</span>
          <ScoreBadge score={review.overall_score} />
        </div>
      )}

      {/* Error message */}
      {review.error_message && (
        <div style={styles.errorBox}>
          <p style={styles.errorText}>❌ {review.error_message}</p>
        </div>
      )}

      {/* Retry button */}
      {review.status === "failed" && (
        <button
          onClick={handleRetry}
          disabled={retrying}
          style={styles.retryButton}
        >
          {retrying ? "Retrying..." : "🔄 Retry Review"}
        </button>
      )}

      {/* Agent Results */}
      {review.agent_results && review.agent_results.length > 0 && (
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>Agent Results</h2>
          {review.agent_results.map((result) => (
            <AgentResultPanel
              key={result.id}
              agent_type={result.agent_type}
              raw_output={result.raw_output}
            />
          ))}
        </div>
      )}

      {/* Pending or processing */}
      {(review.status === "pending" || review.status === "processing") && (
        <div style={styles.processingBox}>
          <p style={styles.processingText}>
            ⏳ Review is being processed. Refresh the page in a moment.
          </p>
        </div>
      )}
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
  header: {
    marginBottom: "24px",
  },
  headerTop: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: "16px",
    marginBottom: "12px",
  },
  title: {
    color: "#cdd6f4",
    fontSize: "22px",
    margin: "0",
    flex: 1,
  },
  meta: {
    display: "flex",
    gap: "16px",
    flexWrap: "wrap",
  },
  metaItem: {
    color: "#a6adc8",
    fontSize: "13px",
  },
  scoreSection: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
    marginBottom: "24px",
    padding: "16px",
    backgroundColor: "#1e1e2e",
    borderRadius: "8px",
    border: "1px solid #313244",
  },
  scoreLabel: {
    color: "#cdd6f4",
    fontSize: "15px",
    fontWeight: "bold",
  },
  errorBox: {
    backgroundColor: "#2a1a1a",
    border: "1px solid #f38ba8",
    borderRadius: "8px",
    padding: "12px 16px",
    marginBottom: "16px",
  },
  errorText: {
    color: "#f38ba8",
    fontSize: "14px",
    margin: "0",
  },
  retryButton: {
    backgroundColor: "#f9e2af",
    color: "#1e1e2e",
    border: "none",
    padding: "10px 20px",
    borderRadius: "8px",
    fontSize: "14px",
    fontWeight: "bold",
    cursor: "pointer",
    marginBottom: "24px",
  },
  section: {
    marginBottom: "24px",
  },
  sectionTitle: {
    color: "#cba6f7",
    fontSize: "20px",
    marginBottom: "16px",
  },
  processingBox: {
    backgroundColor: "#1e1e2e",
    border: "1px solid #89b4fa",
    borderRadius: "8px",
    padding: "24px",
    textAlign: "center",
  },
  processingText: {
    color: "#89b4fa",
    fontSize: "15px",
    margin: "0",
  },
  loading: {
    color: "#89b4fa",
    textAlign: "center",
    fontSize: "16px",
  },
  error: {
    color: "#f38ba8",
    textAlign: "center",
    fontSize: "16px",
  },
};

export default ReviewDetailPage;