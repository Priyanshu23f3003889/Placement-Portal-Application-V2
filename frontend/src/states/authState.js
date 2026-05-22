import { defineStore } from "pinia";

export const useAuthStore = defineStore("auth", {
  state: () => {
    let token = localStorage.getItem("token") || null;
    let role = null;

    if (token) {
      try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        role = payload.role;
      } catch (e) {
        token = null;
        localStorage.removeItem("token");
      }
    }

    return {
      token,
      role,
    };
  },

  actions: {
    async login(email, password) {
      try {
        const response = await fetch("/api/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });

        if (response.ok) {
          const data = await response.json();

          this.token = data.access_token;
          this.role = JSON.parse(atob(this.token.split(".")[1])).role;

          localStorage.setItem("token", this.token);

          return true;
        } else {
          let errorMessage = "An error occurred during login.";
          try {
            const errorData = await response.json();
            errorMessage = errorData.message || errorMessage;
          } catch (e) {
            errorMessage = `Server Error (${response.status})`;
          }
          throw new Error(errorMessage);
        }
      } catch (error) {
        console.error("Login failed:", error.message);
        throw error;
      }
    },

    async register(data) {
      try {
        const response = await fetch("/api/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        });

        if (response.ok) {
          return true;
        } else {
          let errorMessage = "An error occurred during registration.";
          try {
            const errorData = await response.json();
            errorMessage = errorData.message || errorMessage;
          } catch (e) {
            errorMessage = `Server Error (${response.status})`;
          }
          throw new Error(errorMessage);
        }
      } catch (error) {
        console.error("Registration failed:", error.message);
        throw error;
      }
    },

    async logout() {
      this.token = null;
      this.role = null;
      localStorage.removeItem("token");
    },
  },
});
