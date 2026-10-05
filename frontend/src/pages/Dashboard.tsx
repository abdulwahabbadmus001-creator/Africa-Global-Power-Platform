import {
  BarChart3,
  BookOpen,
  FilePlus2,
  Mail,
  Megaphone,
  ShieldCheck,
  Users,
} from 'lucide-react'

import {
  useEffect,
  useState,
} from 'react'

import {
  Link,
} from 'react-router-dom'

import MetricCard
  from '../components/MetricCard'

import StatusBadge
  from '../components/StatusBadge'

import { api } from '../lib/api'
import { useAuth } from '../lib/auth'

import type {
  Analytics,
  Publication,
} from '../types'


export default function Dashboard() {
  const { user } = useAuth()

  const [pubs, setPubs] =
    useState<Publication[]>([])

  const [stats, setStats] =
    useState<Analytics[]>([])

  const [unread, setUnread] =
    useState(0)


  useEffect(() => {
    api<Publication[]>(
      '/publications/mine'
    )
      .then(setPubs)
      .catch(() => {})

    api<Analytics[]>(
      '/analytics/mine'
    )
      .then(setStats)
      .catch(() => {})

    api<{ unread: number }>(
      '/messages/unread-count'
    )
      .then(
        (result) =>
          setUnread(
            result.unread
          )
      )
      .catch(() => {})
  }, [])


  const totals = stats.reduce(
    (accumulator, stat) => ({
      views:
        accumulator.views
        + stat.views,

      readers:
        accumulator.readers
        + stat.unique_readers,

      downloads:
        accumulator.downloads
        + stat.downloads,
    }),
    {
      views: 0,
      readers: 0,
      downloads: 0,
    },
  )


  const editorial = [
    'reviewer',
    'editor',
    'senior_editor',
    'managing_editor',
    'super_admin',
  ].includes(
    user?.role || ''
  )


  return (
    <div className="dashboard page section">

      <div className="dashboard-head">

        <div>

          <div className="eyebrow dark">
            RESEARCHER PORTAL
          </div>

          <h1>
            {user?.first_name}'s
            workspace
          </h1>

          <p>
            Manage research,
            understand readership,
            distribute published
            work and connect with
            the AGP network.
          </p>

        </div>


        <Link
          className="button dark large"
          to="/dashboard/new-publication"
        >
          <FilePlus2 size={18} />

          New publication
        </Link>

      </div>


      <div className="metrics-grid">

        <MetricCard
          label="Publications"
          value={pubs.length}
        />

        <MetricCard
          label="Views"
          value={totals.views}
        />

        <MetricCard
          label="Unique readers"
          value={totals.readers}
        />

        <MetricCard
          label="Downloads"
          value={totals.downloads}
        />

        <MetricCard
          label="Unread messages"
          value={unread}
        />

      </div>


      <div className="dashboard-grid">

        <section className="card panel">

          <div className="panel-head">

            <h2>
              My research
            </h2>

            <Link
              to="/dashboard/new-publication"
            >
              Create draft
            </Link>

          </div>


          {pubs.length
            ? (
                pubs
                  .slice(0, 6)
                  .map(
                    (publication) => (
                      <div
                        className="dashboard-row"
                        key={
                          publication.id
                        }
                      >

                        <div>

                          <Link
                            to={
                              `/dashboard/publications/${publication.id}`
                            }
                          >
                            <strong>
                              {
                                publication.title
                              }
                            </strong>
                          </Link>

                          <small>
                            Updated{' '}
                            {
                              new Date(
                                publication.updated_at
                              )
                                .toLocaleDateString()
                            }

                            {' • '}

                            {
                              stats.find(
                                (stat) =>
                                  stat.publication_id
                                  === publication.id
                              )?.views
                              || 0
                            }

                            {' '}views
                          </small>

                        </div>

                        <StatusBadge
                          status={
                            publication.status
                          }
                        />

                      </div>
                    ),
                  )
              )
            : (
                <div className="empty-inline">
                  Your publication
                  workspace is empty.
                </div>
              )}

        </section>


        <aside className="card panel quick">

          <h2>
            Workspace
          </h2>


          <Link to="/messages">
            <Mail />

            Messages

            <span>
              {unread}
            </span>
          </Link>


          <Link
            to="/dashboard/amplification"
          >
            <Megaphone />

            Research amplification
          </Link>


          <Link to="/researchers">
            <Users />

            Researcher network
          </Link>


          <Link to="/research">
            <BookOpen />

            Saved research
          </Link>


          <span>
            <BarChart3 />

            Analytics
          </span>


          {editorial && (
            <Link
              className="special-link"
              to="/editorial"
            >
              <ShieldCheck />

              Editorial dashboard
            </Link>
          )}


          {editorial && (
            <Link
              className="special-link"
              to="/editorial/amplification"
            >
              <Megaphone />

              Amplification desk
            </Link>
          )}


          {user?.role
            === 'super_admin'
            && (
              <Link
                className="special-link"
                to="/system"
              >
                <ShieldCheck />

                System administration
              </Link>
            )}

        </aside>

      </div>

    </div>
  )
}