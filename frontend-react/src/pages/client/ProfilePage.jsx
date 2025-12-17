import React, { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext.jsx";

export default function ClientProfilePage() {
  const { user, updateProfile } = useAuth();

  const [fullName, setFullName] = useState(user?.full_name ?? "");
  const [phone, setPhone] = useState(user?.phone ?? "");
  const [savingProfile, setSavingProfile] = useState(false);
  const [profileMessage, setProfileMessage] = useState(null);

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [savingPassword, setSavingPassword] = useState(false);
  const [passwordMessage, setPasswordMessage] = useState(null);

  // если профиль подгрузился уже после монтирования — обновляем поля
  useEffect(() => {
    setFullName(user?.full_name ?? "");
    setPhone(user?.phone ?? "");
  }, [user?.full_name, user?.phone]);

  if (!user) {
    return <div>Загрузка профиля...</div>;
  }

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setProfileMessage(null);
    setSavingProfile(true);

    try {
      await updateProfile({
        full_name: fullName || null,
        phone: phone || null,
      });
      setProfileMessage("Профиль обновлён.");
    } catch (err) {
      setProfileMessage(err.message || "Ошибка при обновлении профиля.");
    } finally {
      setSavingProfile(false);
    }
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setPasswordMessage(null);
    if (!currentPassword || !newPassword) {
      setPasswordMessage("Укажите текущий и новый пароль.");
      return;
    }

    setSavingPassword(true);
    try {
      await updateProfile({
        current_password: currentPassword,
        new_password: newPassword,
      });
      setPasswordMessage("Пароль успешно изменён.");
      setCurrentPassword("");
      setNewPassword("");
    } catch (err) {
      setPasswordMessage(err.message || "Ошибка при смене пароля.");
    } finally {
      setSavingPassword(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="client-dashboard-card">
        <h2 className="text-lg font-semibold mb-4">Основная информация</h2>
        <p className="text-sm text-neutral-500 mb-4">
          Здесь вы можете изменить имя и контактный телефон.
        </p>

        <form onSubmit={handleProfileSubmit} className="space-y-4">
          <div>
            <label className="block text-sm mb-1">Email (логин)</label>
            <input
              type="email"
              value={user.email}
              disabled
              className="w-full rounded-md border border-neutral-200 bg-neutral-100 px-3 py-2 text-sm text-neutral-700 cursor-not-allowed"
            />
          </div>

          <div>
            <label className="block text-sm mb-1">Имя</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full rounded-md border border-neutral-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
              placeholder="Как к вам обращаться"
            />
          </div>

          <div>
            <label className="block text-sm mb-1">Телефон</label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="w-full rounded-md border border-neutral-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
              placeholder="+373 ..."
            />
          </div>

          {profileMessage && (
            <div className="text-sm text-neutral-600">{profileMessage}</div>
          )}

          <button
            type="submit"
            disabled={savingProfile}
            className="inline-flex items-center rounded-md bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-500 disabled:bg-sky-300"
          >
            {savingProfile ? "Сохраняем..." : "Сохранить изменения"}
          </button>
        </form>
      </div>

      <div className="client-dashboard-card">
        <h2 className="text-lg font-semibold mb-4">Смена пароля</h2>
        <p className="text-sm text-neutral-500 mb-4">
          Для смены пароля укажите текущий пароль и новый (минимум 8 символов).
        </p>

        <form onSubmit={handlePasswordSubmit} className="space-y-4">
          <div>
            <label className="block text-sm mb-1">Текущий пароль</label>
            <input
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              className="w-full rounded-md border border-neutral-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
              autoComplete="current-password"
            />
          </div>

          <div>
            <label className="block text-sm mb-1">Новый пароль</label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="w-full rounded-md border border-neutral-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sky-500"
              autoComplete="new-password"
            />
          </div>

          {passwordMessage && (
            <div className="text-sm text-neutral-600">{passwordMessage}</div>
          )}

          <button
            type="submit"
            disabled={savingPassword}
            className="inline-flex items-center rounded-md bg-pink-600 px-4 py-2 text-sm font-medium text-white hover:bg-pink-500 disabled:bg-pink-300"
          >
            {savingPassword ? "Меняем..." : "Изменить пароль"}
          </button>
        </form>
      </div>
    </div>
  );
}
