export async function onRequest(context) {
  const response = await context.next();
  const headers = new Headers(response.headers);
  headers.set('X-Debug-Function', 'wasm-function-ran');
  headers.set('Content-Encoding', 'br');
  headers.set('Cache-Control', 'no-transform, public, max-age=86400');
  return new Response(response.body, { status: response.status, headers });
}