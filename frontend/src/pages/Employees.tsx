import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { employeeApi, payrollApi, Employee } from '../api';

function Employees() {
  const navigate = useNavigate();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState('');
  const familyOfficeName = localStorage.getItem('familyOfficeName') || 'Family Office';

  useEffect(() => {
    loadEmployees();
  }, []);

  const loadEmployees = async () => {
    try {
      const data = await employeeApi.getAll();
      setEmployees(data);
    } catch (err) {
      setError('Failed to load employees');
    } finally {
      setLoading(false);
    }
  };

  const handleRunPayroll = async () => {
    setProcessing(true);
    setError('');

    try {
      const employeeIds = employees.map(e => e.id);
      const payrollRun = await payrollApi.runPayroll(employeeIds);
      navigate(`/payroll/${payrollRun.id}`);
    } catch (err) {
      setError('Failed to start payroll run');
      setProcessing(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('familyOfficeName');
    navigate('/login');
  };

  if (loading) {
    return <div className="container">Loading...</div>;
  }

  return (
    <div className="container">
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h1>{familyOfficeName}</h1>
          <button className="button" onClick={handleLogout} style={{ background: '#6c757d' }}>
            Logout
          </button>
        </div>
        
        <h2>Employees ({employees.length})</h2>
        
        {error && <div className="error">{error}</div>}
        
        <ul className="employee-list">
          {employees.map(employee => (
            <li key={employee.id} className="employee-item">
              <div>
                <strong>{employee.name}</strong>
                <div>ID: {employee.id}</div>
              </div>
              <div>
                <strong>${employee.salary.toLocaleString()}</strong>
                <div style={{ fontSize: '14px', color: '#666' }}>Annual Salary</div>
              </div>
            </li>
          ))}
        </ul>
        
        <button
          className="button"
          onClick={handleRunPayroll}
          disabled={processing || employees.length === 0}
          data-cy="run-payroll"
          style={{ width: '100%', marginTop: '20px' }}
        >
          {processing ? 'Starting Payroll Run...' : `Run Payroll for ${employees.length} Employees`}
        </button>
      </div>
    </div>
  );
}

export default Employees;