import { useState, useEffect, useRef } from 'react';
import { fetchCalls } from '../api/client';
import CallsTable from '../components/calls/CallsTable';

export default function CallLog() {
  const [calls, setCalls] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [outcome, setOutcome] = useState('all');
  const [sentiment, setSentiment] = useState('all');
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const fetchRef = useRef(0);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1);
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  useEffect(() => {
    const id = ++fetchRef.current;
    fetchCalls({ page, limit: 20, outcome, sentiment, search: debouncedSearch || undefined })
      .then((data) => {
        if (id === fetchRef.current) {
          setCalls(data.calls);
          setTotalPages(data.pages);
        }
      });
  }, [page, outcome, sentiment, debouncedSearch]);

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-surface border border-border p-4 flex gap-4 items-center">
        <select
          value={outcome}
          onChange={(e) => { setOutcome(e.target.value); setPage(1); }}
          className="border border-border px-3 pr-8 py-2 text-sm bg-white text-primary font-body h-[38px] appearance-none bg-[url('data:image/svg+xml;charset=UTF-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2212%22%20height%3D%2212%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%2394A3B8%22%20stroke-width%3D%222%22%3E%3Cpolyline%20points%3D%226%209%2012%2015%2018%209%22%2F%3E%3C%2Fsvg%3E')] bg-[length:12px] bg-[right_8px_center] bg-no-repeat"
        >
          <option value="all">All Outcomes</option>
          <option value="booked">Booked</option>
          <option value="no_deal_rate">No Deal - Rate</option>
          <option value="no_deal_no_load">No Deal - No Load</option>
          <option value="unverified">Unverified</option>
          <option value="error_escalation">Error Escalation</option>
        </select>

        <select
          value={sentiment}
          onChange={(e) => { setSentiment(e.target.value); setPage(1); }}
          className="border border-border px-3 pr-8 py-2 text-sm bg-white text-primary font-body h-[38px] appearance-none bg-[url('data:image/svg+xml;charset=UTF-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2212%22%20height%3D%2212%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%2394A3B8%22%20stroke-width%3D%222%22%3E%3Cpolyline%20points%3D%226%209%2012%2015%2018%209%22%2F%3E%3C%2Fsvg%3E')] bg-[length:12px] bg-[right_8px_center] bg-no-repeat"
        >
          <option value="all">All Sentiments</option>
          <option value="positive">Positive</option>
          <option value="neutral">Neutral</option>
          <option value="negative">Negative</option>
        </select>

        <input
          type="text"
          placeholder="Search carrier name or MC#..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border border-border px-3 py-2 text-sm bg-white text-primary font-body flex-1"
        />
      </div>

      {/* Table */}
      <div className="bg-surface border border-border">
        <CallsTable calls={calls} />
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <p className="text-xs text-muted">
          Page {page} of {totalPages}
        </p>
        <div className="flex gap-2">
          <button
            onClick={() => setPage(Math.max(1, page - 1))}
            disabled={page === 1}
            className="px-3 py-1.5 border border-border text-xs font-semibold disabled:opacity-30 cursor-pointer"
          >
            Prev
          </button>
          {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => i + 1).map((p) => (
            <button
              key={p}
              onClick={() => setPage(p)}
              className={`px-3 py-1.5 border text-xs font-semibold cursor-pointer ${
                p === page ? 'bg-primary text-white border-primary' : 'border-border'
              }`}
            >
              {p}
            </button>
          ))}
          <button
            onClick={() => setPage(Math.min(totalPages, page + 1))}
            disabled={page === totalPages}
            className="px-3 py-1.5 border border-border text-xs font-semibold disabled:opacity-30 cursor-pointer"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
