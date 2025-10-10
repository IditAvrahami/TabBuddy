export type DrugKind = 'pill' | 'liquid';

export interface DrugDto {
	name: string;
	kind: DrugKind;
	amount_per_dose: number;
	duration: number; // days
	amount_per_day: number;
}

const BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

async function http<T>(path: string, options?: RequestInit): Promise<T> {
	const res = await fetch(`${BASE_URL}${path}`, {
		headers: { 'Content-Type': 'application/json', ...(options?.headers || {}) },
		...options,
	});
	if (!res.ok) {
		const err = await res.json().catch(() => ({}));
		throw new Error(err.detail || res.statusText);
	}
	return res.json();
}

export const api = {
	addDrug: (drug: DrugDto) => http<{ message: string }>('/drug', { method: 'POST', body: JSON.stringify(drug) }),
	listDrugs: () => http<DrugDto[]>('/drug'),
	updateDrug: (name: string, drug: DrugDto) => http<{ message: string }>(`/drug/${encodeURIComponent(name)}`, { method: 'PUT', body: JSON.stringify(drug) }),
	deleteDrug: (name: string) => http<{ message: string }>(`/drug/${encodeURIComponent(name)}`, { method: 'DELETE' }),
};
