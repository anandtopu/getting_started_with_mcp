import js from '@eslint/js';
import tseslint from 'typescript-eslint';
export default tseslint.config(
  { files: ['common/web_ui/app.source.js'], languageOptions: { globals: { document: 'readonly', fetch: 'readonly', setInterval: 'readonly' } } },
  { files: ['scripts/*.mjs'], languageOptions: { globals: { console: 'readonly', process: 'readonly' } } },
  js.configs.recommended, ...tseslint.configs.recommended,
  { files: ['modules/17_extensions/ui/*.js'], languageOptions: { globals: { document: 'readonly' } } },
);
