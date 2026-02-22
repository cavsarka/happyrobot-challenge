export default function KPICards({ data }) {
  if (!data) return null;
  const INDUSTRY_BOOKING_RATE = 17.86;

  const formatDuration = (seconds) => {
    const totalSeconds = Math.max(0, Math.round(Number(seconds) || 0));
    const minutes = Math.floor(totalSeconds / 60);
    const remainingSeconds = totalSeconds % 60;
    return `${minutes}m ${String(remainingSeconds).padStart(2, '0')}s`;
  };

  const cards = [
    {
      label: 'Total Calls',
      value: data.total_calls,
      icon: '☎',
    },
    {
      label: 'Booking Rate',
      value: `${data.booking_rate}%`,
      callout: `${(data.booking_rate / INDUSTRY_BOOKING_RATE).toFixed(1)}x industry avg`,
      icon:  '⇆',
    },
    {
      label: 'Avg Premium Over Loadboard',
      value: `${data.avg_premium_over_loadboard}%`,
      callout: `↓ ${(11 - Number(data.avg_premium_over_loadboard || 0)).toFixed(2)}% Industry Avg`,
      icon: '$',
    },
    {
      label: 'Total Revenue Booked',
      value: `$${Number(data.total_revenue_booked).toLocaleString()}`,
      icon: '⛟',
    },
    {
      label: 'Avg Time to Book',
      value: formatDuration(data.avg_duration_seconds),
      icon: '⏱',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-y-8 gap-x-5">
      {cards.map((card) => (
        <div key={card.label} className="bg-surface border border-border p-6 relative min-h-[146px] transition-colors hover:border-primary">
          <div className="flex items-start justify-between">
            <p className="text-xs font-semibold text-muted uppercase tracking-wider font-body">
              {card.label}
            </p>
            <span className="text-sm text-muted">{card.icon}</span>
          </div>
          <p className={`text-[clamp(2.2rem,2.4vw,3rem)] font-semibold font-mono mt-4 leading-none tracking-tight ${card.valueClass || 'text-primary'}`}>
            {card.value}
          </p>
          {card.callout && (
            <span className="absolute right-4 bottom-4 px-2 py-0.5 text-[10px] font-semibold uppercase bg-accent/20 text-accent border border-accent/40">
              {card.callout}
            </span>
          )}
        </div>
      ))}
    </div>
  );
}
