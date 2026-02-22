const OUTCOME_COLORS = {
  booked: 'bg-accent text-white',
  no_deal_rate: 'bg-error text-white',
  no_deal_no_load: 'bg-warning text-white',
  unverified: 'bg-muted text-white',
  error_escalation: 'bg-primary text-white',
};

const OUTCOME_LABELS = {
  booked: 'Booked',
  no_deal_rate: 'No Deal - Rate',
  no_deal_no_load: 'No Deal - No Load',
  unverified: 'Unverified',
  error_escalation: 'Error Escalation',
};

function frictionBadgeClass(friction) {
  if (friction >= 66) return 'text-error';
  if (friction >= 33) return 'text-warning';
  return 'text-accent';
}

function frictionBarClass(friction) {
  if (friction >= 66) return 'bg-error';
  if (friction >= 33) return 'bg-warning';
  return 'bg-accent';
}

function formatDuration(seconds) {
  const totalSeconds = Math.max(0, Math.round(Number(seconds) || 0));
  const minutes = Math.floor(totalSeconds / 60);
  const remainingSeconds = totalSeconds % 60;
  return `${minutes}m ${String(remainingSeconds).padStart(2, '0')}s`;
}

export default function CarrierDetail({ detail, fallbackFriction }) {
  if (!detail) {
    return (
      <div className="flex-1 flex items-center justify-center text-muted text-sm">
        Select a carrier to view details
      </div>
    );
  }

  const friction = Number(detail.friction ?? fallbackFriction ?? 0);
  const kpis = [
    {
      label: 'Friction',
      value: `${friction}`,
      valueClass: frictionBadgeClass(friction),
      barPct: Math.max(0, Math.min(100, friction)),
      barClass: frictionBarClass(friction),
    },
    { label: 'Total Loads', value: detail.bookings },
    { label: 'Acceptance Rate', value: `${detail.acceptance_rate}%` },
    {
      label: 'Avg Margin ($)',
      value: `$${Number(detail.avg_margin_dollars || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
    },
    { label: 'Avg Time to Book', value: formatDuration(detail.avg_negotiation_time) },
  ];

  return (
    <div className="flex-1 p-6 overflow-y-auto">
      <div className="mb-6">
        <h2 className="text-xl font-heading font-semibold text-primary">{detail.carrier_name}</h2>
        <span className="text-xs font-mono text-muted bg-background px-2 py-1 border border-border">
          {detail.mc_number}
        </span>
      </div>

      <div className="grid grid-cols-5 gap-4 mb-8">
        {kpis.map((kpi) => (
          <div key={kpi.label} className="bg-background border border-border p-4 relative overflow-hidden">
            <p className="text-[10px] font-semibold text-muted uppercase tracking-wider">{kpi.label}</p>
            <p className={`text-2xl font-semibold font-mono mt-1 ${kpi.valueClass || 'text-primary'}`}>{kpi.value}</p>
            {kpi.barPct != null && (
              <div className="absolute left-0 right-0 bottom-0 h-1 bg-border">
                <div className={`h-full ${kpi.barClass}`} style={{ width: `${kpi.barPct}%` }} />
              </div>
            )}
          </div>
        ))}
      </div>

      <h3 className="text-sm font-semibold text-primary mb-3">Recent Interaction History</h3>
      <table className="w-full">
        <thead>
          <tr className="border-b border-border text-left">
            {['Load ID', 'Lane', 'Loadboard → Final', 'Outcome', 'Date'].map((h) => (
              <th key={h} className="pb-3 text-xs font-semibold text-muted uppercase tracking-wider px-2">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {detail.history.map((h) => (
            <tr key={h.call_id} className="border-b border-border h-12">
              <td className="px-2 text-xs font-mono">{h.load_id || '—'}</td>
              <td className="px-2 text-xs">{h.lane || '—'}</td>
              <td className="px-2 text-xs font-mono">
                {h.loadboard_rate ? `$${h.loadboard_rate.toLocaleString()}` : '—'}
                {h.agreed_rate ? ` → $${h.agreed_rate.toLocaleString()}` : ''}
              </td>
              <td className="px-2">
                <span className={`px-2 py-0.5 text-[10px] font-semibold uppercase ${OUTCOME_COLORS[h.outcome] || ''}`}>
                  {OUTCOME_LABELS[h.outcome] || h.outcome}
                </span>
              </td>
              <td className="px-2 text-xs text-muted font-mono">
                {h.created_at ? new Date(h.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
