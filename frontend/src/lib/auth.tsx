import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import { api } from './api'
import type { User } from '../types'

type AuthContextValue = { user:User|null; loading:boolean; refresh:()=>Promise<void>; logout:()=>Promise<void> }
const AuthContext = createContext<AuthContextValue>({user:null,loading:true,refresh:async()=>{},logout:async()=>{}})

export function AuthProvider({children}:{children:ReactNode}){
  const [user,setUser]=useState<User|null>(null); const [loading,setLoading]=useState(true)
  async function refresh(){ try{ setUser(await api<User>('/auth/me')) } catch { setUser(null) } finally { setLoading(false) } }
  async function logout(){ await api('/auth/logout',{method:'POST'}); setUser(null) }
  useEffect(()=>{ refresh() },[])
  return <AuthContext.Provider value={{user,loading,refresh,logout}}>{children}</AuthContext.Provider>
}
export const useAuth=()=>useContext(AuthContext)
