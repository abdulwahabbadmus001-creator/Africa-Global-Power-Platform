import {
  useMemo,
  useState,
} from 'react'

import {
  Link,
  useNavigate,
  useSearchParams,
} from 'react-router-dom'

import { api } from '../lib/api'
import { useAuth } from '../lib/auth'
import type { User } from '../types'


export default function VerifyLogin() {
  const [searchParams] = useSearchParams()

  const navigate = useNavigate()

  const { refresh } = useAuth()

  const email = useMemo(
    () =>
      searchParams
        .get('email')
        ?.trim()
      || '',
    [searchParams],
  )

  const [code, setCode] = useState('')

  const [error, setError] = useState('')

  const [busy, setBusy] = useState(false)


  function changeCode(
    event: React.ChangeEvent<HTMLInputElement>,
  ) {
    const digitsOnly =
      event.target.value.replace(
        /\D/g,
        '',
      )

    setCode(
      digitsOnly.slice(0, 8),
    )
  }


  async function submit(
    event: React.FormEvent,
  ) {
    event.preventDefault()

    if (!email) {
      setError(
        'Your authentication request is incomplete. Please sign in again.',
      )

      return
    }

    if (code.length < 6) {
      setError(
        'Enter the verification code sent to your email.',
      )

      return
    }

    setBusy(true)
    setError('')

    try {
      await api<User>(
        '/auth/verify-login',
        {
          method: 'POST',

          body: JSON.stringify({
            email,
            code,
          }),
        },
      )

      await refresh()

      navigate(
        '/dashboard',
        {
          replace: true,
        },
      )
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : 'Unable to verify your sign-in.'

      setError(message)
    } finally {
      setBusy(false)
    }
  }


  if (!email) {
    return (
      <div className="auth-page">
        <div className="auth-card card">
          <div className="eyebrow dark">
            SECURE SIGN IN
          </div>

          <h1>Sign-in request incomplete.</h1>

          <p>
            Return to the login page and
            enter your credentials again.
          </p>

          <Link
            className="button dark large full"
            to="/login"
          >
            Return to login
          </Link>
        </div>
      </div>
    )
  }


  return (
    <div className="auth-page">
      <form
        className="auth-card card"
        onSubmit={submit}
      >
        <div className="eyebrow dark">
          SECURE SIGN IN
        </div>

        <h1>Check your email.</h1>

        <p>
          Your password was accepted.
          Enter the one-time verification
          code sent to:
        </p>

        <div
          style={{
            fontWeight: 700,
            marginBottom: '20px',
            wordBreak: 'break-word',
          }}
        >
          {email}
        </div>

        {error && (
          <div className="alert error">
            {error}
          </div>
        )}

        <label>
          Sign-in verification code

          <input
            type="text"
            inputMode="numeric"
            autoComplete="one-time-code"
            required
            maxLength={8}
            value={code}
            onChange={changeCode}
            placeholder="00000000"
            style={{
              fontSize: '24px',
              letterSpacing: '0.2em',
              textAlign: 'center',
              fontWeight: 700,
            }}
          />
        </label>

        <small
          style={{
            display: 'block',
            marginBottom: '18px',
            color: '#6c756f',
          }}
        >
          The code expires after 10 minutes
          and can only be used once.
        </small>

        <button
          className="button dark large full"
          type="submit"
          disabled={busy}
        >
          {busy
            ? 'Authenticating…'
            : 'Complete sign in'}
        </button>

        <small>
          Didn't receive the code?{' '}

          <Link to="/login">
            Sign in again to request a new one
          </Link>
        </small>
      </form>
    </div>
  )
}