import { useState, useEffect } from 'react';
import { fetchSummary, fetchCharts } from '../api/client';
import KPICards from '../components/overview/KPICards';
import VolumeChart from '../components/overview/VolumeChart';
import OutcomeDonut from '../components/overview/OutcomeDonut';
import NegotiationFunnel from '../components/overview/NegotiationFunnel';
import RateEfficiencyHistogram from '../components/overview/RateEfficiencyHistogram';
import SentimentChart from '../components/overview/SentimentChart';
import AlertsTable from '../components/overview/AlertsTable';

export default function Overview() {
  const [summary, setSummary] = useState(null);
  const [charts, setCharts] = useState(null);

  useEffect(() => {
    fetchSummary().then(setSummary);
    fetchCharts().then(setCharts);
  }, []);

  return (
    <div className="space-y-8">
      <KPICards data={summary} />

      <div className="grid grid-cols-1 xl:grid-cols-5 gap-8 items-stretch">
        <div className="xl:col-span-3 flex">
          <VolumeChart data={charts?.volume_by_day} />
        </div>
        <div className="xl:col-span-2 flex">
          <OutcomeDonut data={charts?.outcome_breakdown} bookingRate={summary?.booking_rate} />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8">
        <NegotiationFunnel data={charts?.funnel} />
        <RateEfficiencyHistogram data={charts?.negotiation_premium_distribution} />
        <SentimentChart data={charts?.sentiment_breakdown} />
      </div>

      <AlertsTable />
    </div>
  );
}
