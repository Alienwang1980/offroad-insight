// Reassembles offroad.wasm.unityweb from Build/chunks/wasm_* chunks
export async function onRequest(context) {
  const { request } = context;
  const url = new URL(request.url);

  const manifestResp = await fetch(`${url.origin}/Build/chunks/wasm_manifest.json`);
  if (!manifestResp.ok) return new Response('Manifest not found', { status: 500 });
  const chunks = await manifestResp.json();

  const parts = [];
  for (const chunkName of chunks) {
    const chunkResp = await fetch(`${url.origin}/Build/chunks/${chunkName}`);
    if (!chunkResp.ok) return new Response(`Chunk ${chunkName} missing`, { status: 500 });
    parts.push(await chunkResp.arrayBuffer());
  }

  const total = parts.reduce((s, p) => s + p.byteLength, 0);
  const result = new Uint8Array(total);
  let offset = 0;
  for (const part of parts) {
    result.set(new Uint8Array(part), offset);
    offset += part.byteLength;
  }

  return new Response(result, {
    headers: {
      'Content-Type': 'application/wasm',
      'Cache-Control': 'public, max-age=86400',
      'Access-Control-Allow-Origin': '*',
    }
  });
}
