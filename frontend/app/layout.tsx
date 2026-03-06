import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Crypto News Replicator',
  description: 'Replica noticias de crypto con personalidad personalizada',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body className={inter.className}>
        <nav className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16 items-center">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold text-primary">
                  Crypto News Replicator
                </h1>
              </div>
              <div className="flex items-center gap-4">
                <span className="text-sm text-slate-600">Powered by @zuler</span>
              </div>
            </div>
          </div>
        </nav>
        <main className="min-h-screen">
          {children}
        </main>
        <footer className="bg-slate-100 border-t mt-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <p className="text-center text-slate-600 text-sm">
              Crypto News Replicator - Proyecto educacional
            </p>
          </div>
        </footer>
      </body>
    </html>
  )
}
