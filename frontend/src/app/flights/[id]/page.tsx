"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { Box, Button, Typography, Paper, Alert, CircularProgress, Stack } from "@mui/material";
import { useFlightStream } from "@/hooks/useFlightStream";
import { FlightMap } from "@/components/FlightMap";
import { AltitudeChart } from "@/components/AltitudeChart";
import { SpeedChart } from "@/components/SpeedChart";

export default function FlightStreamPage() {
  const params = useParams();
  const flightId = typeof params.id === "string" ? params.id : null;
  const { metrics, history, status, error } = useFlightStream(flightId);

  if (!flightId) {
    return (
      <Alert severity="warning">
        No flight ID. <a href="/">Back to flights</a>
      </Alert>
    );
  }

  return (
    <Box>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px" }}>
      <Typography variant="h5" gutterBottom>
        Flight {flightId.slice(0, 8)}… — Live stream
      </Typography>
      <Button size="small" component={Link} href={`/`} variant="contained" color="primary">
        Back to flights
      </Button>
      </div>


      {status === "connecting" && (
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <CircularProgress size={20} />
          <Typography color="text.secondary">Connecting to stream…</Typography>
        </Box>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {metrics && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="subtitle2" color="text.secondary">
            Current metrics
          </Typography>
          <Stack direction="row" spacing={2} sx={{ mt: 0.5 }} flexWrap="wrap" useFlexGap>
            <Box>
              <Typography variant="body2">Phase</Typography>
              <Typography variant="body1" fontWeight="medium">
                {metrics.phase.replace(/_/g, " ")}
              </Typography>
            </Box>
            <Box>
              <Typography variant="body2">Altitude</Typography>
              <Typography variant="body1" fontWeight="medium">
                {metrics.altitude_ft.toLocaleString()} ft
              </Typography>
            </Box>
            <Box>
              <Typography variant="body2">Speed</Typography>
              <Typography variant="body1" fontWeight="medium">
                {metrics.airspeed_knots} kn
              </Typography>
            </Box>
            <Box>
              <Typography variant="body2">ETA</Typography>
              <Typography variant="body1" fontWeight="medium">
                {Math.floor(metrics.eta_seconds / 60)} min
              </Typography>
            </Box>
          </Stack>
        </Paper>
      )}

      <Box sx={{ mb: 2 }}>
        <FlightMap
          latitude={metrics?.latitude}
          longitude={metrics?.longitude}
          heading={metrics?.heading_degrees}
        />
      </Box>

      {history.length > 0 && (
        <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
          <Box sx={{ flex: 1 }}>
            <AltitudeChart data={history} />
          </Box>
          <Box sx={{ flex: 1 }}>
            <SpeedChart data={history} />
          </Box>
        </Stack>
      )}

      {status === "completed" && (
        <Alert severity="success" sx={{ mt: 2 }}>
          Flight completed. You can go back to the <a href="/">flights list</a>.
        </Alert>
      )}
    </Box>
  );
}
