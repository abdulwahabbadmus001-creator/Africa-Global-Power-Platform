import {
  Navigate,
} from 'react-router-dom'

import { useAuth } from '../lib/auth'

import type {
  Role,
} from '../types'


const EDITORIAL_ROLES: Role[] = [
  'reviewer',
  'editor',
  'senior_editor',
  'managing_editor',
  'super_admin',
]


export default function Protected({
  children,
  roles,
}: {
  children: React.ReactNode
  roles?: Role[]
}) {
  const {
    user,
    loading,
  } = useAuth()

  if (loading) {
    return (
      <div className="page narrow">
        <div className="skeleton card">
          Loading account…
        </div>
      </div>
    )
  }

  const editorialRoute =
    Boolean(
      roles?.some(
        (role) =>
          EDITORIAL_ROLES.includes(
            role,
          ),
      ),
    )

  if (!user) {
    return (
      <Navigate
        to={
          editorialRoute
            ? '/editorial/login'
            : '/login'
        }
        replace
      />
    )
  }

  if (
    roles
    && !roles.includes(user.role)
  ) {
    return (
      <Navigate
        to="/dashboard"
        replace
      />
    )
  }

  return (
    <>
      {children}
    </>
  )
}