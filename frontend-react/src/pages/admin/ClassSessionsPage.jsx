// src/pages/admin/ClassSessionsPage.jsx
import React, { useEffect, useMemo, useState } from "react";
import { useAuth } from "../../context/AuthContext.jsx";
import { adminRequest } from "../../api/adminRequest.js";

function fmtTime(t) {
  // API может вернуть "HH:MM:SS" или "HH:MM"
  if (!t) return "—";
  return String(t).slice(0, 5);
}

const WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];

export default function ClassSessionsPage() {
  const { token } = useAuth();

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // базовые фильтры (A-версия)
  const [locationId, setLocationId] = useState("");
  const [programTypeId, setProgramTypeId] = useState("");
  const [trainerId, setTrainerId] = useState("");
  const [includeInactive, setIncludeInactive] = useState(false);

  const params = useMemo(() => {
    const p = {};
    if (locationId) p.location_id = Number(locationId);
    if (programTypeId) p.program_type_id = Number(programTypeId);
    if (trainerId) p.trainer_id = Number(trainerId);
    if (includeInactive) p.include_inactive = true;
    return p;
  }, [locationId, programTypeId, trainerId, includeInactive]);

  const load = async () => {
    if (!token) return;

    setLoading(true);
    setError(null);
    try {
      const data = await adminRequest("/admin/class-sessions", {
        token,
        method: "GET",
        params,
      });

      // На всякий случай: API может вернуть массив или объект с items
      const arr = Array.isArray(data) ? data : Array.isArray(data?.items) ? data.items : [];
      setItems(arr);
    } catch (e) {
      setError(e?.message || "Не удалось загрузить расписание");
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, params]);

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">Расписание</h1>
          <p className="text-sm text-neutral-400">
            Список class sessions (A): просмотр + фильтры + обновить.
          </p>
        </div>

        <button
          onClick={load}
          className="rounded-md border border-neutral-700 px-3 py-2 text-sm hover:border-pink-500"
          disabled={loading}
        >
          {loading ? "Обновляю..." : "Обновить"}
        </button>
      </div>

      {/* Фильтры */}
      <div className="rounded-xl border border-neutral-800 bg-neutral-950/40 p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <div>
            <label className="block text-xs text-neutral-400 mb-1">Локация ID</label>
            <input
              value={locationId}
              onChange={(e) => setLocationId(e.target.value)}
              className="w-full rounded-md border border-neutral-800 bg-neutral-950 px-3 py-2 text-sm"
              placeholder="например: 1"
              inputMode="numeric"
            />
          </div>

          <div>
            <label className="block text-xs text-neutral-400 mb-1">ProgramType ID</label>
            <input
              value={programTypeId}
              onChange={(e) => setProgramTypeId(e.target.value)}
              className="w-full rounded-md border border-neutral-800 bg-neutral-950 px-3 py-2 text-sm"
              placeholder="например: 2"
              inputMode="numeric"
            />
          </div>

          <div>
            <label className="block text-xs text-neutral-400 mb-1">Trainer ID</label>
            <input
              value={trainerId}
              onChange={(e) => setTrainerId(e.target.value)}
              className="w-full rounded-md border border-neutral-800 bg-neutral-950 px-3 py-2 text-sm"
              placeholder="например: 10"
              inputMode="numeric"
            />
          </div>

          <div className="flex items-end">
            <label className="inline-flex items-center gap-2 text-sm text-neutral-200">
              <input
                type="checkbox"
                checked={includeInactive}
                onChange={(e) => setIncludeInactive(e.target.checked)}
              />
              показывать неактивные
            </label>
          </div>
        </div>
      </div>

      {error && <div className="text-sm text-red-400 wrap-break-words">Ошибка: {error}</div>}

      {/* Таблица */}
      <div className="rounded-xl border border-neutral-800 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-neutral-900/60 text-neutral-300">
            <tr>
              <th className="text-left p-3">ID</th>
              <th className="text-left p-3">День</th>
              <th className="text-left p-3">Время</th>
              <th className="text-left p-3">Локация</th>
              <th className="text-left p-3">Program</th>
              <th className="text-left p-3">Trainer</th>
              <th className="text-left p-3">Мест</th>
              <th className="text-left p-3">Статус</th>
            </tr>
          </thead>

          <tbody>
            {items.map((s) => {
              const wd = Number.isInteger(s.weekday) ? WEEKDAYS[s.weekday] : "—";
              const time = `${fmtTime(s.start_time)}–${fmtTime(s.end_time)}`;

              return (
                <tr key={s.id} className="border-t border-neutral-800">
                  <td className="p-3">{s.id}</td>
                  <td className="p-3">{wd}</td>
                  <td className="p-3">{time}</td>
                  <td className="p-3">{s.location_id ?? "—"}</td>
                  <td className="p-3">{s.program_type_id ?? "—"}</td>
                  <td className="p-3">{s.trainer_id ?? "—"}</td>
                  <td className="p-3">{s.capacity ?? "—"}</td>
                  <td className="p-3">
                    {s.is_active ? (
                      <span className="text-green-400">активно</span>
                    ) : (
                      <span className="text-neutral-500">неактивно</span>
                    )}
                  </td>
                </tr>
              );
            })}

            {!loading && items.length === 0 && (
              <tr>
                <td className="p-4 text-neutral-400" colSpan={8}>
                  Пусто (или фильтры слишком строгие).
                </td>
              </tr>
            )}

            {loading && (
              <tr>
                <td className="p-4 text-neutral-400" colSpan={8}>
                  Загрузка...
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
