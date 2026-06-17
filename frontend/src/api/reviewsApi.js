import api from "./api";

// Get paginated list of reviews
export const getReviews = async (page = 1, limit = 10, status = null) => {
  const params = { page, limit };
  if (status) params.status = status;

  const response = await api.get("/api/reviews", { params });
  return response.data;
};

// Get single review detail
export const getReview = async (reviewId) => {
  const response = await api.get(`/api/reviews/${reviewId}`);
  return response.data;
};

// Get comments for a review
export const getReviewComments = async (reviewId) => {
  const response = await api.get(`/api/reviews/${reviewId}/comments`);
  return response.data;
};

// Retry a failed review
export const retryReview = async (reviewId) => {
  const response = await api.post(`/api/reviews/${reviewId}/retry`);
  return response.data;
};