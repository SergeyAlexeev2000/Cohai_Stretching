// src/pages/LoginPage.jsx
import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  // если нас переадресовали с RequireRole, он положил from в location.state
  const rawFrom = location.state?.from?.pathname;

  // если нас редиректнули с защищённой страницы — вернём туда
  // но если откуда-то прилетело "/" или "/login" — это бесполезно, идём в /cabinet
  const from =
    rawFrom && rawFrom !== "/" && rawFrom !== "/login"
      ? rawFrom
      : "/cabinet";


  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(email, password);
      // если успешно залогинились — отправляем туда, откуда пришли, или в /client
      navigate("/cabinet", { replace: true });
    } catch (err) {
      setError(err.message || "Не удалось войти");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-md mx-auto">
      <h1 className="text-2xl font-semibold mb-4">Вход в личный кабинет</h1>
      <p className="text-sm text-neutral-400 mb-6">
        Введите email и пароль, полученные при регистрации.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm mb-1" htmlFor="email">
            Email
          </label>
          <input
            id="email"
            type="email"
            className="w-full rounded-md border border-neutral-700 bg-neutral-900 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-pink-500"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            required
          />
        </div>

        <div>
          <label className="block text-sm mb-1" htmlFor="password">
            Пароль
          </label>
          <input
            id="password"
            type="password"
            className="w-full rounded-md border border-neutral-700 bg-neutral-900 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-pink-500"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            required
          />
        </div>

        {error && (
          <div className="text-sm text-red-400">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={submitting}
          className="w-full inline-flex items-center justify-center rounded-md bg-pink-500 px-4 py-2 text-sm font-medium text-white hover:bg-pink-400 disabled:bg-pink-800 disabled:opacity-70 transition-colors"
        >
          {submitting ? "Входим..." : "Войти"}
        </button>
      </form>
    </div>
  );
}
