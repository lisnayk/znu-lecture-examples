const byId = id => document.getElementById(id);
const buttons = [byId('check'), byId('refresh')];
const labels = {ok:'Пройдено', error:'Помилка', waiting:'Очікування', skipped:'Пропущено'};
function render(data) {
  byId('mode').textContent = data.mode === 'demo' ? 'Локальне демо' : 'Secrets Manager + роль EC2';
  byId('demo-note').hidden = data.mode !== 'demo';
  byId('summary').textContent = data.ok
    ? 'Усі етапи пройдено. Кеш секрета: ще ' + data.cache_seconds + ' с.' + (data.credential_reloaded ? ' Після відхиленого пароля секрет перечитано.' : '')
    : 'Перевірку зупинено. Перегляньте етап із помилкою.';
  byId('stages').replaceChildren(...data.stages.map(stage => {
    const li = document.createElement('li');
    li.dataset.status = stage.status;
    for (const [className, text] of [['stage-title',stage.title], ['tag',labels[stage.status]], ['stage-detail',stage.detail]]) {
      const span = document.createElement('span'); span.className = className; span.textContent = text; li.append(span);
    }
    return li;
  }));
  byId('db-info').textContent = data.database
    ? data.database.name + ' / ' + data.database.username + ' / ' + data.database.tls_version
    : 'З’єднання не підтверджено.';
  const rows = data.records.map(record => {
    const tr = document.createElement('tr');
    for (const text of [record.id, record.message]) {
      const td = document.createElement('td'); td.textContent = text; tr.append(td);
    }
    return tr;
  });
  if (!rows.length) {
    const tr = document.createElement('tr'), td = document.createElement('td');
    td.colSpan = 2; td.textContent = data.ok ? 'Таблиця порожня.' : 'Дані недоступні.'; tr.append(td); rows.push(tr);
  }
  byId('records').replaceChildren(...rows);
  byId('timestamp').textContent = 'Перевірено ' + new Date(data.checked_at).toLocaleString('uk-UA');
}
async function check(refresh = false) {
  buttons.forEach(button => { button.disabled = true; });
  byId('summary').textContent = 'Перевіряємо роль, секрет і базу даних…';
  try {
    const response = await fetch(refresh ? '/api/refresh' : '/api/status',
      refresh ? {method:'POST', headers:{'X-Demo-Request':'1'}} : {cache:'no-store'});
    if (!response.ok) throw new Error('HTTP');
    render(await response.json());
  } catch {
    byId('summary').textContent = 'Не вдалося отримати результат. Перевірте службу застосунку та мережу.';
  } finally {
    buttons.forEach(button => { button.disabled = false; });
  }
}
byId('check').addEventListener('click', () => check());
byId('refresh').addEventListener('click', () => check(true));
check();
