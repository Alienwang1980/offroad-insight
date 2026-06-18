export async function onRequest(context) {
  const url = new URL(context.request.url);
  const manifestResp = await fetch(`${url.origin}/Build/chunks/wasm_manifest.json`);
  const chunks = await manifestResp.json();
  const parts = [];
  for (const chunkName of chunks) {
    const chunkResp = await fetch(`${url.origin}/Build/chunks/${chunkName}`);
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
      'Content-Type': 'application/octet-stream',
      'Cache-Control': 'public, max-age=86400',
    }
  });
}
