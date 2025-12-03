import { verifyToken } from "../utils/token.js";

export default function checkToken(req, res, next) {
  const token = req.query.token || req.headers["x-widget-token"];

  if (!token) {
    return res.status(403).json({ error: "Token missing" });
  }

  const data = verifyToken(token);

  if (!data) {
    return res.status(403).json({ error: "Invalid or expired token" });
  }

  const origin = req.headers.origin?.replace("https://", "").replace("http://", "");

  if (!origin || origin !== data.domain) {
    return res.status(403).json({ error: "Domain not allowed" });
  }

  req.widgetDomain = data.domain;
  next();
}
