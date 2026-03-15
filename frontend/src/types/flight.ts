export interface FlightMetrics {
  phase: string;
  altitude_ft: number;
  airspeed_knots: number;
  heading_degrees: number;
  latitude: number;
  longitude: number;
  fuel_remaining_gal: number;
  fuel_percent: number;
  oat_celsius: number;
  eta_seconds: number;
}

export interface StreamStatus {
  status?: "completed";
  error?: string;
}
