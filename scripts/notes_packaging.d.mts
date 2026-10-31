export function packagingLesson(kind: 'npm' | 'mcpb'): Promise<{
  kind: 'npm' | 'mcpb';version: string;files: string[];outside_checkout: boolean;tools: string[];matches: number;
}>;
