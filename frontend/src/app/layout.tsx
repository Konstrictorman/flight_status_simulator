import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";
import { AppBar, Toolbar, Typography, Container } from "@mui/material";
import Link from "next/link";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Flight Status Simulator",
  description: "LAX to JFK flight simulation with real-time metrics",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable}`}>
        <Providers>
          <AppBar position="static">
            <Toolbar>
              <Link href="/" style={{ color: "inherit", textDecoration: "none" }}>
                <Typography variant="h6" component="span">
                  Flight Status Simulator
                </Typography>
              </Link>
            </Toolbar>
          </AppBar>
          <Container maxWidth="lg" sx={{ py: 3 }}>
            {children}
          </Container>
        </Providers>
      </body>
    </html>
  );
}
