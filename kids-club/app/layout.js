import './globals.css'

export const metadata = {
  title: 'Oekrainse Kids Club Amsterdam',
  description: 'Український Kids Club в Амстердамі - творчість, дружба, радість',
}

export default function RootLayout({ children }) {
  return (
    <html lang="uk">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap" rel="stylesheet" />
      </head>
      <body style={{fontFamily: "'Nunito', 'Segoe UI', sans-serif"}}>{children}</body>
    </html>
  )
}
