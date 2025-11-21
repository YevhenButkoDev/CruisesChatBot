import express from "express";

const router = express.Router();

router.post("/", async (req, res) => {
  try {
    const { message, email } = req.body;

    if (!message) {
      return res.status(400).json({ error: "Missing message" });
    }

    const API_URL = "https://cruise-ai-agent-620626195243.europe-central2.run.app/ask";
    const TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiY3J1aXNlX2NsaWVudCIsImV4cCI6MTc5MzgwMzM0OSwiaWF0IjoxNzYyMjY3MzQ5fQ.ZCLt-pkUIqpPrG2EwgLCaaS7eDYlDKQ_cO3rlzAO61g";

    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": TOKEN
      },
      body: JSON.stringify({
        question: message,
        chat_id: email || "web_client"
      })
    });

    const data = await response.json();

    console.log("AI RAW RESPONSE:", data);

    // --- FIX: твой API возвращает массив сообщений ---
    let reply = "AI returned empty response";

    if (Array.isArray(data) && data.length > 0) {
      const last = data[data.length - 1];

      if (last && last.content) {
        reply = last.content;
      }
    }

    return res.json({ reply });

  } catch (err) {
    console.error("Error /api/chat:", err);
    res.status(500).json({ error: "AI server error" });
  }
});

export default router;
