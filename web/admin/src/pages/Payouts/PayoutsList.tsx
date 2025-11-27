import { useState, useEffect } from 'react';
import { adminAPI } from '../../api/adminClient';
import type { PayoutListItem } from '../../types/admin';

export default function PayoutsList() {
  const [payouts, setPayouts] = useState<PayoutListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPayouts();
  }, []);

  const loadPayouts = async () => {
    try {
      const data = await adminAPI.getPayouts();
      setPayouts(data);
    } catch (error) {
      console.error('Failed to load payouts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (id: number) => {
    if (!confirm('Approve this payout?')) return;
    try {
      await adminAPI.approvePayout(id);
      loadPayouts();
      alert('Payout approved');
    } catch (error: any) {
      alert('Failed: ' + error.message);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h1 className="page-title">Payouts Management</h1>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Recipient</th>
              <th>Group</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {payouts.map((payout) => (
              <tr key={payout.id}>
                <td>{payout.id}</td>
                <td>{payout.recipient_name}</td>
                <td>{payout.group_name}</td>
                <td>GHS {payout.amount}</td>
                <td>
                  <span className={`badge badge-${
                    payout.status === 'success' ? 'success' :
                    payout.status === 'failed' ? 'danger' : 'warning'
                  }`}>
                    {payout.status}
                  </span>
                </td>
                <td>{payout.payout_date ? new Date(payout.payout_date).toLocaleDateString() : '-'}</td>
                <td>
                  {payout.status === 'pending' && (
                    <button
                      onClick={() => handleApprove(payout.id)}
                      className="btn btn-success"
                      style={{ padding: '0.25rem 0.75rem', fontSize: '0.75rem' }}
                    >
                      Approve
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

