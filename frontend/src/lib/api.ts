const getBaseUrl = () =>
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Flight {
  id: string;
  route: string;
  status: string;
  started_at?: string;
}

export interface FlightListResponse {
  flights: Flight[];
}

export async function fetchFlights(): Promise<FlightListResponse> {
  const res = await fetch(`${getBaseUrl()}/flights`);
  if (!res.ok) throw new Error("Failed to fetch flights");
  return res.json();
}

export async function createFlight(): Promise<Flight> {
  const res = await fetch(`${getBaseUrl()}/flights`, { method: "POST" });
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
