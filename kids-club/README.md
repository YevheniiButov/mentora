# Oekrainse Kids Club - Website

Сайт для українського дитячого клубу в Амстердамі.

## Встановлення

```bash
# Встановити залежності
npm install

# Запустити dev сервер
npm run dev
```

Сайт буде доступний на `http://localhost:3000`

## Деплой на Vercel

1. Створи репозиторій на GitHub
2. Push код туди:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

3. Іди на [vercel.com](https://vercel.com)
4. Натисни "New Project"
5. Імпортуй свій GitHub репо
6. Vercel автоматично задеплоїть проект
7. Готово! 🎉

## Структура проекту

```
kids-club/
├── app/
│   ├── page.js       # Головна сторінка
│   ├── layout.js     # Layout
│   └── globals.css   # Глобальні стилі
├── components/
│   └── ui/           # UI компоненти
├── lib/
│   └── utils.js      # Утиліти
└── package.json
```

## Що далі?

Після деплою можна додати:
- Firebase для галереї фотографій
- Адмін панель для вчителя
- Секцію новин

## Технології

- Next.js 14
- React 18
- Tailwind CSS
- shadcn/ui
- Lucide Icons
