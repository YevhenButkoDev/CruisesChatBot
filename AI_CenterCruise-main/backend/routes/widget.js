import express from "express";
import { createWidgetToken, verifyWidgetToken } from "../utils/token.js";
import path from "path";
import { fileURLToPath } from "url";
import fs from "fs";

const router = express.Router();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Список доменов, которым разрешён доступ
const allowedDomains = [
  "localhost",
  "127.0.0.1",
  "center.cruises",
  "www.center.cruises"
];

// Маршрут получения токена: /widget/token?domain=
router.get("/token", (req, res) => {
  const domain = req.query.domain;

  if (!domain) {
    return res.status(400).json({ error: "Missing domain parameter" });
  }

  if (!allowedDomains.includes(domain)) {
    return res.status(403).json({ error: "Domain not allowed" });
  }

  const token = createWidgetToken(domain);

  res.json({ token });
});

// Маршрут выдачи JS-виджета: /widget/script?token=
router.get("/script", (req, res) => {
  const token = req.query.token;

  if (!token) {
    return res
      .status(401)
      .type("application/javascript")
      .send(`console.error("Missing widget token");`);
  }

  const decoded = verifyWidgetToken(token);

  if (!decoded) {
    return res
      .status(403)
      .type("application/javascript")
      .send(`console.error("Invalid or expired widget token");`);
  }

  const requestedDomain = decoded.domain;

  if (!allowedDomains.includes(requestedDomain)) {
    return res
      .status(403)
      .type("application/javascript")
      .send(`console.error("This domain is not allowed");`);
  }

  const jsPath = path.join(__dirname, "../../widget/dist/widget.min.js");

  if (!fs.existsSync(jsPath)) {
    return res
      .status(500)
      .type("application/javascript")
      .send(`console.error("Widget build is missing");`);
  }

  res.type("application/javascript").sendFile(jsPath);
});

// Маршрут выдачи CSS
router.get("/style.css", (req, res) => {
  const cssPath = path.join(__dirname, "../../widget/style.css");

  if (!fs.existsSync(cssPath)) {
    return res
      .type("text/css")
      .send(`/* CSS not found */`);
  }

  res.type("text/css").sendFile(cssPath);
});

export default router;
