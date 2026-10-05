import { CheckCircle2, Clock3, Download, FileSearch, LockKeyhole, ShieldCheck } from 'lucide-react'
import { useEffect, useState } from 'react'
import MetricCard from '../components/MetricCard'
import StatusBadge from '../components/StatusBadge'
import { API_URL, api } from '../lib/api'
import { useAuth } from '../lib/auth'
import type { EditorialQueueItem, ManuscriptFile, Publication, PublicationStatus, TrustOverview } from '../types'

const next: Record<string, PublicationStatus[]> = {
  submitted: ['desk_review', 'rejected'],
  desk_review: ['editorial_review', 'revision_requested', 'rejected'],
  editorial_review: ['source_check', 'revision_requested', 'rejected'],
  source_check: ['approved', 'revision_requested', 'rejected'],
  approved: ['scheduled', 'published'],
  scheduled: ['published', 'approved'],
  revision_requested: ['desk_review', 'editorial_review'],
}

type History = { id:string; action:string; from_status?:string; to_status?:string; note?:string; created_at:string; actor:string }
type ReviewPackage = { publication: Publication; files: ManuscriptFile[] }

export default function Editorial() {
  const { user } = useAuth()
  const [queue, setQueue] = useState<EditorialQueueItem[]>([])
  const [summary, setSummary] = useState<any>({ counts: {}, total_active: 0 })
  const [selected, setSelected] = useState<EditorialQueueItem | null>(null)
  const [trust, setTrust] = useState<TrustOverview | null>(null)
  const [review, setReview] = useState<ReviewPackage | null>(null)
  const [note, setNote] = useState('')
  const [history, setHistory] = useState<History[]>([])
  const [scheduleAt, setScheduleAt] = useState('')
  const [notice, setNotice] = useState('')

  async function load() {
    setQueue(await api<EditorialQueueItem[]>('/editorial/queue'))
    setSummary(await api('/editorial/summary'))
  }

  async function loadSelected(item: EditorialQueueItem) {
    setSelected(item)
    setReview(null)
    setNotice('')
    setTrust(await api<TrustOverview>(`/trust/publications/${item.id}/overview`))
    api<History[]>(`/editorial/${item.id}/history`).then(setHistory).catch(() => setHistory([]))
  }

  useEffect(() => { load().catch(() => {}) }, [])

  async function claim() {
    if (!selected) return
    const claimed = await api<EditorialQueueItem>(`/editorial/${selected.id}/claim`, { method: 'POST' })
    await load()
    await loadSelected(claimed)
  }

  async function acceptConfidentiality() {
    if (!selected) return
    await api(`/trust/publications/${selected.id}/confidentiality`, { method: 'POST' })
    await loadSelected(selected)
  }

  async function declareNoConflict() {
    if (!selected) return
    await api(`/trust/publications/${selected.id}/conflict`, {
      method: 'POST',
      body: JSON.stringify({ decision: 'no_conflict', note: null }),
    })
    await loadSelected(selected)
  }

  async function recuse() {
    if (!selected) return
    await api(`/trust/publications/${selected.id}/conflict`, {
      method: 'POST',
      body: JSON.stringify({ decision: 'recuse', note: 'Editor recused from this submission.' }),
    })
    setSelected(null)
    setTrust(null)
    setReview(null)
    await load()
  }

  async function openReview() {
    if (!selected) return
    const result = await api<ReviewPackage>(`/trust/editorial/publications/${selected.id}/review-package`)
    setReview(result)
    setNotice('Confidential manuscript access opened and recorded in the author-visible Trust Vault ledger.')
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
  }

  async function move(status: PublicationStatus) {
    if (!selected) return
    const body: any = { to_status: status, note }
    if (status === 'scheduled') {
      if (!scheduleAt) {
        window.alert('Choose the publication date and time first.')
        return
      }
      body.scheduled_for = new Date(scheduleAt).toISOString()
    }
    await api(`/editorial/${selected.id}/transition`, { method: 'POST', body: JSON.stringify(body) })
    setSelected(null)
    setTrust(null)
    setReview(null)
    setNote('')
    setHistory([])
    setScheduleAt('')
    await load()
  }

  const assignedToMe = selected?.assigned_editor_id === user?.id
  const assignedElsewhere = Boolean(selected?.assigned_editor_id && !assignedToMe)
  const activePublication = review?.publication

  return (
    <div className="editorial page section">
      <div className="dashboard-head">
        <div><div className="eyebrow dark">AGP EDITORIAL</div><h1>Research review desk.</h1><p>Submission metadata is visible in the queue. Manuscript content unlocks only after assignment, confidentiality acceptance and conflict declaration.</p></div>
        <div className="editorial-seal"><ShieldCheck /> Secure Editorial access</div>
      </div>

      <div className="metrics-grid">
        <MetricCard label="Active submissions" value={summary.total_active} />
        <MetricCard label="Submitted" value={summary.counts?.submitted || 0} />
        <MetricCard label="Source check" value={summary.counts?.source_check || 0} />
        <MetricCard label="Approved" value={summary.counts?.approved || 0} />
      </div>

      <div className="editorial-grid">
        <section className="card panel">
          <div className="panel-head"><h2>Submission queue</h2><span>{queue.length} items</span></div>
          {queue.map((item) => (
            <button className={`queue-row ${selected?.id === item.id ? 'active' : ''}`} key={item.id} onClick={() => loadSelected(item)}>
              <div><strong>{item.title}</strong><small>{item.author ? `${item.author.first_name} ${item.author.last_name}` : 'Researcher'} • {item.topic} • {item.submission_method}</small></div>
              <StatusBadge status={item.status} />
            </button>
          ))}
        </section>

        <aside className="card review-panel">
          {!selected && <div className="empty-review"><FileSearch /><h3>Select a submission</h3><p>Only metadata is exposed until secure review access is established.</p></div>}

          {selected && (
            <>
              <div className="publication-meta"><span>{selected.publication_type}</span><span>v{selected.current_version}</span><span>{selected.topic}</span></div>
              <h2>{selected.title}</h2>
              <p><strong>Author:</strong> {selected.author ? `${selected.author.first_name} ${selected.author.last_name}` : 'Researcher'}</p>

              {assignedElsewhere && <div className="alert">This submission is assigned to another editor. Manuscript access is unavailable.</div>}

              {!selected.assigned_editor_id && (
                <button className="button dark large" type="button" onClick={claim}><LockKeyhole size={17} /> Claim secure review</button>
              )}

              {assignedToMe && trust?.editor_state && !trust.editor_state.can_access_manuscript && (
                <div className="card panel" style={{ marginTop: 14 }}>
                  <h3>Trust Vault access gate</h3>
                  <p>Before opening unpublished research, complete both declarations. Your actions are visible to the author.</p>
                  {!trust.editor_state.confidentiality_accepted && (
                    <button className="button dark" type="button" onClick={acceptConfidentiality}>Accept confidentiality & non-use declaration</button>
                  )}
                  {trust.editor_state.confidentiality_accepted && <div className="check"><CheckCircle2 /> Confidentiality declaration accepted</div>}
                  {trust.editor_state.conflict_decision !== 'no_conflict' && (
                    <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginTop: 12 }}>
                      <button className="button dark" type="button" onClick={declareNoConflict}>Declare no conflict</button>
                      <button className="button ghost" type="button" onClick={recuse}>Recuse myself</button>
                    </div>
                  )}
                  {trust.editor_state.conflict_decision === 'no_conflict' && <div className="check"><CheckCircle2 /> No-conflict declaration recorded</div>}
                </div>
              )}

              {assignedToMe && trust?.editor_state?.can_access_manuscript && !review && (
                <button className="button dark large" style={{ marginTop: 16 }} type="button" onClick={openReview}><FileSearch size={17} /> Open confidential manuscript</button>
              )}

              {notice && <div className="alert" style={{ marginTop: 14 }}>{notice}</div>}

              {review && activePublication && (
                <>
                  <p className="review-abstract">{activePublication.abstract || 'No public abstract supplied yet.'}</p>
                  {review.files.length > 0 && (
                    <div className="card panel" style={{ marginBottom: 16 }}>
                      <h3>Secured manuscript files</h3>
                      {review.files.map((file) => (
                        <div className="dashboard-row" key={file.id}>
                          <div><strong>v{file.version_number} — {file.original_filename}</strong><small>SHA-256 {file.sha256.slice(0, 18)}…</small></div>
                          <button className="button ghost" type="button" onClick={() => downloadFile(file.id)}><Download size={15} /> Download</button>
                        </div>
                      ))}
                    </div>
                  )}

                  {activePublication.body && (
                    <div className="manuscript-preview">
                      <h3>AGP form manuscript</h3>
                      {activePublication.body.split('\n').filter(Boolean).slice(0, 12).map((text, index) => <p key={index}>{text}</p>)}
                      {activePublication.methodology && <><h3>Methodology</h3><p>{activePublication.methodology}</p></>}
                      {activePublication.limitations && <><h3>Limitations</h3><p>{activePublication.limitations}</p></>}
                      {activePublication.policy_implications && <><h3>Policy implications</h3><p>{activePublication.policy_implications}</p></>}
                      <h3>References</h3><p>{activePublication.references.length} reference record(s) attached.</p>
                    </div>
                  )}

                  <div className="review-checks">
                    <div><FileSearch /><span><b>Research quality</b><small>Argument, methodology, scope, limitations</small></span></div>
                    <div><ShieldCheck /><span><b>Sources & integrity</b><small>Citations, provenance, disclosure, traceability</small></span></div>
                    <div><Clock3 /><span><b>Trust Vault</b><small>Access, decisions and file fingerprints are logged</small></span></div>
                  </div>

                  <label>Editorial note<textarea rows={5} value={note} onChange={(event) => setNote(event.target.value)} placeholder="Reason for transition, revision instructions, source issues…" /></label>
                  {selected.status === 'approved' && <label>Schedule publication <small>Required only when choosing scheduled.</small><input type="datetime-local" value={scheduleAt} onChange={(event) => setScheduleAt(event.target.value)} /></label>}
                  <div className="transition-actions">
                    {(next[selected.status] || []).map((status) => <button className={`button ${status === 'rejected' || status === 'revision_requested' ? 'ghost' : 'dark'}`} key={status} onClick={() => move(status)}>{status === 'approved' && <CheckCircle2 size={16} />} {status.replaceAll('_', ' ')}</button>)}
                  </div>
                </>
              )}

              {history.length > 0 && (
                <div className="history">
                  <h3>Editorial activity</h3>
                  {history.map((item) => <div className="history-row" key={item.id}><strong>{item.actor}</strong><span>{item.from_status || '—'} → {item.to_status || item.action}</span><small>{item.note || 'No note'} • {new Date(item.created_at).toLocaleString()}</small></div>)}
                </div>
              )}
            </>
          )}
        </aside>
      </div>
    </div>
  )
}
