/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // رنگ‌های سفارشی برای تم AI
        primary: {
          50: '#f0f7ff',
          100: '#e0effe',
          200: '#bae0fd',
          300: '#7cc5fb',
          400: '#36a9f8',
          500: '#0c8ee7',
          600: '#0270c4',
          700: '#0259a0',
          800: '#064b85',
          900: '#0c406e',
        },
        secondary: {
          // رنگ‌های بنفش برای جلوه‌های AI
          DEFAULT: '#6366f1',
          dark: '#4338ca',
        }
      },
      fontFamily: {
        // فونت‌های فارسی
        'sans': ['IRANSans', 'sans-serif'],
        'display': ['IRANYekan', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic': 'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'), // برای فرم‌های بهتر
    require('@tailwindcss/typography'), // برای محتوای متنی
    require('@tailwindcss/aspect-ratio'), // برای نسبت تصاویر
  ],
}
