"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Paper, Typography } from "@mui/material";
import type { FlightMetrics } from "@/types/flight";

interface AltitudeChartProps {
  data: FlightMetrics[];
}

export function AltitudeChart({ data }: AltitudeChartProps) {
  const chartData = data.map((d, i) => ({
    index: i,
    altitude: d.altitude_ft,
    phase: d.phase.replace(/_/g, " "),
  }));

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
        Altitude (ft) over time
      </Typography>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="index" hide />
          <YAxis allowDecimals={false} />
          <Tooltip
            formatter={(value: unknown) => [
              typeof value === "number" ? `${value.toLocaleString()} ft` : String(value),
              "Altitude",
            ]}
            labelFormatter={(_, payload) =>
              payload?.[0]?.payload?.phase ? `Phase: ${(payload[0].payload as { phase?: string }).phase}` : ""
            }
          />
          <Area type="monotone" dataKey="altitude" stroke="#1976d2" fill="#1976d2" fillOpacity={0.3} />
        </AreaChart>
      </ResponsiveContainer>
    </Paper>
  );
}
