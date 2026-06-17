const StatusChip = ({ status }) => {
  const getStyle = () => {
    switch (status) {
      case "completed":
        return { backgroundColor: "#a6e3a1", color: "#1e1e2e" };
      case "processing":
        return { backgroundColor: "#89b4fa", color: "#1e1e2e" };
      case "pending":
        return { backgroundColor: "#6c7086", color: "#cdd6f4" };
      case "failed":
        return { backgroundColor: "#f38ba8", color: "#1e1e2e" };
      default:
        return { backgroundColor: "#6c7086", color: "#cdd6f4" };
    }
  };

  return (
    <span style={{
      ...getStyle(),
      padding: "4px 10px",
      borderRadius: "12px",
      fontSize: "12px",
      fontWeight: "bold",
      textTransform: "uppercase",
    }}>
      {status === "processing" ? "⏳ " : ""}
      {status}
    </span>
  );
};

export default StatusChip;