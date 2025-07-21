import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { payrollApi, PayrollRun } from '../api';

function PayrollStatus() {
  const { runId } = useParams<{ runId: string }>();
  const navigate = useNavigate();
  const [payrollRun, setPayrollRun] = useState<PayrollRun | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!runId) return;
    
    const checkStatus = async () => {
      try {
        const data = await payrollApi.getStatus(parseInt(runId));
        setPayrollRun(data);
        
        // Keep polling if still processing
        if (data.status === 'pending' || data.status === 'processing') {
          setTimeout(checkStatus, 2000); // Poll every 2 seconds
        }
      } catch (err) {
        setError('Failed to load payroll status');
      } finally {
        setLoading(false);
      }
    };

    checkStatus();
  }, [runId]);

  const handleDownload = () => {
    if (!runId || !payrollRun || payrollRun.status !== 'completed') return;
    
    const token = localStorage.getItem('token');
    const downloadUrl = payrollApi.downloadPdf(parseInt(runId));
    
    // Create a temporary link with auth header
    window.open(`${downloadUrl}?token=${token}`, '_blank');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return '#28a745';
      case 'failed': return '#dc3545';
      case 'processing': return '#007bff';
      default: return '#6c757d';
    }
  };

  const getProgress = () => {
    if (!payrollRun) return 0;
    switch (payrollRun.status) {
      case 'completed': return 100;
      case 'processing': return 50;
      case 'failed': return 0;
      default: return 10;
    }
  };

  if (loading && !payrollRun) {
    return <div className="container">Loading...</div>;
  }

  return (
    <div className="container">
      <div className="card">
        <button onClick={() => navigate('/employees')} style={{ marginBottom: '20px' }}>
          ← Back to Employees
        </button>
        
        <h1>Payroll Run #{runId}</h1>
        
        {error && <div className="error">{error}</div>}
        
        {payrollRun && (
          <>
            <div style={{ marginBottom: '20px' }}>
              <strong>Status: </strong>
              <span style={{ color: getStatusColor(payrollRun.status), fontWeight: 'bold' }}>
                {payrollRun.status.toUpperCase()}
              </span>
            </div>
            
            <div style={{ marginBottom: '20px' }}>
              <strong>Started: </strong>
              {new Date(payrollRun.created_at).toLocaleString()}
            </div>
            
            {payrollRun.completed_at && (
              <div style={{ marginBottom: '20px' }}>
                <strong>Completed: </strong>
                {new Date(payrollRun.completed_at).toLocaleString()}
              </div>
            )}
            
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${getProgress()}%` }}
              />
            </div>
            
            {payrollRun.status === 'processing' && (
              <div style={{ textAlign: 'center', marginTop: '20px' }}>
                <p>Processing payroll... This may take a few moments.</p>
              </div>
            )}
            
            {payrollRun.status === 'completed' && (
              <button 
                className="button" 
                onClick={handleDownload}
                data-cy="download"
                style={{ width: '100%', marginTop: '20px' }}
              >
                Download Pay Stubs (PDF)
              </button>
            )}
            
            {payrollRun.status === 'failed' && (
              <div className="error" style={{ marginTop: '20px' }}>
                Payroll run failed. Please try again or contact support.
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default PayrollStatus;