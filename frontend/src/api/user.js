import api from "./auth";

export const getUserProfile = async () => {
	try {
		const response = await api.get("/users/me");
		return response.data;
	} catch (error) {
		throw (
			error.response?.data || { detail: "Failed to fetch user profile" }
		);
	}
};

export const updateUserProfile = async (userData) => {
	try {
		const response = await api.put("/users/me", userData);
		return response.data;
	} catch (error) {
		throw (
			error.response?.data || { detail: "Failed to update user profile" }
		);
	}
};

export const changePassword = async (passwordData) => {
	try {
		const response = await api.post("/users/me/password", passwordData);
		return response.data;
	} catch (error) {
		throw error.response?.data || { detail: "Failed to change password" };
	}
};
