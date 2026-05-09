import { useEffect, useState } from 'react';

export function useRunSocket(runId) {
  const [events, setEvents] = useState([]);
  useEffect(() => {
    if (!runId) return;
    const ws = new WebSocket(`ws://localhost:8000/ws/${runId}`);
    ws.onmessage = (ev) => setEvents((prev) => [...prev, JSON.parse(ev.data)]);
    return () => ws.close();
  }, [runId]);
  return events;
}
