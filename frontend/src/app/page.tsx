"use client";

import { useState, useEffect } from "react";
import {
  Box,
  Button,
  Card,
  CardContent,
  CardActions,
  Typography,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Stack,
} from "@mui/material";
import Link from "next/link";
import {
  fetchFlights,
  fetchRoutes,
  createFlight,
  type Flight,
  type RouteInfo,
} from "@/lib/api";

export default function HomePage() {
  const [flights, setFlights] = useState<Flight[]>([]);
  const [routes, setRoutes] = useState<RouteInfo[]>([]);
  const [selectedRoute, setSelectedRoute] = useState("BOG-LHR");
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadFlights = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchFlights();
      setFlights(data.flights);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load flights");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFlights();
    fetchRoutes()
      .then((data) => {
        setRoutes(data.routes);
        if (data.routes.length > 0) {
          setSelectedRoute(data.routes[0].code);
        }
      })
      .catch(() => {});
  }, []);

  const handleCreateFlight = async () => {
    setCreating(true);
    setError(null);
    try {
      createFlight(selectedRoute);
      loadFlights();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create flight");
    } finally {
      setCreating(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Flights
      </Typography>
      <Typography color="text.secondary" sx={{ mb: 2 }}>
        Select a route and start a new simulation, or watch an existing one in real time.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 2 }}>
        <FormControl size="small" sx={{ minWidth: 280 }}>
          <InputLabel id="route-select-label">Route</InputLabel>
          <Select
            labelId="route-select-label"
            value={selectedRoute}
            label="Route"
            onChange={(e) => setSelectedRoute(e.target.value)}
          >
            {routes.map((r) => (
              <MenuItem key={r.code} value={r.code}>
                {r.code} — {r.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        <Button
          variant="contained"
          onClick={handleCreateFlight}
          disabled={creating}
        >
          {creating ? <CircularProgress size={24} /> : "Start new flight"}
        </Button>
      </Stack>

      {loading ? (
        <Box display="flex" justifyContent="center" py={4}>
          <CircularProgress />
        </Box>
      ) : flights.length === 0 ? (
        <Card>
          <CardContent>
            <Typography color="text.secondary">
              No flights yet. Select a route and click &quot;Start new flight&quot; to begin.
            </Typography>
          </CardContent>
        </Card>
      ) : (
        <List>
          {flights.map((f) => (
            <ListItem key={f.id} disablePadding sx={{ mb: 1 }}>
              <Card sx={{ width: "100%" }}>
                <CardContent>
                  <ListItemText
                    primary={`${f.route} — ${f.status}`}
                    secondary={f.started_at ? `Started: ${new Date(f.started_at).toLocaleString()}` : undefined}
                  />
                </CardContent>
                <CardActions>
                  <Button size="small" component={Link} href={`/flights/${f.id}`}>
                    Watch stream
                  </Button>
                </CardActions>
              </Card>
            </ListItem>
          ))}
        </List>
      )}
    </Box>
  );
}
