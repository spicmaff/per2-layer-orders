import {loadJSON,qs,setQS} from './common.js';
const data=await loadJSON('../data/classification-v1.json');
const grid=document.querySelector('#atlas-grid'); const detail=document.querySelector('#detail');
function bitIndex(s){return parseInt([...s].map(c=>c==='M'?'0':'1').join(''),2)}
const records=[...data.records].sort((a,b)=>bitIndex(a.P.slice(0,3))-bitIndex(b.P.slice(0,3))||bitIndex(a.P.slice(3))-bitIndex(b.P.slice(3)));
let selected=qs('word','MMMMVV');
function renderDetail(r){detail.innerHTML=`<h2><code>${r.P}</code></h2><p><b>${r.regime}</b> · ρ=${r.rho}, τ=${r.tau}, δ₀=${r.delta0}, δ₁=${r.delta1}</p><p>Canonical source: <code>${r.canonical_source_family}</code> via <code>${r.exact_transport}</code></p><p>${r.compatibility_rule==='N/A'?'':`Compatibility: <code>${r.compatibility_rule}</code>`}</p><p class="small">Count formula: ${r['C_P(k)']} · theorem-derived record.</p>`}
for(const r of records){const b=document.createElement('button');b.className='atlas-cell';b.dataset.regime=r.regime;b.innerHTML=`<div class="word">${r.P}</div><div class="small">${r.regime.replace('CONSTANT_','')}</div>`;b.addEventListener('click',()=>select(r.P));b.dataset.word=r.P;grid.append(b)}
function select(word){selected=word;setQS({word});for(const b of grid.children)b.setAttribute('aria-pressed',b.dataset.word===word?'true':'false');renderDetail(records.find(r=>r.P===word)||records[0])}
select(selected);
