import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import { useApi } from '../hooks/useApi';
import { api } from '../utils/api';
import { formatDuration, formatDateTime, truncate, getWebsiteLabel } from '../utils/formatters';

const STATUS_FILTERS = ['all', 'success', 'failed', 'timeout', 'running'];

export default function Tasks() {
  const navigate = useNavigate();
  const [statusFilter, setStatusFilter] = useState('all');
  const [search, setSearch] = useState('');

  const { data: tasks, loading } = useApi(
    () => api.getTasks(statusFilter !== 'all' ? { status: statusFilter } : {}),
    [statusFilter]
  );

  const filtered = (tasks || []).filter(t =>
    !search || 
    t.task_id?.toLowerCase().includes(search.toLowerCase()) ||
    t.prompt?.toLowerCase().includes(search.toLowerCase()) ||
    t.target_url?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <>
      <div className="page-header">
        <h2>Task Explorer</h2>
        <p>Browse and analyze all automation executions</p>
      </div>

      <div className="filter-bar">
        <div style={{ position: 'relative', flex: 1, maxWidth: 320 }}>
          <Search size={15} style={{
            position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)',
            color: '#64748b'
          }} />
          <input
            className="filter-input"
            placeholder="Search tasks..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{ paddingLeft: 36, maxWidth: '100%' }}
          />
        </div>
        {STATUS_FILTERS.map(s => (
          <button
            key={s}
            className={`filter-btn${statusFilter === s ? ' active' : ''}`}
            onClick={() => setStatusFilter(s)}
          >
            {s.charAt(0).toUpperCase() + s.slice(1)}
          </button>
        ))}
      </div>

      <div className="card">
        <div className="card-body" style={{ padding: 0 }}>
          {loading ? (
            <div className="loading-container"><div className="spinner" /></div>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Status</th>
                  <th>Task ID</th>
                  <th>Website</th>
                  <th>Prompt</th>
                  <th>Iterations</th>
                  <th>Actions</th>
                  <th>Duration</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(task => (
                  <tr key={task.task_id} onClick={() => navigate(`/tasks/${task.task_id}`)}>
                    <td><StatusBadge status={task.status} /></td>
                    <td className="mono">{task.task_id?.slice(-15)}</td>
                    <td>{getWebsiteLabel(task.website_type)}</td>
                    <td>{truncate(task.prompt, 50)}</td>
                    <td>{task.total_iterations}</td>
                    <td>{task.total_actions}</td>
                    <td>{formatDuration(task.execution_time)}</td>
                    <td>{formatDateTime(task.created_at)}</td>
                  </tr>
                ))}
                {filtered.length === 0 && (
                  <tr><td colSpan={8} style={{ textAlign: 'center', padding: 40, color: '#64748b' }}>
                    {search ? 'No matching tasks' : 'No tasks found'}
                  </td></tr>
                )}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </>
  );
}
