"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Paper, Typography } from "@mui/material";
import type { FlightMetrics } from "@/types/flight";

interface SpeedChartProps {
  data: FlightMetrics[];
}

export function SpeedChart({ data }: SpeedChartProps) {
  const chartData = data.map((d, i) => ({
    index: i,
    speed: d.airspeed_knots,
    phase: d.phase.replace(/_/g, " "),
  }));

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="subtitle2" color="text.secondary" gutterBottom>
        Airspeed (knots) over time
      </Typography>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="index" hide />
          <YAxis allowDecimals={false} />
          <Tooltip
            formatter={(value: unknown) => [
              typeof value === "number" ? `${value} kn` : String(value),
              "Speed",
            ]}
            labelFormatter={(_, payload) =>
              payload?.[0]?.payload?.phase ? `Phase: ${(payload[0].payload as { phase?: string }).phase}` : ""
            }
          />
          <Line type="monotone" dataKey="speed" stroke="#dc004e" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </Paper>
  );
}
