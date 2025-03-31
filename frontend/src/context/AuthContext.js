"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import {
	loginUser,
	registerUser,
	getCurrentUser,
	logoutUser,
} from "../api/auth";
import { message } from "antd";

// Create the AuthContext
const AuthContext = createContext();

// Create the AuthProvider component
export function AuthProvider({ children }) {
	const [user, setUser] = useState(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState(null);

	// Initialize by checking if there's a token and getting the user profile
	useEffect(() => {
		const initializeAuth = async () => {
			const token = localStorage.getItem("token");
			if (token) {
				try {
					const userData = await getCurrentUser();
					setUser(userData);
				} catch (error) {
					console.error("Error loading user:", error);
					localStorage.removeItem("token");
				}
			}
			setLoading(false);
		};

		initializeAuth();
	}, []);

	// Login function
	const login = async (email, password) => {
		setLoading(true);
		setError(null);
		try {
			const data = await loginUser(email, password);
			localStorage.setItem("token", data.access_token);

			// Get user profile after successful login
			const userData = await getCurrentUser();
			setUser(userData);

			message.success("Logged in successfully");
			return true;
		} catch (error) {
			setError(error.detail || "Login failed");
			message.error(error.detail || "Login failed");
			return false;
		} finally {
			setLoading(false);
		}
	};

	// Register function
	const register = async (userData) => {
		setLoading(true);
		setError(null);
		try {
			await registerUser(userData);
			message.success("Registration successful! Please log in.");
			return true;
		} catch (error) {
			setError(error.detail || "Registration failed");
			message.error(error.detail || "Registration failed");
			return false;
		} finally {
			setLoading(false);
		}
	};

	// Logout function
	const logout = () => {
		logoutUser();
		setUser(null);
		message.info("Logged out successfully");
	};

	// Check if user is authenticated
	const isAuthenticated = !!user;

	// Create the context value
	const value = {
		user,
		loading,
		error,
		login,
		register,
		logout,
		isAuthenticated,
	};

	return (
		<AuthContext.Provider value={value}>{children}</AuthContext.Provider>
	);
}

// Create a hook for using the auth context
export const useAuth = () => {
	const context = useContext(AuthContext);
	if (context === undefined) {
		throw new Error("useAuth must be used within an AuthProvider");
	}
	return context;
};

export default AuthContext;
