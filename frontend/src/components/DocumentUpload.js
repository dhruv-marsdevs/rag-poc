"use client";

import React, { useState } from "react";
import { Upload, Button, message, Progress, Modal } from "antd";
import {
	UploadOutlined,
	FileTextOutlined,
	FilePdfOutlined,
	FileExcelOutlined,
} from "@ant-design/icons";
import { uploadDocument } from "../api/documents";

const DocumentUpload = ({ onUploadSuccess }) => {
	const [uploading, setUploading] = useState(false);
	const [progress, setProgress] = useState(0);
	const [fileList, setFileList] = useState([]);
	const [previewOpen, setPreviewOpen] = useState(false);
	const [previewTitle, setPreviewTitle] = useState("");

	const handleUpload = async () => {
		if (fileList.length === 0) {
			message.warning("Please select a file to upload");
			return;
		}

		const file = fileList[0];
		setUploading(true);
		setProgress(0);

		try {
			await uploadDocument(file, setProgress);
			setFileList([]);
			message.success(`${file.name} uploaded successfully`);

			if (onUploadSuccess) {
				onUploadSuccess();
			}
		} catch (error) {
			console.error("Upload error:", error);
			message.error(`${file.name} upload failed. ${error.detail || ""}`);
		} finally {
			setUploading(false);
		}
	};

	const props = {
		onRemove: () => {
			setFileList([]);
		},
		beforeUpload: (file) => {
			// Check file type
			const isPDF = file.type === "application/pdf";
			const isWord =
				file.type ===
					"application/vnd.openxmlformats-officedocument.wordprocessingml.document" ||
				file.type === "application/msword";

			if (!isPDF && !isWord) {
				message.error("You can only upload PDF or Word documents!");
				return Upload.LIST_IGNORE;
			}

			// Check file size (10MB max)
			const isLt10M = file.size / 1024 / 1024 < 10;
			if (!isLt10M) {
				message.error("File must be smaller than 10MB!");
				return Upload.LIST_IGNORE;
			}

			// Add to fileList
			setFileList([file]);
			return false; // Prevent automatic upload
		},
		fileList,
	};

	// Get icon based on file type
	const getFileIcon = (file) => {
		if (!file) return <FileTextOutlined />;

		if (file.type === "application/pdf") {
			return <FilePdfOutlined style={{ color: "#ff4d4f" }} />;
		} else if (file.type.includes("word")) {
			return <FileTextOutlined style={{ color: "#1890ff" }} />;
		}

		return <FileTextOutlined />;
	};

	return (
		<div className="upload-container">
			<Upload
				{...props}
				maxCount={1}
				listType="text"
			>
				<Button icon={<UploadOutlined />}>Select File</Button>
			</Upload>

			{fileList.length > 0 && (
				<div className="mt-4">
					<div className="flex items-center mb-2">
						{getFileIcon(fileList[0])}
						<span className="ml-2">{fileList[0].name}</span>
					</div>

					<Button
						type="primary"
						onClick={handleUpload}
						disabled={fileList.length === 0}
						loading={uploading}
						className="mt-2"
					>
						{uploading ? "Uploading" : "Upload Document"}
					</Button>
				</div>
			)}

			{uploading && (
				<Progress
					percent={progress}
					className="mt-4"
				/>
			)}

			<Modal
				open={previewOpen}
				title={previewTitle}
				footer={null}
				onCancel={() => setPreviewOpen(false)}
			>
				<p>Preview not available for this file type.</p>
			</Modal>
		</div>
	);
};

export default DocumentUpload;
