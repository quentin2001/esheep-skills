var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
  // If the importer is in node compatibility mode or this is not an ESM
  // file that has been converted to a CommonJS file using a Babel-
  // compatible transform (i.e. "__esModule" has not been set), then set
  // "default" to the CommonJS "module.exports" for node compatibility.
  isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
  mod
));

// server.ts
var import_express = __toESM(require("express"), 1);
var import_path = __toESM(require("path"), 1);
var import_fs = __toESM(require("fs"), 1);
var import_url = require("url");
var import_genai = require("@google/genai");
var import_vite = require("vite");
var import_meta = {};
var __filename = (0, import_url.fileURLToPath)(import_meta.url);
var __dirname = import_path.default.dirname(__filename);
var TOPICS_JSON_PATH = import_path.default.join(__dirname, "../data/topics.json");
function readTopicsData() {
  try {
    if (import_fs.default.existsSync(TOPICS_JSON_PATH)) {
      const data = import_fs.default.readFileSync(TOPICS_JSON_PATH, "utf-8");
      return JSON.parse(data);
    }
  } catch (e) {
    console.error("Error reading topics.json:", e);
  }
  return [];
}
function writeTopicsData(topics) {
  try {
    const dir = import_path.default.dirname(TOPICS_JSON_PATH);
    if (!import_fs.default.existsSync(dir)) import_fs.default.mkdirSync(dir, { recursive: true });
    import_fs.default.writeFileSync(TOPICS_JSON_PATH, JSON.stringify(topics, null, 2), "utf-8");
  } catch (e) {
    console.error("Error writing topics.json:", e);
  }
}
async function startServer() {
  const app = (0, import_express.default)();
  const PORT = 18922;
  app.use(import_express.default.json());
  app.get("/api/topics", (req, res) => {
    const topics = readTopicsData();
    res.json(topics);
  });
  app.post("/api/topics/sync", (req, res) => {
    const topics = req.body;
    if (Array.isArray(topics)) {
      writeTopicsData(topics);
      res.json({ success: true, count: topics.length });
    } else {
      res.status(400).json({ error: "Expected array of topics" });
    }
  });
  const getAi = () => {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      throw new Error("GEMINI_API_KEY is not configured");
    }
    return new import_genai.GoogleGenAI({
      apiKey,
      httpOptions: {
        headers: {
          "User-Agent": "aistudio-build"
        }
      }
    });
  };
  app.get("/api/health", (req, res) => {
    res.json({ status: "ok", time: (/* @__PURE__ */ new Date()).toISOString() });
  });
  app.post("/api/gemini/generate-topics", async (req, res) => {
    try {
      const { keyword = "Tech", platform = "X", count = 3 } = req.body;
      const ai = getAi();
      const prompt = `Generate ${count} compelling content topic ideas for a content creator.
Topic category / keyword: "${keyword}"
Target platform: "${platform}"

Return a JSON array of topic objects. Each topic must have:
- title: Short punchy title (max 8 words)
- category: Category name (e.g. ${keyword})
- platform: "${platform}"
- hook: A magnetic 1-2 sentence hook or opener
- contentAngles: 3 bullet points outlining key angles/perspectives
- scriptOutline: A numbered 4-5 step script outline
- tags: Array of 2-3 short relevant tag strings`;
      const response = await ai.models.generateContent({
        model: "gemini-3.6-flash",
        contents: prompt,
        config: {
          responseMimeType: "application/json",
          responseSchema: {
            type: import_genai.Type.ARRAY,
            items: {
              type: import_genai.Type.OBJECT,
              properties: {
                title: { type: import_genai.Type.STRING },
                category: { type: import_genai.Type.STRING },
                platform: { type: import_genai.Type.STRING },
                hook: { type: import_genai.Type.STRING },
                contentAngles: { type: import_genai.Type.STRING },
                scriptOutline: { type: import_genai.Type.STRING },
                tags: {
                  type: import_genai.Type.ARRAY,
                  items: { type: import_genai.Type.STRING }
                }
              },
              required: ["title", "category", "platform", "hook", "tags"]
            }
          }
        }
      });
      const text = response.text;
      if (!text) {
        return res.status(500).json({ error: "No response generated from Gemini API" });
      }
      const topics = JSON.parse(text);
      res.json({ topics });
    } catch (error) {
      console.error("Error generating topics:", error);
      res.status(500).json({ error: error.message || "Failed to generate topics" });
    }
  });
  app.post("/api/gemini/enhance-topic", async (req, res) => {
    try {
      const { title, hook, category, platform } = req.body;
      const ai = getAi();
      const prompt = `Refine and expand the content strategy for this topic:
Title: "${title}"
Category: "${category}"
Platform: "${platform}"
Current Hook: "${hook}"

Please improve the hook to make it irresistible, provide 3 strategic content angles, and create a structured step-by-step script outline.`;
      const response = await ai.models.generateContent({
        model: "gemini-3.6-flash",
        contents: prompt,
        config: {
          responseMimeType: "application/json",
          responseSchema: {
            type: import_genai.Type.OBJECT,
            properties: {
              enhancedTitle: { type: import_genai.Type.STRING },
              enhancedHook: { type: import_genai.Type.STRING },
              contentAngles: { type: import_genai.Type.STRING },
              scriptOutline: { type: import_genai.Type.STRING },
              suggestedTags: {
                type: import_genai.Type.ARRAY,
                items: { type: import_genai.Type.STRING }
              }
            },
            required: ["enhancedTitle", "enhancedHook", "contentAngles", "scriptOutline", "suggestedTags"]
          }
        }
      });
      const text = response.text;
      if (!text) {
        return res.status(500).json({ error: "Failed to enhance topic" });
      }
      res.json(JSON.parse(text));
    } catch (error) {
      console.error("Error enhancing topic:", error);
      res.status(500).json({ error: error.message || "Failed to enhance topic" });
    }
  });
  app.post("/api/gemini/sync-favs", async (req, res) => {
    try {
      const { platform = "All Platforms" } = req.body;
      const ai = getAi();
      const prompt = `Simulate syncing 4 trending saved/favorited topic posts from social media platform "${platform}".
Generate realistic topics that a creator saved for future content inspiration.
Return JSON array of topics with title, category, platform (e.g. X, Bilibili, Reddit, Xiaohongshu, Newsletter, YouTube), hook, contentAngles, scriptOutline, tags.`;
      const response = await ai.models.generateContent({
        model: "gemini-3.6-flash",
        contents: prompt,
        config: {
          responseMimeType: "application/json",
          responseSchema: {
            type: import_genai.Type.ARRAY,
            items: {
              type: import_genai.Type.OBJECT,
              properties: {
                title: { type: import_genai.Type.STRING },
                category: { type: import_genai.Type.STRING },
                platform: { type: import_genai.Type.STRING },
                hook: { type: import_genai.Type.STRING },
                contentAngles: { type: import_genai.Type.STRING },
                scriptOutline: { type: import_genai.Type.STRING },
                tags: {
                  type: import_genai.Type.ARRAY,
                  items: { type: import_genai.Type.STRING }
                }
              },
              required: ["title", "category", "platform", "hook", "tags"]
            }
          }
        }
      });
      const text = response.text;
      if (!text) {
        return res.status(500).json({ error: "Failed to sync favs" });
      }
      res.json({ topics: JSON.parse(text) });
    } catch (error) {
      console.error("Error syncing favs:", error);
      res.status(500).json({ error: error.message || "Failed to sync favs" });
    }
  });
  if (process.env.NODE_ENV !== "production") {
    const vite = await (0, import_vite.createServer)({
      server: { middlewareMode: true },
      appType: "spa"
    });
    app.use(vite.middlewares);
  } else {
    const distPath = import_path.default.join(process.cwd(), "dist");
    app.use(import_express.default.static(distPath));
    app.get("*", (req, res) => {
      res.sendFile(import_path.default.join(distPath, "index.html"));
    });
  }
  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Topic Master server running on http://0.0.0.0:${PORT}`);
  });
}
startServer();
//# sourceMappingURL=server.cjs.map
