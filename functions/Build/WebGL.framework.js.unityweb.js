export async function onRequest(context) {
  const url = new URL(context.request.url);
  url.pathname = url.pathname + '.bin';
  const response = await fetch(url);
  const headers = new Headers(response.headers);
  headers.set('Content-Encoding', 'br');
  headers.set('Cache-Control', 'no-transform, public, max-age=86400');
  headers.set('Content-Type', 'application/javascript');
  return new Response(response.body, { status: response.status, headers });
}