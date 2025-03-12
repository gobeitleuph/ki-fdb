import './globals.css'

export const metadata = {
  title: 'Fördermittel-Finder',
  description: 'Suchen Sie nach Förderprogrammen mit KI-gestütztem Matching',
}

export default function RootLayout({ children }) {
  return (
    <html lang="de">
      <body>
        {children}
      </body>
    </html>
  )
}
