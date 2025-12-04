// src/components/LeadForm.jsx
import React, { useEffect, useState } from 'react';
import {
  getLocations,
  getProgramTypes,
  createLead,
} from "../../api.js";


export function LeadForm() {
  const [locations, setLocations] = useState([]);
  const [programTypes, setProgramTypes] = useState([]);

  const [form, setForm] = useState({
    full_name: '',
    email: '',
    phone: '',
    location_id: '',
    program_type_id: '',
    notes: '',
  });

  const [loading, setLoading] = useState(true);
  const [submitStatus, setSubmitStatus] = useState('idle'); // idle | submitting | success | error
  const [error, setError] = useState('');

  // Загрузка локаций и направлений
  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const [locs, types] = await Promise.all([
          getLocations(),
          getProgramTypes(),
        ]);

        if (cancelled) return;

        setLocations(locs);
        setProgramTypes(types);

        // Если локация ещё не выбрана — выставим первую по умолчанию
        if (locs.length && !form.location_id) {
          setForm((f) => ({ ...f, location_id: String(locs[0].id) }));
        }
      } catch (e) {
        console.error(e);
        if (!cancelled) {
          setError('Не удалось загрузить данные. Попробуйте позже.');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');

    if (!form.full_name.trim()) {
      setError('Пожалуйста, укажите имя.');
      return;
    }
    if (!form.location_id) {
      setError('Пожалуйста, выберите локацию.');
      return;
    }

    setSubmitStatus('submitting');
    try {
      const payload = {
        full_name: form.full_name.trim(),
        email: form.email || null,
        phone: form.phone || null,
        location_id: Number(form.location_id),
        program_type_id: form.program_type_id
          ? Number(form.program_type_id)
          : null,
        notes: form.notes || null,
      };

      await createLead(payload);

      setSubmitStatus('success');
      // очищаем только "второстепенные" поля, чтобы не вводить имя заново
      setForm((f) => ({
        ...f,
        email: '',
        phone: '',
        notes: '',
      }));
    } catch (e) {
      console.error(e);
      setSubmitStatus('error');
      setError('Не удалось отправить заявку. Попробуйте ещё раз.');
    } finally {
      setSubmitStatus('idle');
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-3 text-sm">
      {loading && (
        <p className="text-neutral-400 text-sm">Загружаем данные...</p>
      )}

      {!loading && (
        <>
          <div className="space-y-1">
            <label className="block text-xs uppercase tracking-wide text-neutral-400">
              Имя и фамилия
            </label>
            <input
              type="text"
              name="full_name"
              value={form.full_name}
              onChange={handleChange}
              className="w-full rounded-md bg-neutral-900 border border-neutral-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pink-500"
              placeholder="Как к вам обращаться"
            />
          </div>

          <div className="grid gap-3 md:grid-cols-2">
            <div className="space-y-1">
              <label className="block text-xs uppercase tracking-wide text-neutral-400">
                Телефон
              </label>
              <input
                type="tel"
                name="phone"
                value={form.phone}
                onChange={handleChange}
                className="w-full rounded-md bg-neutral-900 border border-neutral-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pink-500"
                placeholder="+373 ..."
              />
            </div>

            <div className="space-y-1">
              <label className="block text-xs uppercase tracking-wide text-neutral-400">
                E-mail (необязательно)
              </label>
              <input
                type="email"
                name="email"
                value={form.email}
                onChange={handleChange}
                className="w-full rounded-md bg-neutral-900 border border-neutral-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pink-500"
                placeholder="you@example.com"
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="block text-xs uppercase tracking-wide text-neutral-400">
              Локация
            </label>
            <select
              name="location_id"
              value={form.location_id}
              onChange={handleChange}
              className="w-full rounded-md bg-neutral-900 border border-neutral-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pink-500"
            >
              {locations.map((loc) => (
                <option key={loc.id} value={loc.id}>
                  {loc.name}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-1">
            <label className="block text-xs uppercase tracking-wide text-neutral-400">
              Направление (необязательно)
            </label>
            <select
              name="program_type_id"
              value={form.program_type_id}
              onChange={handleChange}
              className="w-full rounded-md bg-neutral-900 border border-neutral-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pink-500"
            >
              <option value="">Мне подскажут</option>
              {programTypes.map((pt) => (
                <option key={pt.id} value={pt.id}>
                  {pt.name}
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-1">
            <label className="block text-xs uppercase tracking-wide text-neutral-400">
              Комментарий (необязательно)
            </label>
            <textarea
              name="notes"
              value={form.notes}
              onChange={handleChange}
              rows={3}
              className="w-full rounded-md bg-neutral-900 border border-neutral-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pink-500 resize-none"
              placeholder="Уровень, пожелания по времени, формат..."
            />
          </div>

          {error && (
            <p className="text-xs text-red-400">
              {error}
            </p>
          )}
          {submitStatus === 'success' && !error && (
            <p className="text-xs text-emerald-400">
              Заявка отправлена! Мы свяжемся с вами в ближайшее время.
            </p>
          )}

          <button
            type="submit"
            disabled={submitStatus === 'submitting' || loading}
            className="
                      w-full rounded-md px-4 py-2 text-sm font-semibold
                     bg-pink-600 hover:bg-pink-500
                     disabled:bg-pink-900 disabled:text-neutral-400
                      transition duration-150 ease-out
                      transform hover:-translate-y-0.5 active:translate-y-0
                      "
          >
            {submitStatus === 'submitting'
              ? 'Отправляем...'
              : 'Записаться на пробное'}
          </button>
        </>
      )}
    </form>
  );
}
