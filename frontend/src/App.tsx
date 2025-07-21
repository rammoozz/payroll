import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Employees from './pages/Employees';
import PayrollStatus from './pages/PayrollStatus';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/employees" element={<PrivateRoute><Employees /></PrivateRoute>} />
          <Route path="/payroll/:runId" element={<PrivateRoute><PayrollStatus /></PrivateRoute>} />
          <Route path="/" element={<Navigate to="/employees" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

// Simple private route component
function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('token');
  return token ? <>{children}</> : <Navigate to="/login" replace />;
}

export default App;