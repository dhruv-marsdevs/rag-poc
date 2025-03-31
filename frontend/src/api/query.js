import api from "./auth";

export const queryDocuments = async (query) => {
	try {
		const response = await api.post("/query", { query });
		return response.data;
	} catch (error) {
		throw error.response?.data || { detail: "Query failed" };
	}
};
