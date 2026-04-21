export function formatDuration(seconds) {
  if (!seconds && seconds !== 0) return '—';
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  const mins = Math.floor(seconds / 60);
  const secs = (seconds % 60).toFixed(0);
  return `${mins}m ${secs}s`;
}

export function formatDate(dateStr) {
  if (!dateStr) return '—';
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric',
    });
  } catch { return dateStr; }
}

export function formatDateTime(dateStr) {
  if (!dateStr) return '—';
  try {
    const d = new Date(dateStr);
    return d.toLocaleString('en-US', {
      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
    });
  } catch { return dateStr; }
}

export function formatNumber(n) {
  if (n === null || n === undefined) return '0';
  return n.toLocaleString();
}

export function truncate(str, len = 60) {
  if (!str) return '';
  return str.length > len ? str.slice(0, len) + '...' : str;
}

export function getWebsiteLabel(type) {
  const labels = {
    youtube: 'YouTube',
    amazon: 'Amazon',
    demoqa: 'DemoQA',
    yahoo_finance: 'Yahoo Finance',
    makemytrip: 'MakeMyTrip',
    custom: 'Custom',
  };
  return labels[type] || type || 'Unknown';
}
