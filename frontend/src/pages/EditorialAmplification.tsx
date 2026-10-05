import {
  CheckCircle2,
  Megaphone,
  Save,
} from 'lucide-react'

import {
  useEffect,
  useState,
} from 'react'

import SharePublication
  from '../components/SharePublication'

import { api } from '../lib/api'


type Announcement = {
  id: string
  publication_id: string
  created_by_id: string
  message: string
  channels: string[]
  distributed_channels: string[]
  status: string
  distributed_at?: string | null
  created_at: string
  updated_at: string
}


type QueueItem = {
  publication_id: string
  title: string
  slug: string
  author_name: string
  published_at?: string | null
  announcement?: Announcement | null
}


export default function EditorialAmplification() {
  const [queue, setQueue] =
    useState<QueueItem[]>([])

  const [selected, setSelected] =
    useState<QueueItem | null>(
      null,
    )

  const [message, setMessage] =
    useState('')

  const [busy, setBusy] =
    useState(false)

  const [notice, setNotice] =
    useState('')


  async function load() {
    const result =
      await api<QueueItem[]>(
        '/amplification/editorial/queue',
      )

    setQueue(result)

    if (selected) {
      const refreshed =
        result.find(
          (item) =>
            item.publication_id
            === selected.publication_id,
        )

      if (refreshed) {
        setSelected(refreshed)

        setMessage(
          refreshed.announcement
            ?.message
            || '',
        )
      }
    }
  }


  useEffect(() => {
    load().catch(() => {})
  }, [])


  function choose(
    item: QueueItem,
  ) {
    setSelected(item)

    setMessage(
      item.announcement
        ?.message
        || '',
    )

    setNotice('')
  }


  async function generate() {
    if (!selected) {
      return
    }

    setBusy(true)
    setNotice('')

    try {
      const announcement =
        await api<Announcement>(
          `/amplification/editorial/publications/${selected.publication_id}/announcement`,
          {
            method: 'POST',
          },
        )

      setMessage(
        announcement.message,
      )

      await load()

      setNotice(
        'Institutional announcement prepared.',
      )
    } finally {
      setBusy(false)
    }
  }


  async function save() {
    if (
      !selected?.announcement
    ) {
      return
    }

    setBusy(true)
    setNotice('')

    try {
      await api(
        `/amplification/editorial/announcements/${selected.announcement.id}`,
        {
          method: 'PATCH',

          body: JSON.stringify({
            message,
            channels: [
              'linkedin',
              'x',
              'facebook',
            ],
          }),
        },
      )

      await load()

      setNotice(
        'Announcement saved.',
      )
    } catch (error) {
      setNotice(
        error instanceof Error
          ? error.message
          : (
              'Unable to save '
              + 'announcement.'
            ),
      )
    } finally {
      setBusy(false)
    }
  }


  async function markDistributed() {
    if (
      !selected?.announcement
    ) {
      return
    }

    setBusy(true)

    try {
      await api(
        `/amplification/editorial/announcements/${selected.announcement.id}/distributed`,
        {
          method: 'POST',

          body: JSON.stringify({
            channels: [
              'linkedin',
              'x',
              'facebook',
            ],
          }),
        },
      )

      await load()

      setNotice(
        'Institutional distribution recorded.',
      )
    } finally {
      setBusy(false)
    }
  }


  return (
    <div className="page section">

      <div className="dashboard-head">

        <div>

          <div className="eyebrow dark">
            AGP AMPLIFICATION DESK
          </div>

          <h1>
            Institutional distribution.
          </h1>

          <p>
            Prepare and distribute
            official AGP announcements
            for newly published
            research.
          </p>

        </div>

        <Megaphone size={36} />

      </div>


      <div
        className="editorial-grid"
      >

        <section className="card panel">

          <div className="panel-head">

            <h2>
              Published research
            </h2>

            <span>
              {queue.length}
            </span>

          </div>


          {queue.map(
            (item) => (
              <button
                key={
                  item.publication_id
                }
                className={
                  `queue-row ${
                    selected?.publication_id
                    === item.publication_id
                      ? 'active'
                      : ''
                  }`
                }
                type="button"
                onClick={() =>
                  choose(item)
                }
              >

                <div>

                  <strong>
                    {item.title}
                  </strong>

                  <small>
                    {item.author_name}

                    {' • '}

                    {item.announcement
                      ? (
                          item.announcement
                            .status
                        )
                      : (
                          'announcement pending'
                        )}
                  </small>

                </div>

              </button>
            ),
          )}

        </section>


        <aside className="card review-panel">

          {!selected && (
            <div className="empty-review">

              <Megaphone />

              <h3>
                Select a publication
              </h3>

              <p>
                Prepare an official
                Africa & Global Power
                publication
                announcement.
              </p>

            </div>
          )}


          {selected && (
            <>

              <div className="eyebrow dark">
                INSTITUTIONAL ANNOUNCEMENT
              </div>

              <h2>
                {selected.title}
              </h2>

              <p>
                Researcher:{' '}
                <strong>
                  {selected.author_name}
                </strong>
              </p>


              {!selected.announcement && (
                <button
                  type="button"
                  className="button dark large"
                  disabled={busy}
                  onClick={generate}
                >
                  <Megaphone
                    size={17}
                  />

                  Generate AGP
                  announcement
                </button>
              )}


              {selected.announcement && (
                <>

                  <label>
                    Announcement copy

                    <textarea
                      rows={10}
                      value={message}
                      onChange={(event) =>
                        setMessage(
                          event.target.value
                        )
                      }
                    />
                  </label>


                  <button
                    type="button"
                    className="button dark"
                    onClick={save}
                    disabled={busy}
                  >
                    <Save size={16} />

                    Save announcement
                  </button>


                  <SharePublication
                    publicationId={
                      selected.publication_id
                    }
                    message={message}
                    context={
                      'agp_institutional'
                    }
                  />


                  <div
                    style={{
                      marginTop: '20px',
                    }}
                  >

                    <button
                      type="button"
                      className="button ghost"
                      onClick={
                        markDistributed
                      }
                      disabled={busy}
                    >
                      <CheckCircle2
                        size={16}
                      />

                      Mark institutional
                      distribution complete
                    </button>

                  </div>


                  {selected
                    .announcement
                    .distributed_channels
                    .length > 0
                    && (
                      <small
                        style={{
                          display:
                            'block',
                          marginTop:
                            '12px',
                        }}
                      >
                        Recorded channels:{' '}
                        {
                          selected
                            .announcement
                            .distributed_channels
                            .join(', ')
                        }
                      </small>
                    )}

                </>
              )}


              {notice && (
                <div
                  className="alert"
                  style={{
                    marginTop: '16px',
                  }}
                >
                  {notice}
                </div>
              )}

            </>
          )}

        </aside>

      </div>

    </div>
  )
}