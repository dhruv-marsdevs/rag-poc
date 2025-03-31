"use client";

import React, { useState, useEffect } from "react";
import {
	Form,
	Input,
	Button,
	Card,
	Typography,
	Divider,
	notification,
} from "antd";
import { UserOutlined, LockOutlined } from "@ant-design/icons";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "../../context/AuthContext";

const { Title, Text } = Typography;

export default function LoginPage() {
	const { login, isAuthenticated, loading } = useAuth();
	const router = useRouter();
	const [form] = Form.useForm();
	const [submitting, setSubmitting] = useState(false);

	// Redirect if already authenticated
	useEffect(() => {
		if (isAuthenticated) {
			router.push("/");
		}
	}, [isAuthenticated, router]);

	const onFinish = async (values) => {
		setSubmitting(true);
		try {
			const success = await login(values.email, values.password);
			if (success) {
				router.push("/");
			}
		} finally {
			setSubmitting(false);
		}
	};

	return (
		<div className="flex items-center justify-center min-h-screen bg-gray-50">
			<Card className="w-full max-w-md">
				<div className="text-center mb-6">
					<Title level={2}>Welcome Back</Title>
					<Text type="secondary">Sign in to your account</Text>
				</div>

				<Form
					form={form}
					name="login"
					layout="vertical"
					initialValues={{ remember: true }}
					onFinish={onFinish}
				>
					<Form.Item
						name="email"
						rules={[
							{
								required: true,
								message: "Please input your email!",
							},
							{
								type: "email",
								message: "Please enter a valid email!",
							},
						]}
					>
						<Input
							prefix={<UserOutlined />}
							placeholder="Email"
							size="large"
						/>
					</Form.Item>

					<Form.Item
						name="password"
						rules={[
							{
								required: true,
								message: "Please input your password!",
							},
						]}
					>
						<Input.Password
							prefix={<LockOutlined />}
							placeholder="Password"
							size="large"
						/>
					</Form.Item>

					<Form.Item>
						<Button
							type="primary"
							htmlType="submit"
							size="large"
							loading={submitting || loading}
							block
						>
							Sign in
						</Button>
					</Form.Item>

					<Divider>
						<Text type="secondary">
							Don&apos;t have an account?
						</Text>
					</Divider>

					<div className="text-center">
						<Link href="/register">
							<Button
								type="default"
								size="large"
								block
							>
								Create an account
							</Button>
						</Link>
					</div>
				</Form>
			</Card>
		</div>
	);
}
