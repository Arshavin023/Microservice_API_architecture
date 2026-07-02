import { useState, useEffect } from 'react'
import { Loader2, Save } from 'lucide-react'
import { usersApi } from '../api'
import { useAuth } from '../context/AuthContext'

export default function Profile() {
  const { userId } = useAuth()
  const [profile, setProfile] = useState(null)
  const [form, setForm] = useState({ full_name: '', delivery_address: '' })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    usersApi.getProfile(userId)
      .then(res => {
        setProfile(res.data)
        setForm({
          full_name: res.data.full_name ?? '',
          delivery_address: res.data.delivery_address ?? '',
        })
      })
      .catch(() => setError('Could not load profile.'))
      .finally(() => setLoading(false))
  }, [userId])

  const save = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      const res = await usersApi.updateProfile(userId, form)
      setProfile(res.data)
      setSuccess('Profile updated.')
      setTimeout(() => setSuccess(''), 2500)
    } catch {
      setError('Could not update profile.')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 className="w-8 h-8 animate-spin text-brand-500" />
    </div>
  )

  return (
    <div className="max-w-xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold mb-8">Profile</h1>

      {success && (
        <div className="bg-green-50 border border-green-200 text-green-700 rounded-lg p-3 text-sm mb-4">
          {success}
        </div>
      )}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-3 text-sm mb-4">
          {error}
        </div>
      )}

      <div className="card p-6 mb-6">
        <p className="text-sm text-gray-500 mb-1">Username</p>
        <p className="font-medium">{profile?.username}</p>
        <p className="text-sm text-gray-500 mt-3 mb-1">Email</p>
        <p className="font-medium">{profile?.email}</p>
        <p className="text-sm text-gray-500 mt-3 mb-1">User ID</p>
        <p className="font-mono text-xs text-gray-400">{profile?.user_id}</p>
      </div>

      <form onSubmit={save} className="card p-6 space-y-4">
        <h2 className="font-semibold text-gray-800">Edit details</h2>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Full name</label>
          <input
            className="input"
            value={form.full_name}
            onChange={e => setForm(f => ({ ...f, full_name: e.target.value }))}
            placeholder="Uche Nnodim"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Delivery address</label>
          <input
            className="input"
            value={form.delivery_address}
            onChange={e => setForm(f => ({ ...f, delivery_address: e.target.value }))}
            placeholder="Abuja, FCT"
          />
        </div>
        <button type="submit" className="btn-primary flex items-center gap-2" disabled={saving}>
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          Save changes
        </button>
      </form>
    </div>
  )
}
