const getBaseUrl = () =>
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Flight {
  id: string;
  route: string;
  status: string;
  started_at?: string;
}

export interface RouteInfo {
  code: string;
  label: string;
  origin: { lat: number; lon: number };
  destination: { lat: number; lon: number };
}

export interface FlightListResponse {
  flights: Flight[];
}

export interface RoutesResponse {
  routes: RouteInfo[];
}

export async function fetchFlights(): Promise<FlightListResponse> {
  const res = await fetch(`${getBaseUrl()}/flights`);
  if (!res.ok) throw new Error("Failed to fetch flights");
  return res.json();
}

export async function fetchRoutes(): Promise<RoutesResponse> {
  const res = await fetch(`${getBaseUrl()}/routes`);
  if (!res.ok) throw new Error("Failed to fetch routes");
  return res.json();
}

export async function createFlight(route?: string): Promise<Flight> {
  const res = await fetch(`${getBaseUrl()}/flights`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ route: route ?? "BOG-LHR" }),
  });
  if (!res.ok) throw new Error("Failed to create flight");
  return res.json();
}

export async function fetchFlight(id: string) {
  const res = await fetch(`${getBaseUrl()}/flights/${id}`);
  if (!res.ok) throw new Error("Failed to fetch flight");
  return res.json();
}

export function getStreamUrl(flightId: string): string {
  return `${getBaseUrl()}/flights/${flightId}/stream`;
}
