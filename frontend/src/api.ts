export type DrugKind = 'pill' | 'liquid';

export interface DrugDto {
	name: string;
	kind: DrugKind;
	amount_per_dose: number;
	duration: number; // days
	amount_per_day: number;
}

export interface MealScheduleDto {
	id: number;
	meal_name: string;
	base_time: string; // HH:MM format
	created_at: string;
}

export interface MealScheduleCreate {
	meal_name: string;
	base_time: string; // HH:MM format
}

export interface MealScheduleUpdate {
	base_time: string; // HH:MM format
}

const BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

async function http<T>(path: string, options?: RequestInit): Promise<T> {
	try {
		const res = await fetch(`${BASE_URL}${path}`, {
			headers: { 'Content-Type': 'application/json', ...(options?.headers || {}) },
			...options,
		});
		if (!res.ok) {
			let errorMessage = res.statusText;
			try {
				const err = await res.json();
				errorMessage = err.detail || err.message || res.statusText;
			} catch {
				// If JSON parsing fails, use status text
			}
			throw new Error(errorMessage);
		}
		return res.json();
	} catch (error) {
		if (error instanceof Error) {
			throw error;
		}
		throw new Error('Network error: Failed to connect to server');
	}
}

export const api = {
	addDrug: (drug: DrugDto) => http<{ message: string }>('/drug', { method: 'POST', body: JSON.stringify(drug) }),
	listDrugs: () => http<DrugDto[]>('/drug'),
	updateDrug: (name: string, drug: DrugDto) => http<{ message: string }>(`/drug/${encodeURIComponent(name)}`, { method: 'PUT', body: JSON.stringify(drug) }),
	deleteDrug: (name: string) => http<{ message: string }>(`/drug/${encodeURIComponent(name)}`, { method: 'DELETE' }),
	
	// Meal schedule endpoints
	getMealSchedules: () => http<MealScheduleDto[]>('/meal-schedules'),
	createMealSchedule: (meal: MealScheduleCreate) => http<{ message: string }>('/meal-schedules', { method: 'POST', body: JSON.stringify(meal) }),
	updateMealSchedule: (mealName: string, meal: MealScheduleUpdate) => http<{ message: string }>(`/meal-schedules/${encodeURIComponent(mealName)}`, { method: 'PUT', body: JSON.stringify(meal) }),
	deleteMealSchedule: (mealName: string) => http<{ message: string }>(`/meal-schedules/${encodeURIComponent(mealName)}`, { method: 'DELETE' }),
};
