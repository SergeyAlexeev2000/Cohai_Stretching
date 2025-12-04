// src/pages/PricesPage.jsx
import React, { useEffect, useState } from 'react';
import { getLocations, getMemberships } from '../api.js';
import { Card } from '../components/ui/Card.jsx';

export default function PricesPage() {
  const [locations, setLocations] = useState([]);
  const [selectedLocationId, setSelectedLocationId] = useState('');
  const [memberships, setMemberships] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // начальная загрузка
  useEffect(() => {
    let cancelled = false;

    async function loadInitial() {
      try {
        const locs = await getLocations();
        if (cancelled) return;

        setLocations(locs);
        if (locs.length) {
          setSelectedLocationId(String(locs[0].id));
        }
      } catch (e) {
        console.error(e);
        if (!cancelled) setError('Не удалось загрузить локации.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadInitial();
    return () => {
      cancelled = true;
    };
  }, []);

  // загрузка тарифов при смене локации
  useEffect(() => {
    if (!selectedLocationId) return;

    let cancelled = false;

    async function loadMemberships() {
      setError('');
      try {
        const qs = `?location_id=${selectedLocationId}`;
        const data = await getMemberships(qs);
        if (!cancelled) setMemberships(data);
      } catch (e) {
        console.error(e);
        if (!cancelled) {
          setError('Не удалось загрузить абонементы.');
          setMemberships([]);
        }
      }
    }

    loadMemberships();
    return () => {
      cancelled = true;
    };
  }, [selectedLocationId]);

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold">Цены и абонементы</h1>
        <p className="text-neutral-300">
          Выберите студию, чтобы увидеть доступные абонементы и разовые
          посещения.
        </p>
      </header>

      <section className="space-y-3">
        <div className="space-y-1">
          <label className="block text-xs uppercase tracking-wide text-neutral-400">
            Локация
          </label>
          <select
            className="w-full max-w-md rounded-md bg-neutral-900 border border-neutral-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pink-500"
            value={selectedLocationId}
            onChange={(e) => setSelectedLocationId(e.target.value)}
          >
            {locations.map((loc) => (
              <option key={loc.id} value={loc.id}>
                {loc.name}
              </option>
            ))}
          </select>
        </div>

        {error && <p className="text-red-400 text-sm">{error}</p>}
      </section>

      <section className="space-y-3">
        {memberships.length === 0 && !error && (
          <p className="text-neutral-400 text-sm">
            Для этой локации пока нет активных абонементов.
          </p>
        )}

        <div className="grid gap-4 md:grid-cols-2">
          {memberships.map((m) => (
            <Card
              key={m.id}
              title={m.name}
              subtitle={m.description}
            >
              <p>
                <span className="text-neutral-400">Продолжительность: </span>
                {m.duration_days ?? '—'} дней
              </p>
              <p>
                <span className="text-neutral-400">Цена: </span>
                {m.price} ₽
              </p>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}
