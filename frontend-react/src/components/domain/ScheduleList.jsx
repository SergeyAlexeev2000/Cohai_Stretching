import React from 'react';

export function ScheduleList({ schedule, programTypesById }) {
  return (
    <div className="mt-4">
      {schedule.length === 0 && (
        <p className="text-neutral-400">Нет занятий для этой локации.</p>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {schedule.map(s => {
          const programName =
            programTypesById[s.program_type_id] ||
            `Программа #${s.program_type_id}`;

          return (
            <div key={s.id} className="card">
              <h3 className="text-lg font-semibold mb-2">{programName}</h3>

              <p><span className="text-neutral-400">Время:</span> {s.start_time} — {s.end_time}</p>
              <p><span className="text-neutral-400">Длительность:</span> {s.duration_minutes} мин</p>
              <p><span className="text-neutral-400">Тренер:</span> #{s.trainer_id}</p>
              <p><span className="text-neutral-400">Мест:</span> {s.capacity}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
