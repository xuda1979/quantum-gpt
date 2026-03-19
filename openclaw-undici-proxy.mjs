import {
  ProxyAgent,
  setGlobalDispatcher,
} from "/Users/daxu/software/openclaw/node_modules/.pnpm/undici@7.22.0/node_modules/undici/index.js";

const proxyUrl =
  process.env.HTTPS_PROXY ||
  process.env.https_proxy ||
  process.env.HTTP_PROXY ||
  process.env.http_proxy;

if (proxyUrl) {
  setGlobalDispatcher(new ProxyAgent(proxyUrl));
}
