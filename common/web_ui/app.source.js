import { AppBridge, PostMessageTransport } from '@modelcontextprotocol/ext-apps/app-bridge';
const $ = selector => document.querySelector(selector);
let csrf = '', busy = false, seenEvents = '', pendingId = '', appId = '', bridge;
const notices = message => { $('#notice').textContent = message; $('#notice').hidden = !message; };
async function api(path, data, bootstrap = false) {
  const response = await fetch('/api/' + path, { method: data === undefined ? 'GET' : 'POST',
    headers: { 'content-type': 'application/json', ...(bootstrap ? {'x-lumen-client':'web'} : {'x-csrf-token':csrf}) },
    body: data === undefined ? undefined : JSON.stringify(data) });
  if (!response.ok) {
    const value = await response.json().catch(() => ({}));
    throw new Error(typeof value.detail === 'string' ? value.detail : 'This request could not finish.');
  }
  return response.json();
}
function element(tag, text, className) {
  const node = document.createElement(tag); if (text !== undefined) node.textContent = text;
  if (className) node.className = className; return node;
}
function events(values) {
  const key = JSON.stringify(values); if (key === seenEvents) return; seenEvents = key;
  const list = $('#conversation'); list.replaceChildren();
  for (const value of values) {
    if (['connection', 'task'].includes(value.type)) continue;
    if (value.type === 'tool_result') {
      const row = element('details', undefined, 'evidence');
      row.append(element('summary', 'Tool evidence · ' + value.tool));
      row.append(element('pre', JSON.stringify(value.result.structuredContent ?? value.result.content, null, 2)));
      list.append(row); continue;
    }
    const row = element('article', undefined, 'message ' + value.type);
    row.append(element('div', value.type === 'assistant' ? 'Lumen' : value.type, 'message-label'));
    row.append(element('p', value.text ?? value.message ?? ('Call declined · ' + value.tool)));
    list.append(row);
  }
  const task = [...values].reverse().find(value => value.type === 'task');
  if (task) list.append(element('div', 'Report task · ' + task.status.replaceAll('_', ' '), 'task-state'));
}
function question(pending) {
  const box = $('#decision'); box.hidden = !pending;
  if (!pending) { pendingId = ''; box.replaceChildren(); return; }
  if (pending.id === pendingId) return; pendingId = pending.id; box.replaceChildren();
  box.append(element('div', 'YOUR REVIEW IS REQUIRED', 'eyebrow teal'));
  box.append(element('h3', pending.kind === 'approval' ? 'Allow this tool call?' : 'A tool needs your input'));
  box.append(element('p', 'This decision applies once. It expires after two minutes.'));
  const fields = new Map();
  if (pending.kind === 'approval') {
    box.append(element('strong', pending.tool));
    box.append(element('p', pending.description));
    box.append(element('pre', JSON.stringify(pending.arguments, null, 2)));
    const detail = element('details'); detail.append(element('summary', 'Connection and tool definition'));
    detail.append(element('pre', JSON.stringify({server:pending.server, schema:pending.schema, definition:pending.definition_hash}, null, 2)));
    box.append(detail);
  } else {
    box.append(element('p', pending.message));
    for (const [name, field] of Object.entries(pending.schema.properties ?? {})) {
      const label = element('label'); const input = element('input');
      input.type = field.type === 'boolean' ? 'checkbox' : ['number','integer'].includes(field.type) ? 'number' : 'text';
      input.name = name; input.maxLength = Math.min(field.maxLength ?? 1000, 1000);
      if (field.type === 'integer') input.step = '1';
      label.append(input, element('span', field.title ?? name.replaceAll('_', ' '))); box.append(label); fields.set(name, {input,field});
    }
  }
  const actions = element('div', undefined, 'decision-actions');
  for (const [action,title] of [['accept', pending.kind === 'approval' ? 'Approve once' : 'Submit input'],['decline','Decline']]) {
    const button = element('button', title); button.type = 'button';
    button.addEventListener('click', async () => {
      const content = {}; for (const [name,{input,field}] of fields) content[name] = field.type === 'boolean' ? input.checked : ['number','integer'].includes(field.type) ? Number(input.value) : input.value;
      button.disabled = true;
      try { await api('answer',{id:pending.id,action,content}); box.hidden = true; }
      catch(error) { notices(error.message); button.disabled = false; }
    }); actions.append(button);
  }
  box.append(actions);
}
async function closeApp() {
  if (bridge) { try { await bridge.teardownResource({}); } catch { /* The view may already be gone. */ } await bridge.close(); bridge = null; }
  $('#app-frame').replaceChildren(); $('#app-panel').hidden = true;
}
async function showApp(app) {
  if (!app || app.id === appId) return;
  await closeApp(); appId = app.id; $('#app-panel').hidden = false;
  const frame = element('iframe'); frame.title = app.title; frame.setAttribute('sandbox','allow-scripts');
  $('#app-frame').append(frame);
  bridge = new AppBridge(null, {name:'Lumen Chat',version:'4.0'}, {serverTools:{}});
  bridge.oncalltool = async params => {
    if (params.name !== 'analytics_dashboard' || Object.keys(params.arguments ?? {}).length) throw new Error('Tool is outside this view.');
    return api('app-call',{name:params.name,arguments:{}});
  };
  bridge.oninitialized = async () => { await bridge.sendToolInput({arguments:{}}); await bridge.sendToolResult(app.result); };
  await bridge.connect(new PostMessageTransport(frame.contentWindow, frame.contentWindow));
  frame.src = '/api/app-view/' + encodeURIComponent(app.id);
}
async function render(state) {
  busy = ['running','waiting'].includes(state.status);
  $('#status').textContent = state.status === 'ready' ? 'Workspace ready' : state.status;
  $('#send').disabled = busy; $('#cancel').disabled = !busy; $('#reconnect').disabled = busy;
  for (const button of document.querySelectorAll('[data-prompt]')) button.disabled = busy;
  $('#connection-count').textContent = state.connections.length;
  const list = $('#connections'); list.replaceChildren();
  for (const connection of state.connections) { const row = element('div',undefined,'service'); const label = element('div',connection.alias); label.append(element('small',connection.protocol)); row.append(label); list.append(row); }
  events(state.events); question(state.pending); await showApp(state.app);
}
async function send(prompt) {
  notices('');
  try { await api('chat',{prompt,provider:$('#provider').value,model:$('#model').value}); $('#prompt').value = ''; busy = true; $('#send').disabled = true; }
  catch(error) { notices(error.message); }
}
$('#composer').addEventListener('submit', event => { event.preventDefault(); if (!busy) send($('#prompt').value); });
for (const button of document.querySelectorAll('[data-prompt]')) button.addEventListener('click', () => send(button.dataset.prompt));
$('#provider').addEventListener('change', () => { const live = $('#provider').value !== 'fake'; $('#model').hidden = !live; $('#mode-note').textContent = live ? 'Uses your server-side provider configuration. Model usage may incur charges.' : 'Practice mode uses real synthetic data and scripted tool choices. No model key needed.'; });
$('#cancel').addEventListener('click', () => api('cancel',{}).catch(error=>notices(error.message)));
$('#reconnect').addEventListener('click', () => api('reconnect',{}).catch(error=>notices(error.message)));
$('#close-app').addEventListener('click', closeApp);
try { const state = await api('session',{},true); csrf = state.csrf; await render(state); }
catch(error) { notices(error.message); }
let polling = false;
setInterval(async () => { if (!csrf || polling) return; polling = true; try { await render(await api('state')); } catch(error) { notices(error.message); } finally { polling = false; } }, 400);
