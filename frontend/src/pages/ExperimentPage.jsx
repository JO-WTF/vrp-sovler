import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import { Button, Card, Col, InputNumber, message, Row, Select, Space, Tag, Timeline, Typography } from 'antd';
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
  const events = useRunSocket(runId);

  useEffect(() => {
    api.get('/api/datasets').then((r) => {
      setCatalog(r.data.instances || {});
      if (!instance && r.data.instances?.vrplib?.length) setInstance(r.data.instances.vrplib[0]);
    }).catch(() => message.error('无法加载数据集列表'));
  }, []);

  useEffect(() => {
    const options = catalog[dataset] || [];
    if (options.length) setInstance(options[0]);
  }, [dataset]);

  const timelineItems = useMemo(() => events.slice(-20).map((e) => ({ children: `${e.type}: ${JSON.stringify(e.payload)}` })), [events]);
  const status = events.at(-1)?.type || 'idle';

  const start = async () => {
    if (!instance) return message.warning('请选择实例');
    setBusy(true);
    try {
      const { data } = await api.post('/api/runs', { dataset, instances: [instance], time_limit_s: timeLimit, population_size: population });
      setRunId(data.run_id);
      message.success('任务已启动');
    } catch (e) {
      message.error(e?.response?.data?.detail || e.message || '启动失败');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={{ padding: 24, background: '#f4f7ff', minHeight: '100vh' }}>
      <Card>
        <Space direction="vertical" size={16} style={{ width: '100%' }}>
          <div>
            <Title level={3} style={{ marginBottom: 4 }}>VRP Lab 控制台</Title>
            <Text type="secondary">后端：{backendHost}</Text>
          </div>

          <Row gutter={12}>
            <Col span={6}><Select style={{ width: '100%' }} value={dataset} onChange={setDataset} options={Object.keys(catalog).map((d) => ({ label: d, value: d }))} /></Col>
            <Col span={8}><Select showSearch optionFilterProp="label" style={{ width: '100%' }} value={instance} onChange={setInstance} options={(catalog[dataset] || []).map((x) => ({ label: x, value: x }))} /></Col>
            <Col span={4}><InputNumber min={1} addonBefore="Time(s)" value={timeLimit} onChange={(v) => setTimeLimit(v || 5)} style={{ width: '100%' }} /></Col>
            <Col span={4}><InputNumber min={10} addonBefore="Pop" value={population} onChange={(v) => setPopulation(v || 80)} style={{ width: '100%' }} /></Col>
            <Col span={2}><Button type="primary" onClick={start} loading={busy} block>Start</Button></Col>
          </Row>

          <Space>
            <Tag color="blue">Run: {runId || 'N/A'}</Tag>
            <Tag color="purple">Status: {status}</Tag>
            <Tag color="green">Events: {events.length}</Tag>
          </Space>

          <ConvergenceChart events={events} />

          <Card size="small" title="运行事件（最近20条）">
            <Timeline items={timelineItems} />
          </Card>
        </Space>
      </Card>
    </div>
  );
}
