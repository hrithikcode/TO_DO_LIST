import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { AuthProvider, useAuth } from './AuthContext';
import Login from './Login';
import Register from './Register';
import ForgotPassword from './ForgotPassword';
import ResetPasswordSimple from './ResetPasswordSimple';
import './App.css';
import './Auth.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID || '1234567890-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com';

// Main Todo Component (only shown when authenticated)
function TodoApp() {
  const [todos, setTodos] = useState([]);
  const [newTodo, setNewTodo] = useState({ title: '', description: '' });
  const [editingTodo, setEditingTodo] = useState(null);
  const [editForm, setEditForm] = useState({ title: '', description: '' });
  const [loading, setLoading] = useState(false);
  const [emailLoading, setEmailLoading] = useState(false);
  const [filter, setFilter] = useState('all'); // all, active, completed
  const { user, logout } = useAuth();

  // Fetch todos from backend
  const fetchTodos = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/todos`);
      setTodos(response.data);
    } catch (error) {
      console.error('Error fetching todos:', error);
      if (error.response?.status === 401 || error.response?.status === 422) {
        const errorMsg = error.response?.data?.msg || 'Session expired. Please login again.';
        alert(errorMsg);
        logout();
      } else {
        alert('Failed to fetch todos. Please check your connection and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Create new todo
  const createTodo = async (e) => {
    e.preventDefault();
    if (!newTodo.title.trim()) return;

    try {
      const response = await axios.post(`${API_BASE_URL}/api/todos`, newTodo);
      setTodos([response.data, ...todos]);
      setNewTodo({ title: '', description: '' });
      
      // Show email status if available
      if (response.data.email_sent === true) {
        alert('✅ Todo created and email notification sent successfully!');
      } else if (response.data.email_sent === false) {
        alert('✅ Todo created successfully!\n⚠️ Email notification failed - please check email configuration.');
      }
    } catch (error) {
      console.error('Error creating todo:', error);
      if (error.response?.status === 401 || error.response?.status === 422) {
        const errorMsg = error.response?.data?.msg || 'Session expired. Please login again.';
        alert(errorMsg);
        logout();
      } else {
        alert('Failed to create todo. Please try again.');
      }
    }
  };

  // Send email summary on demand
  const sendEmailSummary = async () => {
    try {
      setEmailLoading(true);
      const response = await axios.post(`${API_BASE_URL}/api/send-email-summary`);
      
      alert(`📧 Email summary sent successfully!\n\n` +
            `📊 Active tasks: ${response.data.active_tasks_count}\n` +
            `📮 Sent to: ${response.data.email}\n` +
            `⏰ Time: ${new Date(response.data.sent_at).toLocaleString()}\n\n` +
            `Check your email inbox for the detailed summary!`);
    } catch (error) {
      console.error('Error sending email summary:', error);
      
      if (error.response?.status === 401 || error.response?.status === 422) {
        const errorMsg = error.response?.data?.msg || 'Session expired. Please login again.';
        alert(errorMsg);
        logout();
      } else if (error.response?.status === 400) {
        alert('❌ Email configuration not set up.\n\n' +
              'Please configure your email settings to send notifications.\n' +
              'Run: python3 setup_enhanced_email.py');
      } else {
        alert('❌ Failed to send email summary.\n\n' +
              'Please check your email configuration and try again.');
      }
    } finally {
      setEmailLoading(false);
    }
  };

  // Toggle todo completion
  const toggleTodo = async (id, completed) => {
    try {
      const response = await axios.put(`${API_BASE_URL}/api/todos/${id}`, {
        completed: !completed
      });
      setTodos(todos.map(todo => 
        todo.id === id ? response.data : todo
      ));
    } catch (error) {
      console.error('Error updating todo:', error);
      if (error.response?.status === 401 || error.response?.status === 422) {
        const errorMsg = error.response?.data?.msg || 'Session expired. Please login again.';
        alert(errorMsg);
        logout();
      } else {
        alert('Failed to update todo. Please try again.');
      }
    }
  };

  // Start editing a todo
  const startEdit = (todo) => {
    setEditingTodo(todo.id);
    setEditForm({
      title: todo.title,
      description: todo.description || ''
    });
  };

  // Cancel editing
  const cancelEdit = () => {
    setEditingTodo(null);
    setEditForm({ title: '', description: '' });
  };

  // Save edited todo
  const saveEdit = async (id) => {
    if (!editForm.title.trim()) return;

    try {
      const response = await axios.put(`${API_BASE_URL}/api/todos/${id}`, {
        title: editForm.title,
        description: editForm.description
      });
      setTodos(todos.map(todo => 
        todo.id === id ? response.data : todo
      ));
      setEditingTodo(null);
      setEditForm({ title: '', description: '' });
    } catch (error) {
      console.error('Error updating todo:', error);
      if (error.response?.status === 401 || error.response?.status === 422) {
        const errorMsg = error.response?.data?.msg || 'Session expired. Please login again.';
        alert(errorMsg);
        logout();
      } else {
        alert('Failed to update todo. Please try again.');
      }
    }
  };

  // Delete todo
  const deleteTodo = async (id) => {
    if (!window.confirm('Are you sure you want to delete this todo?')) return;

    try {
      await axios.delete(`${API_BASE_URL}/api/todos/${id}`);
      setTodos(todos.filter(todo => todo.id !== id));
    } catch (error) {
      console.error('Error deleting todo:', error);
      if (error.response?.status === 401 || error.response?.status === 422) {
        const errorMsg = error.response?.data?.msg || 'Session expired. Please login again.';
        alert(errorMsg);
        logout();
      } else {
        alert('Failed to delete todo. Please try again.');
      }
    }
  };

  // Clear all completed todos
  const clearCompleted = async () => {
    const completedTodos = todos.filter(todo => todo.completed);
    if (completedTodos.length === 0) return;
    
    if (!window.confirm(`Delete ${completedTodos.length} completed todo(s)?`)) return;

    try {
      await Promise.all(
        completedTodos.map(todo => axios.delete(`${API_BASE_URL}/api/todos/${todo.id}`))
      );
      setTodos(todos.filter(todo => !todo.completed));
    } catch (error) {
      console.error('Error clearing completed todos:', error);
      alert('Failed to clear completed todos. Please try again.');
    }
  };

  // Filter todos based on current filter
  const filteredTodos = todos.filter(todo => {
    if (filter === 'active') return !todo.completed;
    if (filter === 'completed') return todo.completed;
    return true; // 'all'
  });

  const handleLogout = async () => {
    if (window.confirm('Are you sure you want to logout?')) {
      await logout();
    }
  };

  useEffect(() => {
    fetchTodos();
  }, []);

  // Stats
  const totalTodos = todos.length;
  const completedTodos = todos.filter(todo => todo.completed).length;
  const activeTodos = totalTodos - completedTodos;

  return (
    <div className="App">
      <header className="app-header">
        <h1>📝 Todo App</h1>
        <div className="user-info">
          <div>
            <div className="user-welcome">Welcome back,</div>
            <div className="user-name">{user?.username}</div>
          </div>
          <button onClick={handleLogout} className="logout-btn">
            Logout
          </button>
        </div>
      </header>

      <main className="main-content">
        {/* Stats and Email Button */}
        <div className="stats-bar">
          <div className="stat">
            <span className="stat-number">{totalTodos}</span>
            <span className="stat-label">Total</span>
          </div>
          <div className="stat">
            <span className="stat-number">{activeTodos}</span>
            <span className="stat-label">Active</span>
          </div>
          <div className="stat">
            <span className="stat-number">{completedTodos}</span>
            <span className="stat-label">Completed</span>
          </div>
          <button 
            onClick={sendEmailSummary} 
            disabled={emailLoading}
            className="email-summary-btn"
            title="Send email summary of all active tasks"
          >
            {emailLoading ? '📧 Sending...' : '📧 Email Summary'}
          </button>
        </div>

        {/* Add Todo Form */}
        <form onSubmit={createTodo} className="todo-form">
          <div className="form-row">
            <input
              type="text"
              placeholder="What needs to be done?"
              value={newTodo.title}
              onChange={(e) => setNewTodo({...newTodo, title: e.target.value})}
              className="todo-input"
              required
            />
            <button type="submit" className="add-btn">
              ➕ Add
            </button>
          </div>
          <textarea
            placeholder="Description (optional)..."
            value={newTodo.description}
            onChange={(e) => setNewTodo({...newTodo, description: e.target.value})}
            className="todo-textarea"
            rows="2"
          />
        </form>

        {/* Filter Buttons */}
        <div className="filter-bar">
          <button 
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All ({totalTodos})
          </button>
          <button 
            className={`filter-btn ${filter === 'active' ? 'active' : ''}`}
            onClick={() => setFilter('active')}
          >
            Active ({activeTodos})
          </button>
          <button 
            className={`filter-btn ${filter === 'completed' ? 'active' : ''}`}
            onClick={() => setFilter('completed')}
          >
            Completed ({completedTodos})
          </button>
          {completedTodos > 0 && (
            <button 
              className="clear-completed-btn"
              onClick={clearCompleted}
            >
              🗑️ Clear Completed
            </button>
          )}
        </div>

        {/* Todo List */}
        <div className="todo-list">
          {loading ? (
            <div className="loading">Loading todos...</div>
          ) : filteredTodos.length === 0 ? (
            <div className="no-todos">
              {filter === 'all' ? 'No todos yet. Add one above!' : 
               filter === 'active' ? 'No active todos!' : 
               'No completed todos!'}
            </div>
          ) : (
            filteredTodos.map(todo => (
              <div key={todo.id} className={`todo-item ${todo.completed ? 'completed' : ''}`}>
                {editingTodo === todo.id ? (
                  // Edit Mode
                  <div className="todo-edit-form">
                    <input
                      type="text"
                      value={editForm.title}
                      onChange={(e) => setEditForm({...editForm, title: e.target.value})}
                      className="edit-input"
                      autoFocus
                    />
                    <textarea
                      value={editForm.description}
                      onChange={(e) => setEditForm({...editForm, description: e.target.value})}
                      className="edit-textarea"
                      rows="2"
                      placeholder="Description..."
                    />
                    <div className="edit-actions">
                      <button 
                        onClick={() => saveEdit(todo.id)}
                        className="save-btn"
                        disabled={!editForm.title.trim()}
                      >
                        ✅ Save
                      </button>
                      <button 
                        onClick={cancelEdit}
                        className="cancel-btn"
                      >
                        ❌ Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  // View Mode
                  <>
                    <div className="todo-content">
                      <h3 className="todo-title">{todo.title}</h3>
                      {todo.description && (
                        <p className="todo-description">{todo.description}</p>
                      )}
                      <small className="todo-date">
                        Created: {new Date(todo.created_at).toLocaleDateString()}
                        {todo.updated_at !== todo.created_at && (
                          <span> • Updated: {new Date(todo.updated_at).toLocaleDateString()}</span>
                        )}
                      </small>
                    </div>
                    <div className="todo-actions">
                      <button
                        onClick={() => toggleTodo(todo.id, todo.completed)}
                        className={`toggle-btn ${todo.completed ? 'completed' : ''}`}
                        title={todo.completed ? 'Mark as incomplete' : 'Mark as complete'}
                      >
                        {todo.completed ? '✅' : '⭕'}
                      </button>
                      <button
                        onClick={() => startEdit(todo)}
                        className="edit-btn"
                        title="Edit todo"
                      >
                        ✏️
                      </button>
                      <button
                        onClick={() => deleteTodo(todo.id)}
                        className="delete-btn"
                        title="Delete todo"
                      >
                        🗑️
                      </button>
                    </div>
                  </>
                )}
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  );
}

// Authentication wrapper component
function AuthWrapper() {
  const { isAuthenticated, loading } = useAuth();
  const [authMode, setAuthMode] = useState('login'); // 'login', 'register', 'forgot-password', or 'reset-password'

  // Check if there's a reset token in the URL
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    if (token) {
      setAuthMode('reset-password');
    }
  }, []);

  if (loading) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <h2>Loading...</h2>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    if (authMode === 'login') {
      return (
        <Login 
          onToggleMode={() => setAuthMode('register')}
          onForgotPassword={() => setAuthMode('forgot-password')}
        />
      );
    } else if (authMode === 'register') {
      return (
        <Register onToggleMode={() => setAuthMode('login')} />
      );
    } else if (authMode === 'forgot-password') {
      return (
        <ForgotPassword onBackToLogin={() => setAuthMode('login')} />
      );
    } else if (authMode === 'reset-password') {
      return (
        <ResetPasswordSimple onBackToLogin={() => setAuthMode('login')} />
      );
    }
  }

  return <TodoApp />;
}

// Main App component
function App() {
  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <AuthProvider>
        <AuthWrapper />
      </AuthProvider>
    </GoogleOAuthProvider>
  );
}

export default App;
