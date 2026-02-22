import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function VolumeChart({ data }) {
  if (!data || data.length === 0) return null;

  const formatLocalDate = (value) => {
    if (!value) return '';
    const parts = String(value).split('-').map(Number);
    if (parts.length !== 3 || parts.some(Number.isNaN)) return String(value);
    const [year, month, day] = parts;
    const d = new Date(year, month - 1, day);
    return `${d.getMonth() + 1}/${d.getDate()}`;
  };

  return (
    <div className="bg-surface border border-border p-6 flex-1 flex flex-col">
      <div className="mb-5">
        <div>
          <h3 className="text-2xl font-medium font-heading text-primary">Booking Volume</h3>
          <p className="text-xs text-muted mt-1">AI agent performance over time</p>
        </div>
      </div>
      <ResponsiveContainer width="100%" className="flex-1" height={320}>
        <LineChart data={data} margin={{ left: 4, right: 6, top: 10, bottom: 0 }}>
          <CartesianGrid vertical={false} stroke="#F1F5F9" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: '#94A3B8' }}
            tickFormatter={formatLocalDate}
            axisLine={false}
            tickLine={false}
          />
          <YAxis tick={{ fontSize: 11, fill: '#94A3B8' }} axisLine={false} tickLine={false} />
          <Tooltip
            labelFormatter={formatLocalDate}
            contentStyle={{ border: '1px solid #E2E8F0', borderRadius: 0, boxShadow: 'none', background: '#0A1628', color: '#fff' }}
            labelStyle={{ color: '#CBD5E1' }}
            itemStyle={{ color: '#fff' }}
          />
          <Line
            type="monotone"
            dataKey="count"
            stroke="#0A1628"
            strokeWidth={2.5}
            isAnimationActive
            animationDuration={1850}
            animationEasing="ease-out"
            dot={false}
            activeDot={{ r: 4, stroke: '#0A1628', strokeWidth: 2, fill: '#FFFFFF' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
