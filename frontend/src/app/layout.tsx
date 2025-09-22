import './globals.css'
import { ReactNode } from 'react'
import Header from '../components/header'
import Footer from '../components/footer'

export const metadata = {
  title: 'DiagnoVET',
  description: 'Plataforma de diagnóstico veterinario',
}


export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="es">
      <body className="bg-gradient-to-br from-purple-500 to-indigo-500 min-h-screen flex flex-col">
        {/* <Header /> */}
        <main className="flex p-4 justify-center m-4">
          {children}
        </main>
        {/* <Footer /> */}
      </body>
    </html>
  )
}
