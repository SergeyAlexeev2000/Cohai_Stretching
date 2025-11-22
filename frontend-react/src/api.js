const API_BASE = 'http://localhost:8000/api/v1';

export async function fetchLocations() {
  const res = await fetch(`${API_BASE}/locations`);
  if (!res.ok) throw new Error('Failed to load locations');
  return res.json();
}

export async function fetchProgramTypes() {
  const res = await fetch(`${API_BASE}/program-types`);
  if (!res.ok) throw new Error('Failed to load program types');
  return res.json();
}

export async function fetchSchedule(locationId) {
  const res = await fetch(`${API_BASE}/schedule?location_id=${locationId}`);
  if (!res.ok) throw new Error('Failed to load schedule');
  return res.json();
}

export async function fetchMemberships(locationId) {
  const res = await fetch(`${API_BASE}/memberships?location_id=${locationId}`);
  if (!res.ok) throw new Error('Failed to load memberships');
  return res.json();
}

export async function createGuestVisit(payload) {
  const res = await fetch(`${API_BASE}/leads/guest-visit`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Failed to create lead: ${text}`);
  }
  return res.json();
}