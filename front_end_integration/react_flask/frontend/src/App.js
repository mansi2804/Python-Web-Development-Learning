import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import './App.css';

// Components
import Navigation from './components/Navigation';
import TaskList from './components/TaskList';
import TaskForm from './components/TaskForm';
import TaskDetail from './components/TaskDetail';
import Login from './components/Login';
import Register from './components/Register';
import ProtectedRoute from './components/ProtectedRoute';

// API Service
import { checkAuth } from './services/auth';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if the user is authenticated when the app loads
    const checkAuthentication = async () => {
      try {
        const userData = await checkAuth();
        setUser(userData);
      } catch (error) {
        console.error('Authentication check failed:', error);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    checkAuthentication();
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    // Clear token from localStorage
    localStorage.removeItem('token');
    setUser(null);
  };

  if (loading) {
    return <div className="text-center mt-5">Loading...</div>;
  }

  return (
    <Router>
      <div className="App">
        <Navigation user={user} onLogout={handleLogout} />
        <Container className="mt-4">
          <Routes>
            <Route path="/login" element={
              user ? <Navigate to="/" /> : <Login onLogin={handleLogin} />
            } />
            <Route path="/register" element={
              user ? <Navigate to="/" /> : <Register onLogin={handleLogin} />
            } />
            <Route path="/" element={
              <ProtectedRoute user={user}>
                <TaskList />
              </ProtectedRoute>
            } />
            <Route path="/tasks/new" element={
              <ProtectedRoute user={user}>
                <TaskForm />
              </ProtectedRoute>
            } />
            <Route path="/tasks/:id" element={
              <ProtectedRoute user={user}>
                <TaskDetail />
              </ProtectedRoute>
            } />
            <Route path="/tasks/:id/edit" element={
              <ProtectedRoute user={user}>
                <TaskForm />
              </ProtectedRoute>
            } />
          </Routes>
        </Container>
      </div>
    </Router>
  );
}

export default App;
