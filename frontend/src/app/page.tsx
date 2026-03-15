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
} from "@mui/material";
import Link from "next/link";
import { fetchFlights, createFlight, type Flight } from "@/lib/api";

export default function HomePage() {
  const [flights, setFlights] = useState<Flight[]>([]);
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
  }, []);

  const handleCreateFlight = async () => {
    setCreating(true);
    setError(null);
    try {
      await createFlight();
      await loadFlights();
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
        LAX to JFK simulations. Start a new flight or watch an existing one in real time.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Button
        variant="contained"
        onClick={handleCreateFlight}
        disabled={creating}
        sx={{ mb: 2 }}
      >
        {creating ? <CircularProgress size={24} /> : "Start new flight"}
      </Button>

      {loading ? (
        <Box display="flex" justifyContent="center" py={4}>
          <CircularProgress />
        </Box>
      ) : flights.length === 0 ? (
        <Card>
          <CardContent>
            <Typography color="text.secondary">
              No flights yet. Click &quot;Start new flight&quot; to begin a simulation.
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
