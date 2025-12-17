import React, { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext.jsx";

function formatDateTime(value) {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleString("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function statusLabel(status) {
  if (!status) return "";
  switch (status) {
    case "NEW":
      return "Новая заявка";
    case "IN_PROGRESS":
      return "В работе";
    case "DONE":
      return "Обработана";
    case "REJECTED":
      return "Отклонена";
    default:
      return status;
  }
}

function statusClass(status) {
  if (!status) return "badge";
  switch (status) {
    case "NEW":
      return "badge badge--blue";
    case "IN_PROGRESS":
      return "badge badge--yellow";
    case "DONE":
      return "badge badge--green";
    case "REJECTED":
      return "badge badge--red";
    default:
      return "badge";
  }
}

function LeadItem({ lead }) {
  const title = lead.full_name || "Заявка без имени";
  const phone = lead.phone || "—";
  const location =
    lead.location_name ||
    lead.location_title ||
    (lead.location_id ? `Локация #${lead.location_id}` : null);
  const program =
    lead.program_type_name ||
    (lead.program_type_id ? `Направление #${lead.program_type_id}` : null);
  const status = lead.status || null;
  const created = lead.created_at || lead.created || null;
  const comment = lead.comment || lead.note || null;

  return (
    <div className="lead-item">
      <div className="lead-item__header">
        <div>
          <div className="lead-item__title">{title}</div>
          <div className="lead-item__subtitle">
            Телефон: <span>{phone}</span>
          </div>
        </div>
        {status && (
          <span className={statusClass(status)}>
            {statusLabel(status)}
          </span>
        )}
      </div>

      <div className="lead-item__body">
        {location && (
          <div className="lead-item__row">
            <span>Студия</span>
            <span>{location}</span>
          </div>
        )}
        {program && (
          <div className="lead-item__row">
            <span>Направление</span>
            <span>{program}</span>
          </div>
        )}
        {created && (
          <div className="lead-item__row lead-item__row--muted">
            <span>Создана</span>
            <span>{formatDateTime(created)}</span>
          </div>
        )}
        {comment && (
          <div className="lead-item__comment">
            <span className="lead-item__comment-label">Комментарий:</span>
            <span>{comment}</span>
          </div>
        )}
      </div>

      {lead.id && (
        <div className="lead-item__footer">
          <span className="lead-item__id">ID заявки: {lead.id}</span>
        </div>
      )}
    </div>
  );
}

export default function ClientLeadsPage() {
  const { token } = useAuth();
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!token) return;

    let cancelled = false;
    setLoading(true);
    setError(null);

    fetch("/api/v1/me/leads", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
      .then(async (resp) => {
        if (!resp.ok) {
          let msg = "Не удалось загрузить заявки.";
          try {
            const body = await resp.json();
            if (typeof body.detail === "string") {
              msg = body.detail;
            } else if (Array.isArray(body.detail)) {
              msg = body.detail
                .map((d) => d.msg || JSON.stringify(d))
                .join("; ");
            }
          } catch (_) {
            // ignore
          }
          throw new Error(msg);
        }
        return resp.json();
      })
      .then((json) => {
        if (cancelled) return;
        if (Array.isArray(json)) {
          // /me/leads возвращает простой список LeadRead
          setLeads(json);
        } else if (Array.isArray(json.items)) {
          setLeads(json.items);
        } else {
          setLeads([]);
        }
      })
      .catch((err) => {
        if (cancelled) return;
        console.error("Ошибка загрузки заявок:", err);
        setError(err.message || "Ошибка загрузки заявок.");
      })
      .finally(() => {
        if (cancelled) return;
        setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [token]);

  if (loading) {
    return (
      <div className="client-dashboard-card">
        Загрузка заявок...
      </div>
    );
  }

  if (error) {
    return (
      <div className="client-dashboard-card">
        <div className="text-red-600 text-sm mb-2">{error}</div>
        <div className="text-sm text-neutral-600">
          Попробуйте обновить страницу. Если проблема сохраняется —
          напишите администратору.
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="client-dashboard-card">
        <h2 className="text-lg font-semibold mb-2">Мои заявки</h2>
        <p className="text-sm text-neutral-500">
          Здесь отображаются заявки, которые вы оставляли через сайт
          (например, на пробное занятие).
        </p>
      </div>

      {leads.length === 0 ? (
        <div className="client-dashboard-card">
          <p className="text-sm text-neutral-600">
            У вас пока нет заявок.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {leads.map((lead) => (
            <LeadItem key={lead.id} lead={lead} />
          ))}
        </div>
      )}
    </div>
  );
}
