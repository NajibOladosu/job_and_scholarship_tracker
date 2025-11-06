import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthLayout } from './components/layout/AuthLayout';
import { Home } from './pages/Home';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Applications } from './pages/Applications';
import { Documents } from './pages/Documents';
import { Notifications } from './pages/Notifications';
import { Profile } from './pages/Profile';

// Mock authentication check (replace with real auth later)
const isAuthenticated = false; // Change to true to see authenticated routes

function App() {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Login />} /> {/* Reuse login for now */}

        {/* Protected Routes */}
        <Route
          path="/dashboard"
          element={
            isAuthenticated ? (
              <AuthLayout>
                <Dashboard />
              </AuthLayout>
            ) : (
              <Navigate to="/login" />
            )
          }
        />
        <Route
          path="/applications"
          element={
            isAuthenticated ? (
              <AuthLayout>
                <Applications />
              </AuthLayout>
            ) : (
              <Navigate to="/login" />
            )
          }
        />
        <Route
          path="/documents"
          element={
            isAuthenticated ? (
              <AuthLayout>
                <Documents />
              </AuthLayout>
            ) : (
              <Navigate to="/login" />
            )
          }
        />
        <Route
          path="/notifications"
          element={
            isAuthenticated ? (
              <AuthLayout>
                <Notifications />
              </AuthLayout>
            ) : (
              <Navigate to="/login" />
            )
          }
        />
        <Route
          path="/profile"
          element={
            isAuthenticated ? (
              <AuthLayout>
                <Profile />
              </AuthLayout>
            ) : (
              <Navigate to="/login" />
            )
          }
        />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Router>
  );
}

export default App;
