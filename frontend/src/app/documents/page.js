"use client";

import React, { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import {
	Table,
	Typography,
	Button,
	Space,
	Modal,
	message,
	Empty,
	Tag,
	Popconfirm,
	Tabs,
	Spin,
} from "antd";
import {
	FileOutlined,
	FilePdfOutlined,
	DeleteOutlined,
	CloudUploadOutlined,
	GlobalOutlined,
} from "@ant-design/icons";
import useRequireAuth from "../../hooks/useRequireAuth";
import { getDocuments, deleteDocument } from "../../api/documents";
import DocumentUpload from "../../components/DocumentUpload";
import WebScraper from "../../components/WebScraper";

// Import the LayoutWrapper with SSR disabled
const LayoutWrapper = dynamic(() => import("../layout-wrapper"), {
	ssr: false,
});

const { Title, Text } = Typography;
const { TabPane } = Tabs;

export default function DocumentsPage() {
	const { isAuthenticated, loading: authLoading } = useRequireAuth();
	const [documents, setDocuments] = useState([]);
	const [loading, setLoading] = useState(true);
	const [uploadModalVisible, setUploadModalVisible] = useState(false);
	const [scrapeModalVisible, setScrapeModalVisible] = useState(false);
	const [activeTabKey, setActiveTabKey] = useState("1");

	const fetchDocuments = async () => {
		try {
			setLoading(true);
			const data = await getDocuments();
			setDocuments(data);
		} catch (error) {
			console.error("Error fetching documents:", error);
			message.error("Failed to load documents");
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		if (isAuthenticated) {
			fetchDocuments();
		}
	}, [isAuthenticated]);

	const handleDelete = async (id) => {
		try {
			await deleteDocument(id);
			message.success("Document deleted successfully");
			// Refresh the document list
			fetchDocuments();
		} catch (error) {
			console.error("Delete error:", error);
			message.error("Failed to delete document");
		}
	};

	const handleUploadSuccess = () => {
		setUploadModalVisible(false);
		// Refresh the document list
		fetchDocuments();
		message.success("Document uploaded successfully");
	};

	const handleScrapeSuccess = () => {
		setScrapeModalVisible(false);
		// Refresh the document list after a short delay to allow processing
		setTimeout(() => {
			fetchDocuments();
		}, 2000);
	};

	const getFileIcon = (contentType) => {
		if (contentType === "application/pdf") {
			return <FilePdfOutlined style={{ color: "#ff4d4f" }} />;
		}
		return <FileOutlined />;
	};

	// Format file size
	const formatFileSize = (bytes) => {
		if (bytes === 0) return "0 Bytes";
		const k = 1024;
		const sizes = ["Bytes", "KB", "MB", "GB"];
		const i = parseInt(Math.floor(Math.log(bytes) / Math.log(k)));
		return (
			Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i]
		);
	};

	const columns = [
		{
			title: "Name",
			dataIndex: "filename",
			key: "filename",
			render: (text, record) => (
				<Space>
					{getFileIcon(record.content_type)}
					<Text>{text}</Text>
					{record.content_type === "text/plain" && (
						<Tag color="blue">
							<GlobalOutlined /> Website
						</Tag>
					)}
				</Space>
			),
		},
		{
			title: "Size",
			dataIndex: "size",
			key: "size",
			render: (size) => formatFileSize(size),
		},
		{
			title: "Created",
			dataIndex: "created_at",
			key: "created_at",
			render: (date) =>
				date ? new Date(date).toLocaleString() : "Processing...",
		},
		{
			title: "Actions",
			key: "actions",
			render: (_, record) => (
				<Popconfirm
					title="Delete this document?"
					description="Are you sure you want to delete this document?"
					onConfirm={() => handleDelete(record.id)}
					okText="Yes"
					cancelText="No"
				>
					<Button
						danger
						icon={<DeleteOutlined />}
						size="small"
					>
						Delete
					</Button>
				</Popconfirm>
			),
		},
	];

	// Show loading spinner while checking authentication
	if (authLoading) {
		return (
			<div className="flex justify-center items-center h-screen">
				<Spin size="large">
					<div className="p-10 text-center text-gray-500">
						Loading...
					</div>
				</Spin>
			</div>
		);
	}

	// Only render the page content if authenticated
	if (!isAuthenticated) {
		return null; // Will redirect via useRequireAuth
	}

	return (
		<LayoutWrapper>
			<div className="flex justify-between items-center mb-6">
				<Title level={2}>Document Library</Title>
				<Space>
					<Button
						type="primary"
						icon={<GlobalOutlined />}
						onClick={() => setScrapeModalVisible(true)}
					>
						Scrape Website
					</Button>
					<Button
						type="primary"
						icon={<CloudUploadOutlined />}
						onClick={() => setUploadModalVisible(true)}
					>
						Upload Document
					</Button>
				</Space>
			</div>

			<Table
				columns={columns}
				dataSource={documents}
				rowKey="id"
				loading={loading}
				locale={{
					emptyText: <Empty description="No documents found" />,
				}}
			/>

			<Modal
				title="Upload Document"
				open={uploadModalVisible}
				onCancel={() => setUploadModalVisible(false)}
				footer={null}
				width={600}
			>
				<DocumentUpload onUploadSuccess={handleUploadSuccess} />
				<div className="mt-4">
					<Text type="secondary">
						Supported formats: PDF, DOCX, DOC (Max. 10MB)
					</Text>
				</div>
			</Modal>

			<Modal
				title="Scrape Website"
				open={scrapeModalVisible}
				onCancel={() => setScrapeModalVisible(false)}
				footer={null}
				width={600}
			>
				<WebScraper onScrapeSuccess={handleScrapeSuccess} />
			</Modal>
		</LayoutWrapper>
	);
}
