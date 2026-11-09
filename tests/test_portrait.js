const fs=require('fs'),vm=require('vm'),assert=require('assert');
function picture(image){return {attributes:{},style:{image,priority:'',getPropertyValue(){return this.image},getPropertyPriority(){return this.priority},setProperty(k,v,p){this.image=v;this.priority=p}},setAttribute(k,v){this.attributes[k]=v},removeAttribute(k){delete this.attributes[k]}}}
let first=picture('url("original-a.png")'),second=picture('url("original-b.png")');
let state={slots:[0],portrait:'coui://gui/maps/icons/commander_friend/demo.png'};
let slots=[first,second].map(p=>({className:'Slot_a123',querySelector(){return p}}));
let root={querySelectorAll(){return slots}},timer;
const context={Map,Set,Array,JSON,console,
 document:{body:{},querySelectorAll(){return [root]}},
 MutationObserver:class{observe(){} disconnect(){}},
 window:{subViews:{ids(){return [1]},get(){return {model:{commanderFriendJson:JSON.stringify(state)}}}},
 requestAnimationFrame(fn){fn()},setInterval(fn){timer=fn;return 1},clearInterval(){},addEventListener(){}},
 engine:{whenReady:{then(fn){fn()}},on(){}}};
vm.runInNewContext(fs.readFileSync(__dirname+'/../src/portrait.js','utf8'),context);
assert(first.style.image.includes('demo.png'));assert.equal(second.style.image,'url("original-b.png")');
state.slots=[];timer();assert.equal(first.style.image,'url("original-a.png")');
state.slots=[0];timer();
// A native update reuses this DOM slot for another tankman: preserve his image.
first.style.image='url("native-next-commander.png")';timer();
state.slots=[];timer();assert.equal(first.style.image,'url("native-next-commander.png")');
state.slots=[1];timer();assert(second.style.image.includes('demo.png'));
state.portrait='https://untrusted.example/photo.png';timer();assert.equal(second.style.image,'url("original-b.png")');
console.log('PASS: selected slot, toggle restoration, recycled slot, other crew, URL allowlist');
