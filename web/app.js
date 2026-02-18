const translations = {
  ru: {
    languageLabel: 'Язык',
    chip: 'Онлайн-когнитивный тест',
    title: 'Оцените ваш IQ за 5–7 минут',
    subtitle: 'Современный адаптивный мини-тест на логику, числовые и вербальные закономерности.',
    startTest: 'Пройти тест',
    whatIsIqTitle: 'Что такое IQ?',
    whatIsIqText:
      'IQ (Intelligence Quotient) — стандартизированный показатель результатов когнитивных тестов. В большинстве методик шкала нормируется так, что средний IQ в популяции равен 100, а стандартное отклонение — 15.',
    averageTitle: 'Средний IQ',
    avgScale: 'по стандартизированной шкале',
    averageHint: 'Значения около 90–110 обычно считаются типичным диапазоном для взрослой популяции.',
    methodTitle: 'Как считается результат?',
    methodText:
      'Вы отвечаете на 12 вопросов. По числу правильных ответов формируется ориентировочная оценка IQ и сравнительный процентиль.',
    nextQuestion: 'Далее',
    resultTitle: 'Ваш результат',
    restart: 'Пройти ещё раз',
    counter: (current, total) => `${current}/${total}`,
    percentile: (value) => `Вы опередили примерно ${value}% участников этой шкалы.`,
    encouragement: {
      high: 'Отличный результат: у вас выраженное аналитическое мышление и хорошая скорость распознавания закономерностей.',
      medium: 'Хороший результат: вы уверенно справляетесь с логическими задачами и быстро адаптируетесь к новым типам вопросов.',
      base: 'Достойный результат: при регулярной тренировке логики и внимания вы легко сможете подняться ещё выше.'
    },
    bands: {
      veryHigh: 'Очень высокий диапазон',
      high: 'Выше среднего',
      average: 'Средний и выше',
      developing: 'Потенциал к росту'
    },
    questions: [
      { q: 'Какое число продолжает ряд: 2, 6, 12, 20, 30, ...?', a: ['36', '40', '42', '44'] },
      { q: 'Найдите лишнее: Круг, Треугольник, Квадрат, Куб.', a: ['Круг', 'Куб', 'Квадрат', 'Треугольник'] },
      { q: 'Если все фрукты сладкие, а яблоко — фрукт, то яблоко...', a: ['Кислое', 'Сладкое', 'Нейтральное', 'Неизвестно'] },
      { q: 'Продолжите последовательность букв: A, C, F, J, O, ...', a: ['T', 'U', 'V', 'W'] },
      { q: 'Сколько градусов в сумме внутренних углов треугольника?', a: ['90', '120', '180', '360'] },
      { q: 'Какое число не подходит: 8, 27, 64, 100, 125?', a: ['8', '64', '100', '125'] },
      { q: 'Если 5 машин собирают 5 деталей за 5 минут, сколько минут нужно 100 машинам на 100 деталей?', a: ['1', '5', '20', '100'] },
      { q: 'Найдите аналогию: Книга : Читать = Музыка : ...', a: ['Слушать', 'Петь', 'Писать', 'Играть'] },
      { q: 'Что больше: 3/7 или 4/9?', a: ['3/7', '4/9', 'Одинаково', 'Нельзя сравнить'] },
      { q: 'Логика: 1, 1, 2, 3, 5, 8, ...', a: ['11', '12', '13', '14'] },
      { q: 'Сколько сторон у двух пятиугольников вместе?', a: ['5', '7', '10', '12'] },
      { q: 'Найдите пропущенное число: 7, 10, 16, 28, ...', a: ['38', '42', '46', '52'] }
    ]
  },
  en: {
    languageLabel: 'Language',
    chip: 'Online cognitive test',
    title: 'Estimate your IQ in 5–7 minutes',
    subtitle: 'A modern mini-test with logic, numeric, and verbal pattern tasks.',
    startTest: 'Start test',
    whatIsIqTitle: 'What is IQ?',
    whatIsIqText:
      'IQ (Intelligence Quotient) is a standardized score from cognitive tests. Most methods normalize the scale so the population mean is 100 and the standard deviation is 15.',
    averageTitle: 'Average IQ',
    avgScale: 'on a standardized scale',
    averageHint: 'Scores around 90–110 are commonly considered a typical adult range.',
    methodTitle: 'How is the score calculated?',
    methodText: 'You answer 12 questions. An approximate IQ estimate and percentile are calculated from correct answers.',
    nextQuestion: 'Next',
    resultTitle: 'Your result',
    restart: 'Take again',
    counter: (current, total) => `${current}/${total}`,
    percentile: (value) => `You scored above roughly ${value}% of participants on this scale.`,
    encouragement: {
      high: 'Excellent outcome: you show strong analytical thinking and rapid pattern recognition.',
      medium: 'Great outcome: you handle logical tasks confidently and adapt quickly to new question types.',
      base: 'Solid outcome: with regular logic and attention training, you can improve even more.'
    },
    bands: {
      veryHigh: 'Very high range',
      high: 'Above average',
      average: 'Average and above',
      developing: 'Growing potential'
    },
    questions: [
      { q: 'Which number continues the series: 2, 6, 12, 20, 30, ...?', a: ['36', '40', '42', '44'] },
      { q: 'Find the odd one out: Circle, Triangle, Square, Cube.', a: ['Circle', 'Cube', 'Square', 'Triangle'] },
      { q: 'If all fruits are sweet and an apple is a fruit, then an apple is...', a: ['Sour', 'Sweet', 'Neutral', 'Unknown'] },
      { q: 'Continue the letter sequence: A, C, F, J, O, ...', a: ['T', 'U', 'V', 'W'] },
      { q: 'What is the sum of interior angles of a triangle?', a: ['90', '120', '180', '360'] },
      { q: 'Which number does not fit: 8, 27, 64, 100, 125?', a: ['8', '64', '100', '125'] },
      { q: 'If 5 machines make 5 parts in 5 minutes, how many minutes do 100 machines need for 100 parts?', a: ['1', '5', '20', '100'] },
      { q: 'Find analogy: Book : Read = Music : ...', a: ['Listen', 'Sing', 'Write', 'Play'] },
      { q: 'Which is larger: 3/7 or 4/9?', a: ['3/7', '4/9', 'Equal', 'Cannot compare'] },
      { q: 'Logic: 1, 1, 2, 3, 5, 8, ...', a: ['11', '12', '13', '14'] },
      { q: 'How many sides do two pentagons have together?', a: ['5', '7', '10', '12'] },
      { q: 'Find missing number: 7, 10, 16, 28, ...', a: ['38', '42', '46', '52'] }
    ]
  },
  es: {
    languageLabel: 'Idioma',
    chip: 'Prueba cognitiva en línea',
    title: 'Evalúa tu IQ en 5–7 minutos',
    subtitle: 'Mini test moderno con tareas de lógica, números y patrones verbales.',
    startTest: 'Comenzar prueba',
    whatIsIqTitle: '¿Qué es el IQ?',
    whatIsIqText:
      'IQ (Intelligence Quotient) es una puntuación estandarizada de pruebas cognitivas. La mayoría de los métodos normalizan la escala con media 100 y desviación estándar 15.',
    averageTitle: 'IQ promedio',
    avgScale: 'en escala estandarizada',
    averageHint: 'Valores cercanos a 90–110 suelen considerarse un rango típico en adultos.',
    methodTitle: '¿Cómo se calcula?',
    methodText: 'Respondes 12 preguntas. Según aciertos se calcula un IQ aproximado y un percentil comparativo.',
    nextQuestion: 'Siguiente',
    resultTitle: 'Tu resultado',
    restart: 'Repetir prueba',
    counter: (current, total) => `${current}/${total}`,
    percentile: (value) => `Superaste aproximadamente al ${value}% de participantes de esta escala.`,
    encouragement: {
      high: 'Resultado excelente: muestras pensamiento analítico fuerte y gran reconocimiento de patrones.',
      medium: 'Muy buen resultado: resuelves tareas lógicas con confianza y te adaptas rápido.',
      base: 'Buen resultado: con práctica regular de lógica y atención puedes subir aún más.'
    },
    bands: {
      veryHigh: 'Rango muy alto',
      high: 'Superior al promedio',
      average: 'Promedio y superior',
      developing: 'Potencial en desarrollo'
    },
    questions: [
      { q: '¿Qué número sigue la serie: 2, 6, 12, 20, 30, ...?', a: ['36', '40', '42', '44'] },
      { q: 'Encuentra el diferente: Círculo, Triángulo, Cuadrado, Cubo.', a: ['Círculo', 'Cubo', 'Cuadrado', 'Triángulo'] },
      { q: 'Si todas las frutas son dulces y una manzana es fruta, entonces la manzana es...', a: ['Ácida', 'Dulce', 'Neutra', 'Desconocido'] },
      { q: 'Continúa la secuencia: A, C, F, J, O, ...', a: ['T', 'U', 'V', 'W'] },
      { q: '¿Cuánto suman los ángulos interiores de un triángulo?', a: ['90', '120', '180', '360'] },
      { q: '¿Qué número no encaja: 8, 27, 64, 100, 125?', a: ['8', '64', '100', '125'] },
      { q: 'Si 5 máquinas hacen 5 piezas en 5 minutos, ¿cuántos minutos necesitan 100 máquinas para 100 piezas?', a: ['1', '5', '20', '100'] },
      { q: 'Analogía: Libro : Leer = Música : ...', a: ['Escuchar', 'Cantar', 'Escribir', 'Tocar'] },
      { q: '¿Qué es mayor: 3/7 o 4/9?', a: ['3/7', '4/9', 'Iguales', 'No se puede comparar'] },
      { q: 'Lógica: 1, 1, 2, 3, 5, 8, ...', a: ['11', '12', '13', '14'] },
      { q: '¿Cuántos lados tienen dos pentágonos juntos?', a: ['5', '7', '10', '12'] },
      { q: 'Número faltante: 7, 10, 16, 28, ...', a: ['38', '42', '46', '52'] }
    ]
  }
};

const correctAnswers = [2, 1, 1, 1, 2, 2, 1, 0, 1, 2, 2, 2];

let language = 'ru';
let currentQuestion = 0;
let selectedAnswer = null;
let score = 0;

const languageSelect = document.getElementById('languageSelect');
const startBtn = document.getElementById('startBtn');
const quizSection = document.getElementById('quizSection');
const resultSection = document.getElementById('resultSection');
const questionCounter = document.getElementById('questionCounter');
const questionText = document.getElementById('questionText');
const answers = document.getElementById('answers');
const nextBtn = document.getElementById('nextBtn');
const progressBar = document.getElementById('progressBar');
const iqScore = document.getElementById('iqScore');
const iqBand = document.getElementById('iqBand');
const iqPercentile = document.getElementById('iqPercentile');
const encouragement = document.getElementById('encouragement');
const restartBtn = document.getElementById('restartBtn');

function applyTranslations() {
  document.querySelectorAll('[data-i18n]').forEach((node) => {
    const key = node.dataset.i18n;
    node.textContent = translations[language][key];
  });

  if (!quizSection.classList.contains('hidden')) {
    renderQuestion();
  }

  if (!resultSection.classList.contains('hidden')) {
    showResult();
  }
}

function renderQuestion() {
  const { questions, counter } = translations[language];
  const current = questions[currentQuestion];

  questionCounter.textContent = counter(currentQuestion + 1, questions.length);
  questionText.textContent = current.q;
  progressBar.style.width = `${((currentQuestion + 1) / questions.length) * 100}%`;

  answers.innerHTML = '';
  current.a.forEach((option, index) => {
    const btn = document.createElement('button');
    btn.className = 'btn answer-btn';
    btn.textContent = option;
    btn.addEventListener('click', () => {
      selectedAnswer = index;
      nextBtn.disabled = false;
      document.querySelectorAll('.answer-btn').forEach((b) => b.classList.remove('selected'));
      btn.classList.add('selected');
    });
    answers.appendChild(btn);
  });
}

function estimateIq(rawScore) {
  const normalized = rawScore / correctAnswers.length;
  const iq = Math.round(85 + normalized * 45);
  return Math.max(80, Math.min(140, iq));
}

function calculatePercentile(iq) {
  const z = (iq - 100) / 15;
  const p = 1 / (1 + Math.exp(-1.7 * z));
  return Math.round(p * 100);
}

function getBand(iq) {
  const bands = translations[language].bands;
  if (iq >= 125) return bands.veryHigh;
  if (iq >= 110) return bands.high;
  if (iq >= 95) return bands.average;
  return bands.developing;
}

function getEncouragement(iq) {
  const pool = translations[language].encouragement;
  if (iq >= 120) return pool.high;
  if (iq >= 100) return pool.medium;
  return pool.base;
}

function showResult() {
  const iq = estimateIq(score);
  const percentile = calculatePercentile(iq);

  iqScore.textContent = iq;
  iqBand.textContent = getBand(iq);
  iqPercentile.textContent = translations[language].percentile(percentile);
  encouragement.textContent = getEncouragement(iq);
}

function startQuiz() {
  currentQuestion = 0;
  selectedAnswer = null;
  score = 0;
  nextBtn.disabled = true;
  resultSection.classList.add('hidden');
  quizSection.classList.remove('hidden');
  renderQuestion();
}

startBtn.addEventListener('click', startQuiz);

nextBtn.addEventListener('click', () => {
  if (selectedAnswer === correctAnswers[currentQuestion]) {
    score += 1;
  }

  currentQuestion += 1;
  selectedAnswer = null;
  nextBtn.disabled = true;

  if (currentQuestion >= correctAnswers.length) {
    quizSection.classList.add('hidden');
    resultSection.classList.remove('hidden');
    showResult();
    return;
  }

  renderQuestion();
});

restartBtn.addEventListener('click', startQuiz);
languageSelect.addEventListener('change', (event) => {
  language = event.target.value;
  document.documentElement.lang = language;
  applyTranslations();
});

applyTranslations();
