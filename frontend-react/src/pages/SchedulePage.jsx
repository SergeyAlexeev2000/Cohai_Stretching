// src/pages/SchedulePage.jsx
import React, { useEffect, useMemo, useState } from 'react';
import {
  getLocations,
  getProgramTypes,
  getSchedule,
} from '../api.js';
import { Card } from '../components/ui/Card.jsx';

const WEEKDAYS = [
  'Понедельник',
  'Вторник',
  'Среда',
  'Четверг',
  'Пятница',
  'Суббота',
  'Воскресенье',
];

export default function SchedulePage() {
  const [locations, setLocations] = useState([]);
  const [programTypes, setProgramTypes] = useState([]);
  const [selectedLocationId, setSelectedLocationId] = useState('');
  const [selectedProgramTypeId, setSelectedProgramTypeId] = useState('');
  const [schedule, setSchedule] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // мапа id → program type
  const programTypesById = useMemo(() => {
    const map = {};
    for (const pt of programTypes) {
      map[pt.id] = pt;
    }
    return map;
  }, [programTypes]);

  // начальная загрузка
  useEffect(() => {
    let cancelled = false;

    async function loadInitial() {
      try {
        const [locs, types] = await Promise.all([
          getLocations(),
          getProgramTypes(),
        ]);

        if (cancelled) return;

        setLocations(locs);
        setProgramTypes(types);

        if (locs.length) {
          setSelectedLocationId(String(locs[0].id));
        }
      } catch (e) {
        console.error(e);
        if (!cancelled) setError('Не удалось загрузить данные.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    loadInitial();
    return () => {
      cancelled = true;
    };
  }, []);

  // подзагрузка расписания при смене фильтров
  useEffect(() => {
    if (!selectedLocationId) return;

    let cancelled = false;

    async function loadSchedule() {
      setError('');
      try {
        const params = new URLSearchParams();
        params.set('location_id', selectedLocationId);
        if (selectedProgramTypeId) {
          params.set('program_type_id', selectedProgramTypeId);
        }

        const data = await getSchedule('?' + params.toString());
        if (!cancelled) {
          setSchedule(data);
        }
      } catch (e) {
        console.error(e);
        if (!cancelled) {
          setError('Не удалось загрузить расписание.');
          setSchedule([]);
        }
      }
    }

    loadSchedule();
    return () => {
      cancelled = true;
    };
  }, [selectedLocationId, selectedProgramTypeId]);

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold">Расписание занятий</h1>
        <p className="text-neutral-300">
          Выберите студию и направление — и посмотрите, в какие дни и время
          проходят занятия.
        </p>
      </header>

      {/* Фильтры */}
      <section className="grid gap-4 md:grid-cols-2">
        <div className="space-y-1">
          <label className="block text-xs uppercase tracking-wide text-neutral-400">
            Локация
          </label>
          <select
            className="w-full rounded-md bg-neutral-900 border border-neutral-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pink-500"
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

        <div className="space-y-1">
          <label className="block text-xs uppercase tracking-wide text-neutral-400">
            Направление
          </label>
          <select
            className="w-full rounded-md bg-neutral-900 border border-neutral-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-pink-500"
            value={selectedProgramTypeId}
            onChange={(e) => setSelectedProgramTypeId(e.target.value)}
          >
            <option value="">Все направления</option>
            {programTypes.map((pt) => (
              <option key={pt.id} value={pt.id}>
                {pt.name}
              </option>
            ))}
          </select>
        </div>
      </section>

      {error && <p className="text-red-400 text-sm">{error}</p>}

      {/* Список занятий */}
      <section className="space-y-3">
        {schedule.length === 0 && !error && (
          <p className="text-neutral-400 text-sm">
            Нет занятий для выбранных фильтров.
          </p>
        )}

        <div className="grid gap-4 md:grid-cols-2">
          {schedule.map((s) => {
            const pt = programTypesById[s.program_type_id];
            const title = pt ? pt.name : `Программа #${s.program_type_id}`;

            const weekdayName =
              (typeof s.weekday === 'number'
                ? WEEKDAYS[s.weekday] ?? `День ${s.weekday}`
                : null) || '';

            return (
              <Card
                key={s.id}
                title={title}
                subtitle={weekdayName}
              >
                <p>
                  <span className="text-neutral-400">Время: </span>
                  {s.start_time} — {s.end_time}
                </p>
                <p>
                  <span className="text-neutral-400">Длительность: </span>
                  {s.duration_minutes} мин
                </p>
                <p>
                  <span className="text-neutral-400">Тренер: </span>
                  #{s.trainer_id}
                </p>
                <p>
                  <span className="text-neutral-400">Мест: </span>
                  {s.capacity}
                </p>
              </Card>
            );
          })}
        </div>
      </section>
    </div>
  );
}
