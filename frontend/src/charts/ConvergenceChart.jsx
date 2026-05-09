import React from 'react';
import Plot from 'react-plotly.js';

export default function ConvergenceChart({ events }) {
  const points = events.filter((e) => e.type === 'iteration').map((e) => e.payload);
  return (
    <Plot
      data={[{ x: points.map((p) => p.elapsed_s), y: points.map((p) => p.best_cost), type: 'scatter', mode: 'lines', name: 'best' }]}
      layout={{ title: 'Convergence', xaxis: { title: 'Seconds' }, yaxis: { title: 'Cost' }, height: 300 }}
    />
  );
}
