import express from 'express';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';
import { GoogleGenAI, Type } from '@google/genai';
import { createServer as createViteServer } from 'vite';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const TOPICS_JSON_PATH = path.join(__dirname, '../data/topics.json');

function readTopicsData() {
  try {
    if (fs.existsSync(TOPICS_JSON_PATH)) {
      const data = fs.readFileSync(TOPICS_JSON_PATH, 'utf-8');
      return JSON.parse(data);
    }
  } catch (e) {
    console.error('Error reading topics.json:', e);
  }
  return [];
}

function writeTopicsData(topics: any[]) {
  try {
    const dir = path.dirname(TOPICS_JSON_PATH);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(TOPICS_JSON_PATH, JSON.stringify(topics, null, 2), 'utf-8');
  } catch (e) {
    console.error('Error writing topics.json:', e);
  }
}

async function startServer() {
  const app = express();
  const PORT = 18922;

  app.use(express.json());

  // Topics persistence endpoints
  app.get('/api/topics', (req, res) => {
    const topics = readTopicsData();
    res.json(topics);
  });

  app.post('/api/topics/sync', (req, res) => {
    const topics = req.body;
    if (Array.isArray(topics)) {
      writeTopicsData(topics);
      res.json({ success: true, count: topics.length });
    } else {
      res.status(400).json({ error: 'Expected array of topics' });
    }
  });

  // Initialize Gemini AI Client lazily or safely
  const getAi = () => {
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      throw new Error('GEMINI_API_KEY is not configured');
    }
    return new GoogleGenAI({
      apiKey,
      httpOptions: {
        headers: {
          'User-Agent': 'aistudio-build',
        },
      },
    });
  };

  // Health check endpoint
  app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', time: new Date().toISOString() });
  });

  // AI Topic Generator Endpoint
  app.post('/api/gemini/generate-topics', async (req, res) => {
    try {
      const { keyword = 'Tech', platform = 'X', count = 3 } = req.body;
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
        model: 'gemini-3.6-flash',
        contents: prompt,
        config: {
          responseMimeType: 'application/json',
          responseSchema: {
            type: Type.ARRAY,
            items: {
              type: Type.OBJECT,
              properties: {
                title: { type: Type.STRING },
                category: { type: Type.STRING },
                platform: { type: Type.STRING },
                hook: { type: Type.STRING },
                contentAngles: { type: Type.STRING },
                scriptOutline: { type: Type.STRING },
                tags: {
                  type: Type.ARRAY,
                  items: { type: Type.STRING },
                },
              },
              required: ['title', 'category', 'platform', 'hook', 'tags'],
            },
          },
        },
      });

      const text = response.text;
      if (!text) {
        return res.status(500).json({ error: 'No response generated from Gemini API' });
      }

      const topics = JSON.parse(text);
      res.json({ topics });
    } catch (error: any) {
      console.error('Error generating topics:', error);
      res.status(500).json({ error: error.message || 'Failed to generate topics' });
    }
  });

  // AI Enhance / Polish Topic Endpoint
  app.post('/api/gemini/enhance-topic', async (req, res) => {
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
        model: 'gemini-3.6-flash',
        contents: prompt,
        config: {
          responseMimeType: 'application/json',
          responseSchema: {
            type: Type.OBJECT,
            properties: {
              enhancedTitle: { type: Type.STRING },
              enhancedHook: { type: Type.STRING },
              contentAngles: { type: Type.STRING },
              scriptOutline: { type: Type.STRING },
              suggestedTags: {
                type: Type.ARRAY,
                items: { type: Type.STRING },
              },
            },
            required: ['enhancedTitle', 'enhancedHook', 'contentAngles', 'scriptOutline', 'suggestedTags'],
          },
        },
      });

      const text = response.text;
      if (!text) {
        return res.status(500).json({ error: 'Failed to enhance topic' });
      }

      res.json(JSON.parse(text));
    } catch (error: any) {
      console.error('Error enhancing topic:', error);
      res.status(500).json({ error: error.message || 'Failed to enhance topic' });
    }
  });

  // AI Social Favorites Sync Simulation Endpoint
  app.post('/api/gemini/sync-favs', async (req, res) => {
    try {
      const { platform = 'All Platforms' } = req.body;
      const ai = getAi();

      const prompt = `Simulate syncing 4 trending saved/favorited topic posts from social media platform "${platform}".
Generate realistic topics that a creator saved for future content inspiration.
Return JSON array of topics with title, category, platform (e.g. X, Bilibili, Reddit, Xiaohongshu, Newsletter, YouTube), hook, contentAngles, scriptOutline, tags.`;

      const response = await ai.models.generateContent({
        model: 'gemini-3.6-flash',
        contents: prompt,
        config: {
          responseMimeType: 'application/json',
          responseSchema: {
            type: Type.ARRAY,
            items: {
              type: Type.OBJECT,
              properties: {
                title: { type: Type.STRING },
                category: { type: Type.STRING },
                platform: { type: Type.STRING },
                hook: { type: Type.STRING },
                contentAngles: { type: Type.STRING },
                scriptOutline: { type: Type.STRING },
                tags: {
                  type: Type.ARRAY,
                  items: { type: Type.STRING },
                },
              },
              required: ['title', 'category', 'platform', 'hook', 'tags'],
            },
          },
        },
      });

      const text = response.text;
      if (!text) {
        return res.status(500).json({ error: 'Failed to sync favs' });
      }

      res.json({ topics: JSON.parse(text) });
    } catch (error: any) {
      console.error('Error syncing favs:', error);
      res.status(500).json({ error: error.message || 'Failed to sync favs' });
    }
  });

  // Serve Vite in dev or static files in production
  if (process.env.NODE_ENV !== 'production') {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Topic Master server running on http://0.0.0.0:${PORT}`);
  });
}

startServer();
