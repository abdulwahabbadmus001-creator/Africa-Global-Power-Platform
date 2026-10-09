import {useState} from 'react'
import {useNavigate} from 'react-router-dom'
import {api} from '../lib/api'
import {useAuth} from '../lib/auth'
import type {User} from '../types'

type EditorialSuccess={message:string;user:User}

export default function EditorialVerify(){
  const navigate=useNavigate()
  const{refresh}=useAuth()
  const[useRecovery,setUseRecovery]=useState(false)
  const[code,setCode]=useState('')
  const[recoveryCode,setRecoveryCode]=useState('')
  const[error,setError]=useState('')
  const[busy,setBusy]=useState(false)

  async function submit(event:React.FormEvent){
    event.preventDefault()
    setBusy(true)
    setError('')

    try{
      const result=await api<EditorialSuccess>(
        '/auth/editorial/mfa/verify',
        {
          method:'POST',
          body:JSON.stringify(useRecovery?{recovery_code:recoveryCode}:{code}),
        },
      )

      await refresh()
      navigate(result.user.role==='super_admin'?'/system':'/editorial',{replace:true})
    }catch(err){
      setError(err instanceof Error?err.message:'Unable to complete editorial authentication.')
    }finally{
      setBusy(false)
    }
  }

  return <div className="auth-page">
    <form className="auth-card card" onSubmit={submit}>
      <div className="eyebrow dark">EDITORIAL MFA</div>
      <h1>Verify editorial access.</h1>
      <p>Complete multi-factor authentication before the editorial workspace is opened.</p>

      {error&&<div className="alert error">{error}</div>}

      {!useRecovery?<label>
        Authenticator code
        <input inputMode="numeric" maxLength={6} required value={code} onChange={e=>setCode(e.target.value.replace(/\D/g,'').slice(0,6))} autoComplete="one-time-code"/>
      </label>:<label>
        Recovery code
        <input required value={recoveryCode} onChange={e=>setRecoveryCode(e.target.value)} placeholder="AGP-XXXX-XXXX-XXXX"/>
      </label>}

      <button className="button dark large full" type="submit" disabled={busy}>{busy?'Verifying…':'Enter Editorial'}</button>
      <button type="button" className="button ghost large full" style={{marginTop:'10px'}} onClick={()=>{setUseRecovery(v=>!v);setError('')}}>{useRecovery?'Use authenticator code':'Use a recovery code'}</button>
    </form>
  </div>
}
