import { NavLink } from 'react-router-dom';

export default function Header() {
  const link = ({ isActive }) =>
    `px-4 py-2 ${isActive ? 'text-pink-400' : 'hover:text-pink-300'}`;

  return (
    <header className="border-b border-neutral-700">
      <nav className="container mx-auto flex gap-6 px-4 py-4 text-lg">
        <NavLink to="/" className={link}>Главная</NavLink>
        <NavLink to="/newbie" className={link}>Новичку</NavLink>
        <NavLink to="/formats" className={link}>Форматы</NavLink>
        <NavLink to="/schedule" className={link}>Расписание</NavLink>
        <NavLink to="/prices" className={link}>Цены</NavLink>
        <NavLink to="/trainers" className={link}>Тренеры</NavLink>
        <NavLink to="/contacts" className={link}>Контакты</NavLink>
      </nav>
    </header>
  );
}
