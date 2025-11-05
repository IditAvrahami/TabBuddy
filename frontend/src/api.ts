export type DrugKind = 'pill' | 'liquid';
export type DependencyType = 'absolute' | 'meal' | 'drug' | 'independent';

export interface DrugDto {
	id: number;
	name: string;
	kind: DrugKind;
	amount_per_dose: number;
	frequency_per_day: number;
	start_date: string; // YYYY-MM-DD format
	end_date?: string; // YYYY-MM-DD format
	dependency_type: DependencyType;
	absolute_time?: string; // HH:MM format
	meal_schedule_id?: number;
	meal_offset_minutes?: number;
	meal_timing?: 'before' | 'after';
	depends_on_drug_id?: number;
	drug_offset_minutes?: number;
	is_active: boolean;
	created_at: string;
}

export interface DrugCreateDto {
  name: string;
  kind: DrugKind;
  amount_per_dose: number;
  frequency_per_day: number;
  start_date: string; // YYYY-MM-DD format
  end_date?: string; // YYYY-MM-DD format
  dependency_type: DependencyType;
  absolute_time?: string; // HH:MM format
  meal_schedule_id?: number;
  meal_offset_minutes?: number;
  meal_timing?: 'before' | 'after';
  depends_on_drug_id?: number;
  drug_offset_minutes?: number;
}

// Notification types
export interface NotificationDto {
  schedule_id: number;
  drug_id: number;
  drug_name: string;
  kind: DrugKind;
  amount_per_dose: number;
  dependency_type: string;
  scheduled_time: string; // ISO datetime string
}

export interface SnoozeRequest {
  minutes: number;
  day: string; // YYYY-MM-DD format
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
	addDrug: (drug: DrugCreateDto) => http<{ message: string }>('/drug', { method: 'POST', body: JSON.stringify(drug) }),
	listDrugs: () => http<DrugDto[]>('/drug'),
	updateDrug: (drugId: number, drug: DrugCreateDto) => http<{ message: string }>(`/drug-id/${drugId}`, { method: 'PUT', body: JSON.stringify(drug) }),
	deleteDrug: (drugId: number) => http<{ message: string }>(`/drug-id/${drugId}`, { method: 'DELETE' }),
	
	// Meal schedule endpoints
	getMealSchedules: () => http<MealScheduleDto[]>('/meal-schedules'),
	createMealSchedule: (meal: MealScheduleCreate) => http<{ message: string }>('/meal-schedules', { method: 'POST', body: JSON.stringify(meal) }),
	updateMealSchedule: (mealName: string, meal: MealScheduleUpdate) => http<{ message: string }>(`/meal-schedules/${encodeURIComponent(mealName)}`, { method: 'PUT', body: JSON.stringify(meal) }),
	deleteMealSchedule: (mealName: string) => http<{ message: string }>(`/meal-schedules/${encodeURIComponent(mealName)}`, { method: 'DELETE' }),
	
	// Notification endpoints
	getNotifications: (day: string = new Date().toISOString().split('T')[0]) => http<NotificationDto[]>(`/notifications?day=${day}`),
	snoozeNotification: (scheduleId: number, minutes: number, day: string = new Date().toISOString().split('T')[0]) => {
		const payload: SnoozeRequest = { minutes, day };
		return http<void>(`/notifications/${scheduleId}/snooze`, { method: 'POST', body: JSON.stringify(payload) });
	},
	dismissNotification: (scheduleId: number, day: string = new Date().toISOString().split('T')[0]) => {
		return http<void>(`/notifications/${scheduleId}/dismiss`, { method: 'POST', body: JSON.stringify({ day }) });
	},
};
