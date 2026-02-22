const ALERTS = [
  {
    severity: 'CRITICAL',
    time: '2 min ago',
    event: 'Carrier rejection rate exceeded threshold (>3 in 10 min)',
    color: 'bg-error/15 text-error',
  },
  {
    severity: 'WARNING',
    time: '14 min ago',
    event: 'AI negotiating above 10% margin on LAX→PHX lane',
    color: 'bg-warning/15 text-warning',
  },
  {
    severity: 'NOTICE',
    time: '1 hr ago',
    event: '5 calls ended in error escalation in last hour',
    color: 'bg-muted/20 text-muted',
  },
];

export default function AlertsTable() {
  return (
    <div className="bg-surface border border-border p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-2xl font-medium text-primary font-heading">Recent Critical Alerts</h3>
      </div>
      <table className="w-full">
        <thead>
          <tr className="border-b border-border text-left">
            <th className="pb-3 text-xs font-semibold text-muted uppercase tracking-wider w-28">Severity</th>
            <th className="pb-3 text-xs font-semibold text-muted uppercase tracking-wider w-28">Time</th>
            <th className="pb-3 text-xs font-semibold text-muted uppercase tracking-wider">Event Description</th>
            <th className="pb-3 text-xs font-semibold text-muted uppercase tracking-wider w-40">Action</th>
          </tr>
        </thead>
        <tbody>
          {ALERTS.map((alert, i) => (
            <tr key={i} className="border-b border-border h-14">
              <td className="py-3">
                <span className={`px-2 py-1 text-[10px] font-semibold uppercase ${alert.color}`}>
                  {alert.severity}
                </span>
              </td>
              <td className="py-3 text-xs text-muted font-mono">{alert.time}</td>
              <td className="py-3 text-sm text-primary">{alert.event}</td>
              <td className="py-3">
                <div className="flex gap-2">
                  <button className="px-3 py-1.5 bg-primary text-white text-xs font-semibold cursor-pointer hover:opacity-90">
                    REVIEW
                  </button>
                  <button className="px-3 py-1.5 border border-border text-primary text-xs font-semibold cursor-pointer hover:bg-background">
                    ADJUST
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
