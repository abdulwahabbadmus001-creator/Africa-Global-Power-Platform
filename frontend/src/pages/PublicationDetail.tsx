import {
  Bookmark,
  Download,
  ExternalLink,
  MessageSquare,
} from 'lucide-react'

import {
  useEffect,
  useRef,
  useState,
} from 'react'

import {
  Link,
  useParams,
} from 'react-router-dom'

import SharePublication
  from '../components/SharePublication'

import { api } from '../lib/api'

import type {
  Publication,
} from '../types'


function sessionId() {
  let id =
    localStorage.getItem(
      'agp-session'
    )

  if (!id) {
    id = crypto.randomUUID()

    localStorage.setItem(
      'agp-session',
      id,
    )
  }

  return id
}


export default function PublicationDetail() {
  const { slug } = useParams()

  const [publication, setPublication] =
    useState<Publication | null>(
      null,
    )

  const analyticsSent =
    useRef(false)

  const amplificationSent =
    useRef(false)


  useEffect(() => {
    if (!slug) {
      return
    }

    api<Publication>(
      `/publications/${slug}`,
    )
      .then((pub) => {
        setPublication(pub)

        if (!analyticsSent.current) {
          analyticsSent.current = true

          let referrerHost:
            | string
            | null = null

          try {
            referrerHost =
              document.referrer
                ? new URL(
                    document.referrer
                  ).hostname
                : null
          } catch {
            referrerHost = null
          }

          api(
            '/analytics/event',
            {
              method: 'POST',

              body: JSON.stringify({
                publication_id:
                  pub.id,

                event_type:
                  'view',

                session_id:
                  sessionId(),

                referrer_host:
                  referrerHost,
              }),
            },
          ).catch(() => {})
        }


        if (
          !amplificationSent.current
        ) {
          const params =
            new URLSearchParams(
              window.location.search,
            )

          const shareEventId =
            params.get(
              'agp_share'
            )

          if (shareEventId) {
            amplificationSent.current =
              true

            let referrerHost:
              | string
              | null = null

            try {
              referrerHost =
                document.referrer
                  ? new URL(
                      document.referrer
                    ).hostname
                  : null
            } catch {
              referrerHost = null
            }

            api(
              `/amplification/share-events/${shareEventId}/click`,
              {
                method: 'POST',

                body: JSON.stringify({
                  session_id:
                    sessionId(),

                  referrer_host:
                    referrerHost,
                }),
              },
            ).catch(() => {})
          }
        }
      })
  }, [slug])


  if (!publication) {
    return (
      <div className="page section">
        Loading publication…
      </div>
    )
  }


  const p = publication


  return (
    <div className="article-shell">

      <article className="article">

        <div className="article-kicker">

          <span>
            {p.topic}
          </span>

          <span>
            {p.publication_type}
          </span>

          <span>
            Version {p.current_version}
          </span>

        </div>


        <h1>
          {p.title}
        </h1>


        <p className="article-deck">
          {p.abstract}
        </p>


        <div className="article-author">

          By{' '}

          {p.author
            ? (
                <Link
                  to={
                    `/researchers/${p.author.id}`
                  }
                >
                  {p.author.first_name}{' '}
                  {p.author.last_name}
                </Link>
              )
            : 'AGP Research'}

          <span>•</span>

          {p.published_at
            ? new Date(
                p.published_at
              ).toLocaleDateString()
            : ''}

        </div>


        <div className="article-actions">

          <button type="button">
            <Bookmark size={17} />
            Save
          </button>

          <button type="button">
            <Download size={17} />
            PDF
          </button>

          {p.author && (
            <Link
              to={
                `/messages?to=${p.author.id}`
              }
            >
              <MessageSquare
                size={17}
              />

              Contact researcher
            </Link>
          )}

        </div>


        <SharePublication
          publicationId={p.id}
          context="publication_page"
        />


        <div className="article-body">

          {p.body
            .split('\n')
            .filter(Boolean)
            .map(
              (paragraph, index) => (
                <p key={index}>
                  {paragraph}
                </p>
              ),
            )}

        </div>


        {p.methodology && (
          <section className="article-box">

            <h3>
              Methodology
            </h3>

            <p>
              {p.methodology}
            </p>

          </section>
        )}


        {p.limitations && (
          <section className="article-box">

            <h3>
              Limitations
            </h3>

            <p>
              {p.limitations}
            </p>

          </section>
        )}


        {p.policy_implications && (
          <section className="article-box accent">

            <h3>
              Policy implications
            </h3>

            <p>
              {p.policy_implications}
            </p>

          </section>
        )}


        {p.references?.length > 0 && (
          <section className="references">

            <h2>
              Sources & references
            </h2>

            {p.references.map(
              (reference, index) => (
                <div
                  className="reference"
                  key={index}
                >

                  <span>
                    {index + 1}
                  </span>

                  <div>

                    <strong>
                      {reference.title
                        || reference.doi
                        || 'Reference'}
                    </strong>

                    {reference.url && (
                      <a
                        href={
                          reference.url
                        }
                        target="_blank"
                        rel="noreferrer"
                      >
                        Open source

                        <ExternalLink
                          size={14}
                        />
                      </a>
                    )}

                  </div>

                </div>
              ),
            )}

          </section>
        )}

      </article>


      <aside className="article-aside">

        <div className="aside-card">

          <span>
            RESEARCH CONTEXT
          </span>

          <dl>

            <dt>
              Region
            </dt>

            <dd>
              {p.region || '—'}
            </dd>

            <dt>
              Country
            </dt>

            <dd>
              {p.country || '—'}
            </dd>

            <dt>
              Topic
            </dt>

            <dd>
              {p.topic}
            </dd>

            <dt>
              Keywords
            </dt>

            <dd>
              {p.keywords.join(', ')}
            </dd>

          </dl>

        </div>


        <div className="aside-card integrity">

          <ShieldText />

          <strong>
            AGP Research Integrity
          </strong>

          <p>
            This publication displays
            its sources, version and
            review context so readers
            can evaluate the evidence
            behind the analysis.
          </p>

        </div>

      </aside>

    </div>
  )
}


function ShieldText() {
  return (
    <div className="integrity-mark">
      ✓
    </div>
  )
}