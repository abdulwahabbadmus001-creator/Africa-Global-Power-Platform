import {
  Check,
  Copy,
  ExternalLink,
  Share2,
} from 'lucide-react'

import {
  useState,
} from 'react'

import { api } from '../lib/api'


type ShareChannel =
  | 'linkedin'
  | 'x'
  | 'facebook'
  | 'whatsapp'
  | 'email'
  | 'medium'
  | 'researchgate'
  | 'academia'
  | 'github'
  | 'copy'


type ShareLinkResponse = {
  event_id: string
  channel: string
  canonical_url: string
  tracked_url: string
  share_url: string
  suggested_text: string
  mode: string
  manual_instruction?: string | null
}


type Props = {
  publicationId: string
  message?: string
  context?: string
  compact?: boolean
}


const channels: Array<{
  id: ShareChannel
  label: string
}> = [
  {
    id: 'linkedin',
    label: 'LinkedIn',
  },
  {
    id: 'x',
    label: 'X',
  },
  {
    id: 'facebook',
    label: 'Facebook',
  },
  {
    id: 'whatsapp',
    label: 'WhatsApp',
  },
  {
    id: 'medium',
    label: 'Medium',
  },
  {
    id: 'researchgate',
    label: 'ResearchGate',
  },
  {
    id: 'academia',
    label: 'Academia',
  },
  {
    id: 'github',
    label: 'GitHub',
  },
  {
    id: 'email',
    label: 'Email',
  },
]


export default function SharePublication({
  publicationId,
  message,
  context = 'public_page',
  compact = false,
}: Props) {
  const [busy, setBusy] =
    useState<string | null>(null)

  const [notice, setNotice] =
    useState('')

  const [copied, setCopied] =
    useState(false)


  async function createLink(
    channel: ShareChannel,
  ) {
    setBusy(channel)

    setNotice('')

    try {
      const result =
        await api<ShareLinkResponse>(
          `/amplification/publications/${publicationId}/share-link`,
          {
            method: 'POST',

            body: JSON.stringify({
              channel,
              context,
              message_override:
                message || null,
            }),
          },
        )

      if (result.mode === 'copy') {
        await navigator.clipboard.writeText(
          result.tracked_url,
        )

        setCopied(true)

        setNotice(
          'Publication link copied.',
        )

        window.setTimeout(
          () => setCopied(false),
          2000,
        )

        return
      }


      if (
        result.mode
        === 'copy_and_open'
      ) {
        const clipboardText =
          `${result.suggested_text}\n\n`
          + result.tracked_url

        await navigator.clipboard.writeText(
          clipboardText,
        )

        if (
          result.manual_instruction
        ) {
          setNotice(
            result.manual_instruction,
          )
        }

        window.open(
          result.share_url,
          '_blank',
          'noopener,noreferrer',
        )

        return
      }


      if (channel === 'email') {
        window.location.href =
          result.share_url

        return
      }


      window.open(
        result.share_url,
        '_blank',
        'noopener,noreferrer',
      )
    } catch (error) {
      setNotice(
        error instanceof Error
          ? error.message
          : (
              'Unable to prepare '
              + 'the share link.'
            ),
      )
    } finally {
      setBusy(null)
    }
  }


  return (
    <div
      style={{
        marginTop:
          compact ? '12px' : '20px',
      }}
    >

      {!compact && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            marginBottom: '12px',
          }}
        >
          <Share2 size={18} />

          <strong>
            Share this research
          </strong>
        </div>
      )}


      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '8px',
        }}
      >

        {channels.map(
          (channel) => (
            <button
              key={channel.id}
              type="button"
              className="button ghost"
              disabled={
                busy !== null
              }
              onClick={() =>
                createLink(
                  channel.id,
                )
              }
              style={{
                padding:
                  compact
                    ? '7px 10px'
                    : undefined,
              }}
            >
              <ExternalLink
                size={14}
              />

              {busy === channel.id
                ? 'Opening…'
                : channel.label}
            </button>
          ),
        )}


        <button
          type="button"
          className="button ghost"
          disabled={busy !== null}
          onClick={() =>
            createLink('copy')
          }
        >
          {copied
            ? (
                <Check
                  size={14}
                />
              )
            : (
                <Copy
                  size={14}
                />
              )}

          {copied
            ? 'Copied'
            : 'Copy link'}
        </button>

      </div>


      {notice && (
        <div
          style={{
            marginTop: '12px',
            padding: '10px 12px',
            fontSize: '12px',
            lineHeight: 1.5,
            background: '#f5f3ec',
            border:
              '1px solid #ddd7c9',
          }}
        >
          {notice}
        </div>
      )}

    </div>
  )
}