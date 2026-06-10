
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.js,ts,jsx,tsx,mdx',
    './components/**/*.js,ts,jsx,tsx,mdx',
    './app/**/*.js,ts,jsx,tsx,mdx',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      fontSize: {
        'xs': '0.75rem',
        'sm': '0.875rem',
        'base': '1.125rem',
        'lg': '1.5rem',
        'xl': '2.25rem',
        '2xl': '3.75rem',
        '3xl': '5rem',
      },
      spacing: {
        '1': '0.25rem',
        '2': '0.5rem',
        '3': '0.75rem',
        '4': '1rem',
        '5': '1.25rem',
        '6': '1.5rem',
        '8': '2rem',
        '10': '2.5rem',
        '12': '3rem',
        '16': '4rem',
        '20': '5rem',
        '24': '6rem',
        '32': '8rem',
      },
      colors: {
        background: 'var(--color-background)',
        surface: 'var(--color-surface)',
        'glow-primary': 'var(--color-glow-primary)',
        'glow-secondary': 'var(--color-glow-secondary)',
        'text-primary': 'var(--color-text-primary)',
        'text-secondary': 'var(--color-text-secondary)',
        'text-accent': 'var(--color-text-accent)',
      },
    },
  },
  plugins: [],
}
export default config
