import React from 'react';
import Plot from 'react-plotly.js';

const colors = ['#2563eb', '#e11d48', '#059669', '#d97706', '#7c3aed', '#0891b2', '#65a30d'];

export default function RouteMap({ result }) {
  if (!result || !result.routes || !result.locations) return <div>暂无路线结果</div>;

  const traces = [];
  traces.push({
    x: [result.locations[0][0]], y: [result.locations[0][1]], mode: 'markers+text', text: ['Depot'], textposition: 'top center', marker: { size: 12, color: '#111827' }, name: 'Depot', type: 'scatter',
  });

  result.routes.forEach((route, idx) => {
    const full = [0, ...route, 0];
    traces.push({
      x: full.map((n) => result.locations[n][0]),
      y: full.map((n) => result.locations[n][1]),
      mode: 'lines+markers',
      marker: { size: 8 },
      line: { width: 3, color: colors[idx % colors.length] },
      name: `Route ${idx + 1}`,
      type: 'scatter',
    });
  });

  return <Plot style={{ width: '100%' }} useResizeHandler data={traces} layout={{ title: `${result.instance} Final Routes`, height: 480, xaxis: { title: 'X' }, yaxis: { title: 'Y' } }} config={{ responsive: true, displaylogo: false }} />;
}
