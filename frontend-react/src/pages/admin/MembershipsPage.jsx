// src/pages/admin/MembershipsPage.jsx
import React, { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext.jsx";
import { adminRequest } from "../../api/adminRequest.js";

export default function MembershipsPage() {
  const { token } = useAuth();

  const [items, setItems] = useState([]);
  const [locations, setLocations] = useState([]);

  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState(null);

  // create-form
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [locationId, setLocationId] = useState("");

  const [submitting, setSubmitting] = useState(false);

  // inline edit (A): только name, потому что MembershipPlanUpdate на бэке сейчас только name
  const [editId, setEditId] = useState(null);
  const [editName, setEditName] = useState("");

  function locationLabel(id) {
    const loc = locations.find((x) => x.id === id);
    if (!loc) return `#${id}`;
    return loc.name ? `${loc.name}${loc.address ? ` — ${loc.address}` : ""}` : `#${id}`;
  }

  async function load() {
    setLoading(true);
    setErr(null);
    try {
      const [memberships, locs] = await Promise.all([
        adminRequest("/admin/memberships", { token }),
        adminRequest("/admin/locations", { token }),
      ]);

      setItems(Array.isArray(memberships) ? memberships : []);
      setLocations(Array.isArray(locs) ? locs : []);
    } catch (e) {
      setErr(e.message || "Ошибка загрузки");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  async function onCreate(e) {
    e.preventDefault();
    setErr(null);

    // простая валидация на фронте
    const p = Number(price);
    const locId = Number(locationId);

    if (!name.trim()) return setErr("Название обязательно");
    if (!Number.isFinite(p) || p < 0) return setErr("Цена должна быть числом >= 0");
    if (!Number.isInteger(locId) || locId <= 0) return setErr("Выбери локацию");

    setSubmitting(true);
    try {
      const created = await adminRequest("/admin/memberships", {
        token,
        method: "POST",
        body: {
          name: name.trim(),
          description: description.trim() ? description.trim() : null,
          price: p,
          location_id: locId,
        },
      });

      // добавим сверху
      setItems((prev) => [created, ...prev]);

      // reset form
      setName("");
      setDescription("");
      setPrice("");
      setLocationId("");
    } catch (e2) {
      setErr(e2.message || "Не удалось создать тариф");
    } finally {
      setSubmitting(false);
    }
  }

  function startEdit(item) {
    setEditId(item.id);
    setEditName(item.name ?? "");
  }

  function cancelEdit() {
    setEditId(null);
    setEditName("");
  }

  async function saveEdit(id) {
    const newName = (editName || "").trim();
    if (!newName) return alert("Название не может быть пустым");

    try {
      const updated = await adminRequest(`/admin/memberships/${id}`, {
        token,
        method: "PATCH",
        body: { name: newName },
      });

      setItems((prev) => prev.map((x) => (x.id === id ? updated : x)));
      cancelEdit();
    } catch (e) {
      alert(e.message || "Не удалось обновить");
    }
  }

  async function removeItem(id) {
    if (!confirm(`Удалить тариф #${id}?`)) return;

    try {
      await adminRequest(`/admin/memberships/${id}`, {
        token,
        method: "DELETE",
      });
      setItems((prev) => prev.filter((x) => x.id !== id));
      if (editId === id) cancelEdit();
    } catch (e) {
      alert(e.message || "Не удалось удалить");
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-end justify-between gap-3 flex-wrap">
        <div>
          <h1 className="text-2xl font-semibold">Абонементы</h1>
          <div className="text-sm text-neutral-400">
            Список тарифов + создание. Редактирование (A) — только название.
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

      {err && (
        <div className="text-sm text-red-400 border border-red-900/40 bg-red-950/20 rounded-md p-3">
          {err}
        </div>
      )}

      {/* CREATE */}
      <form onSubmit={onCreate} className="border border-neutral-800 rounded-xl p-4 space-y-3">
        <div className="text-sm font-medium">Создать тариф</div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs text-neutral-400 mb-1">Название</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full rounded-md border border-neutral-700 bg-neutral-900 px-3 py-2 text-sm text-white"
              placeholder="Напр.: 8 занятий / месяц"
            />
          </div>

          <div>
            <label className="block text-xs text-neutral-400 mb-1">Цена</label>
            <input
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              className="w-full rounded-md border border-neutral-700 bg-neutral-900 px-3 py-2 text-sm text-white"
              placeholder="Напр.: 1200"
              inputMode="decimal"
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-xs text-neutral-400 mb-1">Описание (опционально)</label>
            <input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full rounded-md border border-neutral-700 bg-neutral-900 px-3 py-2 text-sm text-white"
              placeholder="Напр.: доступ к любым групповым тренировкам"
            />
          </div>

          <div className="md:col-span-2">
            <label className="block text-xs text-neutral-400 mb-1">Локация</label>
            <select
              value={locationId}
              onChange={(e) => setLocationId(e.target.value)}
              className="w-full rounded-md border border-neutral-700 bg-neutral-900 px-3 py-2 text-sm text-white"
            >
              <option value="">— выбери —</option>
              {locations.map((l) => (
                <option key={l.id} value={l.id}>
                  {l.name ? `${l.name}${l.address ? ` — ${l.address}` : ""}` : `#${l.id}`}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="text-sm px-3 py-2 rounded-md bg-pink-500 hover:bg-pink-400 disabled:bg-pink-800 disabled:opacity-70 transition-colors"
        >
          {submitting ? "Создаю..." : "Создать"}
        </button>
      </form>

      {/* LIST */}
      <div className="border border-neutral-800 rounded-xl overflow-hidden">
        <div className="grid grid-cols-12 gap-2 px-3 py-2 text-xs text-neutral-400 bg-neutral-900/60 border-b border-neutral-800">
          <div className="col-span-1">ID</div>
          <div className="col-span-4">Название</div>
          <div className="col-span-2">Цена</div>
          <div className="col-span-3">Локация</div>
          <div className="col-span-2 text-right">Действия</div>
        </div>

        {loading ? (
          <div className="p-4 text-sm text-neutral-300">Загрузка…</div>
        ) : items.length === 0 ? (
          <div className="p-4 text-sm text-neutral-400">Пусто.</div>
        ) : (
          items.map((x) => {
            const isEdit = editId === x.id;
            return (
              <div
                key={x.id}
                className="grid grid-cols-12 gap-2 px-3 py-2 text-sm border-b border-neutral-800 last:border-b-0 items-center"
              >
                <div className="col-span-1 text-neutral-400">{x.id}</div>

                <div className="col-span-4">
                  {isEdit ? (
                    <input
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                      className="w-full rounded-md border border-neutral-700 bg-neutral-900 px-3 py-1.5 text-sm text-white"
                    />
                  ) : (
                    <div className="font-medium">{x.name ?? "—"}</div>
                  )}
                  {x.description && (
                    <div className="text-xs text-neutral-500 wrap-break-words">{x.description}</div>
                  )}
                </div>

                <div className="col-span-2 text-neutral-200">
                  {Number.isFinite(x.price) ? x.price : "—"}
                </div>

                <div className="col-span-3 text-neutral-400 text-xs">
                  {x.location_id ? locationLabel(x.location_id) : "—"}
                </div>

                <div className="col-span-2 flex justify-end gap-2">
                  {isEdit ? (
                    <>
                      <button
                        type="button"
                        onClick={() => saveEdit(x.id)}
                        className="text-xs px-2 py-1 rounded-md border border-neutral-700 hover:border-pink-500 hover:text-pink-400 transition-colors"
                      >
                        Сохранить
                      </button>
                      <button
                        type="button"
                        onClick={cancelEdit}
                        className="text-xs px-2 py-1 rounded-md border border-neutral-700 hover:border-neutral-500 transition-colors"
                      >
                        Отмена
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        type="button"
                        onClick={() => startEdit(x)}
                        className="text-xs px-2 py-1 rounded-md border border-neutral-700 hover:border-pink-500 hover:text-pink-400 transition-colors"
                      >
                        Правка
                      </button>
                      <button
                        type="button"
                        onClick={() => removeItem(x.id)}
                        className="text-xs px-2 py-1 rounded-md border border-neutral-700 hover:border-red-500 hover:text-red-300 transition-colors"
                      >
                        Удалить
                      </button>
                    </>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>

      <div className="text-xs text-neutral-500">
        Примечание: редактирование цены/описания/локации добавим после модалок и/или расширения схемы PATCH на бэке.
      </div>
    </div>
  );
}
