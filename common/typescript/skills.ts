/** Official Skills SDK: verify each file, without activating its instructions. */
import { strict as assert } from 'node:assert';
import { McpServer } from '@modelcontextprotocol/server';
import { SkillsExtension, memorySkillFiles } from '@modelcontextprotocol/server/ext/skills';
import { SkillsClient } from '@modelcontextprotocol/client/ext/skills';
import { inMemory } from './clients.ts';

export async function skillsFactory() {
  const catalog=await SkillsExtension.load(memorySkillFiles({
    'incident-review/SKILL.md':'---\nname: incident-review\ndescription: Review a synthetic incident timeline.\n---\nRead references/checklist.md; report evidence before proposing changes.\n',
    'incident-review/references/checklist.md':'# Checklist\nIdentify impact, timeline, owner and recovery.\n',
  }));
  return ()=>{ const server=new McpServer({name:'Lumen TypeScript skills',version:'1.0'});catalog.attach(server);return server; };
}
export async function skillsDemo() {
  return inMemory(await skillsFactory(),async client=>{
    const skills=new SkillsClient(client);
    const listing=await skills.list();assert.equal(listing.skills.length,1);
    const skill=await skills.get(listing.skills[0].uri);
    assert.ok(skill);
    const file=await skills.read(skill!.skill);assert.ok(file.verified);
    return {verified:true,activated:false};
  });
}
