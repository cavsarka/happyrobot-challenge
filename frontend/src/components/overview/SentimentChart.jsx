import { useRef, useState } from 'react';

const LABELS = {
  booked: 'BOOKED',
  no_deal_rate: 'NO DEAL - RATE DISCREPANCY',
  no_deal_no_load: 'NO DEAL - NO LOAD AVAILABILITY',
  unverified: 'UNVERIFIED / TIMEOUT',
  error_escalation: 'ERROR ESCALATION',
};

export default function SentimentChart({ data }) {
  if (!data || data.length === 0) return null;
  const containerRef = useRef(null);
  const [hovered, setHovered] = useState(null);

  const rows = data
    .map((d) => {
      const positive = Number(d.positive || 0);
      const neutral = Number(d.neutral || 0);
      const negative = Number(d.negative || 0);
      const total = positive + neutral + negative;
      return {
        outcome: LABELS[d.outcome] || String(d.outcome || '').toUpperCase(),
        positive,
        neutral,
        negative,
        total,
      };
    })
    .sort((a, b) => b.total - a.total);

  const percent = (part, total) => (total > 0 ? (part / total) * 100 : 0);
  const onHoverSegment = (event, payload) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    setHovered({
      ...payload,
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    });
  };

  return (
    <div ref={containerRef} className="bg-surface border border-border p-6 h-full relative">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-medium font-heading text-primary">
            Sentiment Outcome Matrix
          </h3>
          <p className="text-[11px] text-muted mt-1">
            Correlation of negotiation results and tonality
          </p>
        </div>
        <div className="flex items-center gap-3 text-[11px] font-semibold text-muted uppercase mt-0.5">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 bg-accent inline-block" />
            <span>POS</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 bg-[#B7C2D1] inline-block" />
            <span>NEU</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 bg-error inline-block" />
            <span>NEG</span>
          </div>
        </div>
      </div>

      <div className="space-y-5">
        {rows.map((row) => (
          <div key={row.outcome}>
            <div className="flex items-center justify-between mb-2">
              <p className="text-[14px] font-semibold uppercase tracking-[0.02em] text-primary">
                {row.outcome}
              </p>
              <p className="text-[14px] font-semibold uppercase tracking-[0.08em] text-primary font-mono">
                {row.total} CALLS
              </p>
            </div>
            <div className="w-full h-6 bg-background flex overflow-hidden border border-border">
              <div
                className="bg-accent cursor-pointer transition-opacity hover:opacity-85"
                style={{ width: `${percent(row.positive, row.total)}%` }}
                onMouseEnter={(e) => onHoverSegment(e, { tone: 'Positive', value: row.positive, total: row.total, outcome: row.outcome })}
                onMouseMove={(e) => onHoverSegment(e, { tone: 'Positive', value: row.positive, total: row.total, outcome: row.outcome })}
                onMouseLeave={() => setHovered(null)}
              />
              <div
                className="bg-[#B7C2D1] cursor-pointer transition-opacity hover:opacity-85"
                style={{ width: `${percent(row.neutral, row.total)}%` }}
                onMouseEnter={(e) => onHoverSegment(e, { tone: 'Neutral', value: row.neutral, total: row.total, outcome: row.outcome })}
                onMouseMove={(e) => onHoverSegment(e, { tone: 'Neutral', value: row.neutral, total: row.total, outcome: row.outcome })}
                onMouseLeave={() => setHovered(null)}
              />
              <div
                className="bg-error cursor-pointer transition-opacity hover:opacity-85"
                style={{ width: `${percent(row.negative, row.total)}%` }}
                onMouseEnter={(e) => onHoverSegment(e, { tone: 'Negative', value: row.negative, total: row.total, outcome: row.outcome })}
                onMouseMove={(e) => onHoverSegment(e, { tone: 'Negative', value: row.negative, total: row.total, outcome: row.outcome })}
                onMouseLeave={() => setHovered(null)}
              />
            </div>
          </div>
        ))}
      </div>

      {hovered && (
        <div
          className="absolute pointer-events-none bg-primary text-white text-[11px] px-2.5 py-1.5 border border-border font-body z-20"
          style={{ left: hovered.x + 10, top: hovered.y - 10, transform: 'translateY(-100%)' }}
        >
          <p className="font-semibold">{hovered.outcome}</p>
          <p>{hovered.tone}: {hovered.value} ({percent(hovered.value, hovered.total).toFixed(1)}%)</p>
        </div>
      )}
    </div>
  );
}
