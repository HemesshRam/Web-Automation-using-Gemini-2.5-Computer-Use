import { useNavigate } from 'react-router-dom';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';
import { Activity, CheckCircle, Clock, MousePointerClick } from 'lucide-react';
import StatsCard from '../components/StatsCard';
import StatusBadge from '../components/StatusBadge';
import { useApi } from '../hooks/useApi';
import { api } from '../utils/api';
import { formatDuration, formatDateTime, truncate, getWebsiteLabel } from '../utils/formatters';

const PIE_COLORS = ['#10b981', '#ef4444', '#f59e0b', '#3b82f6'];

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: '#1a1d2e', border: '1px solid rgba(255,255,255,0.1)',
      borderRadius: 8, padding: '10px 14px', fontSize: 12
    }}>
      <p style={{ color: '#94a3b8', marginBottom: 6 }}>{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color }}>{p.name}: {p.value}</p>
      ))}
    </div>
  );
};

export default function Dashboard() {
  const navigate = useNavigate();
  const { data: stats, loading: statsLoading } = useApi(() => api.getDashboardStats(), []);
  const { data: timeline, loading: timelineLoading } = useApi(() => api.getTimeline(30), []);
  const { data: tasks, loading: tasksLoading } = useApi(() => api.getTasks({ limit: 8 }), []);

  if (statsLoading) {
    return <div className="loading-container"><div className="spinner" /></div>;
  }

  const s = stats || {};

  const pieData = [
    { name: 'Success', value: s.success_count || 0 },
    { name: 'Failed', value: s.failed_count || 0 },
    { name: 'Timeout', value: s.timeout_count || 0 },
    { name: 'Running', value: s.running_count || 0 },
  ].filter(d => d.value > 0);

  return (
    <>
      <div className="page-header">
        <h2>Dashboard</h2>
        <p>Real-time analytics for Gemini 2.5 Computer Use automation</p>
      </div>

      {/* KPI Cards */}
      <div className="stats-grid">
        <StatsCard
          label="Total Tasks"
          value={s.total_tasks || 0}
          sub={`${s.websites_automated?.length || 0} websites automated`}
          icon={Activity}
          color="blue"
        />
        <StatsCard
          label="Success Rate"
          value={`${s.success_rate || 0}%`}
          sub={`${s.success_count || 0} succeeded, ${s.failed_count || 0} failed`}
          icon={CheckCircle}
          color="green"
        />
        <StatsCard
          label="Avg Execution"
          value={formatDuration(s.avg_execution_time)}
          sub={`${s.total_iterations || 0} total iterations`}
          icon={Clock}
          color="purple"
        />
        <StatsCard
          label="Actions Executed"
          value={s.total_actions || 0}
          sub={`~${s.avg_actions_per_task || 0} per task`}
          icon={MousePointerClick}
          color="amber"
        />
      </div>

      {/* Charts */}
      <div className="charts-grid">
        <div className="card">
          <div className="card-header">
            <span className="card-title">Execution Performance Over Time</span>
          </div>
          <div className="card-body" style={{ height: 280 }}>
            {timeline && timeline.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={timeline}>
                  <defs>
                    <linearGradient id="gradSuccess" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="gradFailed" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} tickLine={false} />
                  <YAxis tick={{ fill: '#64748b', fontSize: 11 }} tickLine={false} axisLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="success_count" name="Success" stroke="#10b981" fill="url(#gradSuccess)" strokeWidth={2} />
                  <Area type="monotone" dataKey="failed_count" name="Failed" stroke="#ef4444" fill="url(#gradFailed)" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="empty-state"><p>No timeline data yet</p></div>
            )}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Task Status Distribution</span>
          </div>
          <div className="card-body" style={{ height: 280 }}>
            {pieData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%" cy="45%"
                    innerRadius={55} outerRadius={85}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {pieData.map((_, idx) => (
                      <Cell key={idx} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Legend
                    verticalAlign="bottom"
                    iconType="circle"
                    iconSize={8}
                    formatter={(v) => <span style={{ color: '#94a3b8', fontSize: 12 }}>{v}</span>}
                  />
                  <Tooltip
                    contentStyle={{
                      background: '#1a1d2e', border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: 8, fontSize: 12
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="empty-state"><p>No tasks recorded</p></div>
            )}
          </div>
        </div>
      </div>

      {/* Recent Tasks Table */}
      <div className="card">
        <div className="card-header">
          <span className="card-title">Recent Executions</span>
          <button className="filter-btn" onClick={() => navigate('/tasks')}>View All</button>
        </div>
        <div className="card-body" style={{ padding: 0 }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Status</th>
                <th>Task ID</th>
                <th>Website</th>
                <th>Prompt</th>
                <th>Duration</th>
                <th>Actions</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {(tasks || []).map(task => (
                <tr key={task.task_id} onClick={() => navigate(`/tasks/${task.task_id}`)}>
                  <td><StatusBadge status={task.status} /></td>
                  <td className="mono">{task.task_id?.slice(-12)}</td>
                  <td>{getWebsiteLabel(task.website_type)}</td>
                  <td>{truncate(task.prompt, 45)}</td>
                  <td>{formatDuration(task.execution_time)}</td>
                  <td>{task.total_actions}</td>
                  <td>{formatDateTime(task.created_at)}</td>
                </tr>
              ))}
              {(!tasks || tasks.length === 0) && (
                <tr><td colSpan={7} style={{ textAlign: 'center', padding: 40, color: '#64748b' }}>No tasks found</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
