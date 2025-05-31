import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient, { loginUser, refreshToken as refreshAuthToken } from '../services/apiService'; // Import from apiService

const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  // Store only a flag or user object, tokens are now primarily managed by apiService and localStorage
  const [isAuthenticatedState, setIsAuthenticatedState] = useState(() => {
    return !!localStorage.getItem('accessToken');
  });

  useEffect(() => {
    // On initial load, check token.
    // Actual user data will be set upon login or if you implement a /me endpoint call here.
    const currentToken = localStorage.getItem('accessToken');
    if (currentToken) {
      setIsAuthenticatedState(true);
      // Optionally, you could call a function here to fetch user details using the token:
      // fetchUserDetails();
    } else {
      setIsAuthenticatedState(false);
    }
  }, []);

  // Example: const fetchUserDetails = async () => { ... apiClient.get('/users/me') ... setUser(data) }

  const login = async (email, password) => {
    try {
      const response = await loginUser(email, password); // Use loginUser from apiService
      const { accessToken, refreshToken, user: userData } = response.data;
      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
      setUser(userData || { email }); // Use userData from response if available
      setIsAuthenticatedState(true);
      // apiClient's request interceptor will use the new token from localStorage
      return response.data;
    } catch (error) {
      console.error('Login error in AuthContext:', error.response ? error.response.data : error.message);
      setIsAuthenticatedState(false);
      throw error;
    }
  };

  const logout = async () => {
    try {
      const refreshTokenValue = localStorage.getItem('refreshToken');
      if (refreshTokenValue) {
        // Optional: Call backend logout endpoint using apiClient or a direct axios call
        // await apiClient.post('/auth/logout', { refreshToken: refreshTokenValue });
        console.log('Backend logout successful (simulated or actual if API call is made)');
      }
    } catch (error) {
      console.error('Backend logout error:', error.response ? error.response.data : error.message);
      // Still proceed with client-side logout
    } finally {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      setUser(null);
      setIsAuthenticatedState(false);
      // apiClient's interceptor will no longer find a token in localStorage
    }
  };

  const handleTokenRefresh = async () => {
    try {
      const newAccessToken = await refreshAuthToken(); // Use from apiService
      // Potentially update user state if new token contains different claims
      setIsAuthenticatedState(true); // Ensure auth state is true
      return newAccessToken;
    } catch (error) {
      console.error("Failed to refresh token in AuthContext, logging out:", error);
      logout(); // If refresh fails, logout the user
      throw error;
    }
  };


  const value = {
    user,
    login,
    logout,
    isAuthenticated: () => isAuthenticatedState, // Use the state variable
    // refreshToken: handleTokenRefresh, // Expose the context's refresh handler
    apiClient // Expose the configured axios instance from apiService
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
