import { defineConfig, type Plugin } from 'vite';
import { readdirSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';

/**
 * 모델 뷰어 (strawberry-cake-engine의 뷰어로 public/models 아래 .glb를 본다).
 *   npm run viewer          개발 서버 → http://127.0.0.1:5180/
 *   npm run viewer:build    dist/에 정적 사이트로 빌드 (모델 포함)
 *   npm run viewer:preview  빌드 결과 띄우기
 */
const MODELS_DIR = join(import.meta.dirname, 'public', 'models');

function listModels(dir = MODELS_DIR): { path: string; mtime: number }[] {
  let out: { path: string; mtime: number }[] = [];
  let entries: string[] = [];
  try {
    entries = readdirSync(dir);
  } catch {
    return out;
  }
  for (const name of entries) {
    const p = join(dir, name);
    const st = statSync(p);
    if (st.isDirectory()) out = out.concat(listModels(p));
    else if (name.endsWith('.glb')) out.push({ path: relative(MODELS_DIR, p).split('\\').join('/'), mtime: st.mtimeMs });
  }
  return out.sort((a, b) => a.path.localeCompare(b.path));
}

/** /__models.json: 뷰어 목록. 개발 서버는 요청마다 만들고, 빌드는 정적 파일로 내보낸다 */
function modelsIndex(): Plugin {
  return {
    name: 'models-index',
    generateBundle() {
      this.emitFile({ type: 'asset', fileName: '__models.json', source: JSON.stringify(listModels()) });
    },
    configureServer(server) {
      server.middlewares.use('/__models.json', (_req, res) => {
        res.setHeader('content-type', 'application/json');
        res.setHeader('cache-control', 'no-store');
        res.end(JSON.stringify(listModels()));
      });
    },
  };
}

export default defineConfig({
  base: './',
  server: { host: '127.0.0.1', port: 5180, hmr: false },
  preview: { host: '127.0.0.1', port: 5181 },
  plugins: [modelsIndex()],
  // 엔진은 TypeScript 소스로 배포된다. 미리 묶지 않고 그대로 변환한다
  optimizeDeps: { exclude: ['strawberry-cake-engine'], include: ['three'] },
  build: { rollupOptions: { input: { index: join(import.meta.dirname, 'index.html') } } },
});
