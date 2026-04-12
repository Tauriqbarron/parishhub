<script lang="ts">
	interface Props {
		size?: number;
		variant?: 'light' | 'dark';
		class?: string;
	}

	let { size = 32, variant = 'light', class: className = '' }: Props = $props();

	const stroke = variant === 'light' ? '#0F172A' : '#F8FAFC';
</script>

<svg viewBox="0 0 200 200" width={size} height={size} class={className} aria-label="ParishHub">
	<!-- Shield outline -->
	<path
		d="M100,22 L166,54 L166,118 Q166,168 100,186 Q34,168 34,118 L34,54 Z"
		fill="none"
		{stroke}
		stroke-width="5"
	/>
	<!-- Cross vertical -->
	<rect x="96" y="44" width="8" height="52" rx="1" fill="#D97706" />
	<!-- Cross horizontal -->
	<rect x="80" y="58" width="40" height="8" rx="1" fill="#D97706" />
	<!-- House/church roof -->
	<path
		d="M80,156 L80,130 L100,114 L120,130 L120,156 Z"
		fill="none"
		{stroke}
		stroke-width="2.5"
		stroke-linejoin="round"
	/>
	<!-- Chimney cross -->
	<line x1="100" y1="112" x2="100" y2="104" stroke="#D97706" stroke-width="2" />
	<line x1="96" y1="108" x2="104" y2="108" stroke="#D97706" stroke-width="2" />
	<!-- Door -->
	<rect x="96" y="144" width="8" height="12" rx="4" fill="none" {stroke} stroke-width="1.5" />
</svg>
