import {Bell,BookOpen,ChevronDown,Menu,Search,X} from 'lucide-react'
import {useEffect,useState} from 'react'
import {Link,NavLink,Outlet,useLocation,useNavigate} from 'react-router-dom'
import {useAuth} from '../lib/auth'
import AfricaLogo from './AfricaLogo'

const editorialRoles=['reviewer','editor','senior_editor','managing_editor']
const contentRoles=['editor','senior_editor','managing_editor','super_admin']

export default function Layout(){
  const[open,setOpen]=useState(false)
  const[query,setQuery]=useState('')
  const{user,logout}=useAuth()
  const nav=useNavigate()
  const location=useLocation()

  const editorial=editorialRoles.includes(user?.role||'')
  const superAdmin=user?.role==='super_admin'
  const community=Boolean(user&&!editorial&&!superAdmin)
  const homePath=superAdmin?'/system':editorial?'/editorial':'/dashboard'
  const homeLabel=superAdmin?'Control Centre':editorial?'Editorial Desk':'Dashboard'
  const contentManager=Boolean(user&&contentRoles.includes(user.role))

  useEffect(()=>{
    setOpen(false)
    document.documentElement.scrollTop=0
    document.body.scrollTop=0
    window.scrollTo({top:0,left:0,behavior:'auto'})
  },[location.pathname,location.search])

  function doSearch(e:React.FormEvent){
    e.preventDefault()
    if(query.trim())nav(`/research?q=${encodeURIComponent(query.trim())}`)
  }

  return <div className="app-shell">
    <div className="topline">Independent African research, evidence & policy intelligence</div>

    <header className="header">
      <Link to="/" className="brand" onClick={()=>setOpen(false)}>
        <AfricaLogo/><span><strong>Africa & Global Power</strong><small>Research Africa. Understand Power.</small></span>
      </Link>

      <button className="menu-btn" onClick={()=>setOpen(!open)} aria-label="Toggle navigation" aria-expanded={open}>{open?<X/>:<Menu/>}</button>

      <nav className={open?'nav open':'nav'}>
        <NavLink to="/research">Research</NavLink>
        <NavLink to="/researchers">Researchers</NavLink>
        <NavLink to="/africa">Africa</NavLink>
        <NavLink to="/opportunities">Opportunities</NavLink>

        <div className="nav-more tools-menu">
          <span>Tools <ChevronDown size={15}/></span>
          <div className="tools-dropdown">
            <Link to="/data-lab">Data Lab</Link>
            <Link to="/policy-tracker">Policy Tracker</Link>
            {community&&<Link to="/research-rooms">Research Rooms</Link>}
            {community&&<Link to="/saved">Saved Research</Link>}
            {community&&<Link to="/following">Following</Link>}
            {community&&<Link to="/notifications">Notifications</Link>}
            <Link to="/trust">Trust Centre</Link>
            {(editorial||superAdmin)&&<Link to="/editorial">Editorial Review Desk</Link>}
            {(editorial||superAdmin)&&<Link to="/editorial/amplification">Amplification Desk</Link>}
            {contentManager&&<Link to="/editorial/content">Content Studio</Link>}
            {superAdmin&&<Link to="/system">System Administration</Link>}
          </div>
        </div>

        <NavLink to="/about">About</NavLink>
        <NavLink to="/privacy">Privacy</NavLink>
        <NavLink to="/terms">Terms</NavLink>

        <div className="mobile-auth">
          {user?<>
            <Link className="button ghost" to={homePath}>{homeLabel}</Link>
            {community&&<Link className="button ghost" to="/notifications"><Bell size={16}/> Alerts</Link>}
            <button className="button dark" onClick={logout}>Sign out</button>
          </>:<>
            <Link className="button ghost" to="/login">Sign in</Link>
            <Link className="button lime" to="/register">Join AGP</Link>
          </>}
        </div>
      </nav>

      <div className="nav-actions">
        <form onSubmit={doSearch} className="nav-search"><Search size={17}/><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Search research"/></form>
        {user?<>
          {community&&<Link className="icon-action" to="/notifications" aria-label="Notifications"><Bell size={18}/></Link>}
          <Link className="button ghost" to={homePath}>{homeLabel}</Link>
          <button className="button dark" onClick={logout}>Sign out</button>
        </>:<>
          <Link className="button ghost" to="/login">Sign in</Link>
          <Link className="button lime" to="/register">Join AGP</Link>
        </>}
      </div>
    </header>

    <main><Outlet/></main>

    <footer className="footer">
      <div>
        <div className="brand footer-brand"><AfricaLogo inverse/><span><strong>Africa & Global Power</strong><small>African research, evidence and intelligence for a changing world.</small></span></div>
        <p className="muted">A professional platform connecting researchers, evidence, policy intelligence and African perspectives.</p>
      </div>

      <div><strong>Platform</strong><Link to="/research">Research</Link><Link to="/researchers">Researchers</Link><Link to="/data-lab">Data Lab</Link><Link to="/policy-tracker">Policy Tracker</Link><Link to="/africa">Africa</Link></div>

      <div><strong>Participate</strong><Link to="/register">Create account</Link><Link to="/dashboard/new-publication">Publish research</Link><Link to="/research-rooms">Research Rooms</Link><Link to="/opportunities">Opportunities</Link><Link to="/contact">Contact</Link></div>

      <div><strong>Trust & Legal</strong><Link to="/about">About Us</Link><Link to="/privacy">Privacy Policy</Link><Link to="/terms">Terms & Conditions</Link><Link to="/trust">Trust Centre</Link><Link to="/editorial-policy">Editorial Policy</Link><Link to="/research-integrity">Research Integrity</Link><Link to="/help">Help & Guide</Link><a href="/AGP-User-Guide.pdf" download>Download User Guide</a></div>

      <div className="footer-bottom"><BookOpen size={16}/> Africa & Global Power © {new Date().getFullYear()}</div>
    </footer>
  </div>
}
