import { LeadForm } from '../components/domain/LeadForm.jsx';

export default function HomePage() {
  return (
    <div className="space-y-10">
      {/* Герой-блок */}
      <section className="grid gap-8 md:grid-cols-2 items-center">
        <div className="space-y-4">
          <h1 className="text-4xl md:text-5xl font-bold">
            Cohai Stretching
          </h1>
          <p className="text-lg text-neutral-300">
            Стретчинг-студия в Кишинёве: гибкость, здоровая спина и красивая осанка без боли.
          </p>
          <p className="text-neutral-400">
            Подойдёт любому уровню подготовки: от «никогда не растягивался» до продвинутых.
          </p>
        </div>

        {/* Форма заявки */}
        <div className="bg-neutral-800 rounded-xl p-5 md:p-6 shadow-lg">
          <h2 className="text-2xl font-semibold mb-3">
            Записаться на пробное занятие
          </h2>
          <p className="text-sm text-neutral-400 mb-4">
            Оставьте контакты — администратор свяжется с вами, поможет выбрать формат и время.
          </p>
          <LeadForm />
        </div>
      </section>

      {/* Простейшие преимущества / bullets */}
      <section className="grid gap-4 md:grid-cols-3">
        <div className="bg-neutral-800 rounded-lg p-4">
          <h3 className="font-semibold mb-1">Новичкам комфортно</h3>
          <p className="text-sm text-neutral-300">
            Маленькие группы, внимание к технике и безопасная прогрессия нагрузки.
          </p>
        </div>
        <div className="bg-neutral-800 rounded-lg p-4">
          <h3 className="font-semibold mb-1">Разные форматы</h3>
          <p className="text-sm text-neutral-300">
            Классический стретчинг, спина, шпагаты, женские стили, мини-группы и персоналки.
          </p>
        </div>
        <div className="bg-neutral-800 rounded-lg p-4">
          <h3 className="font-semibold mb-1">Удобное расписание</h3>
          <p className="text-sm text-neutral-300">
            Утренние и вечерние группы в нескольких локациях.
          </p>
        </div>
      </section>
    </div>
  );
}
