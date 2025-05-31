import React from 'react';
import { useAuth } from '../contexts/AuthContext';

function HomePage() {
  const { user, logout, apiClient } = useAuth();

  const handleLogout = async () => {
    await logout();
    // Navigate to login or show logged out message, router might handle redirect via ProtectedRoute
  };

  const fetchSomeData = async () => {
    try {
      // Example of using the apiClient from AuthContext
      const response = await apiClient.get('/api/some-protected-data'); // Replace with an actual endpoint
      console.log('Protected data:', response.data);
      alert('Fetched data successfully! Check console.');
    } catch (error) {
      console.error('Error fetching protected data:', error.response ? error.response.data : error.message);
      alert('Failed to fetch protected data. Check console.');
    }
  };

  return (
    <div>
      <h2>Welcome to the Home Page!</h2>
      {user && <p>You are logged in as: {user.email}</p>}
      <button onClick={fetchSomeData}>Fetch Protected Data</button>
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}

export default HomePage;
