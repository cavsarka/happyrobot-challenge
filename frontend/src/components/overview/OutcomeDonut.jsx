import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const COLORS = {
  booked: '#00C48C',
  no_deal_rate: '#EF4444',
  no_deal_no_load: '#F59E0B',
  unverified: '#94A3B8',
  error_escalation: '#0A1628',
};

const LABELS = {
  booked: 'Booked',
  no_deal_rate: 'No Deal - Rate',
  no_deal_no_load: 'No Deal - No Load',
  unverified: 'Unverified',
  error_escalation: 'Error Escalation',
};

export default function OutcomeDonut({ data, bookingRate }) {
  if (!data || data.length === 0) return null;

  const total = data.reduce((sum, d) => sum + Number(d.count || 0), 0);
  const chartData = data.map((d) => ({
    name: LABELS[d.outcome] || d.outcome,
    value: d.count,
    pct: total > 0 ? (Number(d.count || 0) / total) * 100 : 0,
    color: COLORS[d.outcome] || '#94A3B8',
  }));
  const legendData = [...chartData].sort((a, b) => b.pct - a.pct);

  return (
    <div className="bg-surface border border-border p-6 flex-1 flex flex-col">
      <h3 className="text-2xl font-medium font-heading text-primary mb-6">Outcome Breakdown</h3>
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-[1fr_1fr] gap-10 items-center px-2">
        <div className="relative max-w-[340px] w-full mx-auto">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={72}
                outerRadius={98}
                dataKey="value"
                stroke="none"
              >
                {chartData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ border: '1px solid #E2E8F0', borderRadius: 0, boxShadow: 'none' }}
                wrapperStyle={{ zIndex: 20 }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="flex flex-col items-center">
              <span className="text-4xl font-semibold font-heading text-primary leading-none">{bookingRate}%</span>
              <span className="text-xs text-muted font-semibold uppercase tracking-wider mt-1">Conversion</span>
            </div>
          </div>
        </div>
        <div className="space-y-4 max-w-[420px] w-full">
          {legendData.map((d) => (
            <div key={d.name} className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2 text-primary">
                <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: d.color }} />
                <span>{d.name}</span>
              </div>
              <span className="font-mono text-muted">{d.pct.toFixed(0)}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
