import "./globals.css";

export const metadata = {
  title: "SensoryArch AI (MVP)",
  description: "2D görsel yükle → duyusal risk analizi → heatmap/skor/öneriler",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="tr">
      <body>{children}</body>
    </html>
  );
}

