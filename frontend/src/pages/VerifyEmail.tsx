import {
  useEffect,
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


type MessageResponse = {
  message: string
}


type EmailChangeResponse = {
  message: string
  email: string
}


export default function VerifyEmail() {
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

  const [message, setMessage] = useState('')

  const [busy, setBusy] = useState(false)

  const [resending, setResending] = useState(false)

  const [cooldown, setCooldown] = useState(0)

  const [editingEmail, setEditingEmail] =
    useState(false)

  const [newEmail, setNewEmail] =
    useState(email)

  const [password, setPassword] =
    useState('')

  const [changingEmail, setChangingEmail] =
    useState(false)


  useEffect(() => {
    setNewEmail(email)
  }, [email])


  useEffect(() => {
    if (cooldown <= 0) {
      return
    }

    const timer =
      window.setInterval(() => {
        setCooldown((current) => {
          if (current <= 1) {
            window.clearInterval(
              timer,
            )

            return 0
          }

          return current - 1
        })
      }, 1000)

    return () => {
      window.clearInterval(
        timer,
      )
    }
  }, [cooldown])


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


  async function verify(
    event: React.FormEvent,
  ) {
    event.preventDefault()

    if (!email) {
      setError(
        'Verification email is missing. Please register again.',
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
    setMessage('')

    try {
      await api<User>(
        '/auth/verify-registration',
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
      const errorMessage =
        err instanceof Error
          ? err.message
          : 'Unable to verify your email.'

      setError(
        errorMessage,
      )
    } finally {
      setBusy(false)
    }
  }


  async function resend() {
    if (!email) {
      setError(
        'Verification email is missing. Please register again.',
      )

      return
    }

    if (cooldown > 0) {
      return
    }

    setResending(true)
    setError('')
    setMessage('')

    try {
      const result =
        await api<MessageResponse>(
          '/auth/resend-registration-code',
          {
            method: 'POST',

            body: JSON.stringify({
              email,
            }),
          },
        )

      setMessage(
        `${result.message} Please also check your Spam or Junk folder if the message does not appear in your inbox.`,
      )

      setCooldown(60)

      setCode('')
    } catch (err) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : 'Unable to resend the verification code.'

      setError(
        errorMessage,
      )
    } finally {
      setResending(false)
    }
  }


  async function changeEmail(
    event: React.FormEvent,
  ) {
    event.preventDefault()

    const cleanNewEmail =
      newEmail
        .trim()
        .toLowerCase()

    if (!cleanNewEmail) {
      setError(
        'Enter your new email address.',
      )

      return
    }

    if (
      cleanNewEmail
      === email.toLowerCase()
    ) {
      setError(
        'Enter a different email address.',
      )

      return
    }

    if (!password) {
      setError(
        'Enter your AGP password to confirm the email change.',
      )

      return
    }

    setChangingEmail(true)

    setError('')

    setMessage('')

    try {
      const result =
        await api<EmailChangeResponse>(
          '/auth/change-registration-email',
          {
            method: 'POST',

            body: JSON.stringify({
              current_email: email,

              new_email:
                cleanNewEmail,

              password,
            }),
          },
        )

      setCode('')

      setPassword('')

      setEditingEmail(false)

      setCooldown(60)

      setMessage(
        `${result.message} Please check your Inbox, Spam or Junk folder for the new OTP.`,
      )

      navigate(
        `/verify-email?email=${encodeURIComponent(
          result.email,
        )}`,
        {
          replace: true,
        },
      )
    } catch (err) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : (
              'Unable to change '
              + 'your email address.'
            )

      setError(
        errorMessage,
      )
    } finally {
      setChangingEmail(false)
    }
  }


  if (!email) {
    return (
      <div className="auth-page">

        <div className="auth-card card">

          <div className="eyebrow dark">
            EMAIL VERIFICATION
          </div>

          <h1>
            Verification link incomplete.
          </h1>

          <p>
            We could not determine which
            email address should be
            verified.
          </p>

          <Link
            className="button dark large full"
            to="/register"
          >
            Return to registration
          </Link>

        </div>

      </div>
    )
  }


  return (
    <div className="auth-page">

      <div className="auth-card card">

        <div className="eyebrow dark">
          EMAIL VERIFICATION
        </div>

        <h1>
          Check your email.
        </h1>

        <p>
          We sent an 8-digit
          verification code to:
        </p>

        <div
          style={{
            fontWeight: 700,
            marginBottom: '8px',
            wordBreak: 'break-word',
          }}
        >
          {email}
        </div>

        <button
          type="button"
          onClick={() => {
            setEditingEmail(
              (current) => !current,
            )

            setError('')

            setMessage('')

            setNewEmail(email)

            setPassword('')
          }}
          style={{
            background: 'none',
            border: 0,
            padding: 0,
            marginBottom: '20px',
            textDecoration: 'underline',
            fontWeight: 700,
            fontSize: '12px',
          }}
        >
          {editingEmail
            ? 'Cancel email change'
            : 'Entered the wrong email? Change it'}
        </button>


        {editingEmail && (
          <form
            onSubmit={changeEmail}
            style={{
              background: '#f6f4ee',
              border: '1px solid #d8d3c7',
              padding: '18px',
              marginBottom: '22px',
            }}
          >

            <strong>
              Change verification email
            </strong>

            <p
              style={{
                fontSize: '12px',
                lineHeight: 1.6,
              }}
            >
              Enter the correct email
              address and confirm the
              change with the password
              you used when creating
              this account.
            </p>

            <label>
              New email address

              <input
                type="email"
                required
                value={newEmail}
                onChange={(event) =>
                  setNewEmail(
                    event.target.value,
                  )
                }
                autoComplete="email"
              />
            </label>

            <label>
              Confirm your password

              <input
                type="password"
                required
                value={password}
                onChange={(event) =>
                  setPassword(
                    event.target.value,
                  )
                }
                autoComplete="current-password"
              />
            </label>

            <button
              className="button dark full"
              type="submit"
              disabled={changingEmail}
            >
              {changingEmail
                ? 'Updating email…'
                : (
                    'Update email '
                    + '& send new OTP'
                  )}
            </button>

          </form>
        )}


        <div
          style={{
            background: '#fff7dd',
            border: '1px solid #e4c96f',
            padding: '14px 16px',
            marginBottom: '22px',
            fontSize: '13px',
            lineHeight: 1.6,
          }}
        >

          <strong>
            Can't find the email?
          </strong>

          <div
            style={{
              marginTop: '6px',
            }}
          >
            Please check your{' '}
            <strong>
              Spam or Junk folder
            </strong>.

            Depending on your email
            provider, the message may
            also appear under{' '}
            <strong>
              Promotions
            </strong>
            {' '}or{' '}
            <strong>
              Updates
            </strong>.
          </div>

        </div>


        {error && (
          <div className="alert error">
            {error}
          </div>
        )}


        {message && (
          <div
            className="alert"
            style={{
              background: '#eef4e8',
              color: '#334a2e',
            }}
          >
            {message}
          </div>
        )}


        {!editingEmail && (
          <form onSubmit={verify}>

            <p>
              Enter the code below
              to activate your AGP
              account.
            </p>

            <label>
              Verification code

              <input
                type="text"
                inputMode="numeric"
                autoComplete="one-time-code"
                value={code}
                onChange={changeCode}
                placeholder="00000000"
                maxLength={8}
                required
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
              The verification code
              expires after 10 minutes
              and can only be used once.
            </small>

            <button
              className="button dark large full"
              type="submit"
              disabled={busy}
            >
              {busy
                ? 'Verifying…'
                : 'Verify account'}
            </button>


            <button
              className="button ghost large full"
              type="button"
              onClick={resend}
              disabled={
                resending
                || cooldown > 0
              }
              style={{
                marginTop: '10px',
              }}
            >
              {resending
                ? 'Sending…'
                : cooldown > 0
                  ? (
                      `Resend available in `
                      + `${cooldown}s`
                    )
                  : (
                      'Resend verification '
                      + 'code'
                    )}
            </button>

          </form>
        )}


        <small
          style={{
            display: 'block',
            textAlign: 'center',
            marginTop: '20px',
          }}
        >
          Need to start over?{' '}

          <Link to="/register">
            Return to registration
          </Link>
        </small>

      </div>

    </div>
  )
}