"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import {
	Card,
	Typography,
	Row,
	Col,
	Statistic,
	Spin,
	Tooltip,
	Empty,
} from "antd";
import {
	FileOutlined,
	QuestionCircleOutlined,
	UserOutlined,
	ClockCircleOutlined,
	PieChartOutlined,
} from "@ant-design/icons";
import useRequireAuth from "../hooks/useRequireAuth";
import { getDashboardStats } from "../api/dashboard";

// Import the LayoutWrapper with SSR disabled
const LayoutWrapper = dynamic(() => import("./layout-wrapper"), { ssr: false });

const { Title, Text } = Typography;

export default function Home() {
	// This will redirect to /login if user is not authenticated
	const { isAuthenticated, loading: authLoading } = useRequireAuth();
	const [stats, setStats] = useState(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState(null);

	useEffect(() => {
		// Fetch dashboard statistics when component mounts and user is authenticated
		const fetchStats = async () => {
			if (!isAuthenticated) return;

			setLoading(true);
			try {
				const data = await getDashboardStats();
				setStats(data);
				setError(null);
			} catch (err) {
				console.error("Error fetching dashboard stats:", err);
				setError("Failed to load dashboard statistics");
				setStats(null);
			} finally {
				setLoading(false);
			}
		};

		if (isAuthenticated) {
			fetchStats();
		}
	}, [isAuthenticated]);

	// Show loading spinner while checking authentication
	if (authLoading || loading) {
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
			<div className="mb-6">
				<Title level={2}>Dashboard</Title>
				<Text type="secondary">
					System performance and usage statistics
				</Text>
			</div>

			{error ? (
				<div className="mb-6">
					<Empty
						description={error}
						image={Empty.PRESENTED_IMAGE_SIMPLE}
					/>
				</div>
			) : (
				<Row gutter={[16, 16]}>
					<Col
						xs={24}
						sm={12}
						lg={6}
					>
						<Card>
							<Statistic
								title="Total Documents"
								value={stats?.total_documents || 0}
								prefix={<FileOutlined />}
							/>
						</Card>
					</Col>
					<Col
						xs={24}
						sm={12}
						lg={6}
					>
						<Card>
							<Statistic
								title="Queries Today"
								value={stats?.queries_today || 0}
								prefix={<QuestionCircleOutlined />}
							/>
						</Card>
					</Col>
					<Col
						xs={24}
						sm={12}
						lg={6}
					>
						<Card>
							<Statistic
								title="Active Users"
								value={stats?.active_users || 0}
								prefix={<UserOutlined />}
							/>
						</Card>
					</Col>
					<Col
						xs={24}
						sm={12}
						lg={6}
					>
						<Card>
							<Statistic
								title="Avg Response Time"
								value={stats?.avg_response_time || 0}
								precision={2}
								suffix="sec"
								prefix={<ClockCircleOutlined />}
							/>
						</Card>
					</Col>

					{stats?.document_types &&
						Object.keys(stats.document_types).length > 0 && (
							<Col xs={24}>
								<Card title="Document Types">
									<Row gutter={[16, 16]}>
										{Object.entries(
											stats.document_types
										).map(([type, count]) => (
											<Col
												key={type}
												xs={12}
												sm={8}
												md={6}
												lg={4}
											>
												<Tooltip
													title={`${type} files`}
												>
													<Card
														bordered={false}
														size="small"
													>
														<Statistic
															title={type.toUpperCase()}
															value={count}
															prefix={
																<PieChartOutlined />
															}
														/>
													</Card>
												</Tooltip>
											</Col>
										))}
									</Row>
								</Card>
							</Col>
						)}
				</Row>
			)}
		</LayoutWrapper>
	);
}
