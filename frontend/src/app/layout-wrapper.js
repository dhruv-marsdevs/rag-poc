"use client";

import dynamic from "next/dynamic";
import { useAuth } from "../context/AuthContext";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Spin } from "antd";

// Dynamically import the MainLayout to avoid SSR issues with Ant Design
const MainLayout = dynamic(() => import("../layouts/MainLayout"), {
	ssr: false,
	loading: () => (
		<div className="flex justify-center items-center h-screen">
			<Spin size="large">
				<div className="p-10 text-center text-gray-500">Loading...</div>
			</Spin>
		</div>
	),
});

export default function LayoutWrapper({ children }) {
	const { isAuthenticated, loading } = useAuth();
	const router = useRouter();
	const [mounted, setMounted] = useState(false);

	// Set mounted state on client-side
	useEffect(() => {
		setMounted(true);
	}, []);

	// Redirect unauthenticated users to login
	useEffect(() => {
		if (!loading && !isAuthenticated) {
			router.push("/login");
		}
	}, [isAuthenticated, loading, router]);

	// Don't render anything during server-side rendering or if not authenticated
	if (!mounted || loading || !isAuthenticated) {
		return null; // Don't render anything while loading or redirecting
	}

	// No longer need to wrap with StyleProvider since it's at the root level
	return <MainLayout>{children}</MainLayout>;
}
