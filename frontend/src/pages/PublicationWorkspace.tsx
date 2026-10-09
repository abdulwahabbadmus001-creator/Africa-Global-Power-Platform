import { CheckCircle2, Download, Edit3, FileLock2, Send, ShieldCheck, Trash2, Upload } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import StatusBadge from '../components/StatusBadge'
import { API_URL, api } from '../lib/api'
import type { Analytics, Publication, TrustAccessEvent, TrustOverview } from '../types'

export default function PublicationWorkspace() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [pubs, setPubs] = useState<Publication[]>([])
  const [stats, setStats] = useState<Analytics | null>(null)
  const [trust, setTrust] = useState<TrustOverview | null>(null)
  const [history, setHistory] = useState<TrustAccessEvent[]>([])
  const [busy, setBusy] = useState(false)
  const [notice, setNotice] = useState('')
  const [replacement, setReplacement] = useState<File | null>(null)

  async function load() {
    const publications = await api<Publication[]>('/publications/mine')
    setPubs(publications)
    if (!id) return
    api<Analytics>(`/analytics/publication/${id}`).then(setStats).catch(() => {})
    api<TrustOverview>(`/trust/publications/${id}/overview`).then(setTrust).catch(() => {})
    api<TrustAccessEvent[]>(`/trust/publications/${id}/access-history`).then(setHistory).catch(() => {})
  }

  useEffect(() => { load().catch(() => {}) }, [id])

  const publication = pubs.find((item) => item.id === id)
  if (!publication) return <div className="page section">Loading publication workspaceâ€¦</div>

  const publicationId = publication.id

  const editable = ['draft', 'revision_requested'].includes(publication.status)
  const abstractReady = publication.abstract.trim().length >= 40

  async function submit() {
    setBusy(true)
    setNotice('')
    try {
      await api(`/publications/${publicationId}/submit`, { method: 'POST' })
      await load()
      setNotice('Submission sealed successfully in the AGP Research Trust Vault and sent to Editorial.')
    } catch (error) {
      setNotice(error instanceof Error ? error.message : 'Unable to submit research.')
    } finally {
      setBusy(false)
    }
  }

  async function deleteDraft() {
    if (!publication || publication.status !== 'draft') return
    if (!window.confirm('Delete this unsubmitted private draft? This cannot be undone.')) return
    setBusy(true); setNotice('')
    try { await api(`/publications/${publicationId}`, { method: 'DELETE' }); navigate('/dashboard', { replace: true }) }
    catch (error) { setNotice(error instanceof Error ? error.message : 'Unable to delete this private draft.') }
    finally { setBusy(false) }
  }

  async function uploadReplacement() {
    if (!replacement) return
    setBusy(true)
    setNotice('')
    try {
      const data = new FormData()
      data.append('file', replacement)
      await api(`/trust/publications/${publicationId}/manuscript`, { method: 'POST', body: data })
      setReplacement(null)
      await load()
      setNotice('New manuscript version uploaded. Previous versions remain recorded in the Trust Vault.')
    } catch (error) {
      setNotice(error instanceof Error ? error.message : 'Unable to upload manuscript.')
    } finally {
      setBusy(false)
    }
  }

  async function downloadFile(fileId: string) {
    const response = await fetch(`${API_URL}/trust/manuscripts/${fileId}/download`, { credentials: 'include' })
    if (!response.ok) {
      const data = await response.json().catch(() => ({}))
      window.alert(typeof data.detail === 'string' ? data.detail : 'Unable to download manuscript.')
      return
    }
    const blob = await response.blob()
    const disposition = response.headers.get('content-disposition') || ''
    const match = disposition.match(/filename="?([^";]+)"?/i)
    const filename = match?.[1] || 'AGP-manuscript'
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = filename
    anchor.click()
    URL.revokeObjectURL(url)
    await load()
  }

  const certificate = trust?.latest_snapshot

  return (
    <div className="page section narrow-form">
      <div className="workspace-title">
        <div><div className="eyebrow dark">PUBLICATION WORKSPACE</div><h1>{publication.title}</h1></div>
        <StatusBadge status={publication.status} />
      </div>

      {notice && <div className="alert" style={{ marginBottom: 18 }}>{notice}</div>}

      <div className="metrics-grid workspace-metrics">
        <div className="metric card"><span>Views</span><strong>{stats?.views || 0}</strong></div>
        <div className="metric card"><span>Unique readers</span><strong>{stats?.unique_readers || 0}</strong></div>
        <div className="metric card"><span>Downloads</span><strong>{stats?.downloads || 0}</strong></div>
        <div className="metric card"><span>Current version</span><strong>{publication.current_version}</strong></div>
      </div>

      <div className="card review-summary">
        <h2>Submission readiness</h2>
        <div className="check"><CheckCircle2 /> Research record created</div>
        <div className="check"><CheckCircle2 /> Submission method: {publication.submission_method}</div>
        <div className="check"><CheckCircle2 /> Publication version {publication.current_version} saved</div>
        <div className={abstractReady ? 'check' : 'alert'}><CheckCircle2 /> {abstractReady ? 'Public abstract ready' : 'Add a public abstract of at least 40 characters before Editorial submission'}</div>
        {(publication.submission_method === 'upload' || publication.submission_method === 'both') && (
          <div className="check"><CheckCircle2 /> {trust?.files.length || 0} manuscript version(s) secured</div>
        )}
        <p>Submitting creates an immutable Trust Vault snapshot with a timestamp and SHA-256 fingerprint.</p>
        <div className="form-actions">
          {editable && <Link className="button ghost large" to={`/dashboard/publications/${publicationId}/edit`}><Edit3 size={18} /> Edit draft</Link>}
          {editable && <button className="button lime dark-text large" onClick={submit} disabled={busy || !abstractReady}><Send size={18} /> {busy ? 'Submittingâ€¦' : 'Seal & submit to Editorial'}</button>}
          {publication.status === 'draft' && <button className="button ghost large" style={{borderColor:'#a43737',color:'#a43737'}} type="button" onClick={deleteDraft} disabled={busy}><Trash2 size={18}/> Delete unsubmitted draft</button>}
        </div>
      </div>

      {(publication.submission_method === 'upload' || publication.submission_method === 'both') && (
        <section className="card panel" style={{ marginTop: 18 }}>
          <div className="panel-head"><h2>Private manuscript vault</h2><FileLock2 /></div>
          {(trust?.files || []).map((file) => (
            <div className="dashboard-row" key={file.id}>
              <div>
                <strong>v{file.version_number} â€” {file.original_filename}</strong>
                <small>{(file.size_bytes / 1024 / 1024).toFixed(2)} MB â€¢ SHA-256 {file.sha256.slice(0, 16)}â€¦ {file.is_original_submission ? 'â€¢ Original sealed submission' : ''}</small>
              </div>
              <button className="button ghost" type="button" onClick={() => downloadFile(file.id)}><Download size={15} /> Download</button>
            </div>
          ))}

          {editable && (
            <div style={{ marginTop: 18 }}>
              <label>
                Upload a new manuscript version
                <input type="file" accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document" onChange={(event) => setReplacement(event.target.files?.[0] || null)} />
              </label>
              <button className="button dark" type="button" disabled={!replacement || busy} onClick={uploadReplacement}><Upload size={16} /> Upload new version</button>
            </div>
          )}
        </section>
      )}

      {certificate && (
        <section className="card panel" style={{ marginTop: 18 }}>
          <div className="panel-head"><h2>Research Trust Vault certificate</h2><ShieldCheck /></div>
          <p><strong>Submission ID:</strong> {certificate.submission_id}</p>
          <p><strong>Sealed:</strong> {new Date(certificate.submitted_at).toLocaleString()}</p>
          <p style={{ wordBreak: 'break-all' }}><strong>Fingerprint:</strong> {certificate.fingerprint_sha256}</p>
          <a className="button ghost" href={`${API_URL}/trust/certificates/${certificate.id}/print`} target="_blank" rel="noreferrer">Open printable certificate</a>
        </section>
      )}

      {history.length > 0 && (
        <section className="card panel" style={{ marginTop: 18 }}>
          <h2>Submission security & access history</h2>
          <p>This author-visible ledger records uploads, sealing, editorial declarations, manuscript access and editorial status changes.</p>
          {history.slice(0, 30).map((event) => (
            <div className="history-row" key={event.id}>
              <strong>{event.actor_name}</strong>
              <span>{event.action.replaceAll('_', ' ')}</span>
              <small>{event.actor_role || 'system'} â€¢ {new Date(event.created_at).toLocaleString()} â€¢ {event.event_hash.slice(0, 12)}â€¦</small>
            </div>
          ))}
        </section>
      )}
    </div>
  )
}
