import { useState } from 'react';
import TranscriptPanel from './TranscriptPanel';

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

const SENTIMENT_COLORS = {
  positive: 'bg-accent/20 text-accent',
  neutral: 'bg-muted/20 text-muted',
  negative: 'bg-error/20 text-error',
};

function formatDuration(s) {
  if (!s) return '—';
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return `${m}m ${sec}s`;
}

function formatDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) +
    ', ' +
    d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
}

export default function CallsTable({ calls }) {
  const [expanded, setExpanded] = useState(null);

  if (!calls || calls.length === 0) {
    return <p className="text-sm text-muted p-6">No calls found.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full table-fixed">
        <colgroup>
          <col className="w-[120px]" />
          <col className="w-[180px]" />
          <col className="w-[72px]" />
          <col className="w-[200px]" />
          <col className="w-[100px]" />
          <col className="w-[100px]" />
          <col className="w-[64px]" />
          <col className="w-[80px]" />
          <col className="w-[120px]" />
          <col className="w-[88px]" />
        </colgroup>
        <thead>
          <tr className="border-b border-border text-left">
            {['Time', 'Carrier / MC#', 'Load ID', 'Lane', 'Loadboard Rate', 'Agreed Rate', 'Rounds', 'Duration', 'Outcome', 'Sentiment'].map((h) => (
              <th key={h} className="pb-3 pt-4 text-xs font-semibold text-muted uppercase tracking-wider px-3 whitespace-nowrap">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {calls.map((c) => (
            <>
              <tr
                key={c.call_id}
                className="border-b border-border h-14 cursor-pointer hover:bg-background/50"
                onClick={() => setExpanded(expanded === c.call_id ? null : c.call_id)}
              >
                <td className="px-3 text-xs font-mono text-muted whitespace-nowrap">{formatDate(c.created_at)}</td>
                <td className="px-3">
                  <p className="text-sm font-semibold truncate">{c.carrier_name}</p>
                  <p className="text-xs text-muted">{c.mc_number}</p>
                </td>
                <td className="px-3 text-xs font-mono text-muted whitespace-nowrap">{c.load_id || '—'}</td>
                <td className="px-3 text-xs whitespace-nowrap truncate">{c.lane || '—'}</td>
                <td className="px-3 text-xs font-mono text-muted whitespace-nowrap">
                  {c.loadboard_rate ? `$${c.loadboard_rate.toLocaleString()}` : '—'}
                </td>
                <td className="px-3 text-xs font-mono text-primary whitespace-nowrap">
                  {c.agreed_rate ? `$${c.agreed_rate.toLocaleString()}` : '—'}
                </td>
                <td className="px-3 text-xs font-mono text-muted whitespace-nowrap">{c.negotiation_rounds || '—'}</td>
                <td className="px-3 text-xs font-mono whitespace-nowrap">{formatDuration(c.duration_seconds)}</td>
                <td className="px-3">
                  <span className={`inline-block px-2 py-0.5 text-[10px] font-semibold uppercase whitespace-nowrap ${OUTCOME_COLORS[c.outcome] || 'bg-muted text-white'}`}>
                    {OUTCOME_LABELS[c.outcome] || c.outcome}
                  </span>
                </td>
                <td className="px-3">
                  <span className={`inline-block px-2 py-0.5 text-[10px] font-semibold capitalize whitespace-nowrap ${SENTIMENT_COLORS[c.sentiment] || ''}`}>
                    {c.sentiment || '—'}
                  </span>
                </td>
              </tr>
              {expanded === c.call_id && (
                <tr key={`${c.call_id}-transcript`}>
                  <td colSpan={10} className="p-0 border-b border-border">
                    <TranscriptPanel transcription={c.transcription} />
                  </td>
                </tr>
              )}
            </>
          ))}
        </tbody>
      </table>
    </div>
  );
}
