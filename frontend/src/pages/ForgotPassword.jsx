import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Loader2, Pizza } from 'lucide-react'
import { authApi } from '../api'

export default function ForgotPassword() {
  const [email,   setEmail]   = useState('')
  const [loading, setLoading] = useState(false)
  const [sent,    setSent]    = useState(false)
  const [error,   setError]   = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true); setError('')
    try {
      await authApi.forgotPassword({ email })
      setSent(true)
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="card w-full max-w-sm p-8">
        <div className="text-center mb-8">
          <div className="w-12 h-12 bg-[#FF6B35] rounded-xl flex items-center justify-center mx-auto mb-3">
            <Pizza className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-[#1A1A2E]">Forgot password?</h1>
          <p className="text-gray-500 text-sm mt-1">
            Enter your email and we'll send a reset link
          </p>
        </div>

        {sent ? (
          <div className="bg-green-50 border border-green-200 rounded-xl p-5 text-center">
            <p className="text-2xl mb-2">📬</p>
            <p className="font-semibold text-green-800">Check your email</p>
            <p className="text-sm text-green-700 mt-1">
              If <strong>{email}</strong> is registered, a reset link has been sent.
              The link expires in 1 hour.
            </p>
            <Link to="/login" className="btn-primary text-sm mt-4 inline-block">
              Back to login
            </Link>
          </div>
        ) : (
          <>
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-3 text-sm mb-4">
                {error}
              </div>
            )}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email address
                </label>
                <input
                  className="input"
                  type="email"
                  required
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  autoFocus
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                {loading && <Loader2 className="w-4 h-4 animate-spin" />}
                Send reset link
              </button>
            </form>
            <p className="text-center text-sm text-gray-500 mt-6">
              Remember your password?{' '}
              <Link to="/login" className="text-[#FF6B35] font-medium hover:underline">
                Log in
              </Link>
            </p>
          </>
        )}
      </div>
    </div>
  )
}
