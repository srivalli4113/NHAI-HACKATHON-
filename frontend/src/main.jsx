import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, CalendarCheck, Camera, Cpu, Database, Download, FileWarning, Gauge, Lock, Shield, UserPlus, Users, WifiOff } from 'lucide-react';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from 'recharts';
import './styles.css';

const API = import.meta.env.VITE_API_BASE || '';

function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function apiFetch(path, options = {}, token) {
  const response = await fetch(`${API}${path}`, {
    ...options,
    headers: {
      ...(options.headers || {}),
      ...authHeaders(token)
    }
  });
  if (!response.ok) {
    let detail = await response.text();
    try {
      detail = JSON.parse(detail).detail || detail;
      if (typeof detail === 'object') detail = JSON.stringify(detail);
    } catch {}
    throw new Error(detail || `Request failed: ${response.status}`);
  }
  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) return response.json();
  return response;
}

function readStoredSession() {
  const token = localStorage.getItem('nhai_token');
  if (!token) return null;
  return {
    token,
    role: localStorage.getItem('nhai_role') || 'admin',
    displayName: localStorage.getItem('nhai_display_name') || 'System Administrator'
  };
}

function saveSession(session) {
  localStorage.setItem('nhai_token', session.token);
  localStorage.setItem('nhai_role', session.role);
  localStorage.setItem('nhai_display_name', session.displayName);
}

function clearStoredSession() {
  localStorage.removeItem('nhai_token');
  localStorage.removeItem('nhai_role');
  localStorage.removeItem('nhai_display_name');
}

function useCamera() {
  const videoRef = useRef(null);
  const [ready, setReady] = useState(false);
  const [error, setError] = useState('');

  async function start() {
    try {
      if (!window.isSecureContext && !['localhost', '127.0.0.1'].includes(window.location.hostname)) {
        throw new Error('Camera access is blocked on this address. Open this site through its HTTPS public link or http://127.0.0.1:8000.');
      }
      if (!navigator.mediaDevices?.getUserMedia) {
        throw new Error('Camera API is unavailable in this browser. Use Chrome, Edge, or Safari on localhost.');
      }
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 960, height: 720 }, audio: false });
      videoRef.current.srcObject = stream;
      await videoRef.current.play();
      setReady(true);
    } catch (err) {
      setError(err.message);
    }
  }

  async function captureBlob() {
    const video = videoRef.current;
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth || 960;
    canvas.height = video.videoHeight || 720;
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    return new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', 0.9));
  }

  return { videoRef, ready, error, start, captureBlob };
}

function fileFromInput(setBlob, setMessage) {
  return (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setBlob(file);
    setMessage(`Selected ${file.name}`);
  };
}

function Login({ onLogin }) {
  const [mode, setMode] = useState('signin');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [role, setRole] = useState('operator');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setError('');
    setBusy(true);
    try {
      const path = mode === 'signin' ? '/api/auth/login' : '/api/auth/signup';
      const payload = mode === 'signin'
        ? { username, password }
        : { display_name: displayName, username, password, role };
      const result = await apiFetch(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      onLogin({ token: result.access_token, role: result.role, displayName: result.display_name });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="login-shell">
      <form className="login-panel" onSubmit={submit}>
        <div className="brand-mark"><Shield size={30} /> NHAI Edge AI</div>
        <h1>Offline Face Recognition Console</h1>
        <div className="login-toggle" role="tablist" aria-label="Account access">
          <button type="button" className={mode === 'signin' ? 'active' : ''} onClick={() => { setMode('signin'); setError(''); }}>Sign in</button>
          <button type="button" className={mode === 'signup' ? 'active' : ''} onClick={() => { setMode('signup'); setError(''); }}>Create account</button>
        </div>
        {mode === 'signup' && <label>Full name<input value={displayName} onChange={(e) => setDisplayName(e.target.value)} autoComplete="name" required /></label>}
        <label>Username<input value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" required /></label>
        <label>Password<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete={mode === 'signin' ? 'current-password' : 'new-password'} minLength={mode === 'signup' ? 6 : undefined} required /></label>
        {mode === 'signup' && <>
          <label>Account type
            <select value={role} onChange={(e) => setRole(e.target.value)}>
              <option value="operator">Operator</option>
              <option value="employee">Employee</option>
            </select>
          </label>
          <p className="login-help">Operators have access to the dashboard, recognition, liveness, audit, benchmarks, and Datalake. Employees can access only the face-registration screen.</p>
        </>}
        {error && <p className="error">{error}</p>}
        <button className="primary" disabled={busy}>{mode === 'signin' ? <Lock size={16} /> : <UserPlus size={16} />}{busy ? 'Please wait...' : mode === 'signin' ? 'Sign in' : 'Create account'}</button>
      </form>
    </main>
  );
}

function Stat({ icon, label, value }) {
  return <div className="stat">{icon}<span>{label}</span><strong>{value}</strong></div>;
}

function formatPercent(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '-';
  return (Number(value) * 100).toFixed(1) + '%';
}

function OfflineProof({ benchmark, onBenchmark }) {
  const rows = [
    ['Network', 'Offline / localhost', <WifiOff size={18} />],
    ['Inference', 'Local CPU', <Cpu size={18} />],
    ['Database', 'SQLite local', <Database size={18} />],
    ['Cloud Calls', '0', <Shield size={18} />],
    ['Datalake', 'Local queue-first sync', <Database size={18} />]
  ];
  return (
    <section className="panel proof-panel">
      <div className="panel-head">
        <h2>Offline Proof</h2>
        {onBenchmark && <button onClick={onBenchmark}><Gauge size={15} /> Run Benchmark</button>}
      </div>
      <div className="proof-grid">
        {rows.map(([label, value, icon]) => <div key={label} className="proof-item">{icon}<span>{label}</span><strong>{value}</strong></div>)}
      </div>
      {benchmark && <p className="notice">CPU benchmark: avg {benchmark.average_latency_ms} ms, p95 {benchmark.p95_latency_ms} ms over {benchmark.samples} samples.</p>}
    </section>
  );
}

function EmployeeRoster({ employees }) {
  return (
    <section className="panel">
      <h2>Employee Roster</h2>
      <table>
        <thead><tr><th>Name</th><th>ID</th><th>Department</th><th>Designation</th></tr></thead>
        <tbody>
          {employees.map((employee) => (
            <tr key={employee.employee_id}><td>{employee.name}</td><td>{employee.employee_id}</td><td>{employee.department}</td><td>{employee.designation}</td></tr>
          ))}
        </tbody>
      </table>
      {!employees.length && <p className="muted">No employees registered yet.</p>}
    </section>
  );
}

function Dashboard({ token, hasFullAccess }) {
  const [metrics, setMetrics] = useState(null);
  const [logs, setLogs] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [benchmark, setBenchmark] = useState(null);

  async function load() {
    const [m, e] = await Promise.all([
      apiFetch('/api/dashboard/metrics', {}, token),
      apiFetch('/api/employees', {}, token)
    ]);
    setMetrics(m);
    setEmployees(e);
    if (hasFullAccess) setLogs(await apiFetch('/api/audit/logs?limit=25', {}, token));
  }

  async function runBenchmark() {
    setBenchmark(await apiFetch('/api/benchmark/run?samples=30', { method: 'POST' }, token));
  }

  useEffect(() => { load().catch(console.error); }, []);
  if (!metrics) return <section className="panel">Loading dashboard...</section>;

  return (
    <div className="grid">
      <Stat icon={<Users />} label="Total Employees" value={metrics.total_employees} />
      <Stat icon={<Activity />} label="Recognition Count" value={metrics.recognition_count} />
      <Stat icon={<Shield />} label="Failed Attempts" value={metrics.failed_attempts} />
      <Stat icon={<Gauge />} label="Spoofing Attempts" value={metrics.spoofing_attempts} />
      <OfflineProof benchmark={benchmark} onBenchmark={hasFullAccess ? runBenchmark : undefined} />
      <section className="panel wide">
        <h2>Recognition Trend</h2>
        <ResponsiveContainer width="100%" height={260}>
          <AreaChart data={metrics.daily_activity}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="label" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Area type="monotone" dataKey="count" stroke="#136f4a" fill="#bfe8d4" />
          </AreaChart>
        </ResponsiveContainer>
      </section>
      <section className="panel">
        <h2>Security Incidents</h2>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={metrics.security_incidents}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="type" />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="count" fill="#f08a24" />
          </BarChart>
        </ResponsiveContainer>
      </section>
      <EmployeeRoster employees={employees} />
      {hasFullAccess && <AuditTable token={token} logs={logs} />}
    </div>
  );
}

function Registration({ token, showRoster = true }) {
  const camera = useCamera();
  const [form, setForm] = useState({ name: '', employee_id: '', department: '', designation: '' });
  const [message, setMessage] = useState('');
  const [uploadBlob, setUploadBlob] = useState(null);
  const [employees, setEmployees] = useState([]);

  async function loadEmployees() {
    try {
      setEmployees(await apiFetch('/api/employees', {}, token));
    } catch (err) {
      setMessage(err.message);
    }
  }

  useEffect(() => {
    if (showRoster) loadEmployees();
  }, [showRoster]);

  async function register() {
    setMessage('');
    const blob = uploadBlob || await camera.captureBlob();
    const data = new FormData();
    Object.entries(form).forEach(([key, value]) => data.append(key, value));
    data.append('photograph', blob, `${form.employee_id || 'employee'}.jpg`);
    try {
      const result = await apiFetch('/api/employees/register', { method: 'POST', body: data }, token);
      setUploadBlob(null);
      setMessage(`Registered ${result.employee.name} (${result.employee.employee_id})`);
      if (showRoster) await loadEmployees();
    } catch (err) {
      setMessage(err.message);
    }
  }

  return (
    <section className="split">
      <CameraPanel camera={camera} />
      <div className="panel">
        <h2>Employee Registration</h2>
        {['name', 'employee_id', 'department', 'designation'].map((field) => (
          <label key={field}>{field.replace('_', ' ').toUpperCase()}
            <input value={form[field]} onChange={(e) => setForm({ ...form, [field]: e.target.value })} />
          </label>
        ))}
        <label>UPLOAD PHOTO FALLBACK<input type="file" accept="image/*" onChange={fileFromInput(setUploadBlob, setMessage)} /></label>
        {uploadBlob && <button onClick={() => { setUploadBlob(null); setMessage('Upload cleared. Live camera will be used.'); }}>Use Live Camera Instead</button>}
        <button className="primary" disabled={!camera.ready && !uploadBlob} onClick={register}><UserPlus size={16} /> Register Face</button>
        {showRoster && <>
          <h2 className="subhead">Registered Employees</h2>
          <div className="employees-list">
            {employees.map((employee) => (
              <article key={employee.employee_id} className="employee-row">
                <strong>{employee.name}</strong>
                <span>{employee.employee_id}</span>
                <small>{employee.department} · {employee.designation}</small>
              </article>
            ))}
            {!employees.length && <p className="muted">No employees registered yet.</p>}
          </div>
        </>}
        {message && <p className="notice">{message}</p>}
      </div>
    </section>
  );
}

function Recognition({ token }) {
  const camera = useCamera();
  const [faces, setFaces] = useState([]);
  const [latency, setLatency] = useState(0);
  const [running, setRunning] = useState(false);
  const [uploadBlob, setUploadBlob] = useState(null);
  const [message, setMessage] = useState('');
  const [frameSize, setFrameSize] = useState({ width: 960, height: 720 });

  async function identify(attendance = false) {
    const video = camera.videoRef.current;
    if (video?.videoWidth && video?.videoHeight && !uploadBlob) {
      setFrameSize({ width: video.videoWidth, height: video.videoHeight });
    }
    const blob = uploadBlob || await camera.captureBlob();
    const data = new FormData();
    data.append('image', blob, 'frame.jpg');
    const path = attendance ? '/api/recognition/attendance' : '/api/recognition/identify';
    const result = await apiFetch(path, { method: 'POST', body: data }, token);
    setFaces(result.faces);
    setLatency(result.latency_ms);
  }

  useEffect(() => {
    if (!running) return;
    const timer = setInterval(() => identify(false).catch(console.error), 900);
    return () => clearInterval(timer);
  }, [running, uploadBlob]);

  return (
    <section className="split">
      <CameraPanel camera={camera} faces={faces} frameSize={frameSize} />
      <div className="panel">
        <h2>Real-time Recognition</h2>
        <div className="actions">
          <button className="primary" disabled={!camera.ready} onClick={() => setRunning(!running)}>{running ? 'Stop' : 'Start'} Stream</button>
          <button disabled={!camera.ready && !uploadBlob} onClick={() => identify(true)}>Log Attendance</button>
        </div>
        <label>UPLOAD FRAME FALLBACK<input type="file" accept="image/*" onChange={fileFromInput(setUploadBlob, setMessage)} /></label>
        {uploadBlob && <button onClick={() => { setUploadBlob(null); setMessage('Upload cleared. Live camera will be used.'); }}>Use Live Camera Instead</button>}
        {uploadBlob && <button onClick={() => identify(false)}>Recognize Uploaded Image</button>}
        {message && <p className="notice">{message}</p>}
        <p className="latency">Latency: {latency} ms</p>
        <div className="faces">
          {faces.map((face, index) => <FaceResult key={index} face={face} />)}
          {!faces.length && <p className="muted">No faces detected yet.</p>}
        </div>
      </div>
    </section>
  );
}

function Attendance({ token }) {
  const camera = useCamera();
  const [faces, setFaces] = useState([]);
  const [latency, setLatency] = useState(0);
  const [uploadBlob, setUploadBlob] = useState(null);
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const [frameSize, setFrameSize] = useState({ width: 960, height: 720 });

  async function logAttendance() {
    setMessage('');
    setBusy(true);
    try {
      const video = camera.videoRef.current;
      if (video?.videoWidth && video?.videoHeight && !uploadBlob) {
        setFrameSize({ width: video.videoWidth, height: video.videoHeight });
      }
      const blob = uploadBlob || await camera.captureBlob();
      const data = new FormData();
      data.append('image', blob, 'attendance-frame.jpg');
      const result = await apiFetch('/api/recognition/attendance', { method: 'POST', body: data }, token);
      setFaces(result.faces);
      setLatency(result.latency_ms);
      const verified = result.faces.filter((face) => face.result === 'recognized');
      setMessage(verified.length ? `Attendance recorded for ${verified.map((face) => face.name).join(', ')}.` : 'Attendance check completed. No verified employee match was recorded.');
    } catch (err) {
      setMessage(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="split">
      <CameraPanel camera={camera} faces={faces} frameSize={frameSize} />
      <div className="panel">
        <h2>Log Attendance</h2>
        <p className="muted">Capture one employee at a time for offline identity and liveness verification.</p>
        <label>UPLOAD FRAME FALLBACK<input type="file" accept="image/*" onChange={fileFromInput(setUploadBlob, setMessage)} /></label>
        {uploadBlob && <button onClick={() => { setUploadBlob(null); setMessage('Upload cleared. Live camera will be used.'); }}>Use Live Camera Instead</button>}
        <button className="primary" disabled={busy || (!camera.ready && !uploadBlob)} onClick={logAttendance}><CalendarCheck size={16} />{busy ? 'Checking...' : 'Log Attendance'}</button>
        {message && <p className="notice">{message}</p>}
        <p className="latency">Latency: {latency} ms</p>
        <div className="faces">
          {faces.map((face, index) => <FaceResult key={index} face={face} />)}
          {!faces.length && <p className="muted">No attendance check has been run yet.</p>}
        </div>
      </div>
    </section>
  );
}

function FaceResult({ face }) {
  return (
    <article className={`face ${face.result}`}>
      <strong>{face.name || 'Unknown'}</strong>
      <span>{face.employee_id || 'No employee match'}</span>
      <span>Confidence: {(face.confidence * 100).toFixed(1)}%</span>
      <span>Liveness: {face.liveness.status} ({(face.liveness.score * 100).toFixed(1)}%)</span>
      <small>{new Date(face.timestamp).toLocaleString()}</small>
    </article>
  );
}

function CameraPanel({ camera, faces = [], frameSize = { width: 960, height: 720 } }) {
  return (
    <div className="camera-panel">
      <video ref={camera.videoRef} muted playsInline />
      <div className="face-overlay">
        {faces.map((face, index) => {
          const box = face.box || { x: 0, y: 0, w: 0, h: 0 };
          const style = {
            left: (box.x / frameSize.width) * 100 + '%',
            top: (box.y / frameSize.height) * 100 + '%',
            width: (box.w / frameSize.width) * 100 + '%',
            height: (box.h / frameSize.height) * 100 + '%'
          };
          const label = (face.name || 'Unknown') + ' · ' + formatPercent(face.confidence) + ' · ' + face.liveness.status;
          return <div key={index} className={'overlay-box ' + face.result} style={style}><span>{label}</span></div>;
        })}
      </div>
      {!camera.ready && <button className="primary camera-start" onClick={camera.start}><Camera size={16} /> Start Camera</button>}
      {camera.error && <p className="error">{camera.error}</p>}
    </div>
  );
}

function AuditTable({ token, logs }) {
  async function download(path, filename) {
    const response = await apiFetch(path, {}, token);
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <section className="panel wide">
      <div className="panel-head">
        <h2>Audit Logs</h2>
        <div className="actions">
          <button onClick={() => download('/api/audit/export.csv', 'audit_logs.csv')}><Download size={15} /> CSV</button>
          <button onClick={() => download('/api/audit/export.xlsx', 'audit_logs.xlsx')}><Download size={15} /> Excel</button>
        </div>
      </div>
      <table>
        <thead><tr><th>Time</th><th>User</th><th>Event</th><th>Result</th><th>Confidence</th><th>Liveness</th></tr></thead>
        <tbody>
          {logs.map((log) => (
            <tr key={log.id}>
              <td>{new Date(log.timestamp).toLocaleString()}</td>
              <td>{log.user}</td>
              <td>{log.event_type}</td>
              <td>{log.result}</td>
              <td>{log.confidence ?? '-'}</td>
              <td>{log.liveness_score ?? '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

function SecurityTests({ token }) {
  const [testType, setTestType] = useState('Mobile Screen Test');
  const [image, setImage] = useState(null);
  const [message, setMessage] = useState('');
  const [result, setResult] = useState(null);

  async function runTest() {
    if (!image) {
      setMessage('Choose a test image first.');
      return;
    }
    const data = new FormData();
    data.append('image', image, image.name || 'spoof-test.jpg');
    const response = await apiFetch('/api/liveness/check', { method: 'POST', body: data }, token);
    setResult(response);
    setMessage('');
  }

  return (
    <section className="split">
      <div className="panel">
        <h2>Anti-Spoofing Demo</h2>
        <div className="attack-grid">
          {['Printed Photo Test', 'Mobile Screen Test', 'Replay Attack Test', 'Low Light Test'].map((item) => (
            <button key={item} className={testType === item ? 'active-test' : ''} onClick={() => setTestType(item)}><FileWarning size={15} /> {item}</button>
          ))}
        </div>
        <label>TEST IMAGE<input type="file" accept="image/*" onChange={fileFromInput(setImage, setMessage)} /></label>
        <button className="primary" onClick={runTest}><Shield size={16} /> Run Liveness Test</button>
        {message && <p className="notice">{message}</p>}
      </div>
      <div className="panel">
        <h2>{testType} Result</h2>
        {!result && <p className="muted">Upload a printed-photo, phone-screen, replay-frame, or low-light image to demonstrate local liveness scoring.</p>}
        {result && <div className={'liveness-result ' + result.status.toLowerCase()}>
          <strong>{result.status}</strong>
          <span>Liveness Score: {formatPercent(result.score)}</span>
          <span>Blink/Eye Evidence: {formatPercent(result.blink_score)}</span>
          <span>Head Movement: {formatPercent(result.head_movement_score)}</span>
          <span>Texture: {formatPercent(result.texture_score)}</span>
          <span>Screen Attack Risk: {formatPercent(result.screen_attack_score)}</span>
          <span>Replay Attack Risk: {formatPercent(result.replay_attack_score)}</span>
          <ul>{result.reasons.map((reason) => <li key={reason}>{reason}</li>)}</ul>
        </div>}
      </div>
    </section>
  );
}

function Datalake({ token }) {
  const [queue, setQueue] = useState([]);
  const [message, setMessage] = useState('');

  async function load() {
    setQueue(await apiFetch('/api/datalake/queue', {}, token));
  }

  async function syncLocal() {
    const result = await apiFetch('/api/datalake/sync/local', { method: 'POST' }, token);
    setMessage(`Synced ${result.synced} events to ${result.path}`);
    await load();
  }

  useEffect(() => { load().catch(console.error); }, []);

  return (
    <section className="panel">
      <h2>Datalake 3.0 Queue</h2>
      <button className="primary" onClick={syncLocal}><Database size={16} /> Local Sync</button>
      {message && <p className="notice">{message}</p>}
      <table>
        <thead><tr><th>ID</th><th>Type</th><th>Status</th><th>Attempts</th></tr></thead>
        <tbody>{queue.map((item) => <tr key={item.id}><td>{item.id}</td><td>{item.event_type}</td><td>{item.status}</td><td>{item.attempts}</td></tr>)}</tbody>
      </table>
    </section>
  );
}

function App() {
  const [session, setSession] = useState(readStoredSession);
  const [checkingSession, setCheckingSession] = useState(() => Boolean(readStoredSession()));
  const [tab, setTab] = useState('dashboard');

  useEffect(() => {
    let active = true;
    if (!session) {
      setCheckingSession(false);
      return () => { active = false; };
    }

    setCheckingSession(true);
    apiFetch('/api/auth/me', {}, session.token)
      .then((profile) => {
        if (!active) return;
        const verifiedSession = { ...session, role: profile.role, displayName: profile.display_name };
        saveSession(verifiedSession);
        setSession(verifiedSession);
      })
      .catch(() => {
        if (!active) return;
        clearStoredSession();
        setSession(null);
      })
      .finally(() => {
        if (active) setCheckingSession(false);
      });

    return () => { active = false; };
  }, [session?.token]);

  function acceptLogin(nextSession) {
    saveSession(nextSession);
    setCheckingSession(true);
    setSession(nextSession);
  }

  function logout() {
    if (session?.token) apiFetch('/api/auth/logout', { method: 'POST' }, session.token).catch(() => {});
    clearStoredSession();
    setSession(null);
  }

  if (checkingSession) {
    return <main className="login-shell"><section className="login-panel"><div className="brand-mark"><Shield size={30} /> NHAI Edge AI</div><p className="muted">Checking your secure session...</p></section></main>;
  }

  if (!session) return <Login onLogin={acceptLogin} />;

  const fullAccessTabs = [
    ['dashboard', 'Dashboard', <Activity size={16} />],
    ['register', 'Register', <UserPlus size={16} />],
    ['recognize', 'Recognize', <Camera size={16} />],
    ['attendance', 'Log Attendance', <CalendarCheck size={16} />],
    ['security', 'Security', <Shield size={16} />],
    ['datalake', 'Datalake', <Database size={16} />]
  ];
  const employeeTabs = [['register', 'Register', <UserPlus size={16} />]];
  const tabs = session.role === 'employee' ? employeeTabs : fullAccessTabs;
  const activeTab = tabs.some(([id]) => id === tab) ? tab : tabs[0][0];
  const activeTabLabel = tabs.find(([id]) => id === activeTab)?.[1];

  return (
    <main className="app-shell">
      <aside>
        <div className="brand-mark"><Shield size={28} /> NHAI Edge AI</div>
        <div className="account-meta"><strong>{session.displayName}</strong><span>{session.role === 'employee' ? 'Employee' : session.role === 'operator' ? 'Operator' : 'Administrator'}</span></div>
        <nav>{tabs.map(([id, label, icon]) => <button key={id} className={activeTab === id ? 'active' : ''} onClick={() => setTab(id)}>{icon}{label}</button>)}</nav>
        <button onClick={logout}>Logout</button>
      </aside>
      <section className="content">
        <header><h1>{activeTabLabel}</h1><span>Offline mode active</span></header>
        {activeTab === 'dashboard' && <Dashboard token={session.token} hasFullAccess={session.role !== 'employee'} />}
        {activeTab === 'register' && <Registration token={session.token} showRoster={session.role !== 'employee'} />}
        {activeTab === 'recognize' && <Recognition token={session.token} />}
        {activeTab === 'attendance' && <Attendance token={session.token} />}
        {activeTab === 'security' && <SecurityTests token={session.token} />}
        {activeTab === 'datalake' && <Datalake token={session.token} />}
      </section>
    </main>
  );
}

createRoot(document.getElementById('root')).render(<App />);
