import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

function barColor(start) {
  if (start >= 12) return '#EF4444';
  if (start >= 8) return '#F59E0B';
  return '#00C48C';
}

export default function NegotiationPremiumChart({ data }) {
  if (!data || data.length === 0) return null;

  return (
    <div className="bg-surface border border-border p-6 h-full flex flex-col">
      <h3 className="text-lg font-medium text-primary mb-1 font-heading">Negotiation Premium</h3>
      <p className="text-[11px] text-muted mb-4">Distribution of premium above loadboard</p>
      <div className="flex-1 flex items-center">
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={data}>
            <CartesianGrid vertical={false} stroke="#F1F5F9" />
            <XAxis dataKey="bucket" tick={{ fontSize: 9, fill: '#94A3B8' }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 10, fill: '#94A3B8' }} axisLine={false} tickLine={false} />
            <Tooltip
              contentStyle={{ border: '1px solid #E2E8F0', borderRadius: 0, boxShadow: 'none' }}
            />
            <Bar dataKey="count">
              {data.map((entry, i) => (
                <Cell key={i} fill={barColor(entry.start)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
