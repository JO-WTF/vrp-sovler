import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import { Button, Card, Col, InputNumber, List, message, Row, Select, Space, Tag, Timeline, Typography } from 'antd';
import RouteMap from '../components/RouteMap';
import ConvergenceChart from '../charts/ConvergenceChart';
import { useRunSocket } from '../hooks/useRunSocket';

const backendHost = `${window.location.protocol}//${window.location.hostname}:8082`;
const api = axios.create({ baseURL: backendHost, timeout: 10000 });
const { Title, Text } = Typography;

export default function ExperimentPage() {
  const [dataset, setDataset] = useState('vrplib');
  const [instance, setInstance] = useState();
  const [catalog, setCatalog] = useState({});
  const [runId, setRunId] = useState('');
  const [busy, setBusy] = useState(false);
  const [timeLimit, setTimeLimit] = useState(5);
  const [population, setPopulation] = useState(80);
  const [snapshot, setSnapshot] = useState({ events: [], results: [], status: 'idle' });
  const wsEvents = useRunSocket(runId);

  useEffect(() => { api.get('/api/datasets').then((r) => { setCatalog(r.data.instances || {}); if (!instance && r.data.instances?.vrplib?.length) setInstance(r.data.instances.vrplib[0]); }).catch(() => message.error('无法加载数据集列表')); }, []);
  useEffect(() => { const options = catalog[dataset] || []; if (options.length) setInstance(options[0]); }, [dataset]);

  useEffect(() => {
    if (!runId) return;
    const timer = setInterval(async () => {
      try { const { data } = await api.get(`/api/runs/${runId}`); setSnapshot(data); } catch {}
    }, 1000);
    return () => clearInterval(timer);
  }, [runId]);

  const mergedEvents = useMemo(() => {
    const map = new Map();
    [...(snapshot.events || []), ...wsEvents].forEach((e) => map.set(e.seq ?? `${e.type}-${JSON.stringify(e.payload)}`, e));
    return [...map.values()].sort((a, b) => (a.seq ?? 0) - (b.seq ?? 0));
  }, [snapshot.events, wsEvents]);

  const start = async () => {
    if (!instance) return message.warning('请选择实例');
    setBusy(true);
    try { const { data } = await api.post('/api/runs', { dataset, instance, time_limit_s: timeLimit, population_size: population }); setRunId(data.run_id); message.success('任务已启动'); }
    catch (e) { message.error(e?.response?.data?.detail || e.message || '启动失败'); }
    finally { setBusy(false); }
  };

  const timelineItems = mergedEvents.slice(-30).map((e) => ({ children: `#${e.seq ?? '-'} ${e.type}: ${JSON.stringify(e.payload)}` }));

  return <div style={{ padding: 24, background: '#f4f7ff', minHeight: '100vh' }}><Card><Space direction="vertical" size={16} style={{ width: '100%' }}>
    <div><Title level={3} style={{ marginBottom: 4 }}>VRP Lab 控制台</Title><Text type="secondary">后端：{backendHost}</Text></div>
    <Row gutter={12}><Col span={6}><Select style={{ width: '100%' }} value={dataset} onChange={setDataset} options={Object.keys(catalog).map((d) => ({ label: d, value: d }))} /></Col>
      <Col span={8}><Select showSearch optionFilterProp="label" style={{ width: '100%' }} value={instance} onChange={setInstance} options={(catalog[dataset] || []).map((x) => ({ label: x, value: x }))} /></Col>
      <Col span={4}><InputNumber min={1} addonBefore="Time(s)" value={timeLimit} onChange={(v) => setTimeLimit(v || 5)} style={{ width: '100%' }} /></Col>
      <Col span={4}><InputNumber min={10} addonBefore="Pop" value={population} onChange={(v) => setPopulation(v || 80)} style={{ width: '100%' }} /></Col>
      <Col span={2}><Button type="primary" onClick={start} loading={busy} block>Start</Button></Col></Row>
    <Space><Tag color="blue">Run: {runId || 'N/A'}</Tag><Tag color="purple">Status: {snapshot.status || 'idle'}</Tag><Tag color="green">Events: {mergedEvents.length}</Tag></Space>
    <ConvergenceChart events={mergedEvents} />
    <Card size="small" title="运行事件"><Timeline items={timelineItems} /></Card>
    <Card size="small" title="最终路线结果"><List dataSource={snapshot.results || []} renderItem={(r) => <List.Item style={{ display: 'block', width: '100%' }}><div>{r.instance}: {JSON.stringify(r.routes || [])}</div><RouteMap result={r} /></List.Item>} /></Card>
  </Space></Card></div>;
}
