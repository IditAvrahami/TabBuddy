/**
 * Timezone conversion utilities for handling local time and UTC time conversion
 */

/**
 * Convert local time (HH:MM format) to UTC time (HH:MM format)
 * @param localTime - Time in HH:MM format (e.g., "20:30")
 * @returns UTC time in HH:MM format (e.g., "17:30")
 */
export const convertLocalTimeToUTC = (localTime: string): string => {
  if (!localTime) return localTime;
  
  // Create a date object for today with the local time
  const today = new Date();
  const [hours, minutes] = localTime.split(':').map(Number);
  const localDate = new Date(today.getFullYear(), today.getMonth(), today.getDate(), hours, minutes);
  
  // Get timezone offset in hours
  const offsetHours = localDate.getTimezoneOffset() / 60;
  
  // Convert to UTC by adding the offset (offset is negative for positive timezones)
  const utcHours = (hours + offsetHours + 24) % 24;
  const utcMinutes = minutes;
  
  // Return in HH:MM format
  return utcHours.toString().padStart(2, '0') + ':' + 
         utcMinutes.toString().padStart(2, '0');
};

/**
 * Convert UTC time (HH:MM format) to local time (HH:MM format)
 * @param utcTime - UTC time in HH:MM format (e.g., "17:30")
 * @returns Local time in HH:MM format (e.g., "20:30")
 */
export const convertUTCToLocalTime = (utcTime: string): string => {
  if (!utcTime) return utcTime;
  
  // Create a date object for today to get timezone offset
  const today = new Date();
  const [hours, minutes] = utcTime.split(':').map(Number);
  
  // Get timezone offset in hours
  const offsetHours = today.getTimezoneOffset() / 60;
  
  // Convert to local time by subtracting the offset (offset is negative for positive timezones)
  const localHours = (hours - offsetHours + 24) % 24;
  const localMinutes = minutes;
  
  // Return in HH:MM format
  return localHours.toString().padStart(2, '0') + ':' + 
         localMinutes.toString().padStart(2, '0');
};

/**
 * Format time with timezone information for display
 * @param utcTime - UTC time in HH:MM format
 * @param showUTC - Whether to show UTC indicator
 * @returns Formatted time string
 */
export const formatTimeWithTimezone = (utcTime: string, showUTC: boolean = false): string => {
  if (!utcTime) return utcTime;
  
  const localTime = convertUTCToLocalTime(utcTime);
  const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
  const offset = new Date().getTimezoneOffset();
  const offsetHours = Math.abs(offset) / 60;
  const offsetSign = offset <= 0 ? '+' : '-';
  
  if (showUTC) {
    return `${utcTime} UTC (${localTime} ${timezone})`;
  }
  
  return `${localTime} (${timezone})`;
};

/**
 * Get current timezone offset in hours
 * @returns Timezone offset in hours (e.g., 4 for UTC+4)
 */
export const getTimezoneOffset = (): number => {
  return -new Date().getTimezoneOffset() / 60;
};

/**
 * Get timezone name
 * @returns Timezone name (e.g., "Asia/Jerusalem")
 */
export const getTimezoneName = (): string => {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
};
