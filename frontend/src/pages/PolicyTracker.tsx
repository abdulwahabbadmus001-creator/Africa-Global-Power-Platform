import { ExternalLink, Search, Scale } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { api } from '../lib/api'

type Policy={id:string;title:string;slug:string;country:string;institution:string;policy_area:string;status:string;summary:string;agp_analysis:string;source_url:string;published_date?:string|null;effective_date?:string|null;tags:string[];updated_at:string}
export default function PolicyTracker(){
 const [items,setItems]=useState<Policy[]>([]); const [q,setQ]=useState('')
 useEffect(()=>{api<Policy[]>('/policy-tracker').then(setItems).catch(()=>{})},[])
 const filtered=useMemo(()=>items.filter(x=>`${x.title} ${x.country} ${x.institution} ${x.policy_area} ${x.status} ${x.summary}`.toLowerCase().includes(q.toLowerCase())),[items,q])
 return <div className="page section production-page"><div className="section-head"><div><div className="eyebrow dark">AGP POLICY TRACKER</div><h1>Track the rules shaping Africa.</h1><p className="lead">Follow consequential laws, regulations, strategies and institutional policy changes across African countries.</p></div><Scale size={38}/></div>
 <div className="tool-search"><Search size={17}/><input value={q} onChange={e=>setQ(e.target.value)} placeholder="Search country, institution, policy area or status"/></div>
 <div className="content-grid">{filtered.map(item=><article className="card content-card" key={item.id}><div className="content-meta"><span>{item.country}</span><span>{item.status}</span></div><h2>{item.title}</h2><small>{item.institution} • {item.policy_area}</small><p>{item.summary}</p>{item.agp_analysis&&<div className="analysis-note"><strong>AGP analysis</strong><p>{item.agp_analysis}</p></div>}<a className="button ghost" href={item.source_url} target="_blank" rel="noreferrer">Official source <ExternalLink size={14}/></a></article>)}</div>
 {!filtered.length&&<div className="card panel">No policy records match this search yet.</div>}</div>
}
