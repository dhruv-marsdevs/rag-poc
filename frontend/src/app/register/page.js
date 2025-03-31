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
import { UserOutlined, LockOutlined, MailOutlined } from "@ant-design/icons";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "../../context/AuthContext";

const { Title, Text } = Typography;

export default function RegisterPage() {
	const { register, isAuthenticated } = useAuth();
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
			// Make sure passwords match
			if (values.password !== values.confirmPassword) {
				notification.error({
					message: "Passwords do not match",
					description: "Please ensure your passwords match.",
				});
				return;
			}

			// Create user object without confirm password
			const userData = {
				email: values.email,
				password: values.password,
				full_name: values.fullName,
			};

			const success = await register(userData);
			if (success) {
				// Reset form and redirect to login
				form.resetFields();
				router.push("/login");
			}
		} finally {
			setSubmitting(false);
		}
	};

	return (
		<div className="flex items-center justify-center min-h-screen bg-gray-50">
			<Card className="w-full max-w-md">
				<div className="text-center mb-6">
					<Title level={2}>Create an Account</Title>
					<Text type="secondary">Sign up to get started</Text>
				</div>

				<Form
					form={form}
					name="register"
					layout="vertical"
					initialValues={{ remember: true }}
					onFinish={onFinish}
				>
					<Form.Item
						name="fullName"
						rules={[
							{
								required: true,
								message: "Please input your full name!",
							},
						]}
					>
						<Input
							prefix={<UserOutlined />}
							placeholder="Full Name"
							size="large"
						/>
					</Form.Item>

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
							prefix={<MailOutlined />}
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
							{
								min: 8,
								message:
									"Password must be at least 8 characters!",
							},
						]}
					>
						<Input.Password
							prefix={<LockOutlined />}
							placeholder="Password"
							size="large"
						/>
					</Form.Item>

					<Form.Item
						name="confirmPassword"
						rules={[
							{
								required: true,
								message: "Please confirm your password!",
							},
							({ getFieldValue }) => ({
								validator(_, value) {
									if (
										!value ||
										getFieldValue("password") === value
									) {
										return Promise.resolve();
									}
									return Promise.reject(
										new Error(
											"The two passwords do not match!"
										)
									);
								},
							}),
						]}
					>
						<Input.Password
							prefix={<LockOutlined />}
							placeholder="Confirm Password"
							size="large"
						/>
					</Form.Item>

					<Form.Item>
						<Button
							type="primary"
							htmlType="submit"
							size="large"
							loading={submitting}
							block
						>
							Register
						</Button>
					</Form.Item>

					<Divider>
						<Text type="secondary">Already have an account?</Text>
					</Divider>

					<div className="text-center">
						<Link href="/login">
							<Button
								type="default"
								size="large"
								block
							>
								Sign in
							</Button>
						</Link>
					</div>
				</Form>
			</Card>
		</div>
	);
}
