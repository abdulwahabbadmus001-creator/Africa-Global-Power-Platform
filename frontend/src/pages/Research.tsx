import { Search } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../lib/api'
import type { Publication } from '../types'

export default function Research(){
 const [params,setParams]=useSearchParams(); const [pubs,setPubs]=useState<Publication[]>([]); const [loading,setLoading]=useState(true); const q=params.get('q')||''; const [input,setInput]=useState(q)
 useEffect(()=>{setLoading(true);api<Publication[]>(`/publications${q?`?q=${encodeURIComponent(q)}`:''}`).then(setPubs).finally(()=>setLoading(false))},[q])
 return <div className="page section"><div className="page-title"><div className="eyebrow dark">AGP RESEARCH</div><h1>Evidence for Africa's changing world.</h1><p>Policy analysis, working research and long-form intelligence from researchers across Africa and its global networks.</p></div>
 <form className="research-search" onSubmit={e=>{e.preventDefault();setParams(input?{q:input}:{})}}><Search/><input value={input} onChange={e=>setInput(e.target.value)} placeholder="Search topics, countries, institutions or keywords"/><button className="button dark">Search</button></form>
 <div className="chips"><button>All research</button><button>Geopolitics</button><button>AI & Technology</button><button>Political Economy</button><button>Trade</button><button>Governance</button></div>
 {loading?<div className="skeleton-list">Loading research…</div>:<div className="research-list">{pubs.map(p=><Link to={`/research/${p.slug}`} className="research-row" key={p.id}><div><div className="publication-meta"><span>{p.publication_type}</span><span>{p.topic}</span><span>{p.region||p.country}</span></div><h2>{p.title}</h2><p>{p.abstract}</p><div className="author-line">{p.author?`${p.author.first_name} ${p.author.last_name}`:'AGP Research'} • {p.published_at?new Date(p.published_at).toLocaleDateString():''}</div></div><span className="arrow">→</span></Link>)}</div>}
 {!loading&&!pubs.length&&<div className="empty-card">No published research matches this search.</div>}</div>
}
