import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// GitHub Pages: сайт живе за адресою https://<user>.github.io/<repo>/
// base підхоплюється зі змінної або дефолт '/dobrograd-os/'; локально dev працює з '/'.
const base = process.env.SITE_BASE ?? (process.env.CI ? '/dobrograd-os/' : '/');

export default defineConfig({
  base,
  trailingSlash: 'always',
  build: { format: 'directory' },
  vite: { plugins: [tailwindcss()] },
});
