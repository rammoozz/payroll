import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../api';

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authApi.login({ username: email, password });
      localStorage.setItem('token', response.access_token);
      localStorage.setItem('familyOfficeName', response.family_office_name);
      navigate('/employees');
    } catch (err) {
      setError('Incorrect email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="card" style={{ maxWidth: '400px', margin: '100px auto' }}>
        <h1>Family Office Payroll</h1>
        <p>Demo accounts:</p>
        <ul>
          <li>smith@demo.com / demo123</li>
          <li>jones@demo.com / demo123</li>
        </ul>
        
        <form onSubmit={handleSubmit}>
          <input
            type="email"
            className="input"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            data-cy="email"
          />
          <input
            type="password"
            className="input"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            data-cy="password"
          />
          {error && <div className="error">{error}</div>}
          <button 
            type="submit" 
            className="button" 
            disabled={loading}
            data-cy="submit"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;