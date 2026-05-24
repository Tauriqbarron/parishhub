<script lang="ts">
	interface Props {
		size?: number;
		variant?: 'light' | 'dark';
		detail?: 'simple' | 'full';
		class?: string;
	}

	let { size = 32, variant = 'light', detail = 'full', class: className = '' }: Props = $props();

	const id = Math.random().toString(36).slice(2, 8); // unique ID for gradient defs
</script>

{#if detail === 'simple'}
	<!-- Simple icon version (mobile / small sizes) -->
	<svg viewBox="0 0 200 200" width={size} height={size} class={className} aria-label="ParishHub">
		<defs>
			<linearGradient id="simpleShield-{id}" x1="0" y1="0" x2="0" y2="1">
				<stop offset="0%" stop-color="#1E293B" />
				<stop offset="100%" stop-color="#0F172A" />
			</linearGradient>
		</defs>
		<!-- Shield -->
		<path
			d="M100,22 L166,54 L166,118 Q166,168 100,186 Q34,168 34,118 L34,54 Z"
			fill="url(#simpleShield-{id})"
			stroke="#D97706"
			stroke-width="3"
		/>
		<!-- Cross vertical -->
		<rect x="95" y="46" width="10" height="52" rx="2" fill="#D97706" />
		<!-- Cross horizontal -->
		<rect x="80" y="58" width="40" height="10" rx="2" fill="#D97706" />
		<!-- Church roof -->
		<path
			d="M78,156 L78,130 L100,112 L122,130 L122,156 Z"
			fill="none"
			stroke="#D97706"
			stroke-width="3"
			stroke-linejoin="round"
		/>
		<!-- Door -->
		<path d="M94,156 L94,144 Q94,138 100,138 Q106,138 106,144 L106,156 Z" fill="#D97706" />
	</svg>
{:else}
	<!-- High-fidelity version (desktop / large sizes) -->
	<svg viewBox="0 0 200 200" width={size} height={size} class={className} aria-label="ParishHub">
		<defs>
			<!-- Shield gradient -->
			<linearGradient id="shield-{id}" x1="0" y1="0" x2="0" y2="1">
				<stop offset="0%" stop-color="#1E293B" />
				<stop offset="100%" stop-color="#0F172A" />
			</linearGradient>
			<!-- Shield inner gradient (warm glow) -->
			<linearGradient id="shieldInner-{id}" x1="0" y1="0" x2="0" y2="1">
				<stop offset="0%" stop-color="#FFFBEB" />
				<stop offset="100%" stop-color="#FEF3C7" />
			</linearGradient>
			<!-- Amber gradient for cross -->
			<linearGradient id="amber-{id}" x1="0" y1="0" x2="0" y2="1">
				<stop offset="0%" stop-color="#F59E0B" />
				<stop offset="50%" stop-color="#D97706" />
				<stop offset="100%" stop-color="#B45309" />
			</linearGradient>
			<!-- Church body gradient -->
			<linearGradient id="church-{id}" x1="0" y1="0" x2="0" y2="1">
				<stop offset="0%" stop-color="#F8FAFC" />
				<stop offset="100%" stop-color="#E2E8F0" />
			</linearGradient>
			<!-- Roof gradient -->
			<linearGradient id="roof-{id}" x1="0" y1="0" x2="0" y2="1">
				<stop offset="0%" stop-color="#475569" />
				<stop offset="100%" stop-color="#334155" />
			</linearGradient>
			<!-- Window glow -->
			<radialGradient id="windowGlow-{id}">
				<stop offset="0%" stop-color="#FEF9C3" />
				<stop offset="100%" stop-color="#FDE68A" />
			</radialGradient>
			<!-- Drop shadow filter -->
			<filter id="shadow-{id}" x="-10%" y="-10%" width="130%" height="130%">
				<feDropShadow dx="0" dy="1" stdDeviation="2" flood-color="#0F172A" flood-opacity="0.15" />
			</filter>
		</defs>

		<!-- Shield body -->
		<path
			d="M100,18 L170,52 L170,120 Q170,172 100,192 Q30,172 30,120 L30,52 Z"
			fill="url(#shield-{id})"
			stroke="none"
			filter="url(#shadow-{id})"
		/>
		<!-- Shield border highlight -->
		<path
			d="M100,18 L170,52 L170,120 Q170,172 100,192 Q30,172 30,120 L30,52 Z"
			fill="none"
			stroke="#D97706"
			stroke-width="2"
		/>
		<!-- Shield inner panel -->
		<path
			d="M100,28 L160,58 L160,118 Q160,164 100,182 Q40,164 40,118 L40,58 Z"
			fill="url(#shieldInner-{id})"
		/>

		<!-- Ornate cross — vertical beam -->
		<rect x="95" y="34" width="10" height="60" rx="2" fill="url(#amber-{id})" />
		<!-- Ornate cross — horizontal beam -->
		<rect x="77" y="50" width="46" height="10" rx="2" fill="url(#amber-{id})" />
		<!-- Cross decorative caps — top -->
		<rect x="91" y="32" width="18" height="6" rx="3" fill="url(#amber-{id})" />
		<!-- Cross decorative caps — left -->
		<rect x="73" y="46" width="8" height="18" rx="3" fill="url(#amber-{id})" />
		<!-- Cross decorative caps — right -->
		<rect x="119" y="46" width="8" height="18" rx="3" fill="url(#amber-{id})" />
		<!-- Cross center jewel -->
		<circle cx="100" cy="55" r="4" fill="#FEF3C7" stroke="#B45309" stroke-width="1" />

		<!-- Church building body -->
		<rect
			x="68"
			y="126"
			width="64"
			height="44"
			rx="2"
			fill="url(#church-{id})"
			stroke="#94A3B8"
			stroke-width="1.5"
		/>
		<!-- Roof -->
		<path
			d="M62,128 L100,102 L138,128 Z"
			fill="url(#roof-{id})"
			stroke="#475569"
			stroke-width="1.5"
			stroke-linejoin="round"
		/>
		<!-- Steeple base -->
		<rect
			x="94"
			y="92"
			width="12"
			height="12"
			fill="url(#church-{id})"
			stroke="#94A3B8"
			stroke-width="1"
		/>
		<!-- Steeple spire -->
		<path
			d="M94,94 L100,72 L106,94 Z"
			fill="url(#roof-{id})"
			stroke="#475569"
			stroke-width="1.5"
			stroke-linejoin="round"
		/>
		<!-- Steeple cross -->
		<line
			x1="100"
			y1="72"
			x2="100"
			y2="64"
			stroke="url(#amber-{id})"
			stroke-width="2.5"
			stroke-linecap="round"
		/>
		<line
			x1="96"
			y1="68"
			x2="104"
			y2="68"
			stroke="url(#amber-{id})"
			stroke-width="2.5"
			stroke-linecap="round"
		/>

		<!-- Stained glass window (arched) -->
		<path
			d="M94,132 Q94,126 100,126 Q106,126 106,132 L106,148 L94,148 Z"
			fill="url(#windowGlow-{id})"
			stroke="#D97706"
			stroke-width="1.2"
		/>
		<!-- Window cross divider -->
		<line x1="100" y1="128" x2="100" y2="148" stroke="#D97706" stroke-width="0.8" />
		<line x1="94" y1="140" x2="106" y2="140" stroke="#D97706" stroke-width="0.8" />

		<!-- Side windows -->
		<rect
			x="74"
			y="136"
			width="10"
			height="14"
			rx="5"
			ry="5"
			fill="url(#windowGlow-{id})"
			stroke="#D97706"
			stroke-width="0.8"
		/>
		<rect
			x="116"
			y="136"
			width="10"
			height="14"
			rx="5"
			ry="5"
			fill="url(#windowGlow-{id})"
			stroke="#D97706"
			stroke-width="0.8"
		/>

		<!-- Front door (arched) -->
		<path
			d="M93,170 L93,158 Q93,150 100,150 Q107,150 107,158 L107,170 Z"
			fill="#7C3AED"
			stroke="#5B21B6"
			stroke-width="1.2"
		/>
		<!-- Door handle -->
		<circle cx="104" cy="162" r="1.2" fill="#D97706" />

		<!-- Steps -->
		<rect
			x="78"
			y="170"
			width="44"
			height="4"
			rx="1"
			fill="#CBD5E1"
			stroke="#94A3B8"
			stroke-width="0.5"
		/>
		<rect
			x="82"
			y="174"
			width="36"
			height="4"
			rx="1"
			fill="#E2E8F0"
			stroke="#94A3B8"
			stroke-width="0.5"
		/>

		<!-- Decorative pillars -->
		<rect
			x="70"
			y="130"
			width="4"
			height="40"
			rx="2"
			fill="#CBD5E1"
			stroke="#94A3B8"
			stroke-width="0.8"
		/>
		<rect
			x="126"
			y="130"
			width="4"
			height="40"
			rx="2"
			fill="#CBD5E1"
			stroke="#94A3B8"
			stroke-width="0.8"
		/>
		<!-- Pillar caps -->
		<rect x="69" y="128" width="6" height="4" rx="1" fill="#94A3B8" />
		<rect x="125" y="128" width="6" height="4" rx="1" fill="#94A3B8" />
	</svg>
{/if}
