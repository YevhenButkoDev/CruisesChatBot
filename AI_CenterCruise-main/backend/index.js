import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";
import fs from "fs";

import widgetRouter from "./routes/widget.js";
import chatRouter from "./routes/chat.js";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.use("/api/chat", chatRouter);
app.use("/widget", widgetRouter);

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Папка public
app.use(express.static(path.join(__dirname, "../public")));

// Выдача основного widget.js (если используется напрямую)
app.get("/widget.js", (req, res) => {
  const jsPath = path.join(__dirname, "../widget/dist/widget.min.js");

  if (!fs.existsSync(jsPath)) {
    return res
      .type("application/javascript")
      .send(`console.warn("Widget not built yet");`);
  }

  res.type("application/javascript").sendFile(jsPath);
});

// Выдача стилей
app.get("/widget/style.css", (req, res) => {
  const cssPath = path.join(__dirname, "../widget/style.css");

  if (!fs.existsSync(cssPath)) {
    return res
      .type("text/css")
      .send(`/* Widget CSS not built yet */`);
  }

  res.type("text/css").sendFile(cssPath);
});

app.listen(PORT, () => {
  console.log(`Server running: http://localhost:${PORT}`);
  console.log('Environment:', process.env.NODE_ENV || 'development');
  console.log('Logging enabled for Docker container');
});
