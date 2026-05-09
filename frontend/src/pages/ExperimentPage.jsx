import React, { useState } from 'react';
import axios from 'axios';
import ConvergenceChart from '../charts/ConvergenceChart';
import { useRunSocket } from '../hooks/useRunSocket';

const api = axios.create({ baseURL: 'http://localhost:8082' });

export default function ExperimentPage() {
  const [dataset, setDataset] = useState('vrplib');
  const [instance, setInstance] = useState('A-n32-k5');
  const [runId, setRunId] = useState('');
  const events = useRunSocket(runId);

  const start = async () => {
    const { data } = await api.post('/api/runs', { dataset, instances: [instance], time_limit_s: 5, population_size: 80 });
    setRunId(data.run_id);
  };

  return <div><h2>VRP Lab</h2><input value={dataset} onChange={(e)=>setDataset(e.target.value)}/><input value={instance} onChange={(e)=>setInstance(e.target.value)}/><button onClick={start}>Start</button><div>Run: {runId}</div><ConvergenceChart events={events} /></div>;
}
