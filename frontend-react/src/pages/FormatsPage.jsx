export default function FormatsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold mb-2">Форматы тренировок</h1>

      <section className="grid gap-4 md:grid-cols-2">
        <div className="bg-neutral-800 rounded-lg p-4">
          <h2 className="text-xl font-semibold mb-1">Классический стретчинг</h2>
          <p className="text-sm text-neutral-300">
            Базовые упражнения на гибкость всего тела. Подходит новичкам и тем, кто давно не тренировался.
          </p>
        </div>

        <div className="bg-neutral-800 rounded-lg p-4">
          <h2 className="text-xl font-semibold mb-1">Спина и осанка</h2>
          <p className="text-sm text-neutral-300">
            Мягкая работа с мышцами спины и плечевого пояса, разгрузка шеи и поясницы.
          </p>
        </div>

        <div className="bg-neutral-800 rounded-lg p-4">
          <h2 className="text-xl font-semibold mb-1">Шпагаты</h2>
          <p className="text-sm text-neutral-300">
            Целенаправленная работа на продольные и поперечные шпагаты. Нагрузка подбирается под уровень.
          </p>
        </div>

        <div className="bg-neutral-800 rounded-lg p-4">
          <h2 className="text-xl font-semibold mb-1">Женские стили</h2>
          <p className="text-sm text-neutral-300">
            Мягкие пластичные тренировки с акцентом на осанку, походку и уверенность в себе.
          </p>
        </div>
      </section>

      <p className="text-neutral-400 text-sm">
        Полный список форматов и расписание смотрите на страницах «Расписание» и «Цены».
      </p>
    </div>
  );
}

