(function () {

  function runOutsideAngular(callbackFunction) {
    if (window.Zone && Zone.current && Zone.current.runOutsideAngular) {
      Zone.current.runOutsideAngular(callbackFunction);
    } else {
      callbackFunction();
    }
  }

  runOutsideAngular(function () {

    const script = document.currentScript;
    const params = new URLSearchParams((script.src.split("?")[1] || ""));
    const token = params.get("token");
    const userLang = script.dataset.lang || "en";

    if (!token) {
      console.warn("No token provided — running in DEV mode");
    }

    // Подключение CSS
    const css = document.createElement("link");
    css.rel = "stylesheet";
    css.href = new URL("./widget/style.css", script.src).href;
    document.head.appendChild(css);

    // ЛОКАЛИЗАЦИИ
    const i18n = {
      en: {
        welcome: "Мы тут чтобы помочь! 👋",
        agents: "Наши операторы доступны",
        links: "Полезные ссылки",
        faq: "FAQ",
        contact: "Связаться с нами",
        start: "Чат начат, введите вопрос",
        emailPlaceholder: "eg. john@gmail.com",
        continue: "Подтвердить",
        invalidEmail: "Пожалуйста, введите имейл, чтобы начать чат",
        typeMessage: "Type a message...",
        enterEmailFirst: "Пожалуйста, введите имейл, чтобы начать чат"
      },
      ru: {
        welcome: "Мы готовы помочь! 👋",
        agents: "Наши операторы доступны",
        links: "ПОЛЕЗНЫЕ ССЫЛКИ",
        faq: "FAQ",
        contact: "Связаться с нами",
        start: "Чат начат, введите ваш вопрос",
        emailPlaceholder: "например: ivan@gmail.com",
        continue: "Продолжить",
        invalidEmail: "Введите правильный email.",
        typeMessage: "Введите сообщение...",
        enterEmailFirst: "Введите email, чтобы начать чат."
      },
      pl: {
        welcome: "Jesteśmy tutaj, aby pomóc! 👋",
        agents: "Konsultanci są dostępny",
        links: "PRZYDATNE LINKI",
        faq: "FAQ",
        contact: "Kontakt",
        start: "Rozpocznij rozmowę, wpisz pytanie",
        emailPlaceholder: "np. jan@gmail.com",
        continue: "Kontynuuj",
        invalidEmail: "Wpisz poprawny email.",
        typeMessage: "Napisz wiadomość...",
        enterEmailFirst: "Podaj email, aby rozpocząć rozmowę."
      }
    };

    const t = i18n[userLang] || i18n.en;

    // SVG АВАТАР
    const BOT_AVATAR_SVG = `
      <svg viewBox="0 0 186 186" xmlns="http://www.w3.org/2000/svg">
        <path d="M93.3 140.4h0c-6.9.1-13.5-1.5-19.4-4.9l-5.5 9.9c7.5 4.3 15.7 6.4 24.4 6.4h.5c8.9 0 17.3-2.1 25-6.4l-5.5-9.9c-5.9 3.4-12.4 5-19.4 4.9h0zM186 0H0v186h186V0zM92.8 175.6c-44.1 0-80.3-34.7-82.7-78.2 1.1 0 2.2-.6 3-1.6l35.4-41.3c2.1-2.4 5.7-2.4 7.8 0l28.1 31.8c2.1 2.4 5.2 3.8 8.4 3.8h0c3.2 0 6.2-1.4 8.4-3.7l28.5-31.9c1-1.1 2.4-2.4 3.9-2.4s2.9 1.3 3.8 2.3l35 41.4c.8.9 1.9 1.5 3 1.6-2.4 43.5-38.6 78.2-82.7 78.2h0zM55.7 94.3c-6.4 0-11.5 5.2-11.5 11.5s5.2 11.5 11.5 11.5 11.5-5.2 11.5-11.5S62 94.3 55.7 94.3zm-1.4 8.9l-1 3.1-1-3.1-3.1-1 3.1-1 1-3.1 1 3.1 3.1 1-3.1 1zm79.4-8.9c-6.4 0-11.5 5.2-11.5 11.5s5.2 11.5 11.5 11.5 11.5-5.2 11.5-11.5-5.2-11.5-11.5-11.5zm-1.4 8.9l-1 3.1-1-3.1-3.1-1 3.1-1 1-3.1 1 3.1 3.1 1-3.1 1z"/>
      </svg>
    `;

    // ИКОНКИ ДЛЯ КНОПКИ ОТПРАВКИ / ПАУЗЫ
    const SEND_ICON_SVG = `
      <svg viewBox="0 0 24 24">
        <path d="M2 21l21-9L2 3v7l15 2-15 2v7z"></path>
      </svg>
    `;

    const PAUSE_ICON_SVG = `
      <svg viewBox="0 0 24 24">
        <rect x="6" y="4" width="4" height="16"></rect>
        <rect x="14" y="4" width="4" height="16"></rect>
      </svg>
    `;

function convertCruiseMarkdown(text) {
  if (!text) return "";

  const lines = text
    .split("\n")
    .map(l => l.trim())
    .filter(Boolean);

  const cruises = [];
  const freeText = [];

  let block = [];
  let inCruiseBlock = false;

  const URL_REG = /(https?:\/\/\S+)/i;
  const PRICE_REG = /(?:Price[:\s-]*from\s*\$?|Цена[:\s-]*от\s*\$?)(\d[\d\s]*)/i;
  const NIGHTS_REG = /Nights[:\s-]*(\d+)|(\d+)\s*ноч/i;

  // ---------- SAVE BLOCK ----------
  function saveBlock() {
    if (!block.length) return;

    const raw = block.join("\n");

    const url = (raw.match(URL_REG) || [])[1] || "";
    const price = (raw.match(PRICE_REG) || [])[1] || "";
    const nm = raw.match(NIGHTS_REG);
    const nights = nm ? nm[1] || nm[2] : "";

    const depMatch = raw.match(/Departure\/Return[:\s-]*([^\n]+)/i);
    const departure = depMatch ? depMatch[1].trim() : "";

    // ROUTE multiline
    let routeList = [];
    const startIdx = block.findIndex(l => /^Route[:\s-]*/i.test(l));

    if (startIdx !== -1) {
      const routeLines = [];

      for (let i = startIdx + 1; i < block.length; i++) {
        if (/^(Nights|Price|Link)/i.test(block[i])) break;
        routeLines.push(block[i]);
      }

      routeList = routeLines
        .join(" ")
        .split(/→|,/)
        .map(s => s.trim())
        .filter(Boolean);
    }

    const hasData = url || price || nights || departure || routeList.length;

    if (hasData) {
      cruises.push({ nights, price, url, departure, routeList });
    } else {
      freeText.push(raw);
    }

    block = [];
    inCruiseBlock = false;
  }

  // ---------- BUILD BLOCKS ----------
  lines.forEach(line => {
    if (/^Departure\/Return/i.test(line)) {
      saveBlock();
      inCruiseBlock = true;
      block.push(line);
      return;
    }

    if (inCruiseBlock) {
      block.push(line);

      if (URL_REG.test(line)) {
        saveBlock();
      }
      return;
    }

    // обычный текст
    freeText.push(line);
  });

  saveBlock();

  // ---------- RENDER ----------
  let html = "";

  freeText.forEach(t => {
    html += `<div class="cc-cru-text">${t}</div>`;
  });

  cruises.forEach(c => {
    html += `
      <div class="cru-card">
        <div class="cc-cru-title">Круиз</div>

        <div class="cc-cru-desc">
          <div class="cc-cru-toprow">
            ${c.nights ? `<div class="cc-cru-nights"><b>${c.nights} ночей</b></div>` : ""}
            ${c.price ? `<div class="cc-cru-price"><b>Цена — от ${c.price}</b></div>` : ""}
          </div>

          ${c.departure
            ? `<div class="cc-cru-departure"><b>Отправление/возврат:</b> ${c.departure}</div>`
            : ""
          }

          ${c.routeList.length
            ? `
              <div class="cc-cru-route-wrapper">
                <div class="cc-cru-route-title">Маршрут:</div>
                <div class="cc-cru-route-text">${c.routeList.join(" → ")}</div>
              </div>
            `
            : ""
          }
        </div>

        ${c.url
          ? `<a href="${c.url}" class="cc-cru-btn" target="_blank">Подробнее →</a>`
          : ""
        }
      </div>
    `;
  });

  return html;
}


    // Non-cruise text:
    freeText.push(line);
  });

  saveBlock();

  // ---------- RENDER ----------
  let html = "";

  // Render free text normally
  freeText.forEach(t => {
    html += `<div class="cc-cru-text">${t}</div>`;
  });

  // Render cruise cards
  cruises.forEach(c => {
    html += `
      <div class="cru-card">

        <div class="cc-cru-title">Круиз</div>

        <div class="cc-cru-desc">

          <div class="cc-cru-toprow">
            <div class="cc-cru-nights"><b>${c.nights || "7"} ночей</b></div>
            <div class="cc-cru-price"><b>Цена — от ${c.price}</b></div>
          </div>

          ${
            c.departure
              ? `<div class="cc-cru-departure"><b>Отправление/возврат:</b> ${c.departure}</div>`
              : ""
          }

          ${
            c.routeList.length
              ? `
              <div class="cc-cru-route-wrapper">
                <div class="cc-cru-route-title">Маршрут:</div>
                <div class="cc-cru-route-text">${c.routeList.join(" → ")}</div>
              </div>`
              : ""
          }

        </div>

        ${
          c.url
            ? `<a href="${c.url}" class="cc-cru-btn" target="_blank">Подробнее →</a>`
            : `<button class="cc-cru-btn">Подробнее →</button>`
        }

      </div>
    `;
  });

  return html;
}



    //
    // СОЗДАНИЕ UI
    //
    const wrapper = document.createElement("div");
    wrapper.className = "cc-wrapper";

    // FAB кнопка чата
    const fab = document.createElement("button");
    fab.className = "cc-fab";
    fab.innerHTML =
      `<svg viewBox="0 0 40 40">
         <path d="M5.33333 6H32C33.8333 6 35.3333 7.5 35.3333 9.33333V29.3333C35.3333 31.1667 33.8333 32.6667 32 32.6667H8.66667L2 39.3333V9.33333C2 7.5 3.5 6 5.33333 6Z"></path>
       </svg>`;

    // Основная панель
    const panel = document.createElement("div");
    panel.className = "cc-panel";
    panel.style.height = "390px";

    //
    // SCREEN 1 (welcome экран)
    //
    const screen1 = document.createElement("div");
    screen1.className = "cc-screen1";
    screen1.innerHTML = `
      <button class="cc-screen1-close">✕</button>

      <div class="cc-top-avatars">
        <img src="https://center.cruises/image/00000000-0000-0000-0000-056287328382-f1t1-w500.jpeg">
        <img src="https://center.cruises/image/00000000-0000-0000-0000-056287329137-f1t1-w500.jpeg">
        <img src="https://center.cruises/image/00000000-0000-0000-0000-056287332688-f1t1-w500.jpeg">
      </div>

      <div class="cc-title1">${t.welcome}</div>
      <div class="cc-sub1">${t.agents}</div>

      <div class="cc-links-box">
        <div class="cc-links-title">${t.links}</div>

        <a href="https://center.cruises/for-tourists/" target="_blank" class="cc-link-item">
          <span>${t.faq}</span>
          <svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M13 5l7 7l-7 7v-4H4v-6h9V5z"></path>
          </svg>
        </a>

        <a href="https://center.cruises/contact/" target="_blank" class="cc-link-item">
          <span>${t.contact}</span>
          <svg viewBox="0 0 24 24">
            <path fill="currentColor" d="M13 5l7 7l-7 7v-4H4v-6h9V5z"></path>
          </svg>
        </a>
      </div>

      <button class="cc-start-btn">${t.start}</button>
    `;

    //
    // SCREEN 2 (основной чат)
    //
    const screen2 = document.createElement("div");
    screen2.className = "cc-screen2";
    screen2.style.display = "none";

    // HEADER
    const header = document.createElement("div");
    header.className = "cc-header";
    header.innerHTML = `
      Chat
      <button class="cc-close">✕</button>
    `;

    // Тело переписки
    const body = document.createElement("div");
    body.className = "cc-body";

    //
    // Ввод почты
    //
    const emailArea = document.createElement("div");
    emailArea.className = "cc-email-area";
    emailArea.innerHTML = `
      <input class="cc-email-input" placeholder="${t.emailPlaceholder}">
      <button class="cc-email-btn">${t.continue}</button>
    `;

    //
    // Поле ввода текста
    //
    const inputArea = document.createElement("div");
    inputArea.className = "cc-input-area";
    inputArea.style.display = "none";

    inputArea.innerHTML = `
      <div class="cc-input-container">
        <input class="cc-input" placeholder="${t.typeMessage}">
        <button class="cc-input-send">
          ${SEND_ICON_SVG}
        </button>
      </div>
    `;

    // Формируем screen2
    screen2.append(header, body, emailArea, inputArea);

    // FINALLY: assemble widget
    panel.append(screen1, screen2);
    wrapper.append(fab, panel);
    document.body.append(wrapper);

    //
    // ПОЛУЧАЕМ ЭЛЕМЕНТЫ ДЛЯ ЛОГИКИ
    //
    const closeScreen1Btn = screen1.querySelector(".cc-screen1-close");
    const closeBtn = header.querySelector(".cc-close");
    const startBtn = screen1.querySelector(".cc-start-btn");
    const emailInput = emailArea.querySelector(".cc-email-input");
    const emailBtn = emailArea.querySelector(".cc-email-btn");
    const messageInput = inputArea.querySelector(".cc-input");
    const sendBtn = inputArea.querySelector(".cc-input-send");

    let userEmail = null;

    //
    // ФУНКЦИЯ: добавление сообщения (бот / юзер)
    //
    function addMessage(text, who = "bot") {
  const msg = document.createElement("div");
  msg.className = "cc-msg " + who;

  if (who === "bot") {
    msg.innerHTML = `
      <div class="cc-avatar">
        ${BOT_AVATAR_SVG}
      </div>

      <div class="cc-bot-wrapper">
        ${convertCruiseMarkdown(text)}
      </div>
    `;
  } else {
    msg.innerHTML = `
      <div class="cc-text user">
        ${text}
      </div>
    `;
  }

  body.append(msg);
  body.scrollTop = body.scrollHeight;
}


    //
    // ФУНКЦИЯ: показать индикатор "бот печатает..."
    //
    function showTyping() {
      const msg = document.createElement("div");
      msg.className = "cc-msg bot typing";

      msg.innerHTML = `
        <div class="cc-avatar">
          ${BOT_AVATAR_SVG}
        </div>

        <div class="cc-text bot">
          <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      `;

      body.append(msg);
      body.scrollTop = body.scrollHeight;

      return msg;
    }

    //
    // ОТКРЫТИЕ/ЗАКРЫТИЕ ПАНЕЛИ
    //
    fab.onclick = function () {
      panel.style.height = "390px";
      screen1.style.display = "flex";
      screen2.style.display = "none";
      emailArea.style.display = "flex";
      inputArea.style.display = "none";
      panel.classList.add("visible");
    };

    function closePanel() {
      panel.classList.remove("visible");

      setTimeout(() => {
        panel.style.height = "390px";
      }, 300);
    }

    closeScreen1Btn.onclick = closePanel;
    closeBtn.onclick = closePanel;

    //
    // ПЕРЕХОД С Welcome-экрана на основной чат
    //
    startBtn.onclick = function () {
      screen1.style.display = "none";
      screen2.style.display = "flex";

      panel.style.height = "600px";

      // ТЕПЕРЬ: только одно сообщение про email
      body.innerHTML = "";
      addMessage(t.enterEmailFirst, "bot");

      emailArea.style.display = "flex";
      inputArea.style.display = "none";
    };

    //
    // ОБРАБОТКА EMAIL
    //
    emailBtn.onclick = function () {
      const mail = emailInput.value.trim();
      const valid = /^\S+@\S+\.\S+$/.test(mail);

      if (!valid) {
        addMessage(t.invalidEmail, "bot");
        return;
      }

      userEmail = mail;

      emailArea.style.display = "none";
      inputArea.style.display = "flex";

      addMessage(t.start, "bot");
    };

    //
    // ОТПРАВКА СООБЩЕНИЯ
    //
    let isSending = false;

    async function sendMessage() {
      // Если сейчас идёт запрос к бэку — блокируем отправку, но не блокируем ввод текста
      if (isSending) {
        return;
      }

      const text = messageInput.value.trim();
      if (!text) return;

      isSending = true;
      sendBtn.disabled = true;
      // поле ввода НЕ блокируем
      messageInput.disabled = false;

      // меняем кнопку на "Пауза"
      sendBtn.classList.add("pause");
      sendBtn.innerHTML = PAUSE_ICON_SVG;

      addMessage(text, "user");
      messageInput.value = "";

      const typingMsg = showTyping();

      try {
        const response = await fetch("http://localhost:3000/api/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            message: text,
            email: userEmail,
            token: token
          })
        });

        const data = await response.json();
        typingMsg.remove();
        addMessage(data.reply || "Empty response", "bot");

      } catch (error) {
        typingMsg.remove();
        addMessage("Error contacting server", "bot");
      }

      isSending = false;
      sendBtn.disabled = false;
      sendBtn.classList.remove("pause");
      sendBtn.innerHTML = SEND_ICON_SVG;
      messageInput.disabled = false;
      messageInput.focus();
    }

    //
    // КНОПКИ И ENTER
    //
    sendBtn.onclick = function () {
      // если пауза/запрос в процессе — просто игнорируем
      if (isSending) return;
      sendMessage();
    };

    messageInput.onkeydown = function (event) {
      if (event.key === "Enter") {
        if (isSending) {
          // во время ответа бота Enter не отправляет сообщение
          event.preventDefault();
          return;
        }
        sendMessage();
      }
    };

  });

})();
