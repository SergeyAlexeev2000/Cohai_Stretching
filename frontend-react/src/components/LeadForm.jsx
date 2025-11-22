import React, { useState } from 'react';

export function LeadForm({ locationId, programTypes, onSubmit }) {
  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    program_type_id: programTypes[0]?.id ?? null,
  });

  function handleChange(e) {
    const { name, value } = e.target;
    setForm(prev => ({
      ...prev,
      [name]:
        name === 'program_type_id'
          ? Number(value)
          : value,
    }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    if (!locationId) return;

    onSubmit({
      ...form,
      location_id: locationId,
    });
  }

  const disabled = !locationId || !form.first_name || !form.phone;

  return (
    <form onSubmit={handleSubmit} className="card max-w-lg">
      <div className="space-y-3">
        <input
          type="text"
          name="first_name"
          placeholder="Имя"
          value={form.first_name}
          onChange={handleChange}
          className="w-full rounded-md border border-neutral-600 bg-neutral-900 px-3 py-2 text-sm
                     focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
        />

        <input
          type="text"
          name="last_name"
          placeholder="Фамилия"
          value={form.last_name}
          onChange={handleChange}
          className="w-full rounded-md border border-neutral-600 bg-neutral-900 px-3 py-2 text-sm
                     focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
        />

        <input
          type="email"
          name="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
          className="w-full rounded-md border border-neutral-600 bg-neutral-900 px-3 py-2 text-sm
                     focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
        />

        <input
          type="text"
          name="phone"
          placeholder="Телефон"
          value={form.phone}
          onChange={handleChange}
          className="w-full rounded-md border border-neutral-600 bg-neutral-900 px-3 py-2 text-sm
                     focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
        />

        <div className="mt-2">
          <label className="block text-sm text-neutral-300 mb-1">
            Тип программы:
          </label>
          <select
            name="program_type_id"
            value={form.program_type_id ?? ''}
            onChange={handleChange}
            className="w-full rounded-md border border-neutral-600 bg-neutral-900 px-3 py-2 text-sm
                       focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400"
          >
            {programTypes.map(pt => (
              <option key={pt.id} value={pt.id}>
                {pt.name}
              </option>
            ))}
          </select>
        </div>

        {!locationId && (
          <p className="text-sm text-amber-400 mt-1">
            Сначала выберите локацию выше.
          </p>
        )}

        <button
          type="submit"
          disabled={disabled}
          className={`mt-4 inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium
                     transition
                     ${disabled
                       ? 'bg-neutral-700 text-neutral-400 cursor-not-allowed'
                       : 'bg-emerald-500 hover:bg-emerald-400 text-black'
                     }`}
        >
          Отправить
        </button>
      </div>
    </form>
  );
}

