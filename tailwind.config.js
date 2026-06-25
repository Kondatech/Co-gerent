/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./**/templates/**/*.html",
    "./core/templates/**/*.html",
    "./crm/templates/**/*.html",
    "./ventes/templates/**/*.html",
    "./notifications/templates/**/*.html",
    "./agents/templates/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#F2A91C',
          dark: '#D6920F',
          light: '#FCE3B0',
          soft: '#FFF6E6',
          50: '#FFF9ED',
          100: '#FFF6E6',
          200: '#FCE3B0',
          300: '#F9D07A',
          400: '#F5BD44',
          500: '#F2A91C',
          600: '#D6920F',
          700: '#B0780C',
          800: '#8A5E08',
          900: '#644404',
        },
        gray: {
          50: '#F8F9FA',
          100: '#F4F5F6',
          200: '#E5E6E9',
          300: '#C7C9CE',
          400: '#A9ACB3',
          500: '#71737A',
          600: '#5A5C62',
          700: '#45474D',
          800: '#2E2F33',
          900: '#1C1D21',
        },
        success: {
          DEFAULT: '#2E9E5B',
          bg: '#E9F7EF',
        },
        warning: {
          DEFAULT: '#D6920F',
          bg: '#FFF6E6',
        },
        danger: {
          DEFAULT: '#D14343',
          bg: '#FCEAEA',
        },
        info: {
          DEFAULT: '#3B6FB6',
          bg: '#EAF1FB',
        },
      },
      fontFamily: {
        sans: ['Poppins', 'Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        xl: '24px',
        lg: '16px',
        md: '12px',
        sm: '8px',
        pill: '999px',
      },
      boxShadow: {
        'card': '0 4px 16px rgba(20, 20, 30, 0.06)',
        'card-hover': '0 10px 28px rgba(20, 20, 30, 0.10)',
        'primary': '0 4px 14px rgba(242, 169, 28, 0.28)',
        'primary-hover': '0 8px 22px rgba(242, 169, 28, 0.40)',
      },
      keyframes: {
        'fade-in-up': {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'slide-up': {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'pulse-skeleton': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.4' },
        },
        'typing-bounce': {
          '0%, 60%, 100%': { transform: 'translateY(0)' },
          '30%': { transform: 'translateY(-8px)' },
        },
      },
      animation: {
        'fade-in-up': 'fade-in-up 0.4s ease-out',
        'fade-in': 'fade-in 0.3s ease-out',
        'slide-up': 'slide-up 0.3s ease-out',
        'pulse-skeleton': 'pulse-skeleton 1.5s ease-in-out infinite',
        'typing-bounce': 'typing-bounce 1.4s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}