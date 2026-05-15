<script lang="ts">
	import Anchor from '$lib/components/Anchor/Anchor.svelte';
	import MarkdownRenderer from '$lib/components/MarkdownRenderer.svelte';
	import type { PageData } from './$types';

	interface Props {
		data: PageData;
	}

	let { data }: Props = $props();
	const o = $derived(data.overview);

	const criticalityColor: Record<string, string> = {
		critical: 'bg-red-100 text-red-800',
		high: 'bg-orange-100 text-orange-800',
		medium: 'bg-yellow-100 text-yellow-800',
		low: 'bg-green-100 text-green-800'
	};
	const statusColor: Record<string, string> = {
		draft: 'bg-gray-100 text-gray-700',
		active: 'bg-green-100 text-green-800',
		deprecated: 'bg-gray-200 text-gray-600',
		approved: 'bg-green-100 text-green-800',
		archived: 'bg-gray-200 text-gray-600'
	};
	function resultIcon(result: string): { icon: string; color: string } {
		if (result === 'success') return { icon: 'fa-circle-check', color: 'text-green-600' };
		if (result === 'failure') return { icon: 'fa-circle-xmark', color: 'text-red-600' };
		return { icon: 'fa-circle-exclamation', color: 'text-yellow-600' };
	}
</script>

<div class="flex flex-col space-y-4 p-4">
	<!-- 1. Domain (breadcrumb / badge) -->
	<div class="flex items-center justify-between">
		<div class="flex items-center space-x-2 text-sm">
			<i class="fa-solid fa-sitemap text-gray-500"></i>
			<span class="text-gray-500">Domain:</span>
			{#each o.domain?.path ?? [o.domain?.name] as part, i}
				<span class="font-medium">{part}</span>
				{#if i < (o.domain?.path?.length ?? 1) - 1}<span class="text-gray-400">/</span>{/if}
			{/each}
		</div>
		<Anchor href="/business-services" class="text-sm text-primary-700 hover:text-primary-500">
			<i class="fa-solid fa-arrow-left mr-1"></i>Back to list
		</Anchor>
	</div>

	<div class="flex items-center space-x-3">
		<h1 class="text-2xl font-bold">{o.name}</h1>
		{#if o.ref_id}<span class="text-gray-500">({o.ref_id})</span>{/if}
		<span class="px-2 py-1 rounded text-xs font-semibold {statusColor[o.status] ?? 'bg-gray-100'}"
			>{o.status_display}</span
		>
	</div>
	{#if o.description}<p class="text-gray-600">{o.description}</p>{/if}

	<!-- 2. Service parameters -->
	<section class="card bg-white shadow-sm p-4">
		<h2 class="text-lg font-semibold mb-3">Service parameters</h2>
		<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
			<div>
				<div class="text-xs text-gray-500">Criticality</div>
				<span
					class="px-2 py-1 rounded text-sm font-semibold {criticalityColor[o.criticality] ??
						'bg-gray-100'}">{o.criticality_display}</span
				>
			</div>
			<div>
				<div class="text-xs text-gray-500">RTO (hours)</div>
				<div class="text-lg font-medium">{o.rto_hours ?? '—'}</div>
			</div>
			<div>
				<div class="text-xs text-gray-500">RPO (hours)</div>
				<div class="text-lg font-medium">{o.rpo_hours ?? '—'}</div>
			</div>
			<div>
				<div class="text-xs text-gray-500">MTPD (hours)</div>
				<div class="text-lg font-medium">{o.mtpd_hours ?? '—'}</div>
			</div>
		</div>
		{#if o.owner}
			<div class="mt-3 text-sm"><span class="text-gray-500">Owner:</span> {o.owner}</div>
		{/if}
	</section>

	<!-- 3. Domain impact -->
	<section class="card bg-white shadow-sm p-4">
		<h2 class="text-lg font-semibold mb-3">Domain impact</h2>
		{#if o.domain_impact_description}
			<MarkdownRenderer content={o.domain_impact_description} />
		{:else}
			<p class="text-gray-400 italic">No description provided.</p>
		{/if}
	</section>

	<!-- 4. Assets used -->
	<section class="card bg-white shadow-sm p-4">
		<h2 class="text-lg font-semibold mb-3">Assets used</h2>
		{#if o.assets?.length}
			<table class="w-full text-sm">
				<thead>
					<tr class="text-left border-b text-gray-500">
						<th class="py-2">Asset</th>
						<th class="py-2">Dependency</th>
						<th class="py-2">Impact on service</th>
						<th class="py-2">Recovery procedures</th>
					</tr>
				</thead>
				<tbody>
					{#each o.assets as link}
						<tr class="border-b last:border-0">
							<td class="py-2 font-medium">{link.asset.name}</td>
							<td class="py-2">{link.dependency_type_display}</td>
							<td class="py-2 text-gray-600">{link.asset_impact_description ?? '—'}</td>
							<td class="py-2">
								{#if link.recovery_procedures?.length}
									<div class="flex flex-col">
										{#each link.recovery_procedures as proc}
											<Anchor
												href={`/asset-recovery-procedures`}
												class="text-primary-700 hover:text-primary-500"
												>{proc.name} <span class="text-xs text-gray-400">({proc.procedure_type})</span
												></Anchor
											>
										{/each}
									</div>
								{:else}
									<span class="text-gray-400">—</span>
								{/if}
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		{:else}
			<p class="text-gray-400 italic">No assets linked to this service yet.</p>
		{/if}
	</section>

	<!-- 5. Continuity plans -->
	<section class="card bg-white shadow-sm p-4">
		<h2 class="text-lg font-semibold mb-3">Continuity plan</h2>
		{#if o.continuity_plans?.length}
			<div class="flex flex-col space-y-6">
				{#each o.continuity_plans as plan}
					<div class="border rounded p-4">
						<div class="flex items-center space-x-3 mb-2">
							<h3 class="font-semibold">{plan.name}</h3>
							{#if plan.version}<span class="text-xs text-gray-500">v{plan.version}</span>{/if}
							<span
								class="px-2 py-0.5 rounded text-xs font-semibold {statusColor[plan.status] ??
									'bg-gray-100'}">{plan.status_display}</span
							>
						</div>
						{#if plan.responsible_team}
							<p class="text-sm mb-2">
								<span class="text-gray-500">Responsible team:</span>
								{plan.responsible_team}
							</p>
						{/if}
						{#if plan.scenario}
							<div class="mb-3">
								<div class="text-xs text-gray-500 mb-1">Scenario</div>
								<MarkdownRenderer content={plan.scenario} />
							</div>
						{/if}
						{#if plan.recovery_strategy}
							<div class="mb-3">
								<div class="text-xs text-gray-500 mb-1">Recovery strategy</div>
								<MarkdownRenderer content={plan.recovery_strategy} />
							</div>
						{/if}
						{#if plan.procedure_steps}
							<div class="mb-3">
								<div class="text-xs text-gray-500 mb-1">Procedure steps</div>
								<MarkdownRenderer content={plan.procedure_steps} />
							</div>
						{/if}
						{#if plan.referenced_asset_procedures?.length}
							<div class="text-sm">
								<span class="text-gray-500">Referenced asset procedures:</span>
								{plan.referenced_asset_procedures.map((p) => p.name).join(', ')}
							</div>
						{/if}
					</div>
				{/each}
			</div>
		{:else}
			<p class="text-gray-400 italic">No continuity plan defined for this service yet.</p>
		{/if}
	</section>

	<!-- 6. Test history -->
	<section class="card bg-white shadow-sm p-4">
		<h2 class="text-lg font-semibold mb-3">Test history</h2>
		{#if o.tests?.length}
			<table class="w-full text-sm">
				<thead>
					<tr class="text-left border-b text-gray-500">
						<th class="py-2">Date</th>
						<th class="py-2">Type</th>
						<th class="py-2">Result</th>
						<th class="py-2">Findings</th>
					</tr>
				</thead>
				<tbody>
					{#each o.tests as test}
						<tr class="border-b last:border-0">
							<td class="py-2">{test.test_date}</td>
							<td class="py-2">{test.test_type_display}</td>
							<td class="py-2">
								<span class={resultIcon(test.result).color}>
									<i class="fa-solid {resultIcon(test.result).icon}"></i>
									{test.result_display}
								</span>
							</td>
							<td class="py-2 text-gray-600">{test.findings ?? '—'}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		{:else}
			<p class="text-gray-400 italic">No tests recorded yet.</p>
		{/if}
	</section>

	<!-- 7. Actions -->
	<section class="flex flex-wrap gap-3">
		<Anchor
			href={`/business-services/${o.id}/edit`}
			class="btn preset-filled-primary-500 px-4 py-2 rounded"
		>
			<i class="fa-solid fa-pen mr-1"></i>Edit service
		</Anchor>
		<Anchor
			href="/continuity-plans"
			class="btn preset-tonal px-4 py-2 rounded border"
		>
			<i class="fa-solid fa-plus mr-1"></i>Add continuity plan
		</Anchor>
		<Anchor
			href="/continuity-plan-tests"
			class="btn preset-tonal px-4 py-2 rounded border"
		>
			<i class="fa-solid fa-plus mr-1"></i>Add test
		</Anchor>
	</section>
</div>
