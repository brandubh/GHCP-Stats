import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Metric {
  id: number;
  org: string;
  date: string;
}

const Dashboard = () => {
  const [metrics, setMetrics] = useState<Metric[]>([]);

  useEffect(() => {
    axios.get('/api/metrics').then(res => setMetrics(res.data));
  }, []);

  return (
    <div>
      <h1>GHCP Metrics Dashboard</h1>
      <pre>{JSON.stringify(metrics, null, 2)}</pre>
    </div>
  );
};

export default Dashboard;
