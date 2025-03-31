"use client";

import React, { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import {
	Typography,
	Form,
	Input,
	Button,
	Card,
	Spin,
	Avatar,
	message,
} from "antd";
import { UserOutlined, MailOutlined, SaveOutlined } from "@ant-design/icons";
import { getUserProfile, updateUserProfile } from "../../api/user";
import useRequireAuth from "../../hooks/useRequireAuth";

// Import the LayoutWrapper with SSR disabled
const LayoutWrapper = dynamic(() => import("../layout-wrapper"), {
	ssr: false,
});

const { Title, Text } = Typography;

export default function ProfilePage() {
	const { isAuthenticated, loading: authLoading } = useRequireAuth();
	// Move Form.useForm to top level to maintain consistent hook order
	const [form] = Form.useForm();
	const [userProfile, setUserProfile] = useState(null);
	const [loading, setLoading] = useState(true);
	const [updating, setUpdating] = useState(false);

	// Only fetch profile data when authenticated and component is mounted
	useEffect(() => {
		let mounted = true;

		const fetchProfile = async () => {
			if (!isAuthenticated) return;

			setLoading(true);
			try {
				const data = await getUserProfile();

				// Only update state if component is still mounted
				if (mounted) {
					setUserProfile(data);
					// Only set form values if component is mounted
					form.setFieldsValue({
						email: data.email,
						full_name: data.full_name || "",
					});
				}
			} catch (error) {
				console.error("Error fetching profile:", error);
				if (mounted) {
					message.error("Failed to load profile information");
				}
			} finally {
				if (mounted) {
					setLoading(false);
				}
			}
		};

		if (isAuthenticated) {
			fetchProfile();
		}

		// Cleanup function to prevent setting state on unmounted component
		return () => {
			mounted = false;
		};
	}, [isAuthenticated, form]);

	const handleProfileUpdate = async (values) => {
		setUpdating(true);
		try {
			const updatedData = await updateUserProfile(values);
			setUserProfile(updatedData);
			message.success("Profile updated successfully");
		} catch (error) {
			console.error("Update error:", error);
			message.error(error.detail || "Failed to update profile");
		} finally {
			setUpdating(false);
		}
	};

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
			<div className="max-w-3xl mx-auto">
				<div className="text-center mb-8">
					<Avatar
						size={80}
						icon={<UserOutlined />}
						className="mb-4"
						style={{ backgroundColor: "#1677ff" }}
					/>
					<Title level={2}>My Profile</Title>
					<Text type="secondary">
						Manage your account information
					</Text>
				</div>

				<Card>
					<Form
						form={form}
						layout="vertical"
						onFinish={handleProfileUpdate}
					>
						<Form.Item
							name="email"
							label="Email"
							rules={[
								{
									required: true,
									message: "Email is required",
								},
								{
									type: "email",
									message: "Please enter a valid email",
								},
							]}
						>
							<Input
								prefix={<MailOutlined />}
								placeholder="Email"
								disabled
							/>
						</Form.Item>

						<Form.Item
							name="full_name"
							label="Full Name"
							rules={[
								{
									required: true,
									message: "Full name is required",
								},
							]}
						>
							<Input
								prefix={<UserOutlined />}
								placeholder="Full Name"
							/>
						</Form.Item>

						<Form.Item>
							<Button
								type="primary"
								htmlType="submit"
								icon={<SaveOutlined />}
								loading={updating}
							>
								Save Changes
							</Button>
						</Form.Item>
					</Form>
				</Card>
			</div>
		</LayoutWrapper>
	);
}
