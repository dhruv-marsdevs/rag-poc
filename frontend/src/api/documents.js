import api from "./auth";

export const fetchDocuments = async () => {
	try {
		const response = await api.get("/documents");
		return response.data;
	} catch (error) {
		throw error.response?.data || { detail: "Failed to fetch documents" };
	}
};

export const uploadDocument = async (file, onProgress) => {
	try {
		const formData = new FormData();
		formData.append("file", file);

		const response = await api.post("/documents/upload", formData, {
			headers: {
				"Content-Type": "multipart/form-data",
			},
			onUploadProgress: (progressEvent) => {
				if (onProgress) {
					const percentCompleted = Math.round(
						(progressEvent.loaded * 100) / progressEvent.total
					);
					onProgress(percentCompleted);
				}
			},
		});
		return response.data;
	} catch (error) {
		throw error.response?.data || { detail: "Upload failed" };
	}
};

export const scrapeWebsite = async (data) => {
	try {
		const response = await api.post("/documents/scrape-website", data);
		return response.data;
	} catch (error) {
		throw error.response?.data || { detail: "Website scraping failed" };
	}
};

export const getDocuments = async () => {
	try {
		const response = await api.get("/documents");
		return response.data;
	} catch (error) {
		throw error.response?.data || { detail: "Failed to fetch documents" };
	}
};

export const deleteDocument = async (documentId) => {
	try {
		await api.delete(`/documents/${documentId}`);
		return true;
	} catch (error) {
		throw error.response?.data || { detail: "Failed to delete document" };
	}
};
