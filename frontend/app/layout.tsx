import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RSIP — Real State Investment Portal",
  description: "Real estate investment analysis and portfolio management",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
