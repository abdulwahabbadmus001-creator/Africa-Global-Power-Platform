import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../lib/api'

type RegistrationResponse={message:string;email:string;requires_verification:boolean}

export default function ReaderRegister(){
  const navigate=useNavigate()
  const [form,setForm]=useState({first_name:'',last_name:'',email:'',password:'',country:''})
  const [error,setError]=useState('')
  const [busy,setBusy]=useState(false)

  function change(e:React.ChangeEvent<HTMLInputElement>){
    setForm(current=>({...current,[e.target.name]:e.target.value}))
  }

  async function submit(e:React.FormEvent){
    e.preventDefault()
    setBusy(true)
    setError('')
    try{
      const result=await api<RegistrationResponse>('/auth/register',{
        method:'POST',
        body:JSON.stringify({...form,requested_role:'reader',institution:null})
      })
      navigate(`/verify-email?email=${encodeURIComponent(result.email)}`)
    }catch(err){
      setError(err instanceof Error?err.message:'Unable to create Reader account.')
    }finally{
      setBusy(false)
    }
  }

  return <div className="auth-page">
    <form className="auth-card wide card" onSubmit={submit}>
      <div className="eyebrow dark">READER REGISTRATION</div>
      <h1>Create your Reader account.</h1>
      <p>A lightweight private account for reading, saving, following researchers and sending professional inquiries.</p>

      {error&&<div className="alert error">{error}</div>}

      <div className="form-grid">
        <label>First name<input name="first_name" required minLength={2} value={form.first_name} onChange={change}/></label>
        <label>Last name<input name="last_name" required minLength={2} value={form.last_name} onChange={change}/></label>
        <label className="span-2">Email<input name="email" type="email" required value={form.email} onChange={change}/></label>
        <label>Country<input name="country" value={form.country} onChange={change} placeholder="e.g. Nigeria"/></label>
        <label>Password<input name="password" type="password" required minLength={10} maxLength={128} value={form.password} onChange={change}/><small>Minimum 10 characters.</small></label>
      </div>

      <button className="button dark large full" disabled={busy}>{busy?'Creating Reader account…':'Create Reader Account'}</button>
      <small>Want to publish research? <Link to="/register/researcher">Create a Researcher account</Link></small>
      <small>Already registered? <Link to="/login">Sign in</Link></small>
    </form>
  </div>
}