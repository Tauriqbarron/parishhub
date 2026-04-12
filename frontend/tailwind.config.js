/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			colors: {
				brand: {
					primary: '#0F172A',
					'primary-light': '#1E293B',
					'primary-muted': '#475569',
					accent: '#D97706',
					'accent-light': '#FBBF24',
					'accent-muted': '#FFFBEB',
					'bg-subtle': '#F8FAFC',
					'bg-muted': '#F1F5F9',
					border: '#E2E8F0',
					'border-strong': '#CBD5E1',
					'text-secondary': '#475569',
					'text-muted': '#94A3B8',
					success: '#059669',
					error: '#DC2626',
					info: '#2563EB'
				}
			},
			fontFamily: {
				sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'sans-serif']
			},
			borderRadius: {
				sm: '4px',
				md: '8px',
				lg: '12px',
				xl: '16px'
			},
			transitionDuration: {
				fast: '150ms',
				normal: '200ms',
				slow: '300ms'
			},
			zIndex: {
				dropdown: '10',
				sticky: '20',
				overlay: '30',
				modal: '40',
				toast: '50'
			}
		}
	},
	plugins: [require('@tailwindcss/forms'), require('@tailwindcss/typography')]
};
