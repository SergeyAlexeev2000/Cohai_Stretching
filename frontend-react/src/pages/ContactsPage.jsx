// src/pages/ContactsPage.jsx
import React, { useEffect, useState } from 'react';
import { getLocations } from '../api.js';
import { Card } from '../components/ui/Card.jsx';

export default function ContactsPage() {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const locs = await getLocations();
        if (!cancelled) {
          setLocations(locs);
        }
      } catch (e) {
        console.error(e);
        if (!cancelled) {
          setError('Не удалось загрузить локации.');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="space-y-8">
      <header className="space-y-2">
        <h1 className="text-3xl font-bold">Контакты</h1>
        <p className="text-neutral-300">
          Выберите удобную студию и свяжитесь с нами любым удобным способом.
        </p>
      </header>

      <section className="grid gap-4 md:grid-cols-2">
        <Card title="Администратор студии">
          <p>
            <span className="text-neutral-400">Телефон: </span>
            +373&nbsp;(___)&nbsp;___&nbsp;___
          </p>
          <p>
            <span className="text-neutral-400">WhatsApp / Telegram: </span>
            тот же номер
          </p>
          <p>
            <span className="text-neutral-400">E-mail: </span>
            info@cohai-stretching.example
          </p>
          <p className="pt-2 text-neutral-300">
            Если не можете дозвониться — оставьте заявку на сайте, мы вернёмся к
            вам в ближайшее время.
          </p>
        </Card>

        <Card title="Соцсети">
          <p>
            <span className="text-neutral-400">Instagram: </span>
            @cohai_stretching
          </p>
          <p>
            <span className="text-neutral-400">TikTok: </span>
            @cohai_stretching
          </p>
          <p>
            <span className="text-neutral-400">Facebook: </span>
            Cohai Stretching Studio
          </p>
          <p className="pt-2 text-neutral-300">
            Там мы выкладываем расписание, новости, акции и полезные советы по
            растяжке.
          </p>
        </Card>
      </section>

      <section className="space-y-3">
        <h2 className="text-2xl font-semibold">Адреса студий</h2>

        {loading && (
          <p className="text-neutral-400 text-sm">
            Загружаем локации...
          </p>
        )}

        {error && (
          <p className="text-red-400 text-sm">{error}</p>
        )}

        {!loading && !error && (
          <div className="grid gap-4 md:grid-cols-2">
            {locations.map((loc) => (
              <Card
                key={loc.id}
                title={loc.name}
                subtitle="Студия Cohai Stretching"
              >
                <p>{loc.address}</p>
                {/* позже сюда можно добавить схему проезда или ссылку на карту */}
              </Card>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

