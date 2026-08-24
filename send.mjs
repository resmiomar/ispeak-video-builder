// Отправка собранных выпусков в Telegram.
//
// Отдельный файл без зависимостей: в этом репозитории нет ни package.json, ни
// node_modules, а Node 24 умеет и fetch, и FormData сам.
//
//   node send.mjs                 # всё, что лежит в video/out
//   node send.mjs слово           # только выпуски, чьё имя содержит слово
import { readdirSync, statSync, readFileSync } from "node:fs";
import path from "node:path";

const OUT = path.join(process.cwd(), "video", "out");
const TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const CHAT = process.env.TELEGRAM_CHAT_ID;
// Бот не может отправить файл тяжелее 50 МБ, а урок правила на семи минутах
// подходит к границе, поэтому размер проверяется до отправки.
const LIMIT = 50 * 1024 * 1024;

const KINDS = {
  letters: "Буквы",
  words: "Слова",
  dialogue: "Разговор",
  grammar: "Правило",
  mistakes: "Ошибки",
};
const AGES = { G1: "7-9 лет", G2: "10-13 лет", G3: "14-17 лет" };

function caption(name) {
  const parts = name.replace(/\.mp4$/, "").split("-");
  const lang = parts.at(-1);
  const age = parts.at(-2);
  return `${KINDS[parts[0]] ?? parts[0]}: ${parts.slice(1, -2).join(" ")} · ${AGES[age] ?? age} · ${lang}`;
}

async function send(file) {
  const size = statSync(path.join(OUT, file)).size;
  if (size > LIMIT) {
    console.log(`✗ ${file}: ${(size / 1048576).toFixed(1)} МБ, больше предела Telegram`);
    return false;
  }
  const form = new FormData();
  form.append("chat_id", CHAT);
  form.append("caption", caption(file));
  form.append("supports_streaming", "true");
  form.append("video", new Blob([readFileSync(path.join(OUT, file))], { type: "video/mp4" }), file);

  // Десять машин шлют в один канал одновременно, и Telegram отбивает часть
  // файлов по частоте. Он же говорит, сколько ждать, поэтому ждём именно
  // столько и пробуем снова: иначе выпуск просто теряется.
  let result;
  for (let attempt = 0; attempt < 5; attempt += 1) {
    const response = await fetch(`https://api.telegram.org/bot${TOKEN}/sendVideo`, { method: "POST", body: form });
    result = await response.json();
    if (result.ok) break;
    const wait = result.parameters?.retry_after;
    if (!wait) break;
    console.log(`… ${file}: жду ${wait} с и повторяю`);
    await new Promise((resolve) => setTimeout(resolve, (wait + 2) * 1000));
  }
  if (!result.ok) {
    console.log(`✗ ${file}: ${result.description}`);
    return false;
  }
  console.log(`✓ ${file} (${(size / 1048576).toFixed(1)} МБ)`);
  return true;
}

const only = process.argv[2] ?? "";
const files = readdirSync(OUT).filter((name) => name.endsWith(".mp4") && name.includes(only)).sort();
let sent = 0;
for (const file of files) {
  if (await send(file)) sent += 1;
  // Пауза между отправками: без неё Telegram отбивает половину файлов по частоте.
  await new Promise((resolve) => setTimeout(resolve, 2500));
}
console.log(JSON.stringify({ отправлено: sent, всего: files.length }, null, 1));
