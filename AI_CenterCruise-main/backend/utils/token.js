import jwt from "jsonwebtoken";
import dotenv from "dotenv";

dotenv.config();

const SECRET_KEY = process.env.WIDGET_SECRET || "SUPER_SECRET_WIDGET_KEY";

// Генерация токена для домена (жизнь 24 часа)
export function createWidgetToken(domain) {
  const payload = {
    domain: domain,
    createdAt: Date.now()
  };

  return jwt.sign(payload, SECRET_KEY, { expiresIn: "24h" });
}

// Проверка токена
export function verifyWidgetToken(token) {
  try {
    const decoded = jwt.verify(token, SECRET_KEY);
    return decoded;
  } catch (err) {
    return null;
  }
}
