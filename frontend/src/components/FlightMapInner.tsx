"use client";

import { useMemo } from "react";
import { MapContainer, TileLayer, Polyline, Marker } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix default marker icons in Leaflet with webpack/Next
delete (L.Icon.Default.prototype as unknown as { _getIconUrl?: unknown })._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

interface FlightMapInnerProps {
  latitude?: number;
  longitude?: number;
  heading?: number;
  defaultCenter: [number, number];
  defaultZoom: number;
  routeStart: [number, number];
  routeEnd: [number, number];
}

function PlaneMarker({ lat, lng, heading }: { lat: number; lng: number; heading?: number }) {
  const icon = useMemo(() => {
    return L.divIcon({
      className: "plane-marker",
      html: `<div style="
        width: 24px; height: 24px; background: #1976d2; border-radius: 50%;
        border: 2px solid white; box-shadow: 0 1px 3px rgba(0,0,0,0.3);
        transform: rotate(${heading ?? 0}deg);
      " title="Aircraft"></div>`,
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    });
  }, [heading]);

  return <Marker position={[lat, lng]} icon={icon} />;
}

export default function FlightMapInner({
  latitude,
  longitude,
  heading,
  defaultCenter,
  defaultZoom,
  routeStart,
  routeEnd,
}: FlightMapInnerProps) {
  const route = useMemo(() => [routeStart, routeEnd], [routeStart, routeEnd]);
  const hasPosition = latitude != null && longitude != null;

  return (
    <div style={{ height: 400 }}>
      <MapContainer
        center={defaultCenter}
        zoom={defaultZoom}
        style={{ height: "100%", width: "100%" }}
        scrollWheelZoom
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Polyline positions={route} color="#1976d2" weight={2} opacity={0.7} />
        {hasPosition && (
          <PlaneMarker lat={latitude} lng={longitude} heading={heading} />
        )}
      </MapContainer>
    </div>
  );
}
