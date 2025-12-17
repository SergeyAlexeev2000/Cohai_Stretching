// src/pages/admin/LocationsPage.jsx
import React, { useEffect, useMemo, useState } from "react";
import { useAuth } from "../../context/AuthContext.jsx";

const API_BASE = ""; // оставляем пустым, чтобы работал vite proxy: /api/...

async function apiFetch(path, { token, method = "GET", body } = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const data = await res.json();
      detail = data?.detail ?? JSON.stringify(data);
    } catch {
      // ignore
    }
    throw new Error(detail);
  }

  // 204 No Content
  if (res.status === 204) return null;
  return res.json();
}

export default function LocationsPage() {
  const { token } = useAuth();

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState(null);
  const [error, setError] = useState("");

  // create/edit form state
  const [editingId, setEditingId] = useState(null);
  const [name, setName] = useState("");
  const [address, setAddress] = useState("");

  const isEditing = useMemo(() => editingId !== null, [editingId]);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const data = await apiFetch("/api/v1/admin/locations", { token });
      setItems(Array.isArray(data) ? data : []);
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function resetForm() {
    setEditingId(null);
    setName("");
    setAddress("");
  }

  async function onSubmit(e) {
    e.preventDefault();
    setError("");

    const payload = {
      name: name.trim(),
      address: address.trim() ? address.trim() : null,
    };

    if (!payload.name) {
      setError("Название локации обязательно.");
      return;
    }

    try {
      if (isEditing) {
        setBusyId(editingId);
        const updated = await apiFetch(`/api/v1/admin/locations/${editingId}`, {
          token,
          method: "PATCH",
          body: payload,
        });
        setItems((prev) => prev.map((x) => (x.id === updated.id ? updated : x)));
      } else {
        setBusyId("create");
        const created = await apiFetch("/api/v1/admin/locations", {
          token,
          method: "POST",
          body: payload,
        });
        setItems((prev) => [created, ...prev]);
      }

      resetForm();
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setBusyId(null);
    }
  }

  function startEdit(loc) {
    setEditingId(loc.id);
    setName(loc.name ?? "");
    setAddress(loc.address ?? "");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function remove(loc) {
    const ok = window.confirm(
      `Удалить локацию "${loc.name}"?\n\nВНИМАНИЕ: если к ней привязаны абонементы/занятия, бэк может вернуть ошибку.`
    );
    if (!ok) return;

    setError("");
    setBusyId(loc.id);
    try {
      await apiFetch(`/api/v1/admin/locations/${loc.id}`, {
        token,
        method: "DELETE",
      });
      setItems((prev) => prev.filter((x) => x.id !== loc.id));
      if (editingId === loc.id) resetForm();
    } catch (e) {
      setError(String(e.message || e));
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Локации</h1>
          <p className="text-sm text-neutral-400">
            Список студий/залов. Создание, редактирование и удаление.
          </p>
        </div>

        <button
          type="button"
          onClick={load}
          className="rounded-md border border-neutral-700 px-3 py-2 text-sm text-neutral-200 hover:border-pink-500 hover:text-white transition-colors"
        >
          Обновить
        </button>
      </div>

      {/* CREATE / EDIT */}
      <form
        onSubmit={onSubmit}
        className="rounded-xl border border-neutral-800 bg-neutral-950/60 p-4 space-y-3"
      >
        <div className="flex items-center justify-between gap-3">
          <div className="text-sm font-medium text-neutral-200">
            {isEditing ? `Редактирование локации #${editingId}` : "Создать локацию"}
          </div>
          {isEditing && (
            <button
              type="button"
              onClick={resetForm}
              className="text-sm text-neutral-400 hover:text-white"
            >
              Отменить
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <label className="space-y-1">
            <div className="text-xs text-neutral-400">Название *</div>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full rounded-md border border-neutral-800 bg-neutral-950 px-3 py-2 text-sm text-neutral-100 outline-none focus:border-pink-500"
              placeholder="например: Cohai – Центр"
            />
          </label>

          <label className="space-y-1">
            <div className="text-xs text-neutral-400">Адрес</div>
            <input
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              className="w-full rounded-md border border-neutral-800 bg-neutral-950 px-3 py-2 text-sm text-neutral-100 outline-none focus:border-pink-500"
              placeholder="например: str. Test 10, Chișinău"
            />
          </label>
        </div>

        {error && (
          <div className="text-sm text-red-400 wrap-break-word">
            Ошибка: {error}
          </div>
        )}

        <div className="flex items-center gap-2">
          <button
            type="submit"
            disabled={busyId !== null}
            className="rounded-md bg-pink-600 px-4 py-2 text-sm font-medium text-white hover:bg-pink-500 disabled:opacity-60"
          >
            {isEditing ? "Сохранить" : "Создать"}
          </button>

          <div className="text-xs text-neutral-500">
            {busyId ? "Выполняется запрос…" : ""}
          </div>
        </div>
      </form>

      {/* TABLE */}
      <div className="rounded-xl border border-neutral-800 overflow-hidden">
        <div className="px-4 py-3 bg-neutral-950/60 border-b border-neutral-800 flex items-center justify-between">
          <div className="text-sm text-neutral-200">
            {loading ? "Загрузка…" : `Всего: ${items.length}`}
          </div>
        </div>

        <div className="overflow-auto">
          <table className="min-w-[780px] w-full text-sm">
            <thead className="bg-neutral-950">
              <tr className="text-neutral-400">
                <th className="text-left px-4 py-3 w-[90px]">ID</th>
                <th className="text-left px-4 py-3">Название</th>
                <th className="text-left px-4 py-3">Адрес</th>
                <th className="text-right px-4 py-3 w-[220px]">Действия</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-neutral-900">
              {items.map((loc) => (
                <tr key={loc.id} className="hover:bg-neutral-950/40">
                  <td className="px-4 py-3 text-neutral-400">{loc.id}</td>
                  <td className="px-4 py-3 text-neutral-100 font-medium">
                    {loc.name}
                  </td>
                  <td className="px-4 py-3 text-neutral-300">
                    {loc.address || <span className="text-neutral-600">—</span>}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex justify-end gap-2">
                      <button
                        type="button"
                        onClick={() => startEdit(loc)}
                        disabled={busyId !== null}
                        className="rounded-md border border-neutral-700 px-3 py-1.5 text-xs text-neutral-200 hover:border-pink-500 hover:text-white disabled:opacity-60"
                      >
                        Редактировать
                      </button>

                      <button
                        type="button"
                        onClick={() => remove(loc)}
                        disabled={busyId !== null}
                        className="rounded-md border border-neutral-700 px-3 py-1.5 text-xs text-neutral-200 hover:border-red-500 hover:text-white disabled:opacity-60"
                      >
                        Удалить
                      </button>
                    </div>
                  </td>
                </tr>
              ))}

              {!loading && items.length === 0 && (
                <tr>
                  <td className="px-4 py-8 text-neutral-500" colSpan={4}>
                    Локаций пока нет. Создай первую сверху.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="text-xs text-neutral-600">
        Примечание: если удаление запрещено из-за связей (абонементы/занятия),
        бэк вернёт ошибку — покажем её тут, а потом сделаем “мягкое скрытие”.
      </div>
    </div>
  );
}

