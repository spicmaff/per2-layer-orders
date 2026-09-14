import {loadJSON,qs,setQS} from './common.js';
const data=await loadJSON('../data/row-forms-v1.json');
const kSel=document.querySelector('#k');const pSel=document.querySelector('#p');const signSel=document.querySelector('#sign');const physical=document.querySelector('#physical');const order=document.querySelector('#order');const meta=document.querySelector('#meta');
for(let k=2;k<=12;k++){const o=document.createElement('option');o.value=k;o.textContent=k;kSel.append(o)}
function fillP(){const k=+kSel.value;pSel.innerHTML='';for(let p=1;p<2*k;p++){const o=document.createElement('option');o.value=p;o.textContent=p;pSel.append(o)}pSel.value=Math.min(+qs('p','3'),2*k-1)}
function face(c,cls=''){const d=document.createElement('div');d.className=`face ${cls}`;d.textContent=`F${c}`;return d}
function render(){const k=+kSel.value,p=+pSel.value,sign=signSel.value;const r=data.records.find(x=>x.k===k&&x.pivot===p);if(!r)return;setQS({k,p,sign});physical.innerHTML='';for(let c=1;c<=2*k;c++){const f=face(c,c===p?'pivot-after':'');physical.append(f)}order.innerHTML='';const seq=sign==='+'?r.plus:r.minus;seq.forEach((c,i)=>order.append(face(c,(i===0||i===seq.length-1)?'endpoint':'')));meta.innerHTML=`Pivot <b>p=${p}</b> is the physical seam between F${p} and F${p+1}. First/last in R${sign}: F${seq[0]}, F${seq.at(-1)}.`}
kSel.value=qs('k','3');fillP();pSel.value=qs('p','3');signSel.value=qs('sign','+');kSel.onchange=()=>{fillP();render()};pSel.onchange=render;signSel.onchange=render;render();
