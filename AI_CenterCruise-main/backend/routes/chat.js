import express from "express";

const router = express.Router();

router.post("/", async (req, res) => {
  try {
    const { message, token } = req.body;

    if (!message || !token) {
      return res.status(400).json({ error: "Missing message or token" });
    }

    // Здесь позже будет проверка токена (jwt.verify) и обращение к AI API
    console.log("💬 Message from widget:", message);

    // Временный фейковый ответ от “AI”
    const aiResponse = `Вы написали: "${message}". Спасибо за обращение! 🚢`;

    return res.json({ reply: aiResponse });
  } catch (err) {
    console.error("Error in /api/chat:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});

export default router;
