/* BrigAdress Showcase WebApp (vanilla JS)
   - loads content from FastAPI
   - creates leads (requires Telegram initData)
   - admin area (requires admin Telegram ID)
*/
const view = document.getElementById('view');
const tabs = document.getElementById('tabs');
const userLine = document.getElementById('tg-user-line');

const tg = window.Telegram?.WebApp;
const initData = tg?.initData || "";

function setUserLine() {
  if (!tg) {
    userLine.textContent = "Открыто в браузере (для создания заявки открой через Telegram)";
    return;
  }
  tg.ready();
  tg.expand();
  const u = tg.initDataUnsafe?.user;
  userLine.textContent = u ? `Вы: ${u.first_name || ""} ${u.last_name || ""} (@${u.username || "без_юзернейма"})` : "Telegram WebApp";
}
setUserLine();

function h(tag, attrs={}, children=[]) {
  const el = document.createElement(tag);
  Object.entries(attrs).forEach(([k,v])=>{
    if (k === "class") el.className = v;
    else if (k.startsWith("on") && typeof v === "function") el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, v);
  });
  (Array.isArray(children) ? children : [children]).forEach(ch=>{
    if (ch === null || ch === undefined) return;
    if (typeof ch === "string") el.appendChild(document.createTextNode(ch));
    else el.appendChild(ch);
  });
  return el;
}

async function apiGet(path) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function apiAuth(path, opts={}) {
  const headers = Object.assign({}, opts.headers || {});
  headers["Content-Type"] = "application/json";
  if (initData) headers["X-Telegram-Init-Data"] = initData;
  const res = await fetch(path, Object.assign({}, opts, { headers }));
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function renderFAQ(items) {
  const grid = h("div", {class:"wa-grid"});
  items.forEach(it=>{
    grid.appendChild(
      h("div",{class:"wa-card"},[
        h("div",{style:"font-weight:900;margin-bottom:6px"}, it.question),
        h("div",{class:"wa-muted",style:"white-space:pre-wrap"}, it.answer)
      ])
    );
  });
  return grid;
}

function renderDocs(items) {
  const grid = h("div",{class:"wa-grid"});
  items.forEach(it=>{
    grid.appendChild(
      h("div",{class:"wa-card"},[
        h("div",{style:"font-weight:900;margin-bottom:6px"}, it.title),
        h("a",{class:"wa-btn primary",href:it.url,target:"_blank",rel:"noopener"}, "Скачать PDF")
      ])
    );
  });
  return grid;
}

function renderProjects(items) {
  const grid = h("div",{class:"wa-grid"});
  items.forEach(it=>{
    grid.appendChild(
      h("div",{class:"wa-card"},[
        h("div",{style:"font-weight:900;margin-bottom:6px"}, it.title),
        h("div",{class:"wa-muted"}, it.description || ""),
        it.image ? h("div",{class:"wa-muted",style:"margin-top:8px;font-size:12px"}, `Image: ${it.image}`) : null,
        h("div",{style:"margin-top:10px"},[
          h("span",{class:"wa-badge"},"Реальные данные из brigadress.ru")
        ])
      ])
    );
  });
  return grid;
}

function renderLeadForm() {
  const note = !tg ? h("div",{class:"wa-card"},[
    h("div",{style:"font-weight:900;margin-bottom:6px"}, "Важно"),
    h("div",{class:"wa-muted"}, "Создание заявки работает только внутри Telegram, потому что используется авторизация WebApp (initData).")
  ]) : null;

  const form = h("div",{class:"wa-card"},[
    h("div",{style:"font-weight:900;margin-bottom:8px"}, "Заявка на ремонт / подбор подрядчика"),
    h("div",{class:"wa-row"},[
      h("input",{class:"wa-input",placeholder:"Имя",id:"lead_name"}),
      h("input",{class:"wa-input",placeholder:"Телефон",id:"lead_phone"}),
    ]),
    h("div",{class:"wa-row",style:"margin-top:8px"},[
      h("input",{class:"wa-input",placeholder:"Город",id:"lead_city"}),
      h("input",{class:"wa-input",placeholder:"Тип работ (например: плитка, электрика)",id:"lead_work"}),
    ]),
    h("div",{class:"wa-row",style:"margin-top:8px"},[
      h("input",{class:"wa-input",placeholder:"Бюджет (например: до 500 000 ₽)",id:"lead_budget"}),
    ]),
    h("textarea",{class:"wa-input",placeholder:"Коротко опиши задачу",id:"lead_desc",style:"margin-top:8px;min-height:120px"}),
    h("div",{class:"wa-muted",style:"margin-top:8px"}, "Фото/видео можно отправить прямо боту — он привяжет их к заявке (это часть демо)."),
    h("div",{class:"wa-row",style:"margin-top:10px"},[
      h("button",{class:"wa-btn primary",onclick: async (e)=>{
        e.preventDefault();
        try{
          const payload = {
            lead_type: "client_request",
            name: document.getElementById("lead_name").value || null,
            phone: document.getElementById("lead_phone").value || null,
            city: document.getElementById("lead_city").value || null,
            work_type: document.getElementById("lead_work").value || null,
            budget: document.getElementById("lead_budget").value || null,
            description: document.getElementById("lead_desc").value || null,
          };
          const data = await apiAuth("/api/leads", {method:"POST", body: JSON.stringify(payload)});
          view.innerHTML = "";
          view.appendChild(h("div",{class:"wa-card"},[
            h("div",{style:"font-weight:900;margin-bottom:6px"}, "Готово ✅"),
            h("div",{class:"wa-muted"}, `Заявка #${data.id} создана. Статус: ${data.status}.`),
            h("div",{class:"wa-muted",style:"margin-top:6px"}, "Это демо-бот. В реальном проекте здесь будет чат с менеджером/CRM/статусы.")
          ]));
        }catch(err){
          alert("Ошибка: " + err.message);
        }
      }}, "Отправить заявку")
    ])
  ]);

  const wrapper = h("div",{class:"wa-grid"});
  if (note) wrapper.appendChild(note);
  wrapper.appendChild(form);
  return wrapper;
}

function statusBadge(status) {
  const map = {new:"NEW", in_progress:"IN PROGRESS", done:"DONE", rejected:"REJECTED"};
  return map[status] || status;
}

function renderAdminIntro() {
  return h("div",{class:"wa-card"},[
    h("div",{style:"font-weight:900;margin-bottom:8px"}, "Админка"),
    h("div",{class:"wa-muted"}, "Здесь видно, что проект умеет: авторизация, роли, работа с базой, экспорт, статусы."),
    h("div",{class:"wa-muted",style:"margin-top:6px"}, "Если ты не админ (по Telegram ID), сервер вернёт 403.")
  ]);
}

async function renderAdmin() {
  const wrap = h("div",{class:"wa-grid"},[renderAdminIntro()]);
  if (!tg) return wrap;

  try{
    const leads = await apiAuth("/api/admin/leads?limit=200", {method:"GET"});
    const table = h("table",{class:"wa-table"});
    table.appendChild(h("thead",{},[
      h("tr",{},[
        h("th",{},"ID"),
        h("th",{},"Тип"),
        h("th",{},"Контакт"),
        h("th",{},"Детали"),
        h("th",{},"Статус"),
        h("th",{},"Действия")
      ])
    ]));
    const tbody = h("tbody");
    leads.forEach(l=>{
      const actions = h("div",{class:"wa-row"},[
        h("button",{class:"wa-btn",onclick: async ()=>{
          const s = prompt("Новый статус (new / in_progress / done / rejected):", l.status);
          if (!s) return;
          try{
            await apiAuth(`/api/admin/leads/${l.id}`, {method:"PATCH", body: JSON.stringify({status:s})});
            loadTab("admin");
          }catch(err){ alert("Ошибка: " + err.message); }
        }},"Статус"),
      ]);
      tbody.appendChild(h("tr",{},[
        h("td",{}, String(l.id)),
        h("td",{}, l.lead_type),
        h("td",{}, (l.name||"") + "\n" + (l.phone||"")),
        h("td",{}, (l.city||"") + "\n" + (l.work_type||"") + "\n" + (l.budget||"")),
        h("td",{}, h("span",{class:"wa-status"}, statusBadge(l.status))),
        h("td",{}, actions)
      ]));
    });
    table.appendChild(tbody);

    const exportBtn = h("a",{class:"wa-btn primary",href:"#",onclick:(e)=>{
      e.preventDefault();
      // open export in same webview
      const url = "/api/admin/export/leads.csv";
      // we must include initData - easiest is to fetch and download as blob
      (async ()=>{
        try{
          const headers = {"X-Telegram-Init-Data": initData};
          const res = await fetch(url, {headers});
          if(!res.ok) throw new Error(await res.text());
          const blob = await res.blob();
          const a = document.createElement("a");
          a.href = URL.createObjectURL(blob);
          a.download = "leads.csv";
          document.body.appendChild(a);
          a.click();
          a.remove();
        }catch(err){ alert("Ошибка экспорта: " + err.message); }
      })();
    }}, "Экспорт CSV");

    wrap.appendChild(h("div",{class:"wa-card"},[
      h("div",{style:"font-weight:900;margin-bottom:8px"}, `Заявки (${leads.length})`),
      exportBtn,
      h("div",{style:"margin-top:10px;overflow:auto"}, table)
    ]));

  }catch(err){
    wrap.appendChild(h("div",{class:"wa-card"},[
      h("div",{style:"font-weight:900;margin-bottom:6px"}, "Доступ ограничен"),
      h("div",{class:"wa-muted"}, "Сервер не дал доступ (скорее всего ты не в ADMIN_TELEGRAM_IDS)."),
      h("div",{class:"wa-muted",style:"margin-top:6px"}, "Текст ошибки: " + err.message)
    ]));
  }
  return wrap;
}

async function loadTab(tab) {
  [...tabs.querySelectorAll(".wa-tab")].forEach(t=>t.classList.toggle("active", t.dataset.tab === tab));
  view.innerHTML = "";
  const loader = h("div",{class:"wa-card"},[
    h("div",{style:"font-weight:900;margin-bottom:6px"},"Загрузка…"),
    h("div",{class:"wa-muted"},"Подтягиваем данные с API")
  ]);
  view.appendChild(loader);

  try{
    if (tab === "faq") {
      const items = await apiGet("/api/content/faq");
      view.innerHTML = ""; view.appendChild(renderFAQ(items));
    } else if (tab === "docs") {
      const items = await apiGet("/api/content/documents");
      view.innerHTML = ""; view.appendChild(renderDocs(items));
    } else if (tab === "projects") {
      const items = await apiGet("/api/content/projects");
      view.innerHTML = ""; view.appendChild(renderProjects(items));
    } else if (tab === "lead") {
      view.innerHTML = ""; view.appendChild(renderLeadForm());
    } else if (tab === "admin") {
      view.innerHTML = ""; view.appendChild(await renderAdmin());
    }
  }catch(err){
    view.innerHTML = "";
    view.appendChild(h("div",{class:"wa-card"},[
      h("div",{style:"font-weight:900;margin-bottom:6px"},"Ошибка"),
      h("div",{class:"wa-muted"}, err.message)
    ]));
  }
}

tabs.addEventListener("click", (e)=>{
  const t = e.target.closest(".wa-tab");
  if (!t) return;
  loadTab(t.dataset.tab);
});

// default
loadTab("faq");
