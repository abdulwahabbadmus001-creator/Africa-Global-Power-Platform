import {
  useEffect,
  useState,
} from 'react'

import {
  useNavigate,
} from 'react-router-dom'

import {
  QRCodeSVG,
} from 'qrcode.react'

import { api } from '../lib/api'
import { useAuth } from '../lib/auth'
import type { User } from '../types'


type SetupResponse = {
  issuer: string
  account: string
  secret: string
  otpauth_uri: string
}


type SetupSuccess = {
  message: string
  recovery_codes: string[]
  user: User
}


export default function EditorialMfaSetup() {
  const navigate = useNavigate()

  const { refresh } = useAuth()

  const [setup, setSetup] =
    useState<SetupResponse | null>(
      null,
    )

  const [code, setCode] =
    useState('')

  const [recoveryCodes, setRecoveryCodes] =
    useState<string[]>([])

  const [error, setError] =
    useState('')

  const [busy, setBusy] =
    useState(false)


  useEffect(() => {
    api<SetupResponse>(
      '/auth/editorial/mfa/setup',
    )
      .then(setSetup)
      .catch((err) => {
        setError(
          err instanceof Error
            ? err.message
            : (
                'Unable to begin '
                + 'authenticator setup.'
              ),
        )
      })
  }, [])


  async function confirm(
    event: React.FormEvent,
  ) {
    event.preventDefault()

    setBusy(true)
    setError('')

    try {
      const result =
        await api<SetupSuccess>(
          '/auth/editorial/mfa/setup/confirm',
          {
            method: 'POST',

            body: JSON.stringify({
              code,
            }),
          },
        )

      setRecoveryCodes(
        result.recovery_codes,
      )

      await refresh()
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : (
              'Unable to confirm '
              + 'authenticator setup.'
            ),
      )
    } finally {
      setBusy(false)
    }
  }


  if (recoveryCodes.length > 0) {
    return (
      <div className="auth-page">

        <div
          className="auth-card wide card"
        >

          <div className="eyebrow dark">
            EDITORIAL SECURITY
          </div>

          <h1>
            Save your recovery codes.
          </h1>

          <p>
            Each code can be used once if
            you lose access to your
            authenticator. Store them
            offline in a secure place.
          </p>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns:
                '1fr 1fr',
              gap: '10px',
              margin: '24px 0',
              padding: '20px',
              background: '#f5f3ec',
              border:
                '1px solid #d9d3c4',
            }}
          >
            {recoveryCodes.map(
              (item) => (
                <code
                  key={item}
                  style={{
                    fontWeight: 700,
                    padding: '8px',
                  }}
                >
                  {item}
                </code>
              ),
            )}
          </div>

          <button
            className="button dark large full"
            type="button"
            onClick={() =>
              navigate(
                '/editorial',
                {
                  replace: true,
                },
              )
            }
          >
            I saved my recovery codes
          </button>

        </div>

      </div>
    )
  }


  return (
    <div className="auth-page">

      <form
        className="auth-card wide card"
        onSubmit={confirm}
      >

        <div className="eyebrow dark">
          EDITORIAL SECURITY
        </div>

        <h1>
          Set up your authenticator.
        </h1>

        <p>
          Scan the QR code using Google
          Authenticator, Microsoft
          Authenticator, 1Password,
          Authy, or another compatible
          TOTP application.
        </p>

        {error && (
          <div className="alert error">
            {error}
          </div>
        )}

        {!setup && !error && (
          <p>
            Preparing secure setup…
          </p>
        )}

        {setup && (
          <>
            <div
              style={{
                display: 'grid',
                placeItems: 'center',
                padding: '25px',
                background: '#ffffff',
                margin: '20px 0',
              }}
            >
              <QRCodeSVG
                value={
                  setup.otpauth_uri
                }
                size={220}
                level="M"
              />
            </div>

            <p
              style={{
                fontSize: '12px',
              }}
            >
              If you cannot scan the QR
              code, enter this setup key
              manually:
            </p>

            <div
              style={{
                padding: '14px',
                background: '#f5f3ec',
                wordBreak: 'break-all',
                fontFamily:
                  'monospace',
                fontWeight: 700,
                marginBottom: '20px',
              }}
            >
              {setup.secret}
            </div>

            <label>
              Current 6-digit code

              <input
                inputMode="numeric"
                maxLength={6}
                required
                value={code}
                onChange={(event) =>
                  setCode(
                    event.target.value
                      .replace(
                        /\D/g,
                        '',
                      )
                      .slice(
                        0,
                        6,
                      ),
                  )
                }
                autoComplete="one-time-code"
              />
            </label>

            <button
              className="button dark large full"
              disabled={busy}
              type="submit"
            >
              {busy
                ? 'Verifying…'
                : (
                    'Enable Editorial '
                    + 'MFA'
                  )}
            </button>
          </>
        )}

      </form>

    </div>
  )
}