// src/api.js

// Базовый URL бэкенда.
// Ожидаем, что VITE_API_BASE_URL = 'http://localhost:8000' (БЕЗ /api/v1).
// На проде можно будет подставить другой домен.
const RAW_BASE =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

// убираем возможный слеш в конце
const BASE = RAW_BASE.replace(/\/+$/, '');

// Все публичные ручки — под /public/...
// Итого будет: http://localhost:8000/public/...
const API_BASE = `${BASE}/public`;

// Общий helper для запросов
async function request(path, options = {}) {
  const res = await fetch(API_BASE + path, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!res.ok) {
    let message;
    try {
      message = await res.text();
    } catch {
      message = res.statusText;
    }
    throw new Error(message || `HTTP ${res.status}`);
  }

  return res.json();
}

// ==== Публичные API-функции по плану ====
// План: getLocations() → GET /public/locations
//       getProgramTypes() → GET /public/program-types
//       getMemberships(params) → GET /public/memberships
//       getSchedule(params) → GET /public/schedule
//       createLead(payload) → POST /public/leads

// GET /public/locations
export function getLocations() {
  return request('/locations');
}

// GET /public/program-types
export function getProgramTypes() {
  return request('/program-types');
}

// GET /public/memberships[?query...]
export function getMemberships(queryString = '') {
  return request(`/memberships${queryString}`);
}

// GET /public/schedule[?query...]
export function getSchedule(queryString = '') {
  return request(`/schedule${queryString}`);
}

// POST /public/leads/guest-visit
export function createLead(payload) {
  // Пока у нас на бэке есть только guest-visit,
  // поэтому универсальный createLead бьёт туда же.
  return request('/leads/guest-visit', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

// ==== ВРЕМЕННАЯ ОБРАТНАЯ СОВМЕСТИМОСТЬ ====
// Чтобы старые компоненты (из старого App.jsx) не упали до полной миграции.

export const fetchLocations = getLocations;
export const fetchProgramTypes = getProgramTypes;

export function fetchSchedule(locationId) {
  // старый интерфейс: fetchSchedule(locationId)
  const qs = locationId ? `?location_id=${locationId}` : '';
  return getSchedule(qs);
}

export function fetchMemberships(locationId) {
  const qs = locationId ? `?location_id=${locationId}` : '';
  return getMemberships(qs);
}

export function createGuestVisit(payload) {
  // старое имя → пока та же ручка
  return createLead(payload);
}
