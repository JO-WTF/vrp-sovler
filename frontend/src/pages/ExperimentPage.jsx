import React, { useMemo, useState } from 'react';
import axios from 'axios';
import ConvergenceChart from '../charts/ConvergenceChart';
import { useRunSocket } from '../hooks/useRunSocket';

const backendHost = `${window.location.protocol}//${window.location.hostname}:8082`;
const api = axios.create({ baseURL: backendHost, timeout: 10000 });

const card = { maxWidth: 980, margin: '40px auto', padding: 24, borderRadius: 16, background: '#ffffff', boxShadow: '0 10px 40px rgba(0,0,0,0.08)' };
const row = { display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: 12, alignItems: 'end' };
const inputStyle = { width: '100%', border: '1px solid #d6d6e7', borderRadius: 10, padding: '10px 12px', fontSize: 14 };

export default function ExperimentPage() {
  const [dataset, setDataset] = useState('vrplib');
  const [instance, setInstance] = useState('A-n32-k5');
  const [runId, setRunId] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const events = useRunSocket(runId);

  const instanceDoneCount = useMemo(() => events.filter((e) => e.type === 'instance_done').length, [events]);

  const start = async () => {
    setError('');
    setBusy(true);
    try {
      const payload = { dataset, instances: [instance], time_limit_s: 5, population_size: 80 };
      const { data } = await api.post('/api/runs', payload);
      setRunId(data.run_id);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || '启动失败');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(120deg,#f5f7ff,#ecfbff)', padding: 16 }}>
      <div style={card}>
        <h1 style={{ marginTop: 0, marginBottom: 4, fontSize: 28 }}>VRP Lab Dashboard</h1>
        <p style={{ color: '#666', marginTop: 0 }}>运行 CVRP/CVRPTW 实验并实时查看收敛曲线</p>

        <div style={row}>
          <label>
            Dataset
            <input style={inputStyle} value={dataset} onChange={(e) => setDataset(e.target.value)} placeholder="vrplib | solomon | homberger" />
          </label>
          <label>
            Instance
            <input style={inputStyle} value={instance} onChange={(e) => setInstance(e.target.value)} placeholder="A-n32-k5" />
          </label>
          <button onClick={start} disabled={busy} style={{ height: 42, border: 0, borderRadius: 10, padding: '0 18px', background: busy ? '#9ab3ff' : '#3563ff', color: '#fff', fontWeight: 600, cursor: 'pointer' }}>
            {busy ? 'Starting...' : 'Start'}
          </button>
        </div>

        <div style={{ marginTop: 16, padding: 12, background: '#f8f9ff', borderRadius: 10, fontSize: 14 }}>
          <div><b>Backend:</b> {backendHost}</div>
          <div><b>Run ID:</b> {runId || 'Not started'}</div>
          <div><b>Instances done:</b> {instanceDoneCount}</div>
          {error ? <div style={{ color: '#d90429', marginTop: 8 }}><b>Error:</b> {error}</div> : null}
        </div>

        <div style={{ marginTop: 20 }}>
          <ConvergenceChart events={events} />
        </div>
      </div>
    </div>
  );
}
