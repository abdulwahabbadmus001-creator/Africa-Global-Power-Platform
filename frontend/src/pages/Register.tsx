import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api } from '../lib/api'

type RegistrationResponse = {
  message: string
  email: string
  requires_verification: boolean
}

export default function Register() {
  const navigate = useNavigate()

  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    country: '',
    institution: '',
    requested_role: 'researcher',
  })

  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  function change(
    event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) {
    const { name, value } = event.target

    setForm((current) => ({
      ...current,
      [name]: value,
    }))
  }

  async function submit(event: React.FormEvent) {
    event.preventDefault()

    setBusy(true)
    setError('')

    try {
      const result = await api<RegistrationResponse>('/auth/register', {
        method: 'POST',
        body: JSON.stringify(form),
      })

      navigate(
        `/verify-email?email=${encodeURIComponent(result.email)}`,
      )
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : 'Unable to create account.'

      setError(message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-page">
      <form className="auth-card wide card" onSubmit={submit}>
        <div className="eyebrow dark">
          JOIN THE NETWORK
        </div>

        <h1>Create your AGP account.</h1>

        <p>
          Create your researcher profile and verify your email before
          accessing your workspace.
        </p>

        {error && (
          <div className="alert error">
            {error}
          </div>
        )}

        <div className="form-grid">
          <label>
            First name

            <input
              name="first_name"
              required
              minLength={2}
              value={form.first_name}
              onChange={change}
              autoComplete="given-name"
            />
          </label>

          <label>
            Last name

            <input
              name="last_name"
              required
              minLength={2}
              value={form.last_name}
              onChange={change}
              autoComplete="family-name"
            />
          </label>

          <label>
            Email

            <input
              name="email"
              type="email"
              required
              value={form.email}
              onChange={change}
              autoComplete="email"
            />
          </label>

          <label>
            Country

            <input
              name="country"
              value={form.country}
              onChange={change}
              autoComplete="country-name"
            />
          </label>

          <label className="span-2">
            Institution / organisation

            <input
              name="institution"
              value={form.institution}
              onChange={change}
            />
          </label>

          <label>
            Password

            <input
              name="password"
              type="password"
              required
              minLength={10}
              maxLength={128}
              value={form.password}
              onChange={change}
              autoComplete="new-password"
            />

            <small>
              Minimum 10 characters.
            </small>
          </label>

          <label>
            Account type

            <select
              name="requested_role"
              value={form.requested_role}
              onChange={change}
            >
              <option value="researcher">
                Researcher
              </option>

              <option value="contributor">
                Contributor
              </option>

              <option value="reader">
                Reader
              </option>
            </select>
          </label>
        </div>

        <button
          className="button lime dark-text large full"
          disabled={busy}
          type="submit"
        >
          {busy
            ? 'Creating account…'
            : 'Create account'}
        </button>

        <small>
          Already registered?{' '}
          <Link to="/login">
            Sign in
          </Link>
        </small>
      </form>
    </div>
  )
}