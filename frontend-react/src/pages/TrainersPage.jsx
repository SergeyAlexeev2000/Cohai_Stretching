// src/pages/TrainersPage.jsx
import React from 'react';
import { Card } from '../components/ui/Card.jsx';
import { LeadForm } from '../components/domain/LeadForm.jsx';

// Временно статичный список тренеров.
// Потом можно будет подключить API.
const TRAINERS = [
  {
    id: 1,
    name: 'Анастасия Коханюк',
    role: 'Основатель студии, тренер',
    formats: 'Классический стретчинг, шпагаты, женские стили',
    experience: '7+ лет опыта',
  },
  {
    id: 2,
    name: 'Анастасия Казмирчук',
    role: 'Тренер',
    formats: 'Спина и осанка, мягкий стретчинг для новичков',
    experience: '5+ лет опыта',
  },
  {
    id: 3,
    name: 'Татьяна Спиней',
    role: 'Тренер',
    formats: 'Классический стретчинг, Спина all inclusive, МФР, Активный стретчинг, Гимнастика для детей',
    experience: '4+ года опыта',
  },
  {
    id: 4,
    name: 'Карина Фаншевская',
    role: 'Тренер',
    formats: 'Классический стретчинг, Спина all inclusive, МФР, Активный стретчинг',
    experience: '4+ года опыта',
  },
  {
    id: 5,
    name: 'Ирина Юрченко',
    role: 'Тренер',
    formats: 'Body Ballet, Активный стретчинг, Классический стретчинг, Гимнастика для детей',
    experience: '4+ года опыта',
  },
];

export default function TrainersPage() {
  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold">Тренеры Cohai Stretching</h1>
        <p className="text-neutral-300">
          Команда, которая помогает вам безопасно прокачать гибкость, осанку и
          уверенность в движении.
        </p>
      </header>

      <section className="grid gap-4 md:grid-cols-3">
        {TRAINERS.map((t) => (
          <Card
            key={t.id}
            title={t.name}
            subtitle={t.role}
            className="h-full"
          >
            <p>
              <span className="text-neutral-400">Форматы: </span>
              {t.formats}
            </p>
            <p>
              <span className="text-neutral-400">Опыт: </span>
              {t.experience}
            </p>
            <p className="pt-2 text-neutral-300">{t.tagline}</p>
          </Card>
        ))}
      </section>

      <section className="grid gap-6 md:grid-cols-2 items-start">
        <div className="space-y-3">
          <h2 className="text-2xl font-semibold">Хочу стать тренером</h2>
          <p className="text-neutral-300">
            Если вы тренер по стретчингу, йоге или смежным направлениям и
            хотите работать в Cohai Stretching — оставьте заявку. Мы свяжемся с
            вами, обсудим опыт и возможные форматы сотрудничества.
          </p>
          <p className="text-neutral-400 text-sm">
            Важно: базовое профильное образование или подтверждённые курсы,
            опыт работы с людьми и любовь к аккуратной технике.
          </p>
        </div>

        <div className="bg-neutral-800 rounded-xl p-4 md:p-5 shadow-lg">
          <h3 className="text-xl font-semibold mb-2">
            Заявка тренера
          </h3>
          <p className="text-sm text-neutral-400 mb-3">
            Напишите, какой у вас опыт и в каких форматах вы хотели бы вести
            занятия.
          </p>
          {/* Переиспользуем LeadForm, просто человек может описать опыт в комментарии */}
          <LeadForm />
        </div>
      </section>
    </div>
  );
}

