import { fileURLToPath } from "url";
import path from "path";
import { build } from "esbuild";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const entry = path.resolve(__dirname, "index.js");
const out = path.resolve(__dirname, "dist", "widget.min.js");

build({
  entryPoints: [entry],
  bundle: true,
  minify: true,
  outfile: out,
  format: "iife",
  target: "es2020",

  // 🔥 КЛЮЧЕВЫЕ ФИКСЫ:
  platform: "browser",       // Собираем для браузера, не Node
  define: {
    "process.env.NODE_ENV": `"production"`
  },
  external: [
    "fs", "path", "crypto", "express", "http", "https",
    "os", "zlib", "net", "url", "buffer", "stream"
  ],
})
  .then(() => console.log("✅ Widget build complete"))
  .catch((err) => {
    console.error("❌ Build failed:", err);
    process.exit(1);
  });
