"use strict";
const $ = id => document.getElementById(id);
const titles = {all: "Усі поля", instance: "Інстанс", network: "Мережа", placement: "Розміщення", identity: "Ідентичність", other: "Інші дані"};
const statusNames = {ok: "значення", directory: "каталог", hidden: "приховано", error: "недоступно"};
let snapshot = null, category = "all", polling = null;
function group(path) {
  if (path.startsWith("dynamic/") || path.includes("/iam/") || path.includes("/identity-credentials/") || path.includes("/public-keys/")) return "identity";
  if (path.includes("/network/") || /meta-data\/(local-|public-|mac$|security-groups)/.test(path)) return "network";
  if (path.includes("/placement/")) return "placement";
  if (/meta-data\/(ami-|instance-|hostname$|block-device-mapping\/)/.test(path)) return "instance";
  return "other";
}
function field(path) {
  return snapshot?.records.find(record => record.path === path && record.status === "ok")?.value || "—";
}
function render() {
  if (!snapshot) return;
  $("instance").textContent = field("meta-data/instance-id");
  $("type").textContent = field("meta-data/instance-type");
  $("region").textContent = field("meta-data/placement/availability-zone");
  $("ip").textContent = field("meta-data/local-ipv4");
  $("mode").textContent = snapshot.demo ? "ДЕМОРЕЖИМ · зразкові дані, без звернень до AWS." : "Живі дані цього інстанса через IMDSv2.";
  const messages = {loading: "Збирання метаданих…", ready: "Метадані отримано", partial: "Частину даних не вдалося отримати", unavailable: "Метадані недоступні"};
  $("status").textContent = messages[snapshot.state] + (snapshot.refreshing && snapshot.state !== "loading" ? " · оновлення…" : "");
  $("dot").className = "dot " + (snapshot.state === "ready" ? "ready" : ["partial", "unavailable"].includes(snapshot.state) ? "error" : "");
  $("updated").textContent = snapshot.updated_at ? "Оновлено " + new Date(snapshot.updated_at).toLocaleTimeString("uk-UA") : "";
  $("download").disabled = !snapshot.records.length;
  $("refresh").disabled = snapshot.refreshing;
  $("notice").hidden = !["partial", "unavailable"].includes(snapshot.state);
  $("notice").textContent = snapshot.truncated ? "Досягнуто ліміту обходу. Показано частковий знімок." : snapshot.state === "unavailable" ? "IMDS доступний усередині EC2. Перевірте, чи ввімкнено metadata endpoint. Для локального перегляду запустіть застосунок із --demo." : "Окремі категорії повернули помилку. Деталі наведено біля відповідного шляху.";
  const nav = $("categories");
  nav.replaceChildren();
  const leaves = snapshot.records.filter(record => record.status !== "directory");
  Object.entries(titles).forEach(([key, label]) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = key === category ? "active" : "";
    button.setAttribute("aria-pressed", String(key === category));
    const name = document.createElement("span"), amount = document.createElement("span");
    name.textContent = label;
    amount.textContent = leaves.filter(record => key === "all" || group(record.path) === key).length;
    button.append(name, amount);
    button.addEventListener("click", () => { category = key; render(); });
    nav.append(button);
  });
  $("section-title").textContent = titles[category];
  const search = $("search").value.toLocaleLowerCase("uk-UA");
  const records = leaves.filter(record => (category === "all" || group(record.path) === category) &&
    (record.path + "\n" + record.value).toLocaleLowerCase("uk-UA").includes(search));
  $("count").textContent = records.length + " полів · " + (snapshot.requests || 0) + " запитів до джерела";
  const container = $("records");
  const opened = new Set([...container.querySelectorAll("details[open]")].map(item => item.dataset.path));
  container.replaceChildren();
  if (!records.length) {
    const empty = document.createElement("div");
    empty.className = "empty";
    empty.textContent = snapshot.state === "loading" ? "Вебсервер збирає дані інстанса." : "За заданими умовами полів немає.";
    container.append(empty);
  }
  records.forEach(record => {
    const detail = document.createElement("details"), summary = document.createElement("summary");
    detail.dataset.path = record.path; detail.dataset.status = record.status; detail.open = opened.has(record.path);
    const path = document.createElement("code"), badge = document.createElement("span"), value = document.createElement("pre");
    path.textContent = record.path; badge.className = "record-status";
    badge.textContent = statusNames[record.status] || record.status;
    value.textContent = record.value;
    summary.append(path, badge); detail.append(summary, value); container.append(detail);
  });
}
async function load() {
  try {
    const response = await fetch("/api/metadata", {cache: "no-store"});
    if (!response.ok) throw new Error("HTTP " + response.status);
    snapshot = await response.json(); render();
    clearTimeout(polling);
    polling = setTimeout(load, snapshot.refreshing || snapshot.state === "loading" ? 2000 : 10000);
  } catch (error) {
    $("status").textContent = "Немає зв'язку з вебсервером";
    $("dot").className = "dot error";
    clearTimeout(polling); polling = setTimeout(load, 5000);
  }
}
$("search").addEventListener("input", render);
$("refresh").addEventListener("click", async () => {
  $("refresh").disabled = true;
  try {
    const response = await fetch("/api/refresh", {method: "POST"});
    if (response.status === 429) $("status").textContent = "Наступне оновлення доступне через 30 секунд після попереднього.";
    else if (!response.ok) throw new Error("HTTP " + response.status);
    else await load();
  } catch (error) { $("status").textContent = "Не вдалося запустити оновлення."; }
  finally { $("refresh").disabled = !!snapshot?.refreshing; }
});
$("download").addEventListener("click", () => {
  const url = URL.createObjectURL(new Blob([JSON.stringify(snapshot, null, 2)], {type: "application/json"}));
  const link = document.createElement("a");
  link.href = url; link.download = "ec2-metadata.json"; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
load();
