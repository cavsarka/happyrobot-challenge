import { useState, useMemo } from 'react';

function frictionBadge(friction) {
  if (friction >= 66) return { label: 'High', cls: 'bg-error/20 text-error' };
  if (friction >= 33) return { label: 'Med', cls: 'bg-warning/20 text-warning' };
  return { label: 'Low', cls: 'bg-accent/20 text-accent' };
}

export default function CarrierList({ carriers, selected, onSelect }) {
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    if (!carriers) return [];
    const valid = carriers.filter(
      (c) => c?.carrier_name?.trim?.() && c?.mc_number?.trim?.()
    );
    if (!search) return valid;
    const q = search.toLowerCase();
    return valid.filter(
      (c) => c.carrier_name.toLowerCase().includes(q) || c.mc_number.toLowerCase().includes(q)
    );
  }, [carriers, search]);

  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
  const active = carriers?.filter((c) => c.last_call && new Date(c.last_call) > thirtyDaysAgo).length || 0;

  return (
    <div className="w-80 border-r border-border bg-surface flex flex-col h-full">
      <div className="p-4 border-b border-border">
        <input
          type="text"
          placeholder="Search carriers..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full border border-border px-3 py-2 text-sm bg-white font-body"
        />
        <p className="text-[10px] text-muted mt-2">
          {carriers?.length || 0} Carriers | {active} Active (last 30 days)
        </p>
      </div>
      <div className="flex items-center justify-between px-4 py-2 border-b border-border bg-background/50">
        <span className="text-[10px] font-semibold text-muted uppercase tracking-wider">Carrier</span>
        <span className="text-[10px] font-semibold text-muted uppercase tracking-wider">Friction</span>
      </div>
      <div className="flex-1 overflow-y-auto">
        {filtered.map((c) => {
          const badge = frictionBadge(c.friction);
          const isActive = selected === c.mc_number;
          return (
            <div
              key={c.mc_number}
              onClick={() => onSelect(c.mc_number)}
              className={`px-4 py-3 border-b border-border cursor-pointer flex justify-between items-center ${
                isActive ? 'border-l-2 border-l-accent bg-primary/5' : 'hover:bg-background'
              }`}
            >
              <div>
                <p className="text-sm font-semibold">{c.carrier_name}</p>
                <p className="text-xs text-muted font-mono">{c.mc_number}</p>
              </div>
              <span className={`px-2 py-0.5 text-[10px] font-semibold ${badge.cls}`}>
                {badge.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
