const API_BASE = '/api/v1';

export async function apiFetch(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API Error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export const api = {
  getDashboardStats: () => apiFetch('/dashboard/stats'),
  getTimeline: (days = 30) => apiFetch(`/dashboard/timeline?days=${days}`),
  getTasks: (params = {}) => {
    const query = new URLSearchParams(params).toString();
    return apiFetch(`/tasks${query ? '?' + query : ''}`);
  },
  getTaskDetail: (taskId) => apiFetch(`/tasks/${taskId}`),
  getTaskLogs: (taskId) => apiFetch(`/logs/${taskId}`),
  getRecentLogs: (lines = 200) => apiFetch(`/logs/recent?lines=${lines}`),
  getScreenshots: (taskId) => apiFetch(`/screenshots/${taskId}`),
  getSettings: () => apiFetch('/settings'),
};
