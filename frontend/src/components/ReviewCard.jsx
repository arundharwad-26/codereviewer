import { Link } from "react-router-dom";
import ScoreBadge from "./ScoreBadge";
import StatusChip from "./StatusChip";

const ReviewCard = ({ id, pr_number, pull_request, status, overall_score, triggered_at }) => {
  const repoName = pull_request?.repository?.full_name || "Unknown Repo";
  const prTitle = pull_request?.title || `PR #${pr_number}`;
  const author = pull_request?.author || "Unknown";
  const date = triggered_at
    ? new Date(triggered_at).toLocaleDateString()
    : "Unknown date";

  return (
    <div style={styles.card}>
      <div style={styles.header}>
        <div style={styles.prInfo}>
          <span style={styles.prNumber}>PR #{pull_request?.pr_number || pr_number}</span>
          <span style={styles.repoName}>{repoName}</span>
        </div>
        <StatusChip status={status} />
      </div>

      <p style={styles.title}>{prTitle}</p>

      <div style={styles.footer}>
        <div style={styles.meta}>
          <span style={styles.author}>👤 {author}</span>
          <span style={styles.date}>📅 {date}</span>
        </div>
        <div style={styles.actions}>
          {overall_score !== null && overall_score !== undefined && (
            <ScoreBadge score={overall_score} />
          )}
          <Link to={`/reviews/${id}`} style={styles.link}>
            View Details →
          </Link>
        </div>
      </div>
    </div>
  );
};

const styles = {
  card: {
    backgroundColor: "#1e1e2e",
    border: "1px solid #313244",
    borderRadius: "10px",
    padding: "16px",
    marginBottom: "12px",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "8px",
  },
  prInfo: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
  },
  prNumber: {
    color: "#cba6f7",
    fontWeight: "bold",
    fontSize: "14px",
  },
  repoName: {
    color: "#89b4fa",
    fontSize: "13px",
  },
  title: {
    color: "#cdd6f4",
    fontSize: "15px",
    margin: "0 0 12px 0",
  },
  footer: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  meta: {
    display: "flex",
    gap: "16px",
  },
  author: {
    color: "#a6adc8",
    fontSize: "13px",
  },
  date: {
    color: "#a6adc8",
    fontSize: "13px",
  },
  actions: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
  },
  link: {
    color: "#89b4fa",
    textDecoration: "none",
    fontSize: "13px",
    fontWeight: "bold",
  },
};

export default ReviewCard;