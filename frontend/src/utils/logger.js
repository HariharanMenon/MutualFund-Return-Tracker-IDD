// logger.js — Thin console logger.
// In production builds (import.meta.env.DEV === false) debug/info are suppressed.

const isDev = import.meta.env.DEV;

const logger = {
  debug: (...args) => { if (isDev) console.debug('[DEBUG]', ...args); },
  info:  (...args) => { if (isDev) console.info('[INFO]',  ...args); },
  warn:  (...args) => console.warn('[WARN]',  ...args),
  error: (...args) => console.error('[ERROR]', ...args),
};

export default logger;
