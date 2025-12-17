// src/pages/admin/LeadsPage.jsx
import React, { useEffect, useMemo, useState } from "react";
import { useAuth } from "../../context/AuthContext.jsx";
import { adminRequest } from "../../api/adminRequest.js";

export default function LeadsPage() {
  const { token } = useAuth();

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState(null);

  // фильтры (под GET /admin/leads) :contentReference[oaicite:9]{index=9}
  const [q, setQ] = useState("");
  const [isProcessed, setIsProcessed] = useState(""); // "", "true", "false"

  const params = useMemo(() => {
    return {
      q: q || undefined,
      is_processed:
        isProcessed === ""
          ? undefined
          : isProcessed === "true",
    };
  }, [q, isProcessed]);

  async function load() {
    setLoading(true);
    setErr(null);
    try {
      const data = await adminRequest("/admin/leads", { token, params });
      setItems(Array.isArray(data) ? data : []);
    } catch (e) {
      setErr(e.message || "Ошибка загрузки");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, params]);

  async function markProcessed(id) {
    try {
      // PATCH /admin/leads/{id}/process :contentReference[oaicite:10]{index=10}
      const updated = await adminRequest(`/admin/leads/${id}/process`, {
        token,
        method: "PATCH",
      });
      setItems((prev) => prev.map((x) => (x.id === id ? updated : x)));
    } catch (e) {
      alert(e.message || "Не удалось обновить");
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-end justify-between gap-3 flex-wrap">
        <div>
          <h1 className="text-2xl font-semibold">Заявки</h1>
          <div className="text-sm text-neutral-400">
            Фильтры + пометка “обработано”.
          </div>
        </div>

        <button
          type="button"
          onClick={load}
          className="text-sm px-3 py-2 rounded-md border border-neutral-700 hover:border-pink-500 hover:text-pink-400 transition-colors"
        >
          Обновить
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="md:col-span-2">
          <label className="block text-xs text-neutral-400 mb-1">Поиск (имя/телефон)</label>
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            className="w-full rounded-md border border-neutral-700 bg-neutral-900 px-3 py-2 text-sm text-white"
            placeholder="например: +3736 или 'Ana'"
          />
        </div>

        <div>
          <label className="block text-xs text-neutral-400 mb-1">Обработано</label>
          <select
            value={isProcessed}
            onChange={(e) => setIsProcessed(e.target.value)}
            className="w-full rounded-md border border-neutral-700 bg-neutral-900 px-3 py-2 text-sm text-white"
          >
            <option value="">Все</option>
            <option value="false">Не обработано</option>
            <option value="true">Обработано</option>
          </select>
        </div>
      </div>

      {err && (
        <div className="text-sm text-red-400 border border-red-900/40 bg-red-950/20 rounded-md p-3">
          {err}
        </div>
      )}

      <div className="border border-neutral-800 rounded-xl overflow-hidden">
        <div className="grid grid-cols-12 gap-2 px-3 py-2 text-xs text-neutral-400 bg-neutral-900/60 border-b border-neutral-800">
          <div className="col-span-1">ID</div>
          <div className="col-span-4">Имя</div>
          <div className="col-span-3">Телефон</div>
          <div className="col-span-2">Создан</div>
          <div className="col-span-2 text-right">Действия</div>
        </div>

        {loading ? (
          <div className="p-4 text-sm text-neutral-300">Загрузка…</div>
        ) : items.length === 0 ? (
          <div className="p-4 text-sm text-neutral-400">Пусто.</div>
        ) : (
          items.map((x) => (
            <div
              key={x.id}
              className="grid grid-cols-12 gap-2 px-3 py-2 text-sm border-b border-neutral-800 last:border-b-0"
            >
              <div className="col-span-1 text-neutral-400">{x.id}</div>
              <div className="col-span-4">
                <div className="font-medium">{x.full_name ?? "—"}</div>
                <div className="text-xs text-neutral-500">
                  {x.is_processed ? "✅ обработано" : "🕒 не обработано"}
                </div>
              </div>
              <div className="col-span-3 text-neutral-200">{x.phone ?? "—"}</div>
              <div className="col-span-2 text-neutral-400 text-xs">
                {x.created_at ? new Date(x.created_at).toLocaleString() : "—"}
              </div>
              <div className="col-span-2 flex justify-end">
                {!x.is_processed && (
                  <button
                    type="button"
                    onClick={() => markProcessed(x.id)}
                    className="text-xs px-2 py-1 rounded-md border border-neutral-700 hover:border-pink-500 hover:text-pink-400 transition-colors"
                  >
                    Обработано
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
