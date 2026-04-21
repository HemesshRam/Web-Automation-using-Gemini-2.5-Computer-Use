import { useRef, useEffect, useState, useCallback } from 'react';
import {
  Wifi, WifiOff, Trash2, ChevronDown, Play, Square,
  Search, Terminal, Download, Send, ArrowDown, Filter
} from 'lucide-react';

/* ═══════════════════════════════════════════════════════════════════════
   Live Logs — Full CMD-like console with real-time process output
   ═══════════════════════════════════════════════════════════════════════ */

const TASK_OPTIONS = [
  { value: '1', label: '1 — DemoQA Test' },
  { value: '2', label: '2 — Amazon' },
  { value: '3', label: '3 — YouTube' },
  { value: '4', label: '4 — Yahoo Finance' },
  { value: '5', label: '5 — MakeMyTrip' },
  { value: '6', label: '6 — Custom Website' },
  { value: '7', label: '7 — View Supported Sites' },
  { value: '8', label: '8 — View Settings' },
];

function classifyLine(msg) {
  if (!msg) return 'normal';
  const m = msg.toUpperCase();
  if (m.includes('ERROR') || m.includes('FATAL') || m.includes('FAILED'))  return 'error';
  if (m.includes('WARNING') || m.includes('WARN'))                          return 'warning';
  if (m.includes('SUCCESS') || m.includes('COMPLETE') || m.includes('✓') || m.includes('READY')) return 'success';
  if (m.includes('[GEMINI CU]') || m.includes('[SCREENSHOT]'))              return 'action';
  if (m.includes('[NAVIGATE]') || m.includes('[URL]') || m.includes('[LOADED]')) return 'nav';
  if (m.includes('═') || m.includes('─') || m.includes('====='))           return 'separator';
  if (msg.startsWith('▶') || msg.startsWith('●') || msg.startsWith('■'))   return 'system';
  return 'normal';
}

function parseLine(msg) {
  // Try to extract structured log: "2026-04-19 21:30:01 - Component - LEVEL - message"
  const match = msg.match(
    /^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s*-\s*(\S+)\s*-\s*(\w+)\s*-\s*(.*)/
  );
  if (match) {
    return {
      timestamp: match[1],
      component: match[2],
      level: match[3],
      message: match[4],
      raw: msg,
    };
  }
  return { timestamp: '', component: '', level: '', message: msg, raw: msg };
}

export default function Logs() {
  const [messages, setMessages] = useState([]);
  const [connected, setConnected] = useState(false);
  const [processRunning, setProcessRunning] = useState(false);
  const [autoScroll, setAutoScroll] = useState(true);
  const [levelFilter, setLevelFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTask, setSelectedTask] = useState('1');
  const [inputText, setInputText] = useState('');
  const [lineCount, setLineCount] = useState(0);
  const [showSearch, setShowSearch] = useState(false);

  const containerRef = useRef(null);
  const wsRef = useRef(null);
  const reconnectRef = useRef(null);
  const bottomRef = useRef(null);

  // ── WebSocket connection ────────────────────────────────────────────
  const connect = useCallback(() => {
    try {
      const wsUrl = `ws://${window.location.hostname}:8000/ws/live-console`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => setConnected(true);

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'status') {
            setProcessRunning(data.data?.running ?? false);
            return;
          }

          setMessages(prev => {
            const next = [...prev, data];
            if (next.length > 8000) return next.slice(-6000);
            return next;
          });
          setLineCount(prev => prev + 1);
        } catch {
          setMessages(prev => [...prev, { type: 'output', message: event.data }]);
        }
      };

      ws.onclose = () => {
        setConnected(false);
        reconnectRef.current = setTimeout(connect, 2000);
      };

      ws.onerror = () => ws.close();
      wsRef.current = ws;
    } catch {
      setConnected(false);
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) wsRef.current.close();
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
    };
  }, [connect]);

  // ── Auto-scroll ─────────────────────────────────────────────────────
  useEffect(() => {
    if (autoScroll && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'auto' });
    }
  }, [messages, autoScroll]);

  // ── Actions ─────────────────────────────────────────────────────────
  const sendCommand = (action, extra = {}) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action, ...extra }));
    }
  };

  const handleStart = () => sendCommand('start', { choice: selectedTask });
  const handleStop  = () => sendCommand('stop');
  const handleInput = () => {
    if (inputText.trim()) {
      sendCommand('input', { text: inputText });
      setInputText('');
    }
  };
  const handleClear = () => { setMessages([]); setLineCount(0); };

  const handleExport = () => {
    const text = messages.map(m => m.message || '').join('\n');
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `automation_logs_${new Date().toISOString().slice(0,19).replace(/:/g, '-')}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // ── Filtering ───────────────────────────────────────────────────────
  const filtered = messages.filter(m => {
    const msg = m.message || '';
    const cls = classifyLine(msg);

    if (levelFilter === 'errors' && cls !== 'error') return false;
    if (levelFilter === 'warnings' && cls !== 'warning' && cls !== 'error') return false;
    if (levelFilter === 'actions' && cls !== 'action' && cls !== 'nav') return false;
    if (levelFilter === 'system' && m.type !== 'system') return false;

    if (searchQuery) {
      return msg.toLowerCase().includes(searchQuery.toLowerCase());
    }
    return true;
  });

  // ── Render ──────────────────────────────────────────────────────────
  return (
    <>
      <div className="page-header">
        <h2><Terminal size={22} style={{ verticalAlign: 'text-bottom', marginRight: 8 }} />Live Console</h2>
        <p>Real-time automation output — exactly as it appears in CMD</p>
      </div>

      {/* ── Control Bar ─────────────────────────────────────────────── */}
      <div className="console-controls">
        {/* Connection status */}
        <div className="console-status">
          {connected ? (
            <><Wifi size={14} color="#10b981" /> <span className="status-text connected">Connected</span></>
          ) : (
            <><WifiOff size={14} color="#ef4444" /> <span className="status-text disconnected">Disconnected</span></>
          )}
          {processRunning && <span className="process-badge running">● RUNNING</span>}
          {!processRunning && messages.length > 0 && <span className="process-badge idle">● IDLE</span>}
        </div>

        {/* Task selector + Start/Stop */}
        <div className="console-actions">
          <select
            className="task-select"
            value={selectedTask}
            onChange={e => setSelectedTask(e.target.value)}
            disabled={processRunning}
          >
            {TASK_OPTIONS.map(o => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>

          {processRunning ? (
            <button className="console-btn danger" onClick={handleStop}>
              <Square size={13} /> Stop
            </button>
          ) : (
            <button className="console-btn primary" onClick={handleStart} disabled={!connected}>
              <Play size={13} /> Run
            </button>
          )}
        </div>

        {/* Toolbar right */}
        <div className="console-toolbar-right">
          <button className={`console-icon-btn${showSearch ? ' active' : ''}`}
                  onClick={() => setShowSearch(!showSearch)} title="Search">
            <Search size={14} />
          </button>
          <button className="console-icon-btn" onClick={handleExport} title="Export logs">
            <Download size={14} />
          </button>
          <button className="console-icon-btn" onClick={handleClear} title="Clear">
            <Trash2 size={14} />
          </button>
          <button
            className={`console-icon-btn${autoScroll ? ' active' : ''}`}
            onClick={() => setAutoScroll(!autoScroll)}
            title={autoScroll ? 'Auto-scroll ON' : 'Auto-scroll OFF'}
          >
            <ArrowDown size={14} />
          </button>
          <span className="line-counter">{lineCount.toLocaleString()} lines</span>
        </div>
      </div>

      {/* ── Search & Filter bar ─────────────────────────────────────── */}
      {showSearch && (
        <div className="console-search-bar">
          <Search size={14} style={{ color: 'var(--text-muted)' }} />
          <input
            className="console-search-input"
            placeholder="Search logs..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            autoFocus
          />
          <div className="console-filter-chips">
            {['all', 'errors', 'warnings', 'actions', 'system'].map(f => (
              <button key={f}
                className={`chip${levelFilter === f ? ' active' : ''}`}
                onClick={() => setLevelFilter(f)}>
                {f === 'all' ? 'All' : f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* ── Console Output ──────────────────────────────────────────── */}
      <div className="console-output" ref={containerRef}>
        {filtered.length === 0 ? (
          <div className="console-empty">
            <Terminal size={40} strokeWidth={1} />
            <p>{connected
              ? (processRunning ? 'Waiting for output...' : 'Select a task and click Run to start')
              : 'Connecting to server...'
            }</p>
          </div>
        ) : (
          filtered.map((m, i) => {
            const msg = m.message || '';
            const cls = classifyLine(msg);
            const parsed = parseLine(msg);
            const isSystemMsg = m.type === 'system';

            return (
              <div key={i} className={`console-line ${cls}${isSystemMsg ? ' system-line' : ''}`}>
                <span className="console-line-no">{i + 1}</span>
                {parsed.timestamp && (
                  <span className="console-ts">{parsed.timestamp}</span>
                )}
                {parsed.level && (
                  <span className={`console-level ${parsed.level}`}>{parsed.level}</span>
                )}
                {parsed.component && (
                  <span className="console-comp">{parsed.component}</span>
                )}
                <span className="console-msg"
                      dangerouslySetInnerHTML={
                        searchQuery
                          ? { __html: highlightSearch(parsed.message || msg, searchQuery) }
                          : undefined
                      }
                >
                  {!searchQuery ? (parsed.message || msg) : undefined}
                </span>
              </div>
            );
          })
        )}
        <div ref={bottomRef} />
      </div>

      {/* ── Input Bar (send text to stdin) ──────────────────────────── */}
      {processRunning && (
        <div className="console-input-bar">
          <Send size={14} style={{ color: 'var(--text-muted)', flexShrink: 0 }} />
          <input
            className="console-stdin-input"
            placeholder="Type input for the running process and press Enter..."
            value={inputText}
            onChange={e => setInputText(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') handleInput(); }}
          />
          <button className="console-btn primary small" onClick={handleInput}>Send</button>
        </div>
      )}
    </>
  );
}

function highlightSearch(text, query) {
  if (!query) return text;
  const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return text.replace(
    new RegExp(`(${escaped})`, 'gi'),
    '<mark class="search-highlight">$1</mark>'
  );
}
