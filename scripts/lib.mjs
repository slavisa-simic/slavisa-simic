import fs from 'node:fs/promises';
import path from 'node:path';
import http from 'node:http';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

export const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const config = JSON.parse(await fs.readFile(path.join(root, 'config/network.json'), 'utf8'));
export async function launch() {
  let executablePath = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH;
  if (!executablePath) {
    try { await fs.access(chromium.executablePath()); }
    catch {
      const cache = process.platform === 'win32' ? path.join(process.env.LOCALAPPDATA, 'ms-playwright') : path.join(process.env.HOME, '.cache/ms-playwright');
      try {
        for (const directory of (await fs.readdir(cache)).filter(d => /^chromium-\d+$/.test(d)).sort().reverse()) {
          const binary = process.platform === 'win32' ? 'chrome-win64/chrome.exe' : process.platform === 'darwin' ? 'chrome-mac/Chromium.app/Contents/MacOS/Chromium' : 'chrome-linux64/chrome';
          const candidate = path.join(cache, directory, binary);
          try { await fs.access(candidate); executablePath = candidate; break; } catch {}
        }
      } catch {}
      if (!executablePath) throw new Error('Install Chromium: npx playwright install chromium');
    }
  }
  return chromium.launch({ headless: true, executablePath });
}
export async function serve() {
  const mime = { '.html':'text/html; charset=utf-8','.css':'text/css','.mjs':'text/javascript','.json':'application/json','.png':'image/png','.gif':'image/gif','.svg':'image/svg+xml','.ttf':'font/ttf','.md':'text/plain; charset=utf-8' };
  const server = http.createServer(async (req, res) => {
    try {
      const file = path.resolve(root, `.${decodeURIComponent(new URL(req.url, 'http://localhost').pathname)}`);
      if (!file.startsWith(root + path.sep)) throw new Error('Outside workspace');
      const body = await fs.readFile(file);
      res.writeHead(200, { 'Content-Type': mime[path.extname(file)] || 'application/octet-stream' }); res.end(body);
    } catch { res.writeHead(404); res.end('Not found'); }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  return { origin: `http://127.0.0.1:${server.address().port}`, close: () => new Promise(resolve => server.close(resolve)) };
}
