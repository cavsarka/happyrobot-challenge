import { useState, useEffect } from 'react';
import { fetchLoadsMap, fetchLoadsDetail } from '../api/client';
import LoadMap from '../components/loads/LoadMap';
import LoadTable from '../components/loads/LoadTable';

export default function LoadIntelligence() {
  const [mapData, setMapData] = useState([]);
  const [loads, setLoads] = useState([]);
  const [page, setPage] = useState(1);
  const pageSize = 20;

  useEffect(() => {
    fetchLoadsMap().then(setMapData);
    fetchLoadsDetail().then(setLoads);
  }, []);

  const avgMargin = loads.length > 0
    ? (loads.reduce((s, l) => s + l.margin_percentage, 0) / loads.length).toFixed(1)
    : '0';

  const avgRatePerMile = loads.length > 0
    ? (loads.filter((l) => l.miles).reduce((s, l) => s + l.agreed_rate / l.miles, 0) /
       loads.filter((l) => l.miles).length).toFixed(2)
    : '0';

  const totalSpend = loads.reduce((s, l) => s + l.agreed_rate, 0);
  const totalRevenue = loads.reduce((s, l) => s + (l.revenue ?? 0), 0);
  const sortedLoads = [...loads].sort((a, b) => {
    const aTs = a?.created_at ? new Date(a.created_at).getTime() : 0;
    const bTs = b?.created_at ? new Date(b.created_at).getTime() : 0;
    return bTs - aTs;
  });
  const totalPages = Math.max(1, Math.ceil(sortedLoads.length / pageSize));
  const paginatedLoads = sortedLoads.slice((page - 1) * pageSize, page * pageSize);

  useEffect(() => {
    if (page > totalPages) setPage(totalPages);
  }, [page, totalPages]);

  const kpis = [
    {
      label: 'Total Revenue',
      value: `$${totalRevenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      sub: `Across ${loads.length} booked loads`,
    },
    {
      label: 'Total Spend',
      value: `$${totalSpend.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      sub: `Across ${loads.length} booked loads`,
    },
    {
      label: 'Avg Margin %',
      value: `${avgMargin}%`,
      sub: 'vs. Shipper Rate',
    },
    {
      label: 'Avg Rate Per Mile',
      value: `$${avgRatePerMile}`,
      sub: 'Vs. $2.54 Industry Average',
    },
  ];

  return (
    <div className="space-y-8">
      <LoadMap data={mapData} />

      <div className="grid grid-cols-4 gap-8">
        {kpis.map((kpi) => (
          <div key={kpi.label} className="bg-surface border border-border p-6">
            <p className="text-xs font-semibold text-muted uppercase tracking-wider">{kpi.label}</p>
            <p className="text-3xl font-semibold font-mono mt-2 text-primary">{kpi.value}</p>
            {kpi.sub && <p className="text-xs text-muted mt-1">{kpi.sub}</p>}
          </div>
        ))}
      </div>

      <LoadTable data={paginatedLoads} />

      <div className="flex items-center justify-between">
        <p className="text-xs text-muted">
          Page {page} of {totalPages}
        </p>
        <div className="flex gap-2">
          <button
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
            className="px-3 py-1.5 border border-border text-xs font-semibold disabled:opacity-30 cursor-pointer"
          >
            Prev
          </button>
          {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => i + 1).map((p) => (
            <button
              key={p}
              onClick={() => setPage(p)}
              className={`px-3 py-1.5 border text-xs font-semibold cursor-pointer ${
                p === page ? 'bg-primary text-white border-primary' : 'border-border'
              }`}
            >
              {p}
            </button>
          ))}
          <button
            onClick={() => setPage(Math.min(totalPages, page + 1))}
            disabled={page === totalPages}
            className="px-3 py-1.5 border border-border text-xs font-semibold disabled:opacity-30 cursor-pointer"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
