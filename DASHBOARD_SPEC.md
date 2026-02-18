# ACME × HappyRobot Dashboard — Build Specification

## Overview
A freight brokerage operations dashboard built with React + Tailwind. 
Backend is FastAPI (running on port 8000). Frontend should run on port 3000.
All API calls should go to `http://localhost:8000`.

## Design System — Swiss Administrative Aesthetic

### Colors
- `primary`: #0A1628 (Deep Navy)
- `background`: #F5F7FA (Cool Gray) — app background
- `surface`: #FFFFFF (White) — cards and panels
- `accent`: #00C48C (Robot Green) — success, brand accents
- `border`: #E2E8F0 (Slate) — all borders
- `error`: #EF4444 (Red) — negative outcomes
- `warning`: #F59E0B (Amber) — warnings

### Typography
- Headings + Metrics: `Space Grotesk` (600 for numbers, 500 for headers)
- UI + Body: `Inter` (400 standard, 600 for labels)
- IDs, Timestamps, Currency: `JetBrains Mono`
- Import all three from Google Fonts

### Rules
- 0px border-radius on ALL elements — cards, buttons, inputs, badges
- No drop shadows anywhere — depth via 1px solid #E2E8F0 borders
- 12-column grid, 32px gutters
- Spacing in multiples of 8px
- Table rows: 56px height, horizontal borders only, no zebra striping
- Cards: white background, 1px border, 24px padding

### Navigation
- 64px sticky top bar, white background, 1px bottom border
- Left: "ACME Logistics | HappyRobot" logo lockup in Space Grotesk
  - "ACME Logistics" in primary (#0A1628), bold
  - "|" divider in #E2E8F0
  - "HappyRobot" in accent (#00C48C), bold
- Right: date range picker + user avatar placeholder
- Top nav tabs: Executive Overview | Call Log | Load Intelligence | Carrier CRM
- Active tab: accent green underline, primary text
- Inactive tab: #94A3B8 text

---

## Screen 1 — Executive Overview

### KPI Cards (top row, 4 cards)
Each card: white, 1px border, 24px padding, no radius

1. **Total Calls** — `GET /api/v1/dashboard/summary` → `total_calls`
   - Subtext: trend vs last period (green arrow up, red arrow down)
2. **Booking Rate** — `booking_rate` as percentage
   - Subtext: "Industry avg: 17.86%" in gray
3. **Avg Rate Efficiency** — `avg_rate_efficiency` as percentage
   - Subtext: "% of loadboard rate" in gray
   - Color: green if <106%, amber if 106-110%, red if >110%
4. **Avg Time to Book** — `avg_duration_seconds` converted to minutes
   - Only for booked calls
   - Subtext: "per completed booking"

All numbers in JetBrains Mono. Labels in Inter 600.

### Charts Row 1 (two charts, 60/40 split)
**Call Volume Over Time** (60%)
- Line chart using Recharts
- X axis: date, Y axis: call count
- Single accent green line, no fill
- Data: `GET /api/v1/dashboard/charts` → `volume_by_day`

**Outcome Breakdown** (40%)
- Donut chart, Recharts
- Center text: booking rate percentage in Space Grotesk 600
- Colors:
  - Booked: #00C48C
  - No Deal - Rate: #EF4444
  - No Deal - No Load: #F59E0B
  - Unverified: #94A3B8
  - Error Escalation: #0A1628
- Data: `outcome_breakdown`

### Charts Row 2 (three charts, equal width)
**Negotiation Funnel**
- Vertical funnel using Recharts FunnelChart
- Stages: Calls Received → Verified → Load Matched → Negotiation → Booked
- Each stage shows count and % of previous stage as drop-off label
- Data: `funnel`

**Rate Efficiency Distribution**
- Histogram (bar chart with small bins)
- X axis: agreed/loadboard ratio buckets (100-104%, 104-108%, 108-112%)
- Y axis: number of bookings
- Bars in accent green, red fill for bins above 108%
- Data: `rate_efficiency_distribution`

**Sentiment Distribution**
- Horizontal stacked bar per outcome category
- Colors: Positive #00C48C, Neutral #94A3B8, Negative #EF4444
- Data: `sentiment_breakdown`

### Critical Alerts Table (bottom, full width)
- Title: "⚠ Recent System Alerts" in Inter 600
- Columns: SEVERITY | TIME | EVENT DESCRIPTION | ACTION
- Severity pills: CRITICAL (red), WARNING (amber), NOTICE (gray)
- No zebra striping, horizontal borders only
- Hardcode 3 realistic alerts for demo:
  1. CRITICAL — "Carrier rejection rate exceeded threshold (>3 in 10 min)"
  2. WARNING — "AI negotiating above 10% margin on LAX→PHX lane"  
  3. NOTICE — "5 calls ended in error escalation in last hour"
- Action buttons: "REVIEW" and "ADJUST" — primary style, no radius

---

## Screen 2 — Call Log

### Filters Bar
- Dropdowns: Outcome (all/booked/no_deal_rate/etc), Sentiment, Date Range
- Search input: search by carrier name or MC number
- All inputs: 1px border, no radius, Inter font

### Table
Columns: TIME | CARRIER / MC# | LOAD ID | LANE | LOADBOARD RATE | AGREED RATE | ROUNDS | DURATION | OUTCOME | SENTIMENT

- TIME: JetBrains Mono, format "Feb 18, 10:42 AM"
- CARRIER: carrier_name bold, mc_number below in gray smaller text
- LOAD ID: JetBrains Mono, gray if null (non-booked calls show "—")
- LANE: "Chicago, IL → Dallas, TX" with arrow
- LOADBOARD RATE: JetBrains Mono, gray
- AGREED RATE: JetBrains Mono, primary if at loadboard, green if below, 
  red if above 108%
- ROUNDS: number, gray if 0
- DURATION: "2m 14s" format
- OUTCOME: pill badge, colors match outcome breakdown above
- SENTIMENT: pill badge, Positive/Neutral/Negative

### Expandable Row
Click any row to expand a panel below showing:
- Full text transcript in a scrollable box
- JetBrains Mono font, 14px
- HappyRobot messages left-aligned with green left border
- Carrier messages right-aligned with gray background
- If no transcript: "No transcript available" in gray italic

Data: `GET /api/v1/dashboard/calls?page=1&limit=20`
Pagination at bottom: prev/next + page numbers

---

## Screen 3 — Load Intelligence

### Map (top, full width, 400px height)
- Use react-leaflet with OpenStreetMap tiles
- Each booked load: draw an arc/line from origin to destination
- Line color: accent green (#00C48C), opacity 0.6
- Thicker lines for higher margin loads
- Dot markers at origin (filled) and destination (hollow)
- Tooltip on hover: Load ID, lane, agreed rate, margin %
- Data: `GET /api/v1/dashboard/loads/map`
  Returns: array of { load_id, origin, destination, 
  origin_lat, origin_lng, destination_lat, destination_lng, 
  agreed_rate, loadboard_rate, margin_percentage }

### KPI Row (3 cards below map)
1. Avg Margin % across all bookings
2. Avg Rate Per Mile (agreed_rate / miles from loads table)
3. Total Spend (sum of all agreed_rates)

### Load Table (full width)
Columns: LOAD ID | LANE | CARRIER | AI OFFER | COUNTER | FINAL | MARGIN | ACTION

- LOAD ID: JetBrains Mono
- LANE: "ATL, GA → CHI, IL"
- CARRIER: carrier name + MC badge
- AI OFFER: loadboard_rate in gray (this was the opening offer)
- COUNTER: show as "—" (we don't store individual counters)
- FINAL: agreed_rate, color coded by margin
- MARGIN: inline bar showing % above loadboard, green if <8%, 
  amber 8-10%, red >10%
- ACTION: "REVIEW" button if margin >10%, else "—"

Data: `GET /api/v1/dashboard/loads/detail`

---

## Screen 4 — Carrier CRM

### Layout
- Left sidebar: 320px, scrollable carrier list
- Right panel: carrier detail view

### Carrier List (left)
- Search bar at top
- Each row: carrier name bold, MC# below in gray, 
  right side shows FRICTION score badge
- FRICTION: Low (green), Med (amber), High (red)
  - Calculated as: avg negotiation rounds / 3 * 100
- Active row: left border in accent green, light navy background
- "X Carriers | Y Active (called in last 30 days)"

### Carrier Detail (right)
Header: Carrier name in Space Grotesk 600, MC#, status badge

**4 KPI cards:**
1. Acceptance Rate — % of calls that resulted in booking
2. Total Loads — lifetime count
3. Avg Negotiation Time — avg duration_seconds on booked calls
4. Avg Rate vs Loadboard — avg margin_percentage

**Recent Interaction History table:**
Columns: LOAD ID | LANE | AI OFFER→FINAL | OUTCOME | DATE
- Show last 10 interactions for selected carrier
- Outcome pill badges

Data: 
- `GET /api/v1/dashboard/carriers` — list with aggregated stats
- `GET /api/v1/dashboard/carriers/{mc_number}` — detail + history

---

## API Endpoints Needed
```
GET /api/v1/dashboard/summary
GET /api/v1/dashboard/charts  
GET /api/v1/dashboard/calls?page=&limit=&outcome=&sentiment=&search=
GET /api/v1/dashboard/loads/map
GET /api/v1/dashboard/loads/detail
GET /api/v1/dashboard/carriers
GET /api/v1/dashboard/carriers/{mc_number}
```

All endpoints require header: `X-API-Key: test_api_key_12345`

---

## Tech Stack
- React 18 with Vite
- Tailwind CSS
- Shadcn
- Recharts for all charts
- react-leaflet for the map
- Inter, Space Grotesk, JetBrains Mono from Google Fonts

## File Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── TopNav.jsx
│   │   │   └── Layout.jsx
│   │   ├── overview/
│   │   │   ├── KPICards.jsx
│   │   │   ├── VolumeChart.jsx
│   │   │   ├── OutcomeDonut.jsx
│   │   │   ├── NegotiationFunnel.jsx
│   │   │   ├── RateEfficiencyHistogram.jsx
│   │   │   ├── SentimentChart.jsx
│   │   │   └── AlertsTable.jsx
│   │   ├── calls/
│   │   │   ├── CallsTable.jsx
│   │   │   └── TranscriptPanel.jsx
│   │   ├── loads/
│   │   │   ├── LoadMap.jsx
│   │   │   └── LoadTable.jsx
│   │   └── carriers/
│   │       ├── CarrierList.jsx
│   │       └── CarrierDetail.jsx
│   ├── pages/
│   │   ├── Overview.jsx
│   │   ├── CallLog.jsx
│   │   ├── LoadIntelligence.jsx
│   │   └── CarrierCRM.jsx
│   ├── api/
│   │   └── client.js  ← all API calls centralized here
│   ├── App.jsx
│   └── main.jsx
```

## Notes for Claude Code
- Build one screen at a time, starting with Overview
- All components should be self-contained with their own data fetching
- Use the exact colors and fonts specified — no deviations
- No border radius anywhere, no shadows
- When in doubt, refer to the Swiss Administrative design philosophy:
  clarity over decoration, borders over shadows, density over whitespace