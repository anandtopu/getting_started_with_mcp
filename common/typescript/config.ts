export const specRevision = '2026-07-28';
export function provider(env: NodeJS.ProcessEnv = process.env): string {
  const name = env.LLM_PROVIDER ?? 'fake';
  if (!['fake', 'ollama', 'anthropic', 'openai', 'gemini'].includes(name)) {
    throw new Error('Unknown LLM_PROVIDER. Run uv run python scripts/check_env.py.');
  }
  return name;
}
