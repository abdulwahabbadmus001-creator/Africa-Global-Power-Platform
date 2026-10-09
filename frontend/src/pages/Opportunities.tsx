import {
  BriefcaseBusiness,
  ExternalLink,
  Search,
} from 'lucide-react'
import {
  useEffect,
  useMemo,
  useState,
} from 'react'
import { api } from '../lib/api'


type Opportunity = {
  id: string
  title: string
  organization: string
  category: string
  country?: string | null
  location_mode: string
  deadline?: string | null
  summary: string
  url: string
  tags: string[]
}


const categories = [
  'All',
  'Fellowship',
  'Grant',
  'Collaboration',
  'Call for Papers',
  'Internship',
  'Scholarship',
  'Conference',
  'Research',
]


export default function Opportunities() {
  const [items, setItems] =
    useState<Opportunity[]>([])

  const [q, setQ] =
    useState('')

  const [category, setCategory] =
    useState('All')

  useEffect(() => {
    api<Opportunity[]>(
      '/opportunities',
    )
      .then(setItems)
      .catch(() => {})
  }, [])

  const filtered =
    useMemo(
      () =>
        items.filter((item) => {
          const matchesCategory =
            category === 'All'
            || item.category.toLowerCase()
              === category.toLowerCase()

          const haystack = [
            item.title,
            item.organization,
            item.category,
            item.country || '',
            item.summary,
          ]
            .join(' ')
            .toLowerCase()

          return (
            matchesCategory
            && haystack.includes(
              q.toLowerCase(),
            )
          )
        }),
      [
        items,
        q,
        category,
      ],
    )

  return (
    <div className="page section production-page">
      <div className="section-head">
        <div>
          <div className="eyebrow dark">
            OPPORTUNITIES RADAR
          </div>

          <h1>
            Open doors for African research.
          </h1>

          <p className="lead">
            Fellowships, grants, collaborations,
            calls for papers, internships,
            scholarships, conferences and
            research opportunities curated for
            the AGP community.
          </p>
        </div>

        <BriefcaseBusiness size={38} />
      </div>

      <div className="opportunity-filters">
        {categories.map((item) => (
          <button
            key={item}
            className={
              category === item
                ? 'active'
                : ''
            }
            onClick={() =>
              setCategory(item)}
          >
            {item}
          </button>
        ))}
      </div>

      <div className="tool-search">
        <Search size={17} />

        <input
          value={q}
          onChange={(event) =>
            setQ(event.target.value)}
          placeholder="Search opportunities"
        />
      </div>

      <div className="content-grid">
        {filtered.map((item) => {
          const closed =
            item.tags.includes(
              'AGP-CLOSED',
            )

          return (
            <article
              className="card content-card"
              key={item.id}
            >
              <div className="content-meta">
                <span>{item.category}</span>
                <span>
                  {item.country
                    || item.location_mode}
                </span>
              </div>

              {closed && (
                <div className="closed-badge">
                  Closed
                </div>
              )}

              <h2>{item.title}</h2>

              <strong>
                {item.organization}
              </strong>

              <p>{item.summary}</p>

              <small>
                {item.deadline
                  ? (
                      `Deadline: ${
                        new Date(
                          item.deadline,
                        ).toLocaleDateString()
                      }`
                    )
                  : 'Deadline not specified'}
              </small>

              <div className="card-actions">
                {closed
                  ? (
                      <span className="button ghost">
                        Applications closed
                      </span>
                    )
                  : (
                      <a
                        className="button dark"
                        href={item.url}
                        target="_blank"
                        rel="noreferrer"
                      >
                        View opportunity
                        <ExternalLink size={14} />
                      </a>
                    )}
              </div>
            </article>
          )
        })}
      </div>

      {!filtered.length && (
        <div className="card panel">
          No published opportunities match
          this search or category yet.
        </div>
      )}
    </div>
  )
}
