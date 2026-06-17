const ScoreBadge = ({ score }) => {
  const getColor = () => {
    if (score >= 80) return "#a6e3a1";
    if (score >= 50) return "#f9e2af";
    return "#f38ba8";
  };

  return (
    <span style={{
      backgroundColor: getColor(),
      color: "#1e1e2e",
      padding: "4px 10px",
      borderRadius: "12px",
      fontWeight: "bold",
      fontSize: "13px",
    }}>
      {score !== null && score !== undefined ? `${score}/100` : "N/A"}
    </span>
  );
};

export default ScoreBadge;