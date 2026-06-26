export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname.endsWith('.unityweb')) {
      const resp = await env.ASSETS.fetch(request);
      const h = new Headers(resp.headers);
      h.set('Content-Encoding', 'br');
      h.set('Cache-Control', 'no-transform');
      return new Response(resp.body, { status: resp.status, headers: h });
    }
    return env.ASSETS.fetch(request);
  }
}
