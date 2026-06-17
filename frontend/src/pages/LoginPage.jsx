const LoginPage = () => {
  const handleGitHubLogin = () => {
    window.location.href = "http://localhost:8000/api/auth/github";
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.logo}>🤖</div>
        <h1 style={styles.title}>CodeReviewer</h1>
        <p style={styles.subtitle}>
          AI-Powered Code Review Platform
        </p>
        <p style={styles.description}>
          Automatically review your GitHub Pull Requests
          using advanced AI agents. Get instant feedback
          on code quality and security.
        </p>
        <button onClick={handleGitHubLogin} style={styles.button}>
          <span style={styles.githubIcon}>🐙</span>
          Sign in with GitHub
        </button>
        <p style={styles.note}>
          We only request access to your repositories
          and email address.
        </p>
      </div>
    </div>
  );
};

const styles = {
  container: {
    minHeight: "100vh",
    backgroundColor: "#11111b",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "20px",
  },
  card: {
    backgroundColor: "#1e1e2e",
    border: "1px solid #313244",
    borderRadius: "16px",
    padding: "48px 40px",
    textAlign: "center",
    maxWidth: "420px",
    width: "100%",
  },
  logo: {
    fontSize: "64px",
    marginBottom: "16px",
  },
  title: {
    color: "#cba6f7",
    fontSize: "32px",
    fontWeight: "bold",
    margin: "0 0 8px 0",
  },
  subtitle: {
    color: "#89b4fa",
    fontSize: "16px",
    margin: "0 0 24px 0",
  },
  description: {
    color: "#a6adc8",
    fontSize: "14px",
    lineHeight: "1.6",
    margin: "0 0 32px 0",
  },
  button: {
    backgroundColor: "#cba6f7",
    color: "#1e1e2e",
    border: "none",
    padding: "14px 28px",
    borderRadius: "8px",
    fontSize: "16px",
    fontWeight: "bold",
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    gap: "10px",
    margin: "0 auto 16px auto",
    width: "100%",
    justifyContent: "center",
  },
  githubIcon: {
    fontSize: "20px",
  },
  note: {
    color: "#6c7086",
    fontSize: "12px",
    margin: "0",
  },
};

export default LoginPage;