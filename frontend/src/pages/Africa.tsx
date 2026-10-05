import { Globe2, Search } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import type { Publication } from '../types'

const countries=['Algeria','Angola','Benin','Botswana','Burkina Faso','Burundi','Cabo Verde','Cameroon','Central African Republic','Chad','Comoros','Congo','Côte d’Ivoire','Democratic Republic of the Congo','Djibouti','Egypt','Equatorial Guinea','Eritrea','Eswatini','Ethiopia','Gabon','Gambia','Ghana','Guinea','Guinea-Bissau','Kenya','Lesotho','Liberia','Libya','Madagascar','Malawi','Mali','Mauritania','Mauritius','Morocco','Mozambique','Namibia','Niger','Nigeria','Rwanda','São Tomé and Príncipe','Senegal','Seychelles','Sierra Leone','Somalia','South Africa','South Sudan','Sudan','Tanzania','Togo','Tunisia','Uganda','Zambia','Zimbabwe']
export default function Africa(){
 const [pubs,setPubs]=useState<Publication[]>([]); const [q,setQ]=useState('')
 useEffect(()=>{api<Publication[]>('/publications').then(setPubs).catch(()=>{})},[])
 const counts=useMemo(()=>Object.fromEntries(countries.map(c=>[c,pubs.filter(p=>p.country===c).length])),[pubs])
 const filtered=countries.filter(c=>c.toLowerCase().includes(q.toLowerCase()))
 return <div className="page section production-page"><div className="section-head"><div><div className="eyebrow dark">AFRICA KNOWLEDGE MAP</div><h1>Explore research country by country.</h1><p className="lead">A continent-wide discovery layer connecting countries to published AGP research and evidence.</p></div><Globe2 size={40}/></div><div className="tool-search"><Search size={17}/><input value={q} onChange={e=>setQ(e.target.value)} placeholder="Find an African country"/></div><div className="country-grid">{filtered.map(country=><Link className="card country-card" to={`/research?q=${encodeURIComponent(country)}`} key={country}><strong>{country}</strong><span>{counts[country]} published {counts[country]===1?'work':'works'}</span></Link>)}</div></div>
}
