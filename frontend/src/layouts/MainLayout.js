"use client";

import React, { useState, useEffect } from "react";
import {
	Layout,
	Menu,
	theme,
	Avatar,
	Dropdown,
	Button,
	Breadcrumb,
} from "antd";
import {
	MenuFoldOutlined,
	MenuUnfoldOutlined,
	UserOutlined,
	DashboardOutlined,
	FileOutlined,
	QuestionCircleOutlined,
	HomeOutlined,
	LogoutOutlined,
} from "@ant-design/icons";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "../context/AuthContext";

const { Header, Sider, Content } = Layout;

const MainLayout = ({ children }) => {
	const [collapsed, setCollapsed] = useState(false);
	const {
		token: { colorBgContainer, borderRadiusLG, colorPrimary },
	} = theme.useToken();
	const pathname = usePathname();
	const router = useRouter();
	const { user, logout, isAuthenticated, loading } = useAuth();

	// Redirect if not authenticated
	useEffect(() => {
		if (!loading && !isAuthenticated) {
			router.push("/login");
		}
	}, [isAuthenticated, loading, router]);

	// Don't render anything if not authenticated or still loading
	if (!isAuthenticated || loading) {
		return null;
	}

	// Handle logout
	const handleLogout = () => {
		logout();
		router.push("/login");
	};

	// Generate breadcrumb items based on current path
	const generateBreadcrumbItems = () => {
		const paths = pathname.split("/").filter((path) => path);
		const breadcrumbItems = [
			{
				title: (
					<Link href="/">
						<HomeOutlined style={{ marginRight: 4 }} />
						Home
					</Link>
				),
			},
		];

		let currentPath = "";
		paths.forEach((path) => {
			currentPath += `/${path}`;
			breadcrumbItems.push({
				title: (
					<Link href={currentPath}>
						{path.charAt(0).toUpperCase() + path.slice(1)}
					</Link>
				),
			});
		});

		return breadcrumbItems;
	};

	const userMenuItems = [
		{
			key: "profile",
			icon: <UserOutlined />,
			label: <Link href="/profile">Profile</Link>,
		},
		{
			key: "logout",
			icon: <LogoutOutlined />,
			label: <span onClick={handleLogout}>Logout</span>,
		},
	];

	return (
		<Layout style={{ minHeight: "100vh" }}>
			<Sider
				trigger={null}
				collapsible
				collapsed={collapsed}
				theme="light"
				width={250}
				style={{
					overflow: "auto",
					height: "100vh",
					position: "fixed",
					left: 0,
					top: 0,
					bottom: 0,
					boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
				}}
			>
				<div
					className="logo"
					style={{
						height: 64,
						display: "flex",
						alignItems: "center",
						justifyContent: "center",
						borderBottom: "1px solid #f0f0f0",
					}}
				>
					<h2
						style={{
							color: colorPrimary,
							margin: 0,
							fontSize: collapsed ? "16px" : "20px",
						}}
					>
						{collapsed ? "RAG" : "RAG App"}
					</h2>
				</div>
				<Menu
					theme="light"
					mode="inline"
					defaultSelectedKeys={["1"]}
					selectedKeys={[
						pathname === "/"
							? "1"
							: pathname.startsWith("/documents")
							? "2"
							: pathname.startsWith("/query")
							? "3"
							: "",
					]}
					items={[
						{
							key: "1",
							icon: <DashboardOutlined />,
							label: <Link href="/">Dashboard</Link>,
						},
						{
							key: "2",
							icon: <FileOutlined />,
							label: <Link href="/documents">Documents</Link>,
						},
						{
							key: "3",
							icon: <QuestionCircleOutlined />,
							label: <Link href="/query">Ask Questions</Link>,
						},
					]}
				/>
			</Sider>
			<Layout
				style={{
					marginLeft: collapsed ? 80 : 250,
					transition: "all 0.2s",
				}}
			>
				<Header
					style={{
						padding: 0,
						background: colorBgContainer,
						display: "flex",
						alignItems: "center",
						justifyContent: "space-between",
						boxShadow: "0 1px 4px rgba(0,0,0,0.1)",
					}}
				>
					<Button
						type="text"
						icon={
							collapsed ? (
								<MenuUnfoldOutlined />
							) : (
								<MenuFoldOutlined />
							)
						}
						onClick={() => setCollapsed(!collapsed)}
						style={{
							fontSize: "16px",
							width: 64,
							height: 64,
						}}
					/>
					<div
						style={{
							marginRight: 24,
							display: "flex",
							alignItems: "center",
						}}
					>
						{isAuthenticated ? (
							<>
								{user && (
									<span style={{ marginRight: 12 }}>
										{user.email}
									</span>
								)}
								<Dropdown
									menu={{ items: userMenuItems }}
									placement="bottomRight"
								>
									<Avatar
										size="default"
										icon={<UserOutlined />}
										style={{
											cursor: "pointer",
											backgroundColor: colorPrimary,
										}}
									/>
								</Dropdown>
							</>
						) : (
							<Link href="/login">
								<Button type="primary">Sign In</Button>
							</Link>
						)}
					</div>
				</Header>
				<Content
					style={{
						margin: "24px 16px",
						padding: 24,
						minHeight: 280,
						background: colorBgContainer,
						borderRadius: borderRadiusLG,
					}}
				>
					<Breadcrumb
						items={generateBreadcrumbItems()}
						style={{ marginBottom: 16 }}
					/>
					{children}
				</Content>
			</Layout>
		</Layout>
	);
};

export default MainLayout;
