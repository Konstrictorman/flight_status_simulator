"use client";

import { useEffect, useState, useRef } from "react";
import { getStreamUrl } from "@/lib/api";
import type { FlightMetrics } from "@/types/flight";

const MAX_HISTORY = 100;

export function useFlightStream(flightId: string | null) {
  const [metrics, setMetrics] = useState<FlightMetrics | null>(null);
  const [history, setHistory] = useState<FlightMetrics[]>([]);
  const [status, setStatus] = useState<"connecting" | "active" | "completed" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!flightId) {
      setMetrics(null);
      setHistory([]);
      setStatus(null);
      setError(null);
      return;
    }

    setStatus("connecting");
    setError(null);
    const url = getStreamUrl(flightId);
    const es = new EventSource(url);
    eventSourceRef.current = es;

    es.onopen = () => setStatus("active");

    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.status === "completed") {
          setStatus("completed");
          es.close();
          return;
        }
        if (data.error) {
          setError(data.error);
          es.close();
          return;
        }
        const m = data as FlightMetrics;
        setMetrics(m);
        setHistory((prev) => {
          const next = [...prev, m];
          return next.length > MAX_HISTORY ? next.slice(-MAX_HISTORY) : next;
        });
      } catch {
        // ignore parse errors
      }
    };

    es.onerror = () => {
      setError("Stream connection failed");
      es.close();
    };

    return () => {
      es.close();
      eventSourceRef.current = null;
    };
  }, [flightId]);

  return { metrics, history, status, error };
}
