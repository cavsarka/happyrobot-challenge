const COLORS = ['#0A1628', '#1e3a5f', '#2d5a87', '#3d7ab0', '#00C48C'];

export default function NegotiationFunnel({ data }) {
  if (!data || data.length === 0) return null;

  const maxCount = data[0].count;

  return (
    <div className="bg-surface border border-border p-6 h-full flex flex-col">
      <h3 className="text-lg font-medium text-primary mb-1 font-heading">Negotiation Funnel</h3>
      <p className="text-[11px] text-muted mb-4">Stage-to-stage conversion through booking</p>
      <div className="flex-1 flex flex-col justify-center pt-2">
        <div className="flex flex-col gap-1">
        {data.map((d, i) => {
          const widthPct = maxCount > 0 ? (d.count / maxCount) * 100 : 0;
          const conversionPct = i > 0 && data[i - 1].count > 0
            ? ((d.count / data[i - 1].count) * 100).toFixed(0)
            : null;

          return (
            <div key={d.stage} className="flex items-center gap-3">
              {/* Label column */}
              <div className="w-24 text-right shrink-0">
                <p className="text-[11px] font-semibold text-primary leading-tight">{d.stage}</p>
                {conversionPct && (
                  <p className="text-[9px] font-mono text-accent">{conversionPct}%</p>
                )}
              </div>
              {/* Bar - flat left, tapered right via clip-path */}
              <div className="flex-1 relative h-9">
                <div
                  className="h-full relative"
                  style={{
                    width: `${Math.max(widthPct, 8)}%`,
                    backgroundColor: COLORS[i] || '#94A3B8',
                    clipPath: `polygon(0 0, calc(100% - 8px) 0, 100% 50%, calc(100% - 8px) 100%, 0 100%)`,
                  }}
                >
                  <span className="absolute inset-0 flex items-center justify-center text-white text-[11px] font-semibold font-mono">
                    {d.count}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
        </div>
      </div>
    </div>
  );
}
