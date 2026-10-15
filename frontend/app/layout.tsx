import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ReviewForge — Pull request review with evidence",
  description: "A transparent, testable AI-assisted code review platform.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

