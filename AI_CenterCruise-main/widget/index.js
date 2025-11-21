(function () {

  // Функция, которая позволяет выполнить код вне Angular зоны
  function runOutsideAngular(callbackFunction) {
    if (window.Zone && Zone.current && Zone.current.runOutsideAngular) {
      Zone.current.runOutsideAngular(callbackFunction);
    } else {
      callbackFunction();
    }
  }

  // Основной код виджета запускается вне Angular
  runOutsideAngular(function () {

    const script = document.currentScript;
    const params = new URLSearchParams((script.src.split("?")[1] || ""));
    const token = params.get("token");
    const userLang = script.dataset.lang || "en";

if (!token) {
  console.warn("No token provided — running in DEV mode");
}

    const css = document.createElement("link");
    css.rel = "stylesheet";
    css.href = new URL("./widget/style.css", script.src).href;
    document.head.appendChild(css);

    const i18n = {
      en: {
        welcome: "We're here to help! 👋",
        agents: "Support agents are available to chat",
        links: "USEFUL LINKS",
        faq: "FAQ",
        contact: "Contact us",
        start: "Start a conversation ",
        emailPlaceholder: "eg. john@gmail.com",
        continue: "Continue",
        invalidEmail: "Please enter a valid email.",
        typeMessage: "Type a message..."
      },
      ru: {
        welcome: "Мы готовы помочь! 👋",
        agents: "Наши операторы доступны",
        links: "ПОЛЕЗНЫЕ ССЫЛКИ",
        faq: "FAQ",
        contact: "Связаться с нами",
        start: "Начать общение ",
        emailPlaceholder: "например: ivan@gmail.com",
        continue: "Продолжить",
        invalidEmail: "Введите правильный email.",
        typeMessage: "Введите сообщение..."
      },
      pl: {
        welcome: "Jesteśmy tutaj, aby pomóc! 👋",
        agents: "Konsultanci są доступny",
        links: "PRZYDATNE LINKI",
        faq: "FAQ",
        contact: "Kontakt",
        start: "Rozpocznij rozmowę ",
        emailPlaceholder: "np. jan@gmail.com",
        continue: "Kontynuuj",
        invalidEmail: "Wpisz poprawny email.",
        typeMessage: "Napisz wiadomość..."
      }
    };

    const t = i18n[userLang] || i18n.en;

    const wrapper = document.createElement("div");
    wrapper.className = "cc-wrapper";

    const fab = document.createElement("button");
    fab.className = "cc-fab";
    fab.innerHTML =
      `<svg viewBox="0 0 40 40"><path d="M5.33333 6H32C33.8333 6 35.3333 7.5 35.3333 9.33333V29.3333C35.3333 31.1667 33.8333 32.6667 32 32.6667H8.66667L2 39.3333V9.33333C2 7.5 3.5 6 5.33333 6Z"></path></svg>`;

    const panel = document.createElement("div");
    panel.className = "cc-panel";
    panel.style.height = "390px";

    const screen1 = document.createElement("div");
    screen1.className = "cc-screen1";
    screen1.innerHTML = `
      <button class="cc-screen1-close">✕</button>
      <div class="cc-top-avatars">
        <img src="https://images.unsplash.com/photo-1502685104226-ee32379fefbe?w=200">
        <img src="https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=200">
        <img src="https://images.unsplash.com/photo-1544723795-3fb6469f5b39?w=200">
      </div>
      <div class="cc-title1">${t.welcome}</div>
      <div class="cc-sub1">${t.agents}</div>
      <div class="cc-links-box">
        <div class="cc-links-title">${t.links}</div>
        <a href="https://center.cruises/for-tourists/" target="_blank" class="cc-link-item">
          <span>${t.faq}</span>
          <svg viewBox="0 0 24 24"><path fill="currentColor" d="M13 5l7 7l-7 7v-4H4v-6h9V5z"></path></svg>
        </a>
        <a href="https://center.cruises/contact/" target="_blank" class="cc-link-item">
          <span>${t.contact}</span>
          <svg viewBox="0 0 24 24"><path fill="currentColor" d="M13 5l7 7l-7 7v-4H4v-6h9В5z"></path></svg>
        </a>
      </div>
      <button class="cc-start-btn">${t.start}</button>
    `;

    const screen2 = document.createElement("div");
    screen2.className = "cc-screen2";
    screen2.style.display = "none";

    const header = document.createElement("div");
    header.className = "cc-header";
    header.innerHTML = `Chat <button class="cc-close">✕</button>`;

    const body = document.createElement("div");
    body.className = "cc-body";

    const emailArea = document.createElement("div");
    emailArea.className = "cc-email-area";
    emailArea.innerHTML = `
      <input class="cc-email-input" placeholder="${t.emailPlaceholder}">
      <button class="cc-email-btn">${t.continue}</button>
    `;

    const inputArea = document.createElement("div");
    inputArea.className = "cc-input-area";
    inputArea.style.display = "none";
    inputArea.innerHTML = `
      <div class="cc-input-wrap">
        <input class="cc-input" placeholder="${t.typeMessage}">
      </div>
      <button class="cc-send-btn">
        <svg viewBox="0 0 24 24"><path d="М2 21l21-9L2 3v7l15 2-15 2v7z"></path></svg>
      </button>
    `;

    screen2.append(header, body, emailArea, inputArea);
    panel.append(screen1, screen2);
    wrapper.append(fab, panel);
    document.body.append(wrapper);

    const closeScreen1Btn = screen1.querySelector(".cc-screen1-close");
    const closeBtn = header.querySelector(".cc-close");
    const startBtn = screen1.querySelector(".cc-start-btn");
    const emailInput = emailArea.querySelector(".cc-email-input");
    const emailBtn = emailArea.querySelector(".cc-email-btn");
    const messageInput = inputArea.querySelector(".cc-input");
    const sendBtn = inputArea.querySelector(".cc-send-btn");

    let userEmail = null;

    function addMessage(text, who = "bot") {
      const msg = document.createElement("div");
      msg.className = "cc-msg " + who;
      msg.textContent = text;
      body.append(msg);
      body.scrollTop = body.scrollHeight;
    }

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
      setTimeout(function () {
        panel.style.height = "390px";
      }, 300);
    }

    closeScreen1Btn.onclick = closePanel;
    closeBtn.onclick = closePanel;

    startBtn.onclick = function () {
      screen1.style.display = "none";
      screen2.style.display = "flex";
      panel.style.height = "520px";
      addMessage(t.welcome);
      addMessage(t.agents);
    };

    emailBtn.onclick = function () {
      const mail = emailInput.value.trim();
      if (!mail.match(/^\S+@\S+\.\S+$/)) {
        addMessage(t.invalidEmail);
        return;
      }
      userEmail = mail;
      emailArea.style.display = "none";
      inputArea.style.display = "flex";
      addMessage(t.start);
    };

    async function sendMessage() {
      const text = messageInput.value.trim();
      if (!text) return;

      addMessage(text, "user");
      messageInput.value = "";

      try {
        const response = await fetch("http://localhost:3000/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: text,
            email: userEmail,
            token: token
          })
        });

        const data = await response.json();
        addMessage(data.reply || "...");
      } catch (error) {
        addMessage("Error");
      }
    }

    sendBtn.onclick = sendMessage;

    messageInput.onkeydown = function (event) {
      if (event.key === "Enter") {
        sendMessage();
      }
    };

  });

})();
