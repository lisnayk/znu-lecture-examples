#!/usr/bin/env bash
# Дим-тест браузерної демонстрації. Перевіряємо не вивід у термінал, а те,
# що проєкт справді збирається і потрібний текст потрапив у збірку.
#
# Пошук іде через Node, а не grep: складальник Angular екранує не-ASCII
# у вигляді \uXXXX, тому текст у файлі є, але дослівно не знаходиться.
set -euo pipefail
cd "$(dirname "$0")"
npm install --no-audit --no-fund >/dev/null 2>&1
npm run build >/dev/null 2>&1
node -e '
  const fs = require("fs");
  const files = fs.globSync(process.argv[1]);
  if (!files.length) { console.error("немає зібраних файлів"); process.exit(1) }
  const text = files.map((f) => fs.readFileSync(f, "utf8")).join("")
    .replace(/\\u([0-9a-fA-F]{4})/g, (_, h) => String.fromCharCode(parseInt(h, 16)));
  if (!text.includes(process.argv[2])) { console.error("маркер не знайдено"); process.exit(1) }
' "dist/assets/*.js" "Лічильник — Svelte"
echo "збірка успішна, маркер знайдено: Лічильник — Svelte"
