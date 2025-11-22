import React from 'react';

export function MembershipList({ memberships }) {
  if (!memberships || memberships.length === 0) {
    return <p className="text-neutral-400">Нет абонементов для этой локации.</p>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
      {memberships.map(m => (
        <div key={m.id} className="card">
          <h3 className="text-lg font-semibold mb-2">{m.name}</h3>

          <p>
            <span className="text-neutral-400">Продолжительность:</span>{' '}
            {m.duration_days} дней
          </p>
          <p>
            <span className="text-neutral-400">Цена:</span>{' '}
            {m.price} ₽
          </p>
          {m.description && (
            <p className="mt-2 text-sm text-neutral-300">
              {m.description}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}
