import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import HomePage from './pages/HomePage';
import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider, useAuth } from './contexts/AuthContext';

// A component to handle root redirect based on auth state
function RootRedirect() {
  const { isAuthenticated } = useAuth();
  return isAuthenticated() ? <Navigate to="/" replace /> : <Navigate to="/login" replace />;
}

function AppContent() {
  return (
    <div className="App">
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<HomePage />} />
          {/* Add other protected routes here */}
        </Route>
        {/* Optional: Redirect from a generic path to login or home based on auth state */}
        {/* <Route path="*" element={<RootRedirect />} /> */}
      </Routes>
    </div>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}

export default App;
