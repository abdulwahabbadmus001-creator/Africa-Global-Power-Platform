type AgpLogoProps = {
  size?: number
  label?: string
}

export default function AgpLogo({
  size = 44,
  label = 'Africa & Global Power',
}: AgpLogoProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 128 128"
      role="img"
      aria-label={label}
      xmlns="http://www.w3.org/2000/svg"
      style={{ display: 'block' }}
    >
      <rect width="128" height="128" rx="18" fill="#f6f1e7" />

      <path
        d="M68 10
           L76 18
           L82 17
           L89 24
           L87 31
           L93 38
           L90 46
           L95 57
           L89 64
           L90 75
           L83 85
           L77 88
           L73 95
           L66 102
           L63 112
           L54 118
           L47 112
           L43 101
           L37 96
           L34 87
           L26 82
           L21 73
           L25 62
           L21 54
           L28 45
           L26 36
           L33 28
           L40 27
           L47 18
           L57 17
           L62 12
           Z"
        fill="#D4AF37"
      />

      <path
        d="M69 84
           L73 92
           L69 100
           L64 110
           L57 112
           L52 104
           L55 95
           L61 87
           Z"
        fill="#c39a21"
        opacity="0.9"
      />

      <text
        x="64"
        y="71"
        textAnchor="middle"
        fontFamily="Manrope, DM Sans, Arial, sans-serif"
        fontWeight="900"
        fontSize="26"
        letterSpacing="-1"
        fill="#111111"
      >
        AGP
      </text>
    </svg>
  )
}