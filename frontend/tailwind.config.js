export default {
  content: ['./index.html', './src/**/*.{vue,js,ts}'],
  darkMode: 'media',
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: '#3b82f6', dark: '#2563eb' },
        success: '#10b981',
        danger: '#ef4444',
        warning: '#f59e0b',
        surface: {
          DEFAULT: 'var(--surface)',
          secondary: 'var(--surface-secondary)',
          tertiary: 'var(--surface-tertiary)',
        },
        border: 'var(--border)',
        text: {
          DEFAULT: 'var(--text)',
          secondary: 'var(--text-secondary)',
          muted: 'var(--text-muted)',
        },
      },
      maxWidth: {
        app: '600px',
      },
    },
  },
  plugins: [],
}
