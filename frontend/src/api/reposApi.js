import api from "./api";

// Get all connected repositories
export const getRepos = async () => {
  const response = await api.get("/api/repos");
  return response.data;
};

// Connect a new repository
export const connectRepo = async (fullName) => {
  const response = await api.post("/api/repos", { full_name: fullName });
  return response.data;
};

// Get repository stats
export const getRepoStats = async (repoId) => {
  const response = await api.get(`/api/repos/${repoId}/stats`);
  return response.data;
};