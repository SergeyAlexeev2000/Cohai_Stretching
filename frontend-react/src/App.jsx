// src/App.jsx
import React, { useState } from 'react';
import { Routes, Route, NavLink, Outlet } from 'react-router-dom';

import HomePage from './pages/HomePage.jsx';
import NewbieGuidePage from './pages/NewbieGuidePage.jsx';
import FormatsPage from './pages/FormatsPage.jsx';
import SchedulePage from './pages/SchedulePage.jsx';
import PricesPage from './pages/PricesPage.jsx';
import TrainersPage from './pages/TrainersPage.jsx';
import ContactsPage from './pages/ContactsPage.jsx';

const NAV_ITEMS = [
  { to: '/', label: 'Главная' },
  { to: '/newbie', label: 'Новичку' },
  { to: '/formats', label: 'Форматы' },
  { to: '/schedule', label: 'Расписание' },
  { to: '/prices', label: 'Цены' },
  { to: '/trainers', label: 'Тренеры' },
  { to: '/contacts', label: 'Контакты' },
];

function AppLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);

  const linkClasses = ({ isActive }) =>
    [
      'transition-colors duration-200',
      'text-sm font-medium',
      isActive
        ? 'text-pink-400'
        : 'text-neutral-300 hover:text-white',
    ].join(' ');

  return (
    <div className="min-h-screen bg-neutral-950 text-white flex flex-col">
      {/* HEADER */}
      <header className="border-b border-neutral-800 bg-neutral-950/85 backdrop-blur">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
          {/* Логотип / бренд */}
          <div className="flex flex-col">
            <span className="text-lg font-semibold tracking-tight">
              Cohai Stretching
            </span>
            <span className="hidden sm:inline text-xs text-neutral-500">
              студия стретчинга в Кишинёве
            </span>
          </div>

          {/* Десктоп-меню */}
          <nav className="hidden md:flex items-center gap-5">
            {NAV_ITEMS.map((item) => (
              <NavLink key={item.to} to={item.to} className={linkClasses}>
                {item.label}
              </NavLink>
            ))}
          </nav>

          {/* Мобильный бургер */}
          <button
            type="button"
            className="md:hidden inline-flex items-center gap-2 rounded-md border border-neutral-700 px-3 py-1.5 text-xs font-medium text-neutral-200 hover:text-white hover:border-pink-500 hover:bg-neutral-900/60 transition-colors"
            onClick={() => setMobileOpen((v) => !v)}
          >
            <span>Меню</span>
            <span className="text-lg leading-none">
              {mobileOpen ? '✕' : '☰'}
            </span>
          </button>
        </div>

        {/* Мобильное выпадающее меню */}
        <nav
          className={
            (mobileOpen ? 'block' : 'hidden') +
            ' md:hidden border-t border-neutral-800 bg-neutral-950/95'
          }
        >
          <div className="max-w-6xl mx-auto px-4 py-3 flex flex-col gap-2">
            {NAV_ITEMS.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={linkClasses}
                onClick={() => setMobileOpen(false)}
              >
                {item.label}
              </NavLink>
            ))}
          </div>
        </nav>
      </header>

      {/* MAIN */}
      <main className="flex-1">
        <div className="max-w-6xl mx-auto px-4 py-6 md:py-8">
          <Outlet />
        </div>
      </main>

      {/* FOOTER */}
      <footer className="border-t border-neutral-800 py-4 text-xs text-neutral-500">
        <div className="max-w-6xl mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-2">
          <span>
            Cohai Stretching © {new Date().getFullYear()}
          </span>
          <span className="text-neutral-600">
            Бережная гибкость, здоровая спина и комфортное движение.
          </span>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<HomePage />} />
        <Route path="/newbie" element={<NewbieGuidePage />} />
        <Route path="/formats" element={<FormatsPage />} />
        <Route path="/schedule" element={<SchedulePage />} />
        <Route path="/prices" element={<PricesPage />} />
        <Route path="/trainers" element={<TrainersPage />} />
        <Route path="/contacts" element={<ContactsPage />} />
      </Route>
    </Routes>
  );
}