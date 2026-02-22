import { MapContainer, TileLayer, Polyline, CircleMarker, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

export default function LoadMap({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-surface border border-border" style={{ height: 400 }}>
        <div className="flex items-center justify-center h-full text-muted text-sm">
          No map data available
        </div>
      </div>
    );
  }

  return (
    <div className="bg-surface border border-border" style={{ height: 400 }}>
      <MapContainer
        center={[39.8283, -98.5795]}
        zoom={4}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={false}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap'
        />
        {data.map((load) => {
          const weight = Math.max(1, Math.min(5, load.margin_percentage / 2));
          return (
            <div key={load.load_id}>
              <Polyline
                positions={[
                  [load.origin_lat, load.origin_lng],
                  [load.destination_lat, load.destination_lng],
                ]}
                color="#00C48C"
                weight={weight}
                opacity={0.6}
              >
                <Tooltip>
                  <div className="text-xs">
                    <p className="font-semibold">{load.load_id}</p>
                    <p>{load.origin} → {load.destination}</p>
                    <p>Rate: ${load.agreed_rate.toLocaleString()}</p>
                    <p>Margin: {load.margin_percentage.toFixed(1)}%</p>
                  </div>
                </Tooltip>
              </Polyline>
              <CircleMarker
                center={[load.origin_lat, load.origin_lng]}
                radius={4}
                fillColor="#00C48C"
                fillOpacity={1}
                stroke={false}
              />
              <CircleMarker
                center={[load.destination_lat, load.destination_lng]}
                radius={4}
                fillColor="#00C48C"
                fillOpacity={0.3}
                color="#00C48C"
                weight={2}
              />
            </div>
          );
        })}
      </MapContainer>
    </div>
  );
}
