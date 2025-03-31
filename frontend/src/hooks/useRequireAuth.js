"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../context/AuthContext";

/**
 * Hook to protect routes that require authentication
 * Redirects to login page if user is not authenticated
 */
export default function useRequireAuth(redirectUrl = "/login") {
	const { isAuthenticated, loading } = useAuth();
	const router = useRouter();

	useEffect(() => {
		if (!loading && !isAuthenticated) {
			router.push(redirectUrl);
		}
	}, [isAuthenticated, loading, redirectUrl, router]);

	return { isAuthenticated, loading };
}
