import { useState } from 'react'

import {
  useNavigate,
} from 'react-router-dom'

import { api } from '../lib/api'


type EditorialLoginResponse = {
  message: string
  requires_setup: boolean
  requires_mfa: boolean
}


export default function EditorialLogin() {
  const navigate = useNavigate()

  const [email, setEmail] =
    useState('')

  const [password, setPassword] =
    useState('')

  const [error, setError] =
    useState('')

  const [busy, setBusy] =
    useState(false)


  async function submit(
    event: React.FormEvent,
  ) {
    event.preventDefault()

    setBusy(true)
    setError('')

    try {
      const result =
        await api<EditorialLoginResponse>(
          '/auth/editorial/login',
          {
            method: 'POST',

            body: JSON.stringify({
              email,
              password,
            }),
          },
        )

      if (result.requires_setup) {
        navigate(
          '/editorial/setup-mfa',
        )

        return
      }

      navigate(
        '/editorial/verify',
      )
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : (
              'Unable to authenticate.'
            ),
      )
    } finally {
      setBusy(false)
    }
  }


  return (
    <div className="auth-page">

      <form
        className="auth-card card"
        onSubmit={submit}
      >

        <div className="eyebrow dark">
          AGP EDITORIAL ACCESS
        </div>

        <h1>
          Editorial sign in.
        </h1>

        <p>
          Authorised editorial personnel
          only. All authentication attempts
          and editorial access are audited.
        </p>

        {error && (
          <div className="alert error">
            {error}
          </div>
        )}

        <label>
          Editorial email

          <input
            type="email"
            required
            value={email}
            onChange={(event) =>
              setEmail(
                event.target.value
              )
            }
            autoComplete="username"
          />
        </label>

        <label>
          Password

          <input
            type="password"
            required
            value={password}
            onChange={(event) =>
              setPassword(
                event.target.value
              )
            }
            autoComplete="current-password"
          />
        </label>

        <button
          className="button dark large full"
          disabled={busy}
          type="submit"
        >
          {busy
            ? 'Authenticating…'
            : 'Continue securely'}
        </button>

        <small>
          Editorial accounts cannot be
          created through public
          registration.
        </small>

      </form>

    </div>
  )
}