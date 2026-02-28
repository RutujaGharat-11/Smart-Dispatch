'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import styles from './Login.module.css'

export default function LoginPage() {
  const router = useRouter()
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [rememberMe, setRememberMe] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [selectedRole, setSelectedRole] = useState('USER')
  const [isCheckingAuth, setIsCheckingAuth] = useState(true)

  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'

  useEffect(() => {
    let isMounted = true

    const checkExistingSession = async () => {
      try {
        const response = await fetch(`${apiBaseUrl}/api/check-auth`, {
          method: 'GET',
          credentials: 'include',
        })

        if (response.status === 401) {
          if (isMounted) {
            setIsCheckingAuth(false)
          }
          return
        }

        if (!response.ok) {
          if (isMounted) {
            setIsCheckingAuth(false)
          }
          return
        }

        const data = await response.json().catch(() => ({}))

        if (data.role === 'ADMIN') {
          router.replace('/dashboard')
          return
        }

        if (data.role === 'USER') {
          router.replace('/user-dashboard')
          return
        }

        if (isMounted) {
          setIsCheckingAuth(false)
        }
      } catch {
        if (isMounted) {
          setIsCheckingAuth(false)
        }
      }
    }

    checkExistingSession()

    return () => {
      isMounted = false
    }
  }, [apiBaseUrl, router])

  const handleSubmit = async (event) => {
    event.preventDefault()
    setIsSubmitting(true)
    setErrorMessage('')

    try {
      const response = await fetch(`${apiBaseUrl}/api/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          username: identifier.trim(),
          password: password.trim(),
          selected_role: selectedRole,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        setErrorMessage(errorData.error || 'Invalid login credentials. Please try again.')
        return
      }

      const data = await response.json().catch(() => ({}))
      if (data.role === 'ADMIN') {
        router.push('/dashboard')
      } else if (data.role === 'USER') {
        router.push('/user-dashboard')
      } else {
        router.push('/user-dashboard') // Fallback just in case
      }
    } catch {
      setErrorMessage('Unable to reach the server. Please check if backend is running.')
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isCheckingAuth) {
    return (
      <section className={styles.page}>
        <div className={styles.card}>
          <div className={styles.cardInner}>
            <p className={styles.subtitle}>Checking session...</p>
          </div>
        </div>
      </section>
    )
  }

  return (
    <section className={styles.page}>
      <div className={styles.card}>
        <div className={styles.cardInner}>
          <h1 className={styles.title}>Login</h1>
          <p className={styles.subtitle}>Authorized personnel access only</p>

          <div className={styles.toggleContainer}>
            <div
              className={`${styles.toggleOption} ${selectedRole === 'USER' ? styles.toggleOptionActive : ''}`}
              onClick={() => setSelectedRole('USER')}
            >
              USER
            </div>
            <div
              className={`${styles.toggleOption} ${selectedRole === 'ADMIN' ? styles.toggleOptionActive : ''}`}
              onClick={() => setSelectedRole('ADMIN')}
            >
              ADMIN
            </div>
          </div>

          <div className={`${styles.alert} ${errorMessage ? '' : styles.hidden}`} role="alert">
            {errorMessage}
          </div>

          <form onSubmit={handleSubmit} className={styles.form}>
            <div className={styles.field}>
              <label htmlFor="identifier" className={styles.label}>
                Username or Email
              </label>
              <input
                id="identifier"
                type="text"
                className={styles.input}
                value={identifier}
                onChange={(event) => setIdentifier(event.target.value)}
                autoComplete="username"
                required
              />
            </div>

            <div className={styles.field}>
              <label htmlFor="password" className={styles.label}>
                Password
              </label>
              <input
                id="password"
                type="password"
                className={styles.input}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="current-password"
                required
              />
            </div>

            <div className={styles.rememberRow}>
              <input
                className={styles.checkbox}
                type="checkbox"
                id="rememberMe"
                checked={rememberMe}
                onChange={(event) => setRememberMe(event.target.checked)}
              />
              <label className={styles.rememberLabel} htmlFor="rememberMe">
                Remember me
              </label>
            </div>

            <button type="submit" className={styles.button} disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <span className={styles.spinner} aria-hidden="true" />
                  Signing in...
                </>
              ) : (
                'Login'
              )}
            </button>

            {selectedRole === 'USER' && (
              <p className={styles.signupText}>
                Don&apos;t have an account?{' '}
                <Link href="/create-account" className={styles.signupLink}>
                  Create Account
                </Link>
              </p>
            )}
          </form>
        </div>
      </div>
    </section>
  )
}
