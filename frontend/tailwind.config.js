/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			colors: {
				brand: {
					/* Warm near-black, not cold slate */
					primary: '#1A1A1A',
					'primary-light': '#31302E',
					'primary-muted': '#615D59',
					/* Amber accent (parish warmth) */
					accent: '#D97706',
					'accent-light': '#FBBF24',
					'accent-muted': '#FFFBEB',
					/* Warm white backgrounds */
					'bg-subtle': '#F6F5F4',
					'bg-muted': '#EDECEB',
					/* Whisper borders */
					border: 'rgba(0, 0, 0, 0.08)',
					'border-strong': 'rgba(0, 0, 0, 0.15)',
					/* Warm text tones */
					'text-secondary': '#615D59',
					'text-muted': '#A39E98',
					/* Semantic */
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
			boxShadow: {
				/* Multi-layer Notion-style shadows */
				sm: '0 1px 2px 0 rgba(0, 0, 0, 0.04)',
				md:
					'rgba(0, 0, 0, 0.04) 0px 4px 18px, ' +
					'rgba(0, 0, 0, 0.027) 0px 2px 7px, ' +
					'rgba(0, 0, 0, 0.02) 0px 0.8px 3px, ' +
					'rgba(0, 0, 0, 0.01) 0px 0.2px 1px',
				lg:
					'rgba(0, 0, 0, 0.01) 0px 1px 3px, ' +
					'rgba(0, 0, 0, 0.02) 0px 3px 7px, ' +
					'rgba(0, 0, 0, 0.02) 0px 7px 15px, ' +
					'rgba(0, 0, 0, 0.04) 0px 14px 28px, ' +
					'rgba(0, 0, 0, 0.05) 0px 23px 52px'
			},
			transitionDuration: {
				fast: '150ms',
				normal: '200ms',
				slow: '300ms'
			},
			letterSpacing: {
				tight: '-0.02em',
				tighter: '-0.025em'
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
