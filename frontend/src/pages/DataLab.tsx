import { Database, Download, ExternalLink, Search } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { api } from '../lib/api'

type Dataset={id:string;title:string;slug:string;summary:string;description:string;category:string;region?:string|null;country?:string|null;source_name:string;source_url:string;download_url?:string|null;license_name?:string|null;tags:string[];coverage_start?:string|null;coverage_end?:string|null;updated_at:string}

export default function DataLab(){
 const [items,setItems]=useState<Dataset[]>([]); const [q,setQ]=useState('')
 useEffect(()=>{api<Dataset[]>('/data-lab').then(setItems).catch(()=>{})},[])
 const filtered=useMemo(()=>items.filter(x=>`${x.title} ${x.summary} ${x.category} ${x.country||''} ${x.tags.join(' ')}`.toLowerCase().includes(q.toLowerCase())),[items,q])
 return <div className="page section production-page"><div className="section-head"><div><div className="eyebrow dark">AGP DATA LAB</div><h1>Evidence you can inspect and reuse.</h1><p className="lead">Curated datasets, indicators and source material for African policy, political economy, technology and global-power research.</p></div><Database size={38}/></div>
 <div className="tool-search"><Search size={17}/><input value={q} onChange={e=>setQ(e.target.value)} placeholder="Search datasets, countries, categories or tags"/></div>
 <div className="content-grid">{filtered.map(item=><article className="card content-card" key={item.id}><div className="content-meta"><span>{item.category}</span><span>{item.country||item.region||'Africa'}</span></div><h2>{item.title}</h2><p>{item.summary}</p><small>Source: {item.source_name}{item.license_name?` • ${item.license_name}`:''}</small><div className="card-actions"><a className="button ghost" href={item.source_url} target="_blank" rel="noreferrer">Source <ExternalLink size={14}/></a>{item.download_url&&<a className="button dark" href={item.download_url} target="_blank" rel="noreferrer"><Download size={14}/> Download</a>}</div></article>)}</div>
 {!filtered.length&&<div className="card panel">No published datasets match this search yet.</div>}</div>
}
