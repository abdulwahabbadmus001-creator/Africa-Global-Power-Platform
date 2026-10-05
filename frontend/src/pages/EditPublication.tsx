import {
  useEffect,
  useState,
  type ChangeEvent,
  type FormEvent,
} from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { api } from '../lib/api'
import type { Publication } from '../types'

export default function EditPublication() {
  const { id } = useParams()
  const navigate = useNavigate()

  const [publication, setPublication] = useState<Publication | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    let cancelled = false

    async function loadPublication() {
      setLoading(true)
      setError('')

      try {
        const items = await api<Publication[]>('/publications/mine')

        if (cancelled) {
          return
        }

        const foundPublication =
          items.find((item) => item.id === id) ?? null

        setPublication(foundPublication)

        if (!foundPublication) {
          setError('Publication could not be found.')
        }
      } catch (err) {
        if (cancelled) {
          return
        }

        const message =
          err instanceof Error
            ? err.message
            : 'Unable to load this publication.'

        setError(message)
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadPublication()

    return () => {
      cancelled = true
    }
  }, [id])

  function change(
    event: ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >,
  ) {
    const { name, value } = event.target

    setPublication((currentPublication) => {
      if (!currentPublication) {
        return currentPublication
      }

      return {
        ...currentPublication,
        [name]: value,
      }
    })
  }

  async function save(event: FormEvent) {
    event.preventDefault()

    if (!publication) {
      setError('Publication could not be loaded.')
      return
    }

    const editable = ['draft', 'revision_requested'].includes(
      publication.status,
    )

    if (!editable) {
      setError(
        'This publication cannot be edited while it is in editorial review.',
      )
      return
    }

    setBusy(true)
    setError('')

    try {
      await api(`/publications/${publication.id}`, {
        method: 'PATCH',
        body: JSON.stringify({
          title: publication.title,
          abstract: publication.abstract,
          body: publication.body,
          publication_type: publication.publication_type,
          topic: publication.topic,
          region: publication.region,
          country: publication.country,
          methodology: publication.methodology,
          limitations: publication.limitations,
          policy_implications: publication.policy_implications,
          keywords: publication.keywords,
          references: publication.references,
          change_note: 'Researcher draft update',
        }),
      })

      navigate(`/dashboard/publications/${publication.id}`)
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : 'Unable to save the publication.'

      setError(message)
    } finally {
      setBusy(false)
    }
  }

  if (loading) {
    return (
      <div className="page section">
        Loading draft…
      </div>
    )
  }

  if (!publication) {
    return (
      <div className="page section narrow-form">
        <div className="alert error">
          {error || 'Publication could not be found.'}
        </div>

        <button
          className="button dark"
          type="button"
          onClick={() => navigate('/dashboard')}
        >
          Return to dashboard
        </button>
      </div>
    )
  }

  const editable = ['draft', 'revision_requested'].includes(
    publication.status,
  )

  return (
    <div className="page section narrow-form">
      <div className="page-title">
        <div className="eyebrow dark">
          EDIT RESEARCH
        </div>

        <h1>{publication.title}</h1>

        <p>
          Version {publication.current_version}.{' '}
          {editable
            ? 'Changes create a new recorded version.'
            : 'This publication is locked while it is in editorial review.'}
        </p>
      </div>

      {error && (
        <div className="alert error">
          {error}
        </div>
      )}

      <form
        className="publication-form card"
        onSubmit={save}
      >
        <label>
          Title
          <input
            disabled={!editable}
            name="title"
            value={publication.title}
            onChange={change}
          />
        </label>

        <label>
          Abstract
          <textarea
            disabled={!editable}
            rows={5}
            name="abstract"
            value={publication.abstract}
            onChange={change}
          />
        </label>

        <div className="form-grid">
          <label>
            Publication type
            <input
              disabled={!editable}
              name="publication_type"
              value={publication.publication_type}
              onChange={change}
            />
          </label>

          <label>
            Topic
            <input
              disabled={!editable}
              name="topic"
              value={publication.topic}
              onChange={change}
            />
          </label>

          <label>
            Region
            <input
              disabled={!editable}
              name="region"
              value={publication.region ?? ''}
              onChange={change}
            />
          </label>

          <label>
            Country
            <input
              disabled={!editable}
              name="country"
              value={publication.country ?? ''}
              onChange={change}
            />
          </label>
        </div>

        <label>
          Research body
          <textarea
            disabled={!editable}
            rows={18}
            name="body"
            value={publication.body}
            onChange={change}
          />
        </label>

        <label>
          Methodology
          <textarea
            disabled={!editable}
            rows={4}
            name="methodology"
            value={publication.methodology ?? ''}
            onChange={change}
          />
        </label>

        <label>
          Limitations
          <textarea
            disabled={!editable}
            rows={4}
            name="limitations"
            value={publication.limitations ?? ''}
            onChange={change}
          />
        </label>

        <label>
          Policy implications
          <textarea
            disabled={!editable}
            rows={4}
            name="policy_implications"
            value={publication.policy_implications ?? ''}
            onChange={change}
          />
        </label>

        {editable && (
          <button
            className="button dark large"
            type="submit"
            disabled={busy}
          >
            {busy
              ? 'Saving…'
              : 'Save new version'}
          </button>
        )}
      </form>
    </div>
  )
}