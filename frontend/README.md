# Flight Status Simulator — Frontend

Next.js app that consumes the Flight Status Simulator backend API and displays real-time flight metrics via the SSE stream.

## Stack

- **Next.js** (App Router, TypeScript)
- **Material UI** — layout, buttons, cards, typography
- **React-Leaflet** — map with LAX–JFK route and live aircraft position
- **Recharts** — altitude and airspeed over time
- **SSE** — native `EventSource` for `/flights/{id}/stream`

## Setup

1. Ensure the backend is running (e.g. `cd backend && python -m uvicorn app.main:app --reload --port 8000`).

2. Copy env and install:

   ```bash
   cp .env.local.example .env.local
   npm install
   ```

   If you don’t have `.env.local.example`, create `.env.local` with:

   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. Run the dev server:

   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000). Start a flight from the backend or via the UI, then click **Watch stream** to see the map and charts update in real time.

## Scripts

- `npm run dev` — development server (port 3000)
- `npm run build` — production build
- `npm run start` — run production server
- `npm run lint` — ESLint

## Features

- **Home:** List flights, start a new flight (POST /flights).
- **Flight stream page:** Live map (Leaflet) with plane marker, current metrics panel, and altitude/speed charts fed by the SSE stream.
