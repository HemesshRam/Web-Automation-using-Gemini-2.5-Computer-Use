import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, ExternalLink } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import { useApi } from '../hooks/useApi';
import { api } from '../utils/api';
import { formatDuration, formatDateTime, getWebsiteLabel } from '../utils/formatters';

const TABS = ['Overview', 'AI Summary', 'Screenshots', 'Raw JSON'];

export default function TaskDetail() {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('Overview');
  const { data: task, loading } = useApi(() => api.getTaskDetail(taskId), [taskId]);
  const { data: screenshots } = useApi(() => api.getScreenshots(taskId), [taskId]);

  if (loading) {
    return <div className="loading-container"><div className="spinner" /></div>;
  }

  if (!task) {
    return (
      <div className="empty-state">
        <h3>Task not found</h3>
        <p>Task ID: {taskId}</p>
        <button className="filter-btn" onClick={() => navigate('/tasks')} style={{ marginTop: 16 }}>
          Back to Tasks
        </button>
      </div>
    );
  }

  return (
    <>
      <div className="page-header" style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
        <button onClick={() => navigate('/tasks')} className="filter-btn" style={{ padding: '7px 10px' }}>
          <ArrowLeft size={16} />
        </button>
        <div>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            Task {task.task_id?.slice(-12)}
            <StatusBadge status={task.status} />
          </h2>
          <p>{getWebsiteLabel(task.website_type)} • {formatDateTime(task.created_at)}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        {TABS.map(tab => (
          <button key={tab} className={`tab${activeTab === tab ? ' active' : ''}`} onClick={() => setActiveTab(tab)}>
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'Overview' && (
        <>
          <div className="detail-grid">
            <div className="detail-item">
              <div className="detail-label">Task ID</div>
              <div className="detail-value" style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>{task.task_id}</div>
            </div>
            <div className="detail-item">
              <div className="detail-label">Status</div>
              <div className="detail-value"><StatusBadge status={task.status} /></div>
            </div>
            <div className="detail-item">
              <div className="detail-label">Execution Time</div>
              <div className="detail-value">{formatDuration(task.execution_time)}</div>
            </div>
            <div className="detail-item">
              <div className="detail-label">Total Iterations</div>
              <div className="detail-value">{task.total_iterations}</div>
            </div>
            <div className="detail-item">
              <div className="detail-label">Actions Executed</div>
              <div className="detail-value">{task.total_actions}</div>
            </div>
            <div className="detail-item">
              <div className="detail-label">Pages Visited</div>
              <div className="detail-value">{task.pages_visited}</div>
            </div>
            <div className="detail-item">
              <div className="detail-label">Engine</div>
              <div className="detail-value">{task.engine || 'Gemini Computer Use'}</div>
            </div>
            <div className="detail-item">
              <div className="detail-label">Website Type</div>
              <div className="detail-value">{getWebsiteLabel(task.website_type)}</div>
            </div>
            <div className="detail-item" style={{ gridColumn: '1 / -1' }}>
              <div className="detail-label">Navigation URL</div>
              <div className="detail-value">
                {task.navigation_url && (
                  <a href={task.navigation_url} target="_blank" rel="noopener noreferrer" style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                    {task.navigation_url} <ExternalLink size={12} />
                  </a>
                )}
              </div>
            </div>
            {task.actual_url && (
              <div className="detail-item" style={{ gridColumn: '1 / -1' }}>
                <div className="detail-label">Final URL</div>
                <div className="detail-value">
                  <a href={task.actual_url} target="_blank" rel="noopener noreferrer" style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                    {task.actual_url} <ExternalLink size={12} />
                  </a>
                </div>
              </div>
            )}
          </div>

          {/* Pages visited */}
          {task.unique_pages?.length > 0 && (
            <div style={{ marginTop: 22 }}>
              <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 10 }}>Pages Visited</h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {task.unique_pages.map((url, i) => (
                  <a key={i} href={url} target="_blank" rel="noopener noreferrer"
                    style={{ fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--accent-blue)', display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                    {url} <ExternalLink size={10} />
                  </a>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {activeTab === 'AI Summary' && (
        <div className="card">
          <div className="card-header">
            <span className="card-title">AI Agent Summary</span>
          </div>
          <div className="card-body">
            {task.ai_summary ? (
              <div className="ai-summary">{task.ai_summary}</div>
            ) : (
              <div className="empty-state"><p>No AI summary available for this task</p></div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'Screenshots' && (
        <div className="card">
          <div className="card-header">
            <span className="card-title">Step Screenshots ({screenshots?.length || 0})</span>
          </div>
          <div className="card-body">
            {screenshots && screenshots.length > 0 ? (
              <div className="screenshots-grid">
                {screenshots.map((ss, i) => (
                  <div key={i} className="screenshot-card" onClick={() => window.open(ss.url, '_blank')}>
                    <img src={ss.url} alt={ss.filename} loading="lazy" />
                    <div className="screenshot-card-footer">
                      {ss.step_number != null ? `Step ${ss.step_number}` : ''} — {ss.filename}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state"><p>No screenshots found for this task</p></div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'Raw JSON' && (
        <div className="card">
          <div className="card-header">
            <span className="card-title">Execution Result JSON</span>
          </div>
          <div className="card-body">
            <pre style={{
              background: '#0a0c12', padding: 20, borderRadius: 'var(--radius-md)',
              fontSize: 12, fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)',
              overflow: 'auto', maxHeight: 500, lineHeight: 1.6
            }}>
              {JSON.stringify(task.raw_json || task, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </>
  );
}
