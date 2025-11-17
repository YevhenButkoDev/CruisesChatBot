import express from "express";

const router = express.Router();

router.post("/", async (req, res) => {
  try {
    const { message, email } = req.body;

    if (!message) {
      return res.status(400).json({ error: "Missing message" });
    }

    console.log("💬 Message from widget:", message, "📧", email || "email not provided");

    const aiResponse = `Вы написали: "${message}". Спасибо за обращение! 🚢`;

    return res.json({ reply: aiResponse });
  } catch (err) {
    console.error("Error in /api/chat:", err);
    res.status(500).json({ error: "Internal server error" });
  }
});


export default router;
