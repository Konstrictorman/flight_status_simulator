"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { Paper, Typography } from "@mui/material";

const LAX = [33.9425, -118.4081] as [number, number];
const JFK = [40.6413, -73.7781] as [number, number];
const DEFAULT_CENTER: [number, number] = [37.5, -96]; // US center
const DEFAULT_ZOOM = 4;

const DynamicMap = dynamic(() => import("./FlightMapInner"), {
  ssr: false,
  loading: () => (
    <Paper sx={{ height: 400, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <Typography color="text.secondary">Loading map…</Typography>
    </Paper>
  ),
});

interface FlightMapProps {
  latitude?: number;
  longitude?: number;
  heading?: number;
}

export function FlightMap({ latitude, longitude, heading }: FlightMapProps) {
  return (
    <Paper sx={{ overflow: "hidden" }}>
      <Typography variant="subtitle2" sx={{ p: 1, pb: 0 }} color="text.secondary">
        Position (live)
      </Typography>
      <DynamicMap
        latitude={latitude}
        longitude={longitude}
        heading={heading}
        defaultCenter={DEFAULT_CENTER}
        defaultZoom={DEFAULT_ZOOM}
        routeStart={LAX}
        routeEnd={JFK}
      />
    </Paper>
  );
}
