import { useEffect } from "react";
import { getReviews } from "../api/reviewsApi";
import { getRepos } from "../api/reposApi";
import useReviewStore from "../store/reviewStore";
import useAuthStore from "../store/authStore";
import ReviewCard from "../components/ReviewCard";

const DashboardPage = () => {
  const user = useAuthStore((state) => state.user);
  const { reviews, loading, error, total, setReviews, setLoading, setError } =
    useReviewStore();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const data = await getReviews(1, 10);
        setReviews(data.items, data.total);
      } catch (err) {
        setError("Failed to load reviews");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>
          Welcome back, {user?.username || "Developer"} 👋
        </h1>
        <p style={styles.subtitle}>
          {total} total reviews
        </p>
      </div>

      {loading && (
        <p style={styles.loading}>Loading reviews...</p>
      )}

      {error && (
        <p style={styles.error}>{error}</p>
      )}

      {!loading && !error && reviews.length === 0 && (
        <div style={styles.empty}>
          <p style={styles.emptyText}>No reviews yet.</p>
          <p style={styles.emptyHint}>
            Connect a repository and open a Pull Request to get started.
          </p>
        </div>
      )}

      {!loading && reviews.map((review) => (
        <ReviewCard
          key={review.id}
          id={review.id}
          pr_number={review.pull_request?.pr_number}
          pull_request={review.pull_request}
          status={review.status}
          overall_score={review.overall_score}
          triggered_at={review.triggered_at}
        />
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
  header: {
    marginBottom: "32px",
  },
  title: {
    color: "#cdd6f4",
    fontSize: "28px",
    margin: "0 0 8px 0",
  },
  subtitle: {
    color: "#a6adc8",
    fontSize: "14px",
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
};

export default DashboardPage;