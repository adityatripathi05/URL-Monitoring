import axios from 'axios';

// Function to get tokens from localStorage
const getTokens = () => {
  const accessToken = localStorage.getItem('accessToken');
  const refreshToken = localStorage.getItem('refreshToken');
  return { accessToken, refreshToken };
};

// Create an axios instance
const apiClient = axios.create({
  baseURL: '/api', // Assuming your backend API is prefixed with /api
  // You can add other default settings here
});

// Request interceptor to add the auth token to headers
apiClient.interceptors.request.use(
  (config) => {
    const { accessToken } = getTokens();
    if (accessToken) {
      config.headers['Authorization'] = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const { refreshToken: currentRefreshToken } = getTokens();

    // Check if it's a 401 error, not a retry request, and a refresh token exists
    if (error.response?.status === 401 && !originalRequest._retry && currentRefreshToken) {
      originalRequest._retry = true; // Mark as retried

      try {
        // Call your refresh token endpoint
        // Note: Using axios.post directly here to avoid circular dependency with apiClient
        const refreshResponse = await axios.post('/auth/refresh', { refreshToken: currentRefreshToken });
        const { accessToken: newAccessToken } = refreshResponse.data;

        // Store the new access token
        localStorage.setItem('accessToken', newAccessToken);

        // Update the Authorization header for the original request
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;

        // Update default Authorization header for subsequent requests with the new token for the main axios instance
        // This is important if other parts of the app use the global axios instance.
        // However, for apiClient, the request interceptor will pick up the new token from localStorage.
        axios.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`;


        // Retry the original request with the new token
        return apiClient(originalRequest);
      } catch (refreshError) {
        console.error('Token refresh error:', refreshError.response ? refreshError.response.data : refreshError.message);
        // If refresh fails, clear tokens and redirect to login (or let AuthContext handle it)
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        // Optionally, dispatch a logout event or redirect
        // window.location.href = '/login'; // This is a hard redirect, consider using useNavigate in a component
        return Promise.reject(refreshError); // Propagate the error
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;

// You can also export specific API functions if needed
// export const fetchSomeData = () => apiClient.get('/some-data');
// export const loginUser = (email, password) => axios.post('/auth/login', { email, password });
// export const refreshTokenRequest = (refreshToken) => axios.post('/auth/refresh', { refreshToken });

// The login and refresh token calls might be better outside apiClient if they don't need the auth header,
// or if their failure modes are different (e.g., refresh token failure should trigger logout).
// For simplicity, login is often done with a basic axios call in AuthContext,
// and refresh token can also be a specific function.

export const loginUser = async (email, password) => {
  // Use a direct axios call for login as it doesn't need prior auth
  return axios.post('/auth/login', { email, password });
};

export const refreshToken = async () => {
  const { refreshToken: currentRefreshToken } = getTokens();
  if (!currentRefreshToken) {
    throw new Error("No refresh token available");
  }
  // Use a direct axios call for refresh
  const response = await axios.post('/auth/refresh', { refreshToken: currentRefreshToken });
  localStorage.setItem('accessToken', response.data.accessToken); // Update access token
  return response.data.accessToken;
};
