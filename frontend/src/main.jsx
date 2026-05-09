import React from 'react';
import { createRoot } from 'react-dom/client';
import { ConfigProvider } from 'antd';
import 'antd/dist/reset.css';
import ExperimentPage from './pages/ExperimentPage';

createRoot(document.getElementById('root')).render(
  <ConfigProvider theme={{ token: { colorPrimary: '#3662ff', borderRadius: 10 } }}>
    <ExperimentPage />
  </ConfigProvider>,
);
