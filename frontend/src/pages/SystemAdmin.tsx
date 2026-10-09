import {
  BarChart3,
  Database,
  FileText,
  Pencil,
  RefreshCw,
  ShieldCheck,
  Trash2,
  Users,
} from 'lucide-react'
import {
  useEffect,
  useState,
} from 'react'
import { api } from '../lib/api'
import type {
  Role,
  User,
} from '../types'


const roles: Role[] = [
  'reader',
  'researcher',
  'contributor',
  'reviewer',
  'editor',
  'senior_editor',
  'managing_editor',
  'super_admin',
]

const opportunityCategories = [
  'Fellowship',
  'Grant',
  'Collaboration',
  'Call for Papers',
  'Internship',
  'Scholarship',
  'Conference',
  'Research',
]

type Tab =
  | 'overview'
  | 'users'
  | 'opportunities'
  | 'policies'
  | 'datasets'

type Summary = {
  users: number
  researchers: number
  publications: number
  opportunities: number
  policies: number
  datasets: number
  research_rooms: number
}

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
  is_published: boolean
}

type Policy = {
  id: string
  title: string
  country: string
  institution: string
  policy_area: string
  status: string
  summary: string
  agp_analysis: string
  source_url: string
  published_date?: string | null
  effective_date?: string | null
  tags: string[]
  is_published: boolean
}

type Dataset = {
  id: string
  title: string
  summary: string
  description: string
  category: string
  region?: string | null
  country?: string | null
  source_name: string
  source_url: string
  download_url?: string | null
  license_name?: string | null
  tags: string[]
  coverage_start?: string | null
  coverage_end?: string | null
  is_published: boolean
}


function tagsToText(tags: string[]) {
  return tags
    .filter((tag) =>
      tag !== 'AGP-CLOSED')
    .join(', ')
}


function textToTags(value: string) {
  return [
    ...new Set(
      value
        .split(',')
        .map((item) =>
          item.trim())
        .filter(Boolean),
    ),
  ]
}


export default function SystemAdmin() {
  const [tab, setTab] =
    useState<Tab>('overview')

  const [summary, setSummary] =
    useState<Summary | null>(null)

  const [users, setUsers] =
    useState<User[]>([])

  const [opportunities, setOpportunities] =
    useState<Opportunity[]>([])

  const [policies, setPolicies] =
    useState<Policy[]>([])

  const [datasets, setDatasets] =
    useState<Dataset[]>([])

  const [notice, setNotice] =
    useState('')

  const [editOpportunity, setEditOpportunity] =
    useState<Opportunity | null>(null)

  const [editPolicy, setEditPolicy] =
    useState<Policy | null>(null)

  const [editDataset, setEditDataset] =
    useState<Dataset | null>(null)

  async function loadSummary() {
    setSummary(
      await api<Summary>(
        '/admin/summary',
      ),
    )
  }

  async function loadUsers() {
    setUsers(
      await api<User[]>(
        '/admin/users',
      ),
    )
  }

  async function loadOpportunities() {
    setOpportunities(
      await api<Opportunity[]>(
        '/admin/content/opportunities',
      ),
    )
  }

  async function loadPolicies() {
    setPolicies(
      await api<Policy[]>(
        '/admin/content/policies',
      ),
    )
  }

  async function loadDatasets() {
    setDatasets(
      await api<Dataset[]>(
        '/admin/content/datasets',
      ),
    )
  }

  useEffect(() => {
    loadSummary().catch(() => {})
  }, [])

  useEffect(() => {
    if (tab === 'users') {
      loadUsers().catch(() => {})
    }

    if (tab === 'opportunities') {
      loadOpportunities().catch(() => {})
    }

    if (tab === 'policies') {
      loadPolicies().catch(() => {})
    }

    if (tab === 'datasets') {
      loadDatasets().catch(() => {})
    }
  }, [tab])

  async function changeUser(
    user: User,
    role: Role,
    isActive = user.is_active,
  ) {
    await api(
      `/admin/users/${user.id}`,
      {
        method: 'PATCH',
        body: JSON.stringify({
          role,
          is_active: isActive,
        }),
      },
    )

    await loadUsers()
    await loadSummary()
  }

  async function patchOpportunity(
    item: Opportunity,
    payload: Record<string, unknown>,
  ) {
    await api(
      `/admin/content/opportunities/${item.id}`,
      {
        method: 'PATCH',
        body: JSON.stringify(payload),
      },
    )

    setNotice('Opportunity updated.')
    setEditOpportunity(null)
    await loadOpportunities()
    await loadSummary()
  }

  async function toggleClosed(
    item: Opportunity,
  ) {
    const closed =
      item.tags.includes('AGP-CLOSED')

    await api(
      `/admin/content/opportunities/${item.id}/${
        closed
          ? 'reopen'
          : 'close'
      }`,
      {
        method: 'POST',
      },
    )

    setNotice(
      closed
        ? 'Opportunity reopened.'
        : 'Opportunity marked closed.',
    )

    await loadOpportunities()
  }

  async function deleteOpportunity(
    item: Opportunity,
  ) {
    if (
      !confirm(
        `Delete "${item.title}" permanently?`,
      )
    ) return

    await api(
      `/admin/content/opportunities/${item.id}`,
      {
        method: 'DELETE',
      },
    )

    setNotice('Opportunity deleted.')
    await loadOpportunities()
    await loadSummary()
  }

  async function patchPolicy(
    item: Policy,
    payload: Record<string, unknown>,
  ) {
    await api(
      `/admin/content/policies/${item.id}`,
      {
        method: 'PATCH',
        body: JSON.stringify(payload),
      },
    )

    setNotice('Policy record updated.')
    setEditPolicy(null)
    await loadPolicies()
    await loadSummary()
  }

  async function deletePolicy(
    item: Policy,
  ) {
    if (
      !confirm(
        `Delete "${item.title}" permanently?`,
      )
    ) return

    await api(
      `/admin/content/policies/${item.id}`,
      {
        method: 'DELETE',
      },
    )

    setNotice('Policy record deleted.')
    await loadPolicies()
    await loadSummary()
  }

  async function patchDataset(
    item: Dataset,
    payload: Record<string, unknown>,
  ) {
    await api(
      `/admin/content/datasets/${item.id}`,
      {
        method: 'PATCH',
        body: JSON.stringify(payload),
      },
    )

    setNotice('Dataset updated.')
    setEditDataset(null)
    await loadDatasets()
    await loadSummary()
  }

  async function deleteDataset(
    item: Dataset,
  ) {
    if (
      !confirm(
        `Delete "${item.title}" permanently?`,
      )
    ) return

    await api(
      `/admin/content/datasets/${item.id}`,
      {
        method: 'DELETE',
      },
    )

    setNotice('Dataset deleted.')
    await loadDatasets()
    await loadSummary()
  }

  return (
    <div className="page section">
      <div className="section-head">
        <div>
          <div className="eyebrow dark">
            SUPER ADMIN CONTROL CENTRE
          </div>

          <h1 className="settings-title">
            Platform Administration.
          </h1>

          <p className="lead">
            Govern accounts and public intelligence
            content without bypassing AGP's
            editorial and trust controls.
          </p>
        </div>

        <ShieldCheck size={38} />
      </div>

      <div className="admin-tabs">
        <button
          className={
            tab === 'overview'
              ? 'active'
              : ''
          }
          onClick={() =>
            setTab('overview')}
        >
          <BarChart3 size={16} />
          Overview
        </button>

        <button
          className={
            tab === 'users'
              ? 'active'
              : ''
          }
          onClick={() =>
            setTab('users')}
        >
          <Users size={16} />
          Users
        </button>

        <button
          className={
            tab === 'opportunities'
              ? 'active'
              : ''
          }
          onClick={() =>
            setTab('opportunities')}
        >
          Opportunities
        </button>

        <button
          className={
            tab === 'policies'
              ? 'active'
              : ''
          }
          onClick={() =>
            setTab('policies')}
        >
          <FileText size={16} />
          Policies
        </button>

        <button
          className={
            tab === 'datasets'
              ? 'active'
              : ''
          }
          onClick={() =>
            setTab('datasets')}
        >
          <Database size={16} />
          Data Lab
        </button>
      </div>

      {notice && (
        <div className="alert success">
          {notice}
        </div>
      )}

      {tab === 'overview' && (
        <div className="admin-summary-grid">
          {[
            ['Users', summary?.users ?? '—'],
            ['Researchers', summary?.researchers ?? '—'],
            ['Publications', summary?.publications ?? '—'],
            ['Opportunities', summary?.opportunities ?? '—'],
            ['Policies', summary?.policies ?? '—'],
            ['Datasets', summary?.datasets ?? '—'],
            ['Research Rooms', summary?.research_rooms ?? '—'],
          ].map(([label, value]) => (
            <div
              className="card admin-summary-card"
              key={label}
            >
              <small>{label}</small>
              <strong>{value}</strong>
            </div>
          ))}
        </div>
      )}

      {tab === 'users' && (
        <div className="card table-wrap">
          <table>
            <thead>
              <tr>
                <th>User</th>
                <th>Country</th>
                <th>Institution</th>
                <th>Role</th>
                <th>Status</th>
                <th>Control</th>
              </tr>
            </thead>

            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td>
                    <strong>
                      {user.first_name}{' '}
                      {user.last_name}
                    </strong>
                    <small>
                      {user.email}
                    </small>
                  </td>

                  <td>
                    {user.country || '—'}
                  </td>

                  <td>
                    {user.institution || '—'}
                  </td>

                  <td>
                    <select
                      value={user.role}
                      onChange={(event) =>
                        changeUser(
                          user,
                          (event.target.value as Role),
                        )}
                    >
                      {roles.map((role) => (
                        <option
                          key={role}
                        >
                          {role}
                        </option>
                      ))}
                    </select>
                  </td>

                  <td>
                    {user.is_active
                      ? 'Active'
                      : 'Disabled'}
                  </td>

                  <td>
                    <button
                      className="button ghost"
                      onClick={() =>
                        changeUser(
                          user,
                          user.role,
                          !user.is_active,
                        )}
                    >
                      {user.is_active
                        ? 'Disable'
                        : 'Activate'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === 'opportunities' && (
        <div className="admin-content-list">
          {opportunities.map((item) => {
            const closed =
              item.tags.includes(
                'AGP-CLOSED',
              )

            return (
              <article
                className="card admin-content-card"
                key={item.id}
              >
                <div>
                  <div className="content-meta">
                    <span>
                      {item.category}
                    </span>
                    <span>
                      {item.is_published
                        ? 'Published'
                        : 'Unpublished'}
                    </span>
                    {closed && (
                      <span>Closed</span>
                    )}
                  </div>

                  <h2>{item.title}</h2>
                  <strong>
                    {item.organization}
                  </strong>
                  <p>{item.summary}</p>
                </div>

                <div className="admin-actions">
                  <button
                    className="button ghost"
                    onClick={() =>
                      setEditOpportunity(
                        item,
                      )}
                  >
                    <Pencil size={14} />
                    Edit
                  </button>

                  <button
                    className="button ghost"
                    onClick={() =>
                      patchOpportunity(
                        item,
                        {
                          is_published:
                            !item.is_published,
                        },
                      )}
                  >
                    {item.is_published
                      ? 'Unpublish'
                      : 'Publish'}
                  </button>

                  <button
                    className="button ghost"
                    onClick={() =>
                      toggleClosed(item)}
                  >
                    <RefreshCw size={14} />
                    {closed
                      ? 'Reopen'
                      : 'Mark Closed'}
                  </button>

                  <button
                    className="button danger"
                    onClick={() =>
                      deleteOpportunity(
                        item,
                      )}
                  >
                    <Trash2 size={14} />
                    Delete
                  </button>
                </div>
              </article>
            )
          })}
        </div>
      )}

      {editOpportunity && (
        <OpportunityEditor
          item={editOpportunity}
          onCancel={() =>
            setEditOpportunity(null)}
          onSave={patchOpportunity}
        />
      )}

      {tab === 'policies' && (
        <div className="admin-content-list">
          {policies.map((item) => (
            <article
              className="card admin-content-card"
              key={item.id}
            >
              <div>
                <div className="content-meta">
                  <span>
                    {item.country}
                  </span>
                  <span>
                    {item.status}
                  </span>
                  <span>
                    {item.is_published
                      ? 'Published'
                      : 'Unpublished'}
                  </span>
                </div>

                <h2>{item.title}</h2>
                <strong>
                  {item.institution}
                </strong>
                <p>{item.summary}</p>
              </div>

              <div className="admin-actions">
                <button
                  className="button ghost"
                  onClick={() =>
                    setEditPolicy(item)}
                >
                  <Pencil size={14} />
                  Edit
                </button>

                <button
                  className="button ghost"
                  onClick={() =>
                    patchPolicy(
                      item,
                      {
                        is_published:
                          !item.is_published,
                      },
                    )}
                >
                  {item.is_published
                    ? 'Unpublish'
                    : 'Publish'}
                </button>

                <button
                  className="button danger"
                  onClick={() =>
                    deletePolicy(item)}
                >
                  <Trash2 size={14} />
                  Delete
                </button>
              </div>
            </article>
          ))}
        </div>
      )}

      {editPolicy && (
        <PolicyEditor
          item={editPolicy}
          onCancel={() =>
            setEditPolicy(null)}
          onSave={patchPolicy}
        />
      )}

      {tab === 'datasets' && (
        <div className="admin-content-list">
          {datasets.map((item) => (
            <article
              className="card admin-content-card"
              key={item.id}
            >
              <div>
                <div className="content-meta">
                  <span>
                    {item.category}
                  </span>
                  <span>
                    {item.country
                      || item.region
                      || 'Africa'}
                  </span>
                  <span>
                    {item.is_published
                      ? 'Published'
                      : 'Unpublished'}
                  </span>
                </div>

                <h2>{item.title}</h2>
                <strong>
                  {item.source_name}
                </strong>
                <p>{item.summary}</p>
              </div>

              <div className="admin-actions">
                <button
                  className="button ghost"
                  onClick={() =>
                    setEditDataset(item)}
                >
                  <Pencil size={14} />
                  Edit
                </button>

                <button
                  className="button ghost"
                  onClick={() =>
                    patchDataset(
                      item,
                      {
                        is_published:
                          !item.is_published,
                      },
                    )}
                >
                  {item.is_published
                    ? 'Unpublish'
                    : 'Publish'}
                </button>

                <button
                  className="button danger"
                  onClick={() =>
                    deleteDataset(item)}
                >
                  <Trash2 size={14} />
                  Delete
                </button>
              </div>
            </article>
          ))}
        </div>
      )}

      {editDataset && (
        <DatasetEditor
          item={editDataset}
          onCancel={() =>
            setEditDataset(null)}
          onSave={patchDataset}
        />
      )}
    </div>
  )
}


function OpportunityEditor({
  item,
  onCancel,
  onSave,
}: {
  item: Opportunity
  onCancel: () => void
  onSave: (
    item: Opportunity,
    payload: Record<string, unknown>,
  ) => Promise<void>
}) {
  const [form, setForm] =
    useState({
      ...item,
      deadline:
        item.deadline || '',
      tags: tagsToText(
        item.tags,
      ),
    })

  return (
    <form
      className="card admin-editor"
      onSubmit={(event) => {
        event.preventDefault()

        onSave(
          item,
          {
            title: form.title,
            organization:
              form.organization,
            category: form.category,
            country:
              form.country || null,
            location_mode:
              form.location_mode,
            deadline:
              form.deadline || null,
            summary: form.summary,
            url: form.url,
            tags: [
              ...textToTags(
                form.tags,
              ),
              ...(
                item.tags.includes(
                  'AGP-CLOSED',
                )
                  ? ['AGP-CLOSED']
                  : []
              ),
            ],
          },
        )
      }}
    >
      <h2>Edit Opportunity</h2>

      <label>
        Title
        <input
          value={form.title}
          onChange={(event) =>
            setForm({
              ...form,
              title:
                event.target.value,
            })}
        />
      </label>

      <div className="form-grid">
        <label>
          Organization
          <input
            value={form.organization}
            onChange={(event) =>
              setForm({
                ...form,
                organization:
                  event.target.value,
              })}
          />
        </label>

        <label>
          Category
          <select
            value={form.category}
            onChange={(event) =>
              setForm({
                ...form,
                category:
                  event.target.value,
              })}
          >
            {opportunityCategories.map(
              (category) => (
                <option
                  key={category}
                >
                  {category}
                </option>
              ),
            )}
          </select>
        </label>

        <label>
          Country
          <input
            value={form.country || ''}
            onChange={(event) =>
              setForm({
                ...form,
                country:
                  event.target.value,
              })}
          />
        </label>

        <label>
          Deadline
          <input
            type="date"
            value={form.deadline}
            onChange={(event) =>
              setForm({
                ...form,
                deadline:
                  event.target.value,
              })}
          />
        </label>
      </div>

      <label>
        Summary
        <textarea
          rows={5}
          value={form.summary}
          onChange={(event) =>
            setForm({
              ...form,
              summary:
                event.target.value,
            })}
        />
      </label>

      <label>
        Application URL
        <input
          type="url"
          value={form.url}
          onChange={(event) =>
            setForm({
              ...form,
              url:
                event.target.value,
            })}
        />
      </label>

      <label>
        Tags
        <input
          value={form.tags}
          onChange={(event) =>
            setForm({
              ...form,
              tags:
                event.target.value,
            })}
        />
      </label>

      <div className="form-actions">
        <button className="button dark">
          Save Opportunity
        </button>

        <button
          type="button"
          className="button ghost"
          onClick={onCancel}
        >
          Cancel
        </button>
      </div>
    </form>
  )
}


function PolicyEditor({
  item,
  onCancel,
  onSave,
}: {
  item: Policy
  onCancel: () => void
  onSave: (
    item: Policy,
    payload: Record<string, unknown>,
  ) => Promise<void>
}) {
  const [form, setForm] =
    useState({
      ...item,
      published_date:
        item.published_date || '',
      effective_date:
        item.effective_date || '',
      tags: tagsToText(
        item.tags,
      ),
    })

  return (
    <form
      className="card admin-editor"
      onSubmit={(event) => {
        event.preventDefault()

        onSave(
          item,
          {
            title: form.title,
            country: form.country,
            institution:
              form.institution,
            policy_area:
              form.policy_area,
            status: form.status,
            summary: form.summary,
            agp_analysis:
              form.agp_analysis,
            source_url:
              form.source_url,
            published_date:
              form.published_date
              || null,
            effective_date:
              form.effective_date
              || null,
            tags: textToTags(
              form.tags,
            ),
          },
        )
      }}
    >
      <h2>Edit Policy Record</h2>

      <label>
        Title
        <input
          value={form.title}
          onChange={(event) =>
            setForm({
              ...form,
              title:
                event.target.value,
            })}
        />
      </label>

      <div className="form-grid">
        <label>
          Country
          <input
            value={form.country}
            onChange={(event) =>
              setForm({
                ...form,
                country:
                  event.target.value,
              })}
          />
        </label>

        <label>
          Institution
          <input
            value={form.institution}
            onChange={(event) =>
              setForm({
                ...form,
                institution:
                  event.target.value,
              })}
          />
        </label>

        <label>
          Policy Area
          <input
            value={form.policy_area}
            onChange={(event) =>
              setForm({
                ...form,
                policy_area:
                  event.target.value,
              })}
          />
        </label>

        <label>
          Status
          <input
            value={form.status}
            onChange={(event) =>
              setForm({
                ...form,
                status:
                  event.target.value,
              })}
          />
        </label>
      </div>

      <label>
        Summary
        <textarea
          rows={4}
          value={form.summary}
          onChange={(event) =>
            setForm({
              ...form,
              summary:
                event.target.value,
            })}
        />
      </label>

      <label>
        AGP Analysis
        <textarea
          rows={5}
          value={form.agp_analysis}
          onChange={(event) =>
            setForm({
              ...form,
              agp_analysis:
                event.target.value,
            })}
        />
      </label>

      <label>
        Official Source URL
        <input
          type="url"
          value={form.source_url}
          onChange={(event) =>
            setForm({
              ...form,
              source_url:
                event.target.value,
            })}
        />
      </label>

      <label>
        Tags
        <input
          value={form.tags}
          onChange={(event) =>
            setForm({
              ...form,
              tags:
                event.target.value,
            })}
        />
      </label>

      <div className="form-actions">
        <button className="button dark">
          Save Policy
        </button>

        <button
          type="button"
          className="button ghost"
          onClick={onCancel}
        >
          Cancel
        </button>
      </div>
    </form>
  )
}


function DatasetEditor({
  item,
  onCancel,
  onSave,
}: {
  item: Dataset
  onCancel: () => void
  onSave: (
    item: Dataset,
    payload: Record<string, unknown>,
  ) => Promise<void>
}) {
  const [form, setForm] =
    useState({
      ...item,
      region: item.region || '',
      country: item.country || '',
      download_url:
        item.download_url || '',
      license_name:
        item.license_name || '',
      tags: tagsToText(
        item.tags,
      ),
    })

  return (
    <form
      className="card admin-editor"
      onSubmit={(event) => {
        event.preventDefault()

        onSave(
          item,
          {
            title: form.title,
            summary: form.summary,
            description:
              form.description,
            category:
              form.category,
            region:
              form.region || null,
            country:
              form.country || null,
            source_name:
              form.source_name,
            source_url:
              form.source_url,
            download_url:
              form.download_url
              || null,
            license_name:
              form.license_name
              || null,
            tags: textToTags(
              form.tags,
            ),
          },
        )
      }}
    >
      <h2>Edit Dataset</h2>

      <label>
        Title
        <input
          value={form.title}
          onChange={(event) =>
            setForm({
              ...form,
              title:
                event.target.value,
            })}
        />
      </label>

      <div className="form-grid">
        <label>
          Category
          <input
            value={form.category}
            onChange={(event) =>
              setForm({
                ...form,
                category:
                  event.target.value,
              })}
          />
        </label>

        <label>
          Country
          <input
            value={form.country}
            onChange={(event) =>
              setForm({
                ...form,
                country:
                  event.target.value,
              })}
          />
        </label>
      </div>

      <label>
        Summary
        <textarea
          rows={3}
          value={form.summary}
          onChange={(event) =>
            setForm({
              ...form,
              summary:
                event.target.value,
            })}
        />
      </label>

      <label>
        Description
        <textarea
          rows={5}
          value={form.description}
          onChange={(event) =>
            setForm({
              ...form,
              description:
                event.target.value,
            })}
        />
      </label>

      <div className="form-grid">
        <label>
          Source Name
          <input
            value={form.source_name}
            onChange={(event) =>
              setForm({
                ...form,
                source_name:
                  event.target.value,
              })}
          />
        </label>

        <label>
          Source URL
          <input
            type="url"
            value={form.source_url}
            onChange={(event) =>
              setForm({
                ...form,
                source_url:
                  event.target.value,
              })}
          />
        </label>
      </div>

      <label>
        Download URL
        <input
          type="url"
          value={form.download_url}
          onChange={(event) =>
            setForm({
              ...form,
              download_url:
                event.target.value,
            })}
        />
      </label>

      <label>
        Tags
        <input
          value={form.tags}
          onChange={(event) =>
            setForm({
              ...form,
              tags:
                event.target.value,
            })}
        />
      </label>

      <div className="form-actions">
        <button className="button dark">
          Save Dataset
        </button>

        <button
          type="button"
          className="button ghost"
          onClick={onCancel}
        >
          Cancel
        </button>
      </div>
    </form>
  )
}
