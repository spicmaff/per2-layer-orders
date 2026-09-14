export async function loadJSON(url){const r=await fetch(url);if(!r.ok)throw new Error(`${r.status} ${url}`);return r.json()}
export function qs(name, fallback=null){const u=new URL(location.href);return u.searchParams.get(name)??fallback}
export function setQS(values){const u=new URL(location.href);Object.entries(values).forEach(([k,v])=>{if(v==null)u.searchParams.delete(k);else u.searchParams.set(k,String(v))});history.replaceState(null,'',u)}
export function escapeText(x){return String(x)}
