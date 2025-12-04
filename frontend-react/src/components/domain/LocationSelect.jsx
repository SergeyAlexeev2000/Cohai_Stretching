import React from 'react';

export function LocationSelect({ locations, value, onChange }) {
  function handleChange(e) {
    const id = Number(e.target.value);
    onChange(id || null);
  }

  return (
    <div className="mb-6">
      <select
        value={value ?? ''}
        onChange={handleChange}
        className="w-full max-w-sm rounded-md border border-neutral-600 bg-neutral-900 px-3 py-2
                   text-sm focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
      >
        {locations.map(loc => (
          <option key={loc.id} value={loc.id}>
            {loc.name}
          </option>
        ))}
      </select>
    </div>
  );
}

