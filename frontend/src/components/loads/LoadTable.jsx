function marginColor(margin) {
  if (margin >= 8) return 'text-accent';
  if (margin >= 5) return 'text-warning';
  return 'text-error';
}

function marginBarColor(margin) {
  if (margin >= 8) return 'bg-accent';
  if (margin >= 5) return 'bg-warning';
  return 'bg-error';
}

export default function LoadTable({ data }) {
  if (!data || data.length === 0) {
    return <p className="text-sm text-muted p-6">No load data available.</p>;
  }

  return (
    <div className="bg-surface border border-border">
      <table className="w-full">
        <thead>
          <tr className="border-b border-border text-left">
            {['Load ID', 'Lane', 'Carrier', 'Loadboard Rate', 'Final Rate', 'Broker Revenue', 'Margin'].map((h) => (
              <th key={h} className="p-4 text-xs font-semibold text-muted uppercase tracking-wider whitespace-nowrap">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((load) => (
            <tr key={load.load_id} className="border-b border-border h-14">
              <td className="px-4 text-xs font-mono">{load.load_id}</td>
              <td className="px-4 text-xs whitespace-nowrap">{load.lane}</td>
              <td className="px-4">
                <p className="text-sm">{load.carrier_name}</p>
                <span className="text-[10px] font-mono text-muted bg-background px-1.5 py-0.5 border border-border">
                  {load.mc_number}
                </span>
              </td>
              <td className="px-4 text-xs font-mono text-muted whitespace-nowrap">
                ${load.loadboard_rate.toLocaleString()}
              </td>
              <td className="px-4 text-xs font-mono whitespace-nowrap">
                ${load.agreed_rate.toLocaleString()}
              </td>
              <td className="px-4 text-xs font-mono text-muted whitespace-nowrap">
                {load.revenue != null ? `$${load.revenue.toLocaleString()}` : '—'}
              </td>
              <td className="px-4">
                <div className="flex items-center gap-2">
                  <div className="w-16 h-2 bg-background">
                    <div
                      className={`h-full ${marginBarColor(load.margin_percentage)}`}
                      style={{ width: `${Math.min(100, load.margin_percentage * 5)}%` }}
                    />
                  </div>
                  <span className={`text-xs font-mono ${marginColor(load.margin_percentage)}`}>
                    {load.margin_percentage.toFixed(1)}%
                  </span>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
