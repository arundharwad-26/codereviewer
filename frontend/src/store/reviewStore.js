import { create } from "zustand";

const useReviewStore = create((set) => ({
  // State
  reviews: [],
  selectedReview: null,
  loading: false,
  error: null,
  total: 0,
  page: 1,
  limit: 10,

  // Actions
  setReviews: (reviews, total) => set({
    reviews,
    total,
  }),

  setSelectedReview: (review) => set({
    selectedReview: review,
  }),

  setLoading: (loading) => set({ loading }),

  setError: (error) => set({ error }),

  setPage: (page) => set({ page }),

  clearSelectedReview: () => set({
    selectedReview: null,
  }),

  clearError: () => set({
    error: null,
  }),
}));

export default useReviewStore;