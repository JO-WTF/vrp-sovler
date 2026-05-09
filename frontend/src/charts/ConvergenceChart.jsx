import React from 'react';
import Plot from 'react-plotly.js';

export default function ConvergenceChart({ events }) {
  const points = events.filter((e) => e.type === 'iteration').map((e) => e.payload);
  return (
    <Plot
      style={{ width: '100%' }}
      useResizeHandler
      data={[
        { x: points.map((p) => p.elapsed_s), y: points.map((p) => p.best_cost), type: 'scatter', mode: 'lines', line: { color: '#3b82f6', width: 3 }, name: 'Best cost' },
        { x: points.map((p) => p.elapsed_s), y: points.map((p) => p.current_cost), type: 'scatter', mode: 'lines', line: { color: '#8b5cf6', width: 2, dash: 'dot' }, name: 'Current cost' },
      ]}
      layout={{ title: { text: 'Convergence (Realtime)' }, xaxis: { title: 'Elapsed time (s)' }, yaxis: { title: 'Cost' }, height: 420, paper_bgcolor: 'white', plot_bgcolor: 'white', margin: { l: 50, r: 20, t: 50, b: 50 } }}
      config={{ displaylogo: false, responsive: true }}
    />
  );
}
