import axios from "axios";

const API_URL =
	process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Create axios instance with base configuration
const api = axios.create({
	baseURL: API_URL,
	headers: {
		"Content-Type": "application/json",
	},
});

// Add token to request if available
api.interceptors.request.use(
	(config) => {
		const token = localStorage.getItem("token");
		if (token) {
			config.headers["Authorization"] = `Bearer ${token}`;
		}
		return config;
	},
	(error) => Promise.reject(error)
);

export const loginUser = async (email, password) => {
	try {
		const response = await api.post(
			"/auth/login/access-token",
			new URLSearchParams({
				username: email,
				password: password,
			}),
			{
				headers: {
					"Content-Type": "application/x-www-form-urlencoded",
				},
			}
		);
		return response.data;
	} catch (error) {
		throw error.response?.data || { detail: "Login failed" };
	}
};

export const registerUser = async (userData) => {
	try {
		const response = await api.post("/users/signup", userData);
		return response.data;
	} catch (error) {
		throw error.response?.data || { detail: "Registration failed" };
	}
};

export const getCurrentUser = async () => {
	try {
		const response = await api.get("/users/me");
		return response.data;
	} catch (error) {
		throw error.response?.data || { detail: "Failed to get user data" };
	}
};

export const logoutUser = () => {
	localStorage.removeItem("token");
};

export default api;
