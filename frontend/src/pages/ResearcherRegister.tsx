import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../lib/api'

type RegistrationResponse={message:string;email:string;requires_verification:boolean}

export default function ResearcherRegister(){
  const navigate=useNavigate()
  const [form,setForm]=useState({
    first_name:'',
    last_name:'',
    email:'',
    password:'',
    country:'',
    institution:'',
    professional_headline:'',
    expertise:''
  })
  const [error,setError]=useState('')
  const [busy,setBusy]=useState(false)

  function change(e:React.ChangeEvent<HTMLInputElement|HTMLTextAreaElement>){
    setForm(current=>({...current,[e.target.name]:e.target.value}))
  }

  async function submit(e:React.FormEvent){
    e.preventDefault()
    setBusy(true)
    setError('')
    try{
      const result=await api<RegistrationResponse>('/auth/register',{
        method:'POST',
        body:JSON.stringify({...form,requested_role:'researcher'})
      })
      navigate(`/verify-email?email=${encodeURIComponent(result.email)}`)
    }catch(err){
      setError(err instanceof Error?err.message:'Unable to create Researcher account.')
    }finally{
      setBusy(false)
    }
  }

  return <div className="auth-page">
    <form className="auth-card wide card researcher-register" onSubmit={submit}>
      <div className="eyebrow dark">RESEARCHER REGISTRATION</div>
      <h1>Create your Researcher account.</h1>
      <p>Start your professional AGP research identity. After email verification, complete your full public profile and submit research for editorial review.</p>

      {error&&<div className="alert error">{error}</div>}

      <div className="form-grid">
        <label>First name<input name="first_name" required minLength={2} value={form.first_name} onChange={change}/></label>
        <label>Last name<input name="last_name" required minLength={2} value={form.last_name} onChange={change}/></label>
        <label>Email<input name="email" type="email" required value={form.email} onChange={change}/></label>
        <label>Country<input name="country" required value={form.country} onChange={change} placeholder="e.g. Nigeria"/></label>
        <label className="span-2">Institution / organisation<input name="institution" required value={form.institution} onChange={change} placeholder="University, research institute, organisation or Independent researcher"/></label>
        <label className="span-2">Professional headline<input name="professional_headline" required maxLength={180} value={form.professional_headline} onChange={change} placeholder="e.g. AI Governance Researcher & Policy Analyst"/></label>
        <label className="span-2">Primary expertise / research focus<textarea name="expertise" required rows={3} value={form.expertise} onChange={change} placeholder="Briefly describe your main research areas."/></label>
        <label className="span-2">Password<input name="password" type="password" required minLength={10} maxLength={128} value={form.password} onChange={change}/><small>Minimum 10 characters.</small></label>
      </div>

      <div className="researcher-register-note">After verification, use <strong>Edit Public Profile</strong> to add your biography, research interests, tools, technical stack, languages, ORCID, LinkedIn, Google Scholar, ResearchGate and Featured Works.</div>

      <button className="button lime dark-text large full" disabled={busy}>{busy?'Creating Researcher account…':'Create Researcher Account'}</button>
      <small>Only want to read and follow research? <Link to="/register/reader">Create a Reader account</Link></small>
      <small>Already registered? <Link to="/login">Sign in</Link></small>
    </form>
  </div>
}