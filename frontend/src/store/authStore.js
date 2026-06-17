import { create } from "zustand";

const useAuthStore = create((set) => ({
  // State
  user: null,
  token: null,
  isAuthenticated: false,

  // Actions
  setAuth: (user, token) => {
    localStorage.setItem("access_token", token);
    set({
      user,
      token,
      isAuthenticated: true,
    });
  },

  clearAuth: () => {
    localStorage.removeItem("access_token");
    set({
      user: null,
      token: null,
      isAuthenticated: false,
    });
  },

  // Initialize from localStorage on app load
  initAuth: () => {
    const token = localStorage.getItem("access_token");
    if (token) {
      set({
        token,
        isAuthenticated: true,
      });
    }
  },
}));

export default useAuthStore;