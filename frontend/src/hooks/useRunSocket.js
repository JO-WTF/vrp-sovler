import { useEffect, useState } from 'react';

const wsProto = window.location.protocol === 'https:' ? 'wss' : 'ws';
const wsBase = `${wsProto}://${window.location.hostname}:8082`; 

export function useRunSocket(runId) {
  const [events, setEvents] = useState([]);
  useEffect(() => {
    if (!runId) return;
    setEvents([]);
    const ws = new WebSocket(`${wsBase}/ws/${runId}`);
    ws.onmessage = (ev) => setEvents((prev) => [...prev, JSON.parse(ev.data)]);
    ws.onerror = () => setEvents((prev) => [...prev, { type: 'socket_error', payload: {} }]);
    return () => ws.close();
  }, [runId]);
  return events;
}
