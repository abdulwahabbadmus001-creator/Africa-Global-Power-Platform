import { FileText, Upload, PenLine } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../lib/api'
import type { ManuscriptFile, Publication, SubmissionMethod } from '../types'

export default function NewPublication() {
  const nav = useNavigate()
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const [mode, setMode] = useState<SubmissionMethod>('form')
  const [file, setFile] = useState<File | null>(null)
  const [form, setForm] = useState({
    title: '',
    abstract: '',
    body: '',
    publication_type: 'analysis',
    topic: 'AI & Technology',
    region: 'Africa',
    country: '',
    keywords: '',
    methodology: '',
    limitations: '',
    policy_implications: '',
    references: '',
  })

  function change(event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) {
    setForm({ ...form, [event.target.name]: event.target.value })
  }

  function chooseMode(nextMode: SubmissionMethod) {
    setMode(nextMode)
    setError('')
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError('')

    try {
      if ((mode === 'upload' || mode === 'both') && !file) {
        throw new Error('Choose a PDF or DOCX manuscript before saving this draft.')
      }

      const title = form.title.trim() || file?.name.replace(/\.(pdf|docx)$/i, '') || ''
      if (title.length < 3) throw new Error('Enter a research title.')

      const refs = form.references
        .split('\n')
        .map((item) => item.trim())
        .filter(Boolean)
        .map((url) => ({ title: url, url }))

      const payload = {
        ...form,
        title,
        abstract: mode === 'upload' ? form.abstract.trim() : form.abstract,
        body: mode === 'upload' ? '' : form.body,
        submission_method: mode,
        keywords: form.keywords.split(',').map((item) => item.trim()).filter(Boolean),
        references: refs,
      }

      const publication = await api<Publication>('/publications', {
        method: 'POST',
        body: JSON.stringify(payload),
      })

      if (file) {
        const data = new FormData()
        data.append('file', file)
        await api<ManuscriptFile>(`/trust/publications/${publication.id}/manuscript`, {
          method: 'POST',
          body: data,
        })
      }

      nav(`/dashboard/publications/${publication.id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to create publication draft.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page section narrow-form">
      <div className="page-title">
        <div className="eyebrow dark">NEW RESEARCH</div>
        <h1>Start a publication.</h1>
        <p>Your work stays private until you submit it to the AGP editorial workflow.</p>
      </div>

      <div className="card panel" style={{ marginBottom: 18 }}>
        <strong>Choose how you want to submit your research</strong>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, marginTop: 14 }}>
          <button type="button" className={`button ${mode === 'form' ? 'dark' : 'ghost'}`} onClick={() => chooseMode('form')}>
            <PenLine size={16} /> Fill AGP form
          </button>
          <button type="button" className={`button ${mode === 'upload' ? 'dark' : 'ghost'}`} onClick={() => chooseMode('upload')}>
            <Upload size={16} /> Upload manuscript
          </button>
          <button type="button" className={`button ${mode === 'both' ? 'dark' : 'ghost'}`} onClick={() => chooseMode('both')}>
            <FileText size={16} /> Form + manuscript
          </button>
        </div>
      </div>

      {error && <div className="alert error">{error}</div>}

      <form className="publication-form card" onSubmit={submit}>
        <label>
          Title
          <input required={mode !== 'upload'} minLength={3} name="title" value={form.title} onChange={change} placeholder={mode === 'upload' ? 'Optional if the filename already contains the title' : ''} />
        </label>

        <div className="form-grid">
          <label>
            Publication type
            <select name="publication_type" value={form.publication_type} onChange={change}>
              <option>analysis</option><option>policy brief</option><option>working paper</option><option>report</option><option>commentary</option>
            </select>
          </label>
          <label>
            Topic
            <select name="topic" value={form.topic} onChange={change}>
              <option>AI & Technology</option><option>Geopolitics</option><option>Political Economy</option><option>Trade & Investment</option><option>Governance</option><option>Security</option><option>Climate & Energy</option>
            </select>
          </label>
          <label>Region<input name="region" value={form.region} onChange={change} /></label>
          <label>Country<input name="country" value={form.country} onChange={change} /></label>
        </div>

        <label>Keywords <small>Comma separated</small><input name="keywords" value={form.keywords} onChange={change} /></label>

        {(mode === 'form' || mode === 'both') && (
          <>
            <label>Abstract<textarea required minLength={40} rows={5} name="abstract" value={form.abstract} onChange={change} /></label>
            <label>Research body<textarea required minLength={100} rows={18} name="body" value={form.body} onChange={change} /></label>
            <label>Methodology<textarea rows={4} name="methodology" value={form.methodology} onChange={change} /></label>
            <label>Limitations<textarea rows={4} name="limitations" value={form.limitations} onChange={change} /></label>
            <label>Policy implications<textarea rows={4} name="policy_implications" value={form.policy_implications} onChange={change} /></label>
            <label>References <small>One URL per line</small><textarea rows={5} name="references" value={form.references} onChange={change} /></label>
          </>
        )}

        {mode === 'upload' && (
          <label>
            Optional public abstract
            <textarea rows={5} name="abstract" value={form.abstract} onChange={change} placeholder="You can add the public abstract now or complete it during revision before publication." />
          </label>
        )}

        {(mode === 'upload' || mode === 'both') && (
          <label>
            Manuscript file <small>PDF or DOCX, maximum 25 MB</small>
            <input type="file" accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" required onChange={(event) => setFile(event.target.files?.[0] || null)} />
          </label>
        )}

        <div className="form-actions">
          <button className="button dark large" disabled={busy}>
            {busy ? 'Saving…' : 'Save private draft'}
          </button>
        </div>
      </form>
    </div>
  )
}
