"use client";

import React, { useState } from "react";
import { Form, Input, Button, InputNumber, message, Card, Alert } from "antd";
import { GlobalOutlined, ScanOutlined } from "@ant-design/icons";
import { scrapeWebsite } from "../api/documents";

const WebScraper = ({ onScrapeSuccess }) => {
	const [form] = Form.useForm();
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState(null);

	const handleSubmit = async (values) => {
		setLoading(true);
		setError(null);

		try {
			const result = await scrapeWebsite({
				url: values.url,
				max_pages: values.max_pages,
				max_depth: values.max_depth,
			});

			message.success(
				`Started scraping website. Processing ${values.max_pages} pages in the background.`
			);
			form.resetFields();

			if (onScrapeSuccess) {
				onScrapeSuccess(result);
			}
		} catch (err) {
			console.error("Scraping error:", err);
			setError(err.detail || "Failed to start website scraping");
			message.error("Failed to start website scraping");
		} finally {
			setLoading(false);
		}
	};

	return (
		<Card
			title="Website Scraper"
			className="mb-6"
		>
			{error && (
				<Alert
					message="Error"
					description={error}
					type="error"
					className="mb-4"
					showIcon
					closable
					onClose={() => setError(null)}
				/>
			)}

			<Form
				form={form}
				layout="vertical"
				onFinish={handleSubmit}
				initialValues={{
					max_pages: 30,
					max_depth: 2,
				}}
			>
				<Form.Item
					name="url"
					label="Website URL"
					rules={[
						{
							required: true,
							message: "Please enter a website URL",
						},
						{
							type: "url",
							message: "Please enter a valid URL",
						},
					]}
				>
					<Input
						prefix={<GlobalOutlined />}
						placeholder="https://example.com"
						allowClear
					/>
				</Form.Item>

				<Form.Item
					label="Maximum Pages"
					name="max_pages"
					rules={[
						{
							required: true,
							message: "Please enter maximum number of pages",
						},
					]}
					tooltip="Maximum number of pages to scrape (1-100)"
				>
					<InputNumber
						min={1}
						max={100}
						placeholder="50"
						style={{ width: "100%" }}
					/>
				</Form.Item>

				<Form.Item
					label="Maximum Depth"
					name="max_depth"
					rules={[
						{
							required: true,
							message: "Please enter maximum link depth",
						},
					]}
					tooltip="Maximum depth of links to follow from starting page (1-5)"
				>
					<InputNumber
						min={1}
						max={5}
						placeholder="3"
						style={{ width: "100%" }}
					/>
				</Form.Item>

				<Form.Item>
					<Button
						type="primary"
						icon={<ScanOutlined />}
						loading={loading}
						htmlType="submit"
						block
					>
						Start Scraping
					</Button>
				</Form.Item>
			</Form>

			<div className="text-sm text-gray-500 mt-4">
				<p>
					This tool will scrape the content from the provided website
					URL and all linked pages within the same domain, up to the
					specified maximum pages and link depth.
				</p>
				<p>
					The scraped content will be processed, indexed, and added to
					your document library. Once processing is complete, you can
					query this content just like any other document in the
					system.
				</p>
				<p>
					The processing runs in the background and may take several
					minutes depending on the website size and complexity.
				</p>
			</div>
		</Card>
	);
};

export default WebScraper;
