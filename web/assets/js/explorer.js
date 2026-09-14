import {loadJSON, qs, setQS} from './common.js';

const mvData = await loadJSON('../data/explorer/mvp-mvmmmm-k3-v1.json');
const mmData = await loadJSON('../data/explorer/mmmmvv-scenes-v1.json');

const els = {
  mechanism: document.querySelector('#mechanismSelect'), sceneControl: document.querySelector('#sceneControl'), scene: document.querySelector('#sceneSelect'),
  aControl: document.querySelector('#aControl'), bControl: document.querySelector('#bControl'),
  a: document.querySelector('#aSelect'), b: document.querySelector('#bSelect'),
  annotation: document.querySelector('#annotationSelect'), stackMode: document.querySelector('#stackMode'),
  labels: document.querySelector('#labelsToggle'), mv: document.querySelector('#mvToggle'), motionControl: document.querySelector('#motionControl'), motion: document.querySelector('#motionToggle'),
  traceControls: document.querySelector('#traceControls'), prev: document.querySelector('#prevBtn'), next: document.querySelector('#nextBtn'), reset: document.querySelector('#resetBtn'),
  stepStatus: document.querySelector('#stepStatus'), status: document.querySelector('#statusBand'),
  map: document.querySelector('#mapPanel'), mapText: document.querySelector('#mapText'), rows: document.querySelector('#rowPanel'),
  layer: document.querySelector('#layerPanel'), traceSummary: document.querySelector('#traceSummary'), stack: document.querySelector('#stackPanel'),
  traceTableWrap: document.querySelector('#traceTableWrap'), traceHead: document.querySelector('#traceHead'), traceRows: document.querySelector('#traceRows'),
  witness: document.querySelector('#witnessPanel'), proof: document.querySelector('#proofContent'),
  eyebrow: document.querySelector('#explorerEyebrow'), lead: document.querySelector('#explorerLead'),
  mapDesc: document.querySelector('#mapDesc'), rowsDesc: document.querySelector('#rowsDesc'), layerDesc: document.querySelector('#layerDesc'),
  traceTitle: document.querySelector('#traceTitle'), traceDesc: document.querySelector('#traceDesc'), proofDesc: document.querySelector('#proofDesc'), staticRefs: document.querySelector('#staticRefs')
};

for (let p=1; p<=5; p++) {
  for (const sel of [els.a, els.b]) {
    const o=document.createElement('option'); o.value=p; o.textContent=p; sel.append(o);
  }
}

const mmSceneOptions = [
  {key:'diagonal', id:mmData.sentinels.diagonal_success},
  {key:'boundary', id:mmData.sentinels.boundary_success},
  {key:'obstruction', id:mmData.sentinels.interior_obstruction},
];
for (const item of mmSceneOptions) {
  const scene = mmData.scenes.find(s => s.id === item.id);
  const o=document.createElement('option'); o.value=item.key; o.textContent=scene.display.name; els.scene.append(o);
}

let state = {
  mechanism: qs('mechanism', 'mvmmmm'),
  scene: qs('scene', 'diagonal'),
  a: Number(qs('a', mvData.defaults.a)), b: Number(qs('b', mvData.defaults.b)),
  step: Number(qs('step', 0)), selectedFace: null,
  annotation: qs('annotations', mvData.defaults.annotation_level), stackMode: qs('stack', mvData.defaults.stack_mode),
  motion: false
};
if (!['mvmmmm','mmmmvv'].includes(state.mechanism)) state.mechanism='mvmmmm';
if (!mmSceneOptions.some(x => x.key===state.scene)) state.scene='diagonal';
if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) state.motion = false;

function faceLabel(id){ return id?.replace('face:','') ?? ''; }
function creaseLabel(id){ return id?.replace('crease:','') ?? ''; }
function svgEl(name,attrs={}){const e=document.createElementNS('http://www.w3.org/2000/svg',name);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,v);return e;}
function setSelection(faceId){ state.selectedFace = state.selectedFace===faceId ? null : faceId; renderSelection(); }

function mvPairRecord(){ return mvData.pairs.find(r => r.a===state.a && r.b===state.b); }
function mvTrace(){ const r=mvPairRecord(); return mvData.traces[r.trace_id]; }
function mvRowForm(row,pivot){ return mvData.row_forms[row].find(r => r.pivot===pivot); }
function mmScene(){ const item=mmSceneOptions.find(x=>x.key===state.scene) ?? mmSceneOptions[0]; return mmData.scenes.find(s=>s.id===item.id); }
function currentMap(){ return state.mechanism==='mvmmmm' ? mvData.map : mmData.map; }
function currentRows(){
  if(state.mechanism==='mvmmmm') return {A:mvRowForm('A',state.a), B:mvRowForm('B',state.b)};
  const s=mmScene(); return {A:s.upper_row, B:s.lower_row};
}
function currentPivots(){ const rows=currentRows(); return {a:rows.A.pivot,b:rows.B.pivot}; }
function currentEvent(){ if(state.mechanism!=='mvmmmm' || state.step<=0) return null; const tr=mvTrace(); return tr.events[Math.min(state.step-1,tr.events.length-1)]; }
function maxStep(){
  if(state.mechanism==='mvmmmm') return mvTrace().events.length;
  const s=mmScene(); return s.witness ? s.witness.edges.length : 0;
}

function configureControls(){
  const isMV=state.mechanism==='mvmmmm';
  els.mechanism.value=state.mechanism; els.scene.value=state.scene;
  els.sceneControl.hidden=isMV; els.aControl.hidden=!isMV; els.bControl.hidden=!isMV; els.motionControl.hidden=!isMV;
  els.a.value=state.a; els.b.value=state.b; els.annotation.value=state.annotation; els.stackMode.value=state.stackMode; els.motion.checked=state.motion;
  const steps=maxStep(); els.traceControls.hidden=steps===0;
  if(isMV){
    els.eyebrow.textContent='Canonical mechanism · fixed k=3 · MVMMMM';
    els.lead.textContent='A coordinated view of the physical map, row normal forms, literal layer-order prefix, and the theorem-derived LIFO reconstruction.';
    els.layerDesc.textContent='Committed trace prefix, written top-to-bottom. Failed candidates are never inserted.';
    els.traceTitle.textContent='LIFO reconstruction trace';
    els.traceDesc.textContent='Upper openers, lower closer requests, and the exact horizontal stack.';
    els.staticRefs.innerHTML='Static references: <a href="../visualization/generated/05_map_explorer_success.svg">MVMMMM success (2,3)</a> · <a href="../visualization/generated/06_map_explorer_failure.svg">MVMMMM failure (2,4)</a> · <a href="../data/explorer/mvp-mvmmmm-k3-v1.json">source data</a>.';
  } else {
    const s=mmScene();
    els.eyebrow.textContent='Canonical mechanism · fixed k=4 · MMMMVV';
    els.lead.textContent='Prepared theorem scenes for boundary/diagonal compatibility and an explicit directed-cycle obstruction. The browser selects and renders exported records only.';
    els.layerDesc.textContent=s.compatible?'Exact labelled order from the exported theorem construction.':'No layer order is fabricated for an incompatible scene.';
    els.traceTitle.textContent=s.witness?'Directed-cycle witness':'Theorem construction';
    els.traceDesc.textContent=s.witness?'Exported inequalities are revealed one at a time; the last exported edge closes the cycle.':'Exact construction metadata and its independent semantic check.';
    els.staticRefs.innerHTML='Static references: <a href="../visualization/generated/mmmmvv_diagonal_success.svg">diagonal</a> · <a href="../visualization/generated/mmmmvv_boundary_success.svg">boundary</a> · <a href="../visualization/generated/mmmmvv_interior_obstruction.svg">obstruction</a> · <a href="../data/explorer/mmmmvv-scenes-v1.json">source data</a>.';
  }
}

function renderStatus(){
  if(state.mechanism==='mvmmmm'){
    const r=mvPairRecord(); const statusClass=r.compatible?'status-ok':'status-bad'; const symbol=r.compatible?'✓':'×';
    els.status.className=`status-band ${statusClass}`;
    els.status.innerHTML=`<div><b>${symbol} (a,b)=(${r.a},${r.b})</b> · BR(a)=${r.br_a}, BR(b)=${r.br_b} · ${r.compatible?'compatible: equal exported BR block':'incompatible: unequal exported BR blocks'}</div><div class="small">THEOREM-DERIVED COMBINATORIAL TRACE · fixed k=3 canonical MVMMMM</div>`;
    return;
  }
  const s=mmScene(); const symbol=s.compatible?'✓':'×';
  els.status.className=`status-band ${s.compatible?'status-ok':'status-bad'}`;
  els.status.innerHTML=`<div><b>${symbol} ${s.display.name} · (a,b)=(${s.a},${s.b})</b> · ${s.display.reason_label}</div><div class="small">${s.display.compatibility_label.toUpperCase()} · PYTHON-EXPORTED THEOREM RECORD · fixed k=${s.k} canonical MMMMVV</div>`;
}

function renderMap(){
  const map=currentMap(), rows=currentRows();
  const n=map.n, compact=window.matchMedia('(max-width:700px)').matches;
  const cw=compact?38:88, ch=compact?58:68, x0=compact?18:72, y0=compact?34:46;
  const width=x0+n*cw+(compact?18:42), height=compact?218:250;
  const svg=svgEl('svg',{viewBox:`0 0 ${width} ${height}`,class:`explorer-map-svg ${compact?'compact-map':''}`,'aria-label':`2 by ${n} physical map`});
  const pivotIds=new Set([rows.A.pivot_crease_id,rows.B.pivot_crease_id]);
  for(const f of map.faces){
    const x=x0+(f.column-1)*cw, y=y0+(f.row==='A'?0:ch);
    const g=svgEl('g',{'data-face':f.id,class:`map-face-group row-${f.row.toLowerCase()}`});
    const rect=svgEl('rect',{x,y,width:cw,height:ch,rx:3,class:'map-face-rect',tabindex:'0',role:'button','aria-label':f.label}); g.append(rect);
    if(els.labels.checked){const t=svgEl('text',{x:x+cw/2,y:y+ch/2+5,'text-anchor':'middle',class:'map-face-label'});t.textContent=f.label;g.append(t)}
    g.addEventListener('click',()=>setSelection(f.id)); g.addEventListener('keydown',ev=>{if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();setSelection(f.id)}}); svg.append(g);
  }
  for(const c of map.creases){
    let x1,y1,x2,y2,labelX,labelY;
    if(c.kind==='H'){x1=x0+(c.index-1)*cw;x2=x1+cw;y1=y2=y0+ch;labelX=x1+cw/2;labelY=y1+15;}
    else {x1=x2=x0+c.index*cw;const upper=c.kind==='U';y1=upper?y0:y0+ch;y2=y1+ch;labelX=x1+(upper?(compact?-7:-13):(compact?7:13));labelY=y1+ch/2;}
    const line=svgEl('line',{x1,y1,x2,y2,class:`map-crease mv-${c.mv.toLowerCase()} ${pivotIds.has(c.id)?'pivot-crease':''}`,'data-crease':c.id});svg.append(line);
    if(els.mv.checked){const t=svgEl('text',{x:labelX,y:labelY,'text-anchor':'middle',class:`crease-label ${pivotIds.has(c.id)?'pivot-label':''}`});t.textContent=`${c.label}:${c.mv}`;svg.append(t)}
  }
  const piv=currentPivots(); const note=svgEl('text',{x:width-(compact?8:20),y:height-(compact?10:18),'text-anchor':'end',class:'map-note'});note.textContent=`pA=${piv.a} on U${piv.a} · pB=${piv.b} on L${piv.b}`;svg.append(note);
  els.map.replaceChildren(svg);
  els.mapText.textContent=`Physical map k=${map.k}, word ${map.word}. Upper pivot U${piv.a}; lower pivot L${piv.b}.`;
}

function faceCard(id,classes=''){
  const label=faceLabel(id), row=label[0];
  const b=document.createElement('button'); b.type='button'; b.className=`explorer-face row-${row.toLowerCase()} ${classes}`; b.dataset.face=id; b.textContent=els.labels.checked?label:'·'; b.setAttribute('aria-label',label); b.onclick=()=>setSelection(id); return b;
}
function strip(label,ids,{pivot=null,first=null,last=null,physical=false}={}){
  const wrap=document.createElement('div');wrap.className='row-line';
  const lab=document.createElement('div');lab.className='row-line-label';lab.textContent=label;wrap.append(lab);
  const s=document.createElement('div');s.className='row-cards';
  ids.forEach((id,i)=>{const classes=[];if(id===first||id===last)classes.push('endpoint');if(physical&&pivot&&i===pivot-1)classes.push('pivot-after');s.append(faceCard(id,classes.join(' ')))});wrap.append(s);return wrap;
}
function signGlyph(sign){return sign==='-'?'R⁻':'R⁺';}
function renderRows(){
  const rows=currentRows(); const frag=document.createDocumentFragment();
  for(const [row,title] of [['A','Upper A row'],['B','Lower B row']]){
    const rf=rows[row]; const box=document.createElement('div');box.className='row-form-block';
    box.innerHTML=`<div class="row-form-title"><b>${title}</b><span class="mono">${signGlyph(rf.sign)} · p=${rf.pivot}</span></div>`;
    box.append(strip('PHYSICAL',rf.physical_order_face_ids,{pivot:rf.pivot,physical:true}));
    box.append(strip('LAYER ORDER',rf.layer_order_face_ids,{first:rf.first_face_id,last:rf.last_face_id})); frag.append(box);
  }
  els.rows.replaceChildren(frag);
}

function mvCommittedPrefix(){ const ev=currentEvent();return ev?ev.emitted_prefix_after:[]; }
function orderList(ids,{emptyMessage='No exported layer order for this scene.'}={}){
  const stack=document.createElement('ol'); stack.className=`global-layer-stack ${els.stackMode.value==='exploded'?'exploded':''}`;
  ids.forEach((id,i)=>{const li=document.createElement('li');li.append(faceCard(id.startsWith('face:')?id:`face:${id}`));if(els.stackMode.value==='exploded')li.style.transform=`translateX(${Math.min(i,10)*3}px)`;stack.append(li)});
  if(!ids.length){const e=document.createElement('div');e.className='empty-layer';e.textContent=emptyMessage;stack.append(e)} return stack;
}
function renderLayer(){
  if(state.mechanism==='mvmmmm'){
    const tr=mvTrace(), prefix=mvCommittedPrefix();
    const head=document.createElement('div');head.className='layer-meta';head.innerHTML=`<span>TOP ↓</span><span>${prefix.length}/${2*mvData.map.n} committed</span>`;
    const stack=orderList(prefix,{emptyMessage:'No committed events yet. Step the theorem trace.'});
    const foot=document.createElement('div');foot.className='layer-foot';
    if(tr.success&&state.step===tr.events.length)foot.innerHTML='<b>Complete literal order.</b> All 12 faces committed; horizontal stack is empty.';
    else if(!tr.success&&state.step===tr.events.length){const f=tr.failure;foot.innerHTML=`<b>STOP before ${faceLabel(f.candidate_face_id)}.</b> Failed candidate is not inserted into the layer order.`}
    else foot.textContent='Partial theorem reconstruction prefix.';
    els.layer.replaceChildren(head,stack,foot); return;
  }
  const s=mmScene(); const ids=s.construction?s.construction.layer_order_face_ids:[];
  const head=document.createElement('div');head.className='layer-meta';head.innerHTML=`<span>TOP ↓</span><span>${ids.length?`${ids.length}/${2*mmData.map.n} faces`:'no state exported'}</span>`;
  const stack=orderList(ids,{emptyMessage:'Incompatible scene: no exact labelled state is exported. Inspect the directed-cycle witness instead.'});
  const foot=document.createElement('div');foot.className='layer-foot';
  foot.innerHTML=s.construction?`<b>Exact theorem construction.</b> Independent semantic check: ${s.construction.independent_semantic_check.accepted?'accepted':'not accepted'}.`:`<b>No fabricated order.</b> ${s.display.reason_summary}`;
  els.layer.replaceChildren(head,stack,foot);
}

function renderMvTrace(){
  const tr=mvTrace(), ev=currentEvent();
  els.witness.hidden=true; els.traceTableWrap.hidden=false; els.stack.hidden=false;
  els.traceSummary.innerHTML=ev?`<div class="trace-heads"><div><span>Upper head before</span><b class="mono">${ev.upper_head_before??'∅'}</b></div><div><span>Lower request before</span><b class="mono">${ev.lower_head_before??'∅'}</b></div><div><span>Current event</span><b class="mono">${ev.face_label} · ${ev.action.toUpperCase()}</b></div></div>`:`<div class="small trace-reset-note">At reset: no event has been committed. Upper/lower streams are fixed by exported row forms.</div>`;
  const stackVals=ev?ev.stack_after_labels:[]; const stackTitle=document.createElement('div');stackTitle.className='stack-title';stackTitle.innerHTML='<span>Horizontal stack · bottom → top</span>';
  const chips=document.createElement('div');chips.className='stack-chips'; if(stackVals.length)stackVals.forEach((h,i)=>{const x=document.createElement('span');x.className='stack-chip';x.textContent=h;if(i===stackVals.length-1)x.classList.add('top');chips.append(x)});else{const x=document.createElement('span');x.className='stack-empty';x.textContent='∅';chips.append(x)} els.stack.replaceChildren(stackTitle,chips);
  els.traceHead.innerHTML='<tr><th>Step</th><th>Face</th><th>Action</th><th>Heads before</th><th>Stack after</th></tr>'; els.traceRows.innerHTML='';
  tr.events.forEach((e,i)=>{const row=document.createElement('tr');row.dataset.step=i+1;row.className=(state.step===i+1?'current-step ':'')+(e.status==='failed_candidate'?'failed-step':'');row.innerHTML=`<td>${String(e.display_step).padStart(2,'0')}</td><td class="mono"><button type="button" class="trace-face-link" data-face="${e.face_id}">${e.face_label}</button></td><td>${e.status==='failed_candidate'?'× '+(e.reason_code||'STOP'):e.action.toUpperCase()}</td><td class="mono">${e.upper_head_before??'∅'} / ${e.lower_head_before??'∅'}</td><td class="mono">${e.stack_after_labels.join(' ')||'∅'}</td>`;row.onclick=()=>{state.step=i+1;updateURL();renderStepDependent()};row.querySelector('.trace-face-link').onclick=ev2=>{ev2.stopPropagation();setSelection(e.face_id)};els.traceRows.append(row)});
}

function cycleGraph(scene){
  const w=scene.witness, width=460,height=300; const svg=svgEl('svg',{viewBox:`0 0 ${width} ${height}`,class:'cycle-witness-svg','aria-label':'Directed four-cycle witness'});
  const defs=svgEl('defs');const marker=svgEl('marker',{id:'cycleArrow',viewBox:'0 0 10 10',refX:'8',refY:'5',markerWidth:'7',markerHeight:'7',orient:'auto-start-reverse'});marker.append(svgEl('path',{d:'M 0 0 L 10 5 L 0 10 z',fill:'currentColor'}));defs.append(marker);svg.append(defs);
  const labels=w.cycle_labels.slice(0,-1); const pos=[[95,70],[365,70],[365,225],[95,225]]; const nodeW=84,nodeH=44;
  const edgeGeom=[
    [pos[0][0]+nodeW/2,pos[0][1],pos[1][0]-nodeW/2,pos[1][1]],
    [pos[1][0],pos[1][1]+nodeH/2,pos[2][0],pos[2][1]-nodeH/2],
    [pos[2][0]-nodeW/2,pos[2][1],pos[3][0]+nodeW/2,pos[3][1]],
    [pos[3][0],pos[3][1]-nodeH/2,pos[0][0],pos[0][1]+nodeH/2],
  ];
  w.edges.forEach((edge,i)=>{if(i>=state.step)return;const g=edgeGeom[i];const line=svgEl('line',{x1:g[0],y1:g[1],x2:g[2],y2:g[3],class:`cycle-edge ${edge.closes_cycle?'cycle-close':''}`,'marker-end':'url(#cycleArrow)'});svg.append(line);});
  labels.forEach((label,i)=>{const [x,y]=pos[i];const g=svgEl('g',{'data-face':`face:${label}`,class:`cycle-node ${state.selectedFace===`face:${label}`?'selected-face':''}`});g.append(svgEl('rect',{x:x-nodeW/2,y:y-nodeH/2,width:nodeW,height:nodeH,rx:7,class:`cycle-node-box row-${label[0].toLowerCase()}`}));const t=svgEl('text',{x,y:y+5,'text-anchor':'middle',class:'cycle-node-label'});t.textContent=label;g.append(t);g.addEventListener('click',()=>setSelection(`face:${label}`));svg.append(g)});
  return svg;
}
function renderMmMechanism(){
  const s=mmScene(); els.traceRows.innerHTML=''; els.traceHead.innerHTML='';
  if(s.construction){
    els.traceTableWrap.hidden=true; els.witness.hidden=true; els.stack.hidden=true;
    const c=s.construction; const box=document.createElement('div');box.className='construction-summary';
    box.innerHTML=`<div class="construction-kicker">${s.display.name}</div><h3>${s.display.reason_label}</h3><p>${s.display.reason_summary}</p><dl class="construction-facts"><div><dt>Construction family</dt><dd class="mono">${c.construction_family}</dd></div><div><dt>Parameter</dt><dd class="mono">${c.parameter_s??'—'}</dd></div><div><dt>Exact order</dt><dd>${c.layer_order.length} labelled faces</dd></div><div><dt>Semantic check</dt><dd>${c.independent_semantic_check.accepted?'✓ accepted':'not accepted'}</dd></div></dl><p class="small">No event-by-event physical or combinatorial trace is claimed for this prepared construction.</p>`;
    els.traceSummary.replaceChildren(box); return;
  }
  els.traceTableWrap.hidden=true; els.stack.hidden=true; els.witness.hidden=false;
  const edges=s.witness.edges; const shown=edges.slice(0,state.step);
  const summary=document.createElement('div');summary.className='witness-summary';summary.innerHTML=`<div><b>${s.display.reason_label}</b></div><p>${s.display.reason_summary}</p><div class="small">revealed ${shown.length} / ${edges.length} exported inequalities</div>`;els.traceSummary.replaceChildren(summary);
  const graph=cycleGraph(s); const list=document.createElement('ol');list.className='witness-edge-list';
  edges.forEach((e,i)=>{const revealed=i<state.step;const li=document.createElement('li');li.className=`witness-edge-item ${revealed?'revealed':'pending'} ${e.closes_cycle?'closing-edge':''}`;li.innerHTML=revealed?`<span class="mono">${e.relation_label}</span><span>${e.origin_label}</span>${e.closes_cycle?'<b>closes cycle</b>':''}`:`<span class="mono">step ${i+1}</span><span>pending exported inequality</span>`;list.append(li)});
  const status=document.createElement('div');status.className=`cycle-status ${state.step===edges.length?'complete':''}`;status.textContent=state.step===edges.length?s.witness.final_status_label:'Cycle not yet complete in this stepped view.';
  els.witness.replaceChildren(graph,list,status);
}
function renderTrace(){ if(state.mechanism==='mvmmmm')renderMvTrace(); else renderMmMechanism(); }

function renderProof(){
  if(state.mechanism==='mvmmmm'){
    const r=mvPairRecord(), tr=mvTrace(), ev=currentEvent(); const p=document.createElement('div');p.className='proof-grid';
    const left=document.createElement('div');left.innerHTML=`<div class="eyebrow">THEOREM REASON</div><h3>${r.compatible?'Equal exported BR blocks':'Unequal exported BR blocks'}</h3><p><span class="mono">BR(a)=${r.br_a}</span> · <span class="mono">BR(b)=${r.br_b}</span></p>`;
    const right=document.createElement('div');right.innerHTML=`<div class="eyebrow">TRACE PROVENANCE</div><p>The browser reads compatibility, reason codes, events, stack snapshots, and any failure record from the Python export.</p><p class="small">Movement, when enabled, is schematic correspondence only—not a physical folding trajectory.</p>`;
    if(ev?.status==='failed_candidate')right.innerHTML+=`<div class="failure"><b>${ev.reason_code}</b><br>requested ${ev.requested_closer}; blocking top ${ev.blocking_label}; stack ${ev.stack_before_labels.join(' ')}</div>`;
    if(els.annotation.value==='proof')left.innerHTML+=`<p class="small mono">trace_id=${r.trace_id}</p><p class="small">reason_codes=${r.reason_codes.join(', ')}</p>`;
    p.append(left,right);els.proof.replaceChildren(p);return;
  }
  const s=mmScene(), p=document.createElement('div');p.className='proof-grid'; const left=document.createElement('div'); const right=document.createElement('div');
  left.innerHTML=`<div class="eyebrow">THEOREM REASON</div><h3>${s.display.reason_label}</h3><p>${s.display.reason_summary}</p><p class="small mono">reason_codes=${s.reason_codes.join(', ')}</p>`;
  if(s.construction){right.innerHTML=`<div class="eyebrow">CONSTRUCTION / CHECK</div><p>Exact order comes from <span class="mono">${s.construction.construction_provenance.generation_path}</span>.</p><p>Independent theorem-blind semantic check: <b>${s.construction.independent_semantic_check.accepted?'accepted':'not accepted'}</b>.</p><p class="small">This is a combinatorial layer-order construction, not a physical folding trajectory.</p>`;}
  else {right.innerHTML=`<div class="eyebrow">OBSTRUCTION WITNESS</div><p>The four directed inequalities and their reveal order are read from the exported witness record.</p><p class="small mono">witness source=${s.witness.provenance.generation_path}</p><p class="small">No exact state is exported for this incompatible scene.</p>`;}
  if(els.annotation.value==='proof')right.innerHTML+=`<p class="small mono">scene_id=${s.id}</p>`; p.append(left,right);els.proof.replaceChildren(p);
}

function renderSelection(){document.querySelectorAll('[data-face]').forEach(el=>el.classList.toggle('selected-face',!!state.selectedFace&&el.dataset.face===state.selectedFace));}
function renderStepDependent(){
  const max=maxStep(); state.step=Math.max(0,Math.min(state.step,max)); els.traceControls.hidden=max===0; els.prev.disabled=state.step===0; els.next.disabled=state.step>=max; els.stepStatus.textContent=max?`step ${state.step} / ${max}`:'';
  renderLayer();renderTrace();renderProof();renderSelection(); if(state.motion)document.documentElement.classList.add('motion-on');else document.documentElement.classList.remove('motion-on');
}
function renderAll(){configureControls();renderStatus();renderMap();renderRows();renderStepDependent();}
function updateURL(){
  if(state.mechanism==='mvmmmm')setQS({mechanism:'mvmmmm',scene:null,a:state.a,b:state.b,step:state.step||null,annotations:state.annotation,stack:state.stackMode});
  else setQS({mechanism:'mmmmvv',scene:state.scene,a:null,b:null,step:state.step||null,annotations:state.annotation,stack:state.stackMode});
}
function changePair(){state.a=+els.a.value;state.b=+els.b.value;state.step=0;state.selectedFace=null;updateURL();renderAll();}
function changeMechanism(){state.mechanism=els.mechanism.value;state.step=0;state.selectedFace=null;state.motion=false;updateURL();renderAll();}
function changeScene(){state.scene=els.scene.value;state.step=0;state.selectedFace=null;updateURL();renderAll();}

els.mechanism.onchange=changeMechanism; els.scene.onchange=changeScene; els.a.onchange=changePair; els.b.onchange=changePair;
els.annotation.onchange=()=>{state.annotation=els.annotation.value;updateURL();renderProof();};
els.stackMode.onchange=()=>{state.stackMode=els.stackMode.value;updateURL();renderLayer();renderSelection();};
els.labels.onchange=()=>{renderMap();renderRows();renderLayer();renderSelection();}; els.mv.onchange=renderMap;
els.motion.onchange=()=>{state.motion=els.motion.checked&&!window.matchMedia('(prefers-reduced-motion: reduce)').matches;renderStepDependent();};
els.prev.onclick=()=>{state.step--;updateURL();renderStepDependent();}; els.next.onclick=()=>{state.step++;updateURL();renderStepDependent();}; els.reset.onclick=()=>{state.step=0;state.selectedFace=null;updateURL();renderAll();};
window.addEventListener('keydown',e=>{if(['INPUT','SELECT','TEXTAREA'].includes(document.activeElement?.tagName))return;if(e.key==='ArrowRight'&&state.step<maxStep()){state.step++;updateURL();renderStepDependent()}if(e.key==='ArrowLeft'&&state.step>0){state.step--;updateURL();renderStepDependent()}});


const compactMapMedia=window.matchMedia('(max-width:700px)');
compactMapMedia.addEventListener?.('change',()=>{renderMap();renderSelection();});

state.a=Math.min(5,Math.max(1,state.a)); state.b=Math.min(5,Math.max(1,state.b)); state.step=Math.min(state.step,maxStep()); renderAll();
