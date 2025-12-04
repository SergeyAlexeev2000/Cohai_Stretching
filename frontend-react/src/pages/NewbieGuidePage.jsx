export default function NewbieGuidePage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold mb-2">Памятка новичку</h1>

      <section className="space-y-2">
        <h2 className="text-xl font-semibold">С чего начать?</h2>
        <ul className="list-disc list-inside space-y-1 text-neutral-300">
          <li>Выберите удобную локацию и формат занятия.</li>
          <li>Запишитесь на пробное занятие через форму на главной.</li>
          <li>Приходите за 10–15 минут до начала, чтобы спокойно переодеться.</li>
        </ul>
      </section>

      <section className="space-y-2">
        <h2 className="text-xl font-semibold">Что взять с собой?</h2>
        <ul className="list-disc list-inside space-y-1 text-neutral-300">
          <li>Удобную одежду, не стесняющую движений.</li>
          <li>Носки, резинку для волос, при желании — своё полотенце.</li>
          <li>Бутылку воды.</li>
        </ul>
      </section>

      <section className="space-y-2">
        <h2 className="text-xl font-semibold">Как проходит тренировка?</h2>
        <p className="text-neutral-300">
          Занятие включает разминку, основную часть с растяжкой и заминку. Тренер
          подсказывает варианты упражнений под ваш уровень, следит за техникой и дыханием.
        </p>
      </section>
    </div>
  );
}
