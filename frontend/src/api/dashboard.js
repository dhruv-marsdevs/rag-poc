import api from "./auth";

export const getDashboardStats = async () => {
	try {
		const response = await api.get("/system/stats");
		return response.data;
	} catch (error) {
		throw (
			error.response?.data || {
				detail: "Failed to fetch dashboard statistics",
			}
		);
	}
};
