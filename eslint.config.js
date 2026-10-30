import js from '@eslint/js';
import tseslint from 'typescript-eslint';
export default tseslint.config(
  js.configs.recommended, ...tseslint.configs.recommended,
  { files: ['modules/17_extensions/ui/*.js'], languageOptions: { globals: { document: 'readonly' } } },
);
