const SeverityBadge = ({ severity }) => {
  const getColor = () => {
    switch (severity) {
      case "critical": return "#f38ba8";
      case "high": return "#fab387";
      case "medium": return "#f9e2af";
      case "low": return "#a6e3a1";
      default: return "#6c7086";
    }
  };

  return (
    <span style={{
      backgroundColor: getColor(),
      color: "#1e1e2e",
      padding: "3px 8px",
      borderRadius: "8px",
      fontSize: "11px",
      fontWeight: "bold",
      textTransform: "uppercase",
    }}>
      {severity || "unknown"}
    </span>
  );
};

export default SeverityBadge;