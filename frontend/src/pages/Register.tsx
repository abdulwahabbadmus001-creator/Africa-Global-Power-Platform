import { ArrowRight, BookOpen, Microscope } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function Register(){
  return <div className="auth-page join-choice-page">
    <div className="join-choice-shell">
      <div className="eyebrow dark">JOIN AFRICA & GLOBAL POWER</div>
      <h1>Choose how you want to use AGP.</h1>
      <p className="join-choice-intro">Reader and Researcher accounts serve different purposes, so each has its own registration form and workspace.</p>

      <div className="join-choice-grid">
        <article className="card join-choice-card">
          <div className="join-choice-icon"><BookOpen size={28}/></div>
          <div className="eyebrow dark">READER ACCOUNT</div>
          <h2>Read, save and connect.</h2>
          <p>For readers, professionals and organisations that want to discover African research and connect with researchers.</p>
          <ul>
            <li>Save research</li>
            <li>Follow researchers</li>
            <li>Receive notifications</li>
            <li>Send opportunity or collaboration inquiries</li>
          </ul>
          <Link className="button dark large full" to="/register/reader">Create Reader Account <ArrowRight size={17}/></Link>
        </article>

        <article className="card join-choice-card researcher-choice">
          <div className="join-choice-icon"><Microscope size={28}/></div>
          <div className="eyebrow dark">RESEARCHER ACCOUNT</div>
          <h2>Build your research identity.</h2>
          <p>For researchers who want a public professional profile and access to AGP's research publishing workflow.</p>
          <ul>
            <li>Public researcher profile</li>
            <li>Submit research for editorial review</li>
            <li>Publication analytics and amplification</li>
            <li>Receive collaboration and opportunity inquiries</li>
          </ul>
          <Link className="button lime dark-text large full" to="/register/researcher">Create Researcher Account <ArrowRight size={17}/></Link>
        </article>
      </div>

      <div className="join-signin">Already have an AGP account? <Link to="/login">Sign in</Link></div>
    </div>
  </div>
}