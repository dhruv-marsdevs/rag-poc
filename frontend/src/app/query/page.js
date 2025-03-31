"use client";

import React, { useState } from "react";
import dynamic from "next/dynamic";
import {
	Typography,
	Input,
	Button,
	Card,
	Spin,
	Alert,
	Divider,
	Empty,
	List,
} from "antd";
import {
	SearchOutlined,
	SendOutlined,
	LoadingOutlined,
} from "@ant-design/icons";
import { queryDocuments } from "../../api/query";
import useRequireAuth from "../../hooks/useRequireAuth";

// Import the LayoutWrapper with SSR disabled
const LayoutWrapper = dynamic(() => import("../layout-wrapper"), {
	ssr: false,
});

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

export default function QueryPage() {
	const { isAuthenticated, loading: authLoading } = useRequireAuth();
	const [query, setQuery] = useState("");
	const [loading, setLoading] = useState(false);
	const [result, setResult] = useState(null);
	const [error, setError] = useState(null);

	const handleQuery = async () => {
		if (!query.trim()) {
			return;
		}

		setLoading(true);
		setError(null);

		try {
			const data = await queryDocuments(query);
			setResult(data);
		} catch (error) {
			console.error("Query error:", error);
			setError(error.detail || "Failed to process your query");
			setResult(null);
		} finally {
			setLoading(false);
		}
	};

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
			<Title level={2}>Ask Questions About Your Documents</Title>
			<Paragraph className="mb-6">
				Enter your question below to search through your uploaded
				documents.
			</Paragraph>

			<Card className="mb-6">
				<div className="flex flex-col space-y-6">
					<TextArea
						placeholder="What would you like to know about your documents?"
						value={query}
						onChange={(e) => setQuery(e.target.value)}
						autoSize={{ minRows: 3, maxRows: 6 }}
						className="text-base"
					/>
					<div className="flex justify-end mt-4">
						<Button
							type="primary"
							icon={
								loading ? <LoadingOutlined /> : <SendOutlined />
							}
							onClick={handleQuery}
							loading={loading}
							disabled={!query.trim()}
							size="large"
						>
							{loading ? "Processing" : "Ask Question"}
						</Button>
					</div>
				</div>
			</Card>

			{error && (
				<Alert
					message="Error"
					description={error}
					type="error"
					showIcon
					className="mb-6"
				/>
			)}

			{result && (
				<Card
					title="Answer"
					className="mb-6"
				>
					<Paragraph>{result.answer}</Paragraph>

					{result.sources && result.sources.length > 0 && (
						<>
							<Divider orientation="left">Sources</Divider>
							<List
								itemLayout="horizontal"
								dataSource={result.sources}
								renderItem={(source, index) => (
									<List.Item>
										<List.Item.Meta
											avatar={
												<div className="bg-gray-200 w-8 h-8 rounded-full flex items-center justify-center">
													{index + 1}
												</div>
											}
											title={source.document_name}
											description={source.text}
										/>
									</List.Item>
								)}
							/>
						</>
					)}
				</Card>
			)}

			{!loading && !result && !error && (
				<div className="flex justify-center items-center p-12">
					<Empty
						description="Ask a question to see answers from your documents"
						image={Empty.PRESENTED_IMAGE_SIMPLE}
					/>
				</div>
			)}
		</LayoutWrapper>
	);
}
