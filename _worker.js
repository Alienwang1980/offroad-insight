// Cloudflare Pages _worker.js — reassembles chunked .unityweb files
// Chunks live in Build/chunks/ with manifest.json files listing chunk names

const CHUNK_CONFIG = {
  'Build/offroad.data.unityweb': 'data',
  'Build/offroad.wasm.unityweb': 'wasm',
};

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/^\//, '');

    if (!CHUNK_CONFIG[path]) {
      return env.ASSETS.fetch(request);
    }

    const prefix = CHUNK_CONFIG[path];
    
    // Fetch manifest
    const manifestResp = await env.ASSETS.fetch(
      new Request(`${url.origin}/Build/chunks/${prefix}_manifest.json`)
    );
    if (!manifestResp.ok) {
      return new Response('Manifest not found', { status: 500 });
    }
    const chunks = await manifestResp.json();

    // Set content type
    const ct = path.endsWith('.wasm.unityweb') 
      ? 'application/wasm' 
      : 'application/octet-stream';

    // Create a streaming response that concatenates all chunks
    const { readable, writable } = new TransformStream();
    const writer = writable.getWriter();

    ctx.waitUntil((async () => {
      try {
        for (const chunkName of chunks) {
          const chunkResp = await env.ASSETS.fetch(
            new Request(`${url.origin}/Build/chunks/${chunkName}`)
          );
          if (!chunkResp.ok) {
            writer.abort(new Error(`Chunk ${chunkName} not found`));
            return;
          }
          const reader = chunkResp.body.getReader();
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            await writer.write(value);
          }
        }
        await writer.close();
      } catch (e) {
        await writer.abort(e);
      }
    })());

    return new Response(readable, {
      headers: {
        'Content-Type': ct,
        'Cache-Control': 'public, max-age=86400',
        'Access-Control-Allow-Origin': '*',
      }
    });
  }
};
