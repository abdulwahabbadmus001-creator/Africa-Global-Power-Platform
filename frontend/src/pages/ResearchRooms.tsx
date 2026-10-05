import { Lock, Plus, Users } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'

type Room={id:string;owner_id:string;title:string;slug:string;description:string;topic:string;visibility:string;join_policy:string;member_count:number;is_member:boolean;created_at:string}
export default function ResearchRooms(){
 const [rooms,setRooms]=useState<Room[]>([]); const [show,setShow]=useState(false); const [form,setForm]=useState({title:'',description:'',topic:'',visibility:'public',join_policy:'open'}); const [error,setError]=useState('')
 const load=()=>api<Room[]>('/research-rooms').then(setRooms).catch(e=>setError(e instanceof Error?e.message:'Unable to load rooms'))
 useEffect(()=>{load()},[])
 async function create(e:React.FormEvent){e.preventDefault();setError('');try{await api('/research-rooms',{method:'POST',body:JSON.stringify(form)});setShow(false);setForm({title:'',description:'',topic:'',visibility:'public',join_policy:'open'});load()}catch(e){setError(e instanceof Error?e.message:'Unable to create room')}}
 return <div className="page section production-page"><div className="section-head"><div><div className="eyebrow dark">AGP RESEARCH ROOMS</div><h1>Collaborate around serious questions.</h1><p className="lead">Create focused research spaces, bring peers together, discuss evidence and organise useful resources.</p></div><button className="button dark large" onClick={()=>setShow(!show)}><Plus size={18}/> New room</button></div>
 {error&&<div className="alert error">{error}</div>}
 {show&&<form className="card production-form" onSubmit={create}><h2>Create research room</h2><label>Room title<input required value={form.title} onChange={e=>setForm({...form,title:e.target.value})}/></label><label>Topic<input required value={form.topic} onChange={e=>setForm({...form,topic:e.target.value})}/></label><label>Description<textarea rows={4} value={form.description} onChange={e=>setForm({...form,description:e.target.value})}/></label><div className="form-grid"><label>Visibility<select value={form.visibility} onChange={e=>setForm({...form,visibility:e.target.value})}><option value="public">Public</option><option value="private">Private</option></select></label><label>Join policy<select value={form.join_policy} onChange={e=>setForm({...form,join_policy:e.target.value})}><option value="open">Open</option><option value="invite">Invite only</option></select></label></div><button className="button dark" type="submit">Create room</button></form>}
 <div className="content-grid">{rooms.map(room=><Link to={`/research-rooms/${room.slug}`} className="card content-card" key={room.id}><div className="content-meta"><span>{room.topic}</span><span>{room.visibility==='private'?<><Lock size={12}/> Private</>: 'Public'}</span></div><h2>{room.title}</h2><p>{room.description}</p><small><Users size={13}/> {room.member_count} members • {room.is_member?'Joined':room.join_policy==='open'?'Open to join':'Invite only'}</small></Link>)}</div>{!rooms.length&&<div className="card panel">No research rooms yet. Create the first one.</div>}</div>
}
