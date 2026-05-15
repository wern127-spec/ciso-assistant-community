import { BASE_API_URL } from '$lib/utils/constants';
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch, params }) => {
	const res = await fetch(
		`${BASE_API_URL}/business-continuity/business-services/${params.id}/overview/`
	);

	if (!res.ok) {
		throw error(res.status, `Failed to load business service overview (${res.status})`);
	}

	const overview = await res.json();

	return {
		overview,
		title: overview?.name ?? 'Business service'
	};
};
