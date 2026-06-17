import SeverityBadge from "./SeverityBadge";

const AgentResultPanel = ({ agent_type, raw_output }) => {
  const isCodeReview = agent_type === "code_review";

  return (
    <div style={styles.panel}>
      <h3 style={styles.title}>
        {isCodeReview ? "📋 Code Review" : "🔒 Security Analysis"}
      </h3>

      <p style={styles.summary}>
        {raw_output?.summary || "No summary available"}
      </p>

      {isCodeReview && raw_output?.issues?.length > 0 && (
        <div>
          <h4 style={styles.subTitle}>Issues Found ({raw_output.issues.length})</h4>
          {raw_output.issues.map((issue, index) => (
            <div key={index} style={styles.item}>
              <div style={styles.itemHeader}>
                <span style={styles.file}>📄 {issue.file}</span>
                {issue.line && (
                  <span style={styles.line}>Line {issue.line}</span>
                )}
                <SeverityBadge severity={issue.severity} />
              </div>
              <p style={styles.message}>{issue.message}</p>
              {issue.suggestion && (
                <p style={styles.suggestion}>
                  💡 {issue.suggestion}
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {!isCodeReview && raw_output?.vulnerabilities?.length > 0 && (
        <div>
          <h4 style={styles.subTitle}>
            Vulnerabilities Found ({raw_output.vulnerabilities.length})
          </h4>
          {raw_output.vulnerabilities.map((vuln, index) => (
            <div key={index} style={styles.item}>
              <div style={styles.itemHeader}>
                <span style={styles.file}>📄 {vuln.file}</span>
                {vuln.line && (
                  <span style={styles.line}>Line {vuln.line}</span>
                )}
                <SeverityBadge severity={vuln.severity} />
              </div>
              <p style={styles.message}>{vuln.description}</p>
              {vuln.recommendation && (
                <p style={styles.suggestion}>
                  🔧 {vuln.recommendation}
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {isCodeReview && raw_output?.issues?.length === 0 && (
        <p style={styles.noIssues}>✅ No issues found</p>
      )}

      {!isCodeReview && raw_output?.vulnerabilities?.length === 0 && (
        <p style={styles.noIssues}>✅ No vulnerabilities found</p>
      )}
    </div>
  );
};

const styles = {
  panel: {
    backgroundColor: "#181825",
    border: "1px solid #313244",
    borderRadius: "10px",
    padding: "20px",
    marginBottom: "16px",
  },
  title: {
    color: "#cba6f7",
    fontSize: "18px",
    marginBottom: "10px",
  },
  summary: {
    color: "#cdd6f4",
    fontSize: "14px",
    marginBottom: "16px",
    lineHeight: "1.6",
  },
  subTitle: {
    color: "#89b4fa",
    fontSize: "15px",
    marginBottom: "10px",
  },
  item: {
    backgroundColor: "#1e1e2e",
    border: "1px solid #313244",
    borderRadius: "8px",
    padding: "12px",
    marginBottom: "10px",
  },
  itemHeader: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    marginBottom: "6px",
    flexWrap: "wrap",
  },
  file: {
    color: "#89b4fa",
    fontSize: "13px",
    fontFamily: "monospace",
  },
  line: {
    color: "#a6adc8",
    fontSize: "12px",
  },
  message: {
    color: "#cdd6f4",
    fontSize: "13px",
    margin: "4px 0",
  },
  suggestion: {
    color: "#a6e3a1",
    fontSize: "13px",
    margin: "4px 0",
    fontStyle: "italic",
  },
  noIssues: {
    color: "#a6e3a1",
    fontSize: "14px",
  },
};

export default AgentResultPanel;