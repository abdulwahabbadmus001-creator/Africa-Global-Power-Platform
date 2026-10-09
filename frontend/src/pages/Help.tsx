import {
  BookOpen,
  Download,
  LockKeyhole,
  MessageSquare,
  Search,
  UserRound,
} from 'lucide-react'


export default function Help() {
  return (
    <div className="page section production-page">
      <div className="section-head">
        <div>
          <div className="eyebrow dark">
            HELP & RESOURCES
          </div>

          <h1>
            Navigate AGP with confidence.
          </h1>

          <p className="lead">
            A short orientation for Readers,
            Researchers and anyone exploring
            Africa & Global Power.
          </p>
        </div>

        <BookOpen size={38} />
      </div>

      <a
        className="button dark large guide-download"
        href="/AGP-User-Guide.pdf"
        download
      >
        <Download size={18} />
        Download AGP User Guide (PDF)
      </a>

      <div className="help-grid">
        <article className="card help-card">
          <Search />
          <h2>Readers</h2>
          <p>
            Discover publications, save research,
            follow researchers, browse opportunities
            and send professional inquiries.
          </p>
        </article>

        <article className="card help-card">
          <UserRound />
          <h2>Researchers</h2>
          <p>
            Build a public profile, submit work,
            manage Featured Works, view analytics
            and receive collaboration inquiries.
          </p>
        </article>

        <article className="card help-card">
          <MessageSquare />
          <h2>Research Network</h2>
          <p>
            AGP messaging keeps professional
            conversations inside the platform
            without displaying private email
            addresses publicly.
          </p>
        </article>

        <article className="card help-card">
          <LockKeyhole />
          <h2>Private Editorial</h2>
          <p>
            Editorial access is intentionally
            private to protect unpublished work,
            reduce fraudulent access and limit
            bias or inappropriate influence.
          </p>
        </article>
      </div>
    </div>
  )
}
