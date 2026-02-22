import { useState } from 'react';
import Layout from './components/layout/Layout';
import Overview from './pages/Overview';
import CallLog from './pages/CallLog';
import LoadIntelligence from './pages/LoadIntelligence';
import CarrierCRM from './pages/CarrierCRM';

function App() {
  const [tab, setTab] = useState('overview');

  const pages = {
    overview: <Overview />,
    calls: <CallLog />,
    loads: <LoadIntelligence />,
    carriers: <CarrierCRM />,
  };

  return (
    <Layout activeTab={tab} onTabChange={setTab}>
      {pages[tab]}
    </Layout>
  );
}

export default App;
