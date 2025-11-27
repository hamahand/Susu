import { useState, useEffect } from 'react';
import { adminAPI } from '../../api/adminClient';
import type { PaymentListItem } from '../../types/admin';

export default function PaymentsList() {
  const [payments, setPayments] = useState<PaymentListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPayments();
  }, []);

  const loadPayments = async () => {
    try {
      const data = await adminAPI.getPayments({ limit: 100 });
      setPayments(data);
    } catch (error) {
      console.error('Failed to load payments:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2rem' }}>
        <h1 className="page-title">Payments</h1>
        <button onClick={() => adminAPI.exportPayments()} className="btn btn-outline">
          📥 Export CSV
        </button>
      </div>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>User</th>
              <th>Group</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Type</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {payments.map((payment) => (
              <tr key={payment.id}>
                <td>{payment.id}</td>
                <td>{payment.user_name}</td>
                <td>{payment.group_name}</td>
                <td>GHS {payment.amount}</td>
                <td>
                  <span className={`badge badge-${
                    payment.status === 'success' ? 'success' :
                    payment.status === 'failed' ? 'danger' : 'warning'
                  }`}>
                    {payment.status}
                  </span>
                </td>
                <td>{payment.payment_type}</td>
                <td>{payment.payment_date ? new Date(payment.payment_date).toLocaleDateString() : '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

