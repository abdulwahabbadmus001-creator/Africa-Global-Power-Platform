import {
  BarChart3,
  ExternalLink,
  Megaphone,
  MousePointerClick,
  Share2,
} from 'lucide-react'

import {
  useEffect,
  useState,
} from 'react'

import {
  Link,
} from 'react-router-dom'

import SharePublication
  from '../components/SharePublication'

import { api } from '../lib/api'


type AmplificationMetrics = {
  publication_id: string
  title: string
  slug: string
  published_at?: string | null
  share_actions: number
  referral_clicks: number
  channels: Record<
    string,
    number
  >
}


export default function ResearchAmplification() {
  const [
    publications,
    setPublications,
  ] = useState<
    AmplificationMetrics[]
  >([])

  const [loading, setLoading] =
    useState(true)


  useEffect(() => {
    api<AmplificationMetrics[]>(
      '/amplification/mine',
    )
      .then(setPublications)
      .finally(
        () => setLoading(false)
      )
  }, [])


  const totalShares =
    publications.reduce(
      (sum, item) =>
        sum + item.share_actions,
      0,
    )


  const totalClicks =
    publications.reduce(
      (sum, item) =>
        sum + item.referral_clicks,
      0,
    )


  return (
    <div className="page section">

      <div className="dashboard-head">

        <div>

          <div className="eyebrow dark">
            RESEARCH AMPLIFICATION
          </div>

          <h1>
            Distribute your research.
          </h1>

          <p>
            Share published research
            across professional,
            academic and social
            networks and understand
            which channels bring
            readers back to AGP.
          </p>

        </div>

        <Megaphone size={34} />

      </div>


      <div className="metrics-grid">

        <div className="card panel">

          <Share2 />

          <strong
            style={{
              fontSize: '28px',
              display: 'block',
              marginTop: '8px',
            }}
          >
            {totalShares}
          </strong>

          <small>
            Share actions
          </small>

        </div>


        <div className="card panel">

          <MousePointerClick />

          <strong
            style={{
              fontSize: '28px',
              display: 'block',
              marginTop: '8px',
            }}
          >
            {totalClicks}
          </strong>

          <small>
            Referral readers
          </small>

        </div>


        <div className="card panel">

          <BarChart3 />

          <strong
            style={{
              fontSize: '28px',
              display: 'block',
              marginTop: '8px',
            }}
          >
            {publications.length}
          </strong>

          <small>
            Published works
          </small>

        </div>

      </div>


      {loading && (
        <div className="card panel">
          Loading amplification
          analytics…
        </div>
      )}


      {!loading
        && publications.length === 0
        && (
          <div className="card panel">

            <h2>
              No published research yet
            </h2>

            <p>
              Research Amplification
              becomes available once a
              publication has completed
              editorial review and is
              published by AGP.
            </p>

          </div>
        )}


      {publications.map(
        (publication) => (
          <section
            key={
              publication.publication_id
            }
            className="card panel"
            style={{
              marginTop: '18px',
            }}
          >

            <div className="panel-head">

              <div>

                <h2>
                  {publication.title}
                </h2>

                <small>
                  {publication.published_at
                    ? (
                        'Published '
                        + new Date(
                          publication.published_at
                        ).toLocaleDateString()
                      )
                    : 'Published'}
                </small>

              </div>

              <Link
                to={
                  `/research/${publication.slug}`
                }
              >
                View publication{' '}

                <ExternalLink
                  size={14}
                />
              </Link>

            </div>


            <div
              style={{
                display: 'flex',
                gap: '24px',
                flexWrap: 'wrap',
                marginTop: '14px',
              }}
            >

              <div>

                <strong>
                  {
                    publication
                      .share_actions
                  }
                </strong>

                <small
                  style={{
                    display: 'block',
                  }}
                >
                  Share actions
                </small>

              </div>


              <div>

                <strong>
                  {
                    publication
                      .referral_clicks
                  }
                </strong>

                <small
                  style={{
                    display: 'block',
                  }}
                >
                  Referral clicks
                </small>

              </div>


              {Object.entries(
                publication.channels,
              ).map(
                ([
                  channel,
                  count,
                ]) => (
                  <div key={channel}>

                    <strong>
                      {count}
                    </strong>

                    <small
                      style={{
                        display:
                          'block',
                        textTransform:
                          'capitalize',
                      }}
                    >
                      {channel}
                    </small>

                  </div>
                ),
              )}

            </div>


            <SharePublication
              publicationId={
                publication.publication_id
              }
              context={
                'researcher_dashboard'
              }
            />

          </section>
        ),
      )}

    </div>
  )
}