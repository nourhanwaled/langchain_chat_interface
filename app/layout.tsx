import "./globals.css";

export const metadata = {
  title: "AI Assistant Chat",
  description: "AI Assistant Chat Interface",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body style={{ backgroundColor: "rgb(95, 158, 160)" }}>{children}</body>
    </html>
  );
}
