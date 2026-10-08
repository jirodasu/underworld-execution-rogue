// Exercise the generated boot script without loading the network runtime.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html = fs.readFileSync('index.html', 'utf8');
const script = html.match(/<script>\s*([\s\S]*?)<\/script>/)[1];
function boot() {
  const elements = {};
  for (const id of ['boot','boot-start','boot-status','game-link','copy-link','copy-status','retry','failure-message','failure-detail','failure'])
    elements[id] = {style:{},hidden:false,disabled:true,isConnected:true,textContent:'',addEventListener(event,fn){this[event]=fn},focus(){},select(){},remove(){this.isConnected=false}};
  const state={elements,clipboard:[],cleared:false};
  const context={document:{getElementById:id=>elements[id]||null,createElement:()=>({}),head:{appendChild:r=>state.runtime=r},body:{}},location:{href:'https://example.com/game/#test'},navigator:{clipboard:{writeText:async value=>state.clipboard.push(value)}},setTimeout:fn=>(state.timeout=fn,1),clearTimeout:()=>state.cleared=true,MutationObserver:class{constructor(fn){state.observe=fn}observe(){}}};
  vm.runInNewContext(script,context);
  return state;
}
(async()=>{
  let s=boot();s.runtime.onerror();assert.match(s.elements['failure-message'].textContent,/起動/);assert.equal(s.elements.retry.hidden,false);assert.equal(s.elements['copy-link'].hidden,true);
  s=boot();s.timeout();assert.match(s.elements['failure-detail'].textContent,/60秒/);
  s=boot();s.elements['pyxel-prompt']={};s.observe();assert.equal(s.elements['boot-start'].disabled,false);assert.equal(s.cleared,true);
  delete s.elements['pyxel-prompt'];s.observe();assert.equal(s.elements.boot.isConnected,false);
  s.elements['pyxel-error-overlay']={textContent:'Failed to create OpenGL context'};s.observe();assert.equal(s.elements.retry.hidden,true);assert.equal(s.elements['copy-link'].hidden,false);assert.equal(s.elements['game-link'].hidden,false);
  await s.elements['copy-link'].click();assert.deepEqual(s.clipboard,['https://example.com/game/']);assert.match(s.elements['copy-status'].textContent,/コピーしました/);
  console.log('Boot checks passed: network failure, timeout, ready gesture, OpenGL routing, copy link.');
})().catch(error=>{console.error(error);process.exit(1)});
