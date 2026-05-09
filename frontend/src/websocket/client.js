export function createRunSocket(runId) {
  return new WebSocket(`ws://localhost:8000/ws/${runId}`);
}
