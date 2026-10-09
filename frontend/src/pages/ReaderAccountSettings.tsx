import { Save, UserRound } from 'lucide-react'
import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { useAuth } from '../lib/auth'

export default function ReaderAccountSettings(){
  const {user,refresh}=useAuth()
  const [form,setForm]=useState({first_name:'',last_name:'',country:''})
  const [busy,setBusy]=useState(false)
  const [message,setMessage]=useState('')
  const [error,setError]=useState('')

  useEffect(()=>{
    if(user)setForm({
      first_name:user.first_name||'',
      last_name:user.last_name||'',
      country:user.country||''
    })
  },[user])

  function change(e:React.ChangeEvent<HTMLInputElement>){
    setForm({...form,[e.target.name]:e.target.value})
  }

  async function submit(e:React.FormEvent){
    e.preventDefault()
    setBusy(true)
    setMessage('')
    setError('')
    try{
      await api('/auth/me',{method:'PATCH',body:JSON.stringify(form)})
      await refresh()
      setMessage('Your Reader account settings have been updated.')
    }catch(err){
      setError(err instanceof Error?err.message:'Unable to update account.')
    }finally{
      setBusy(false)
    }
  }

  return <div className="page section narrow-form">
    <div className="page-title">
      <div className="eyebrow dark">READER ACCOUNT</div>
      <h1>Account Settings.</h1>
      <p>Manage the basic information attached to your private Reader account. Reader accounts are never listed in the public Researchers directory.</p>
    </div>

    <form className="card publication-form" onSubmit={submit}>
      <div className="profile-editor-heading">
        <UserRound/>
        <div><strong>Private account information</strong><small>Your registered email is {user?.email}.</small></div>
      </div>

      {message&&<div className="alert success">{message}</div>}
      {error&&<div className="alert error">{error}</div>}

      <div className="form-grid">
        <label>First name<input name="first_name" required value={form.first_name} onChange={change}/></label>
        <label>Last name<input name="last_name" required value={form.last_name} onChange={change}/></label>
        <label className="span-2">Country<input name="country" value={form.country} onChange={change}/></label>
      </div>

      <div className="form-actions">
        <button className="button dark large" disabled={busy}><Save size={17}/>{busy?'Saving…':'Save Account Settings'}</button>
      </div>
    </form>
  </div>
}