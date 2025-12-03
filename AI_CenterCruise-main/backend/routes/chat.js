import express from "express";

const router = express.Router();

router.post("/", async (req, res) => {
  try {
    const { message, email } = req.body;

    if (!message) {
      return res.status(400).json({ error: "Missing message" });
    }

    const API_URL = process.env.API_URL;
    const TOKEN = process.env.TOKEN;

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
