import { Globe, Monitor, Shield, Database, Cpu, Brain } from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { api } from '../utils/api';

export default function SettingsPage() {
  const { data: settings, loading } = useApi(() => api.getSettings(), []);

  if (loading) {
    return <div className="loading-container"><div className="spinner" /></div>;
  }

  const s = settings || {};

  const sections = [
    {
      title: 'Application', icon: Globe,
      rows: [
        ['App Name', s.app_name],
        ['Version', s.app_version],
        ['Environment', s.environment],
      ]
    },
    {
      title: 'AI Models', icon: Brain,
      rows: [
        ['Gemini Model', s.gemini_model],
        ['Computer Use', s.computer_use_model],
      ]
    },
    {
      title: 'Browser', icon: Monitor,
      rows: [
        ['Type', s.browser_type],
        ['Headless', s.headless ? 'Yes' : 'No'],
        ['Window Size', `${s.window_width}×${s.window_height}`],
      ]
    },
    {
      title: 'Security', icon: Shield,
      rows: [
        ['Anti-Bot', s.anti_bot_enabled ? 'Enabled' : 'Disabled'],
        ['Max Retries', s.max_retry_attempts],
      ]
    },
    {
      title: 'Database', icon: Database,
      rows: [
        ['URL', s.database_url],
        ['Screenshots', s.screenshots_enabled ? 'Enabled' : 'Disabled'],
      ]
    },
    {
      title: 'Logging', icon: Cpu,
      rows: [
        ['Log Level', s.log_level],
      ]
    },
  ];

  return (
    <>
      <div className="page-header">
        <h2>Settings</h2>
        <p>Current configuration (read-only)</p>
      </div>

      <div className="settings-grid">
        {sections.map(({ title, icon: Icon, rows }) => (
          <div key={title} className="settings-section">
            <h3><Icon size={16} /> {title}</h3>
            {rows.map(([key, val]) => (
              <div key={key} className="settings-row">
                <span className="settings-key">{key}</span>
                <span className="settings-value">{String(val ?? '—')}</span>
              </div>
            ))}
          </div>
        ))}
      </div>
    </>
  );
}
