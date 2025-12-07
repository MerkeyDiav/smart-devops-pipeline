import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Tech News Reader',
  description: 'Stay updated with the latest tech news',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
