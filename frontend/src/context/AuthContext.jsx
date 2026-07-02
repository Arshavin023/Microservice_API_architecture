import { createContext, useContext, useState, useCallback } from 'react'
import { authApi } from '../api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [userId, setUserId] = useState(() => localStorage.getItem('user_id'))
  const [username, setUsername] = useState(() => localStorage.getItem('username'))
  const isAuthenticated = !!userId

  const login = useCallback(async (credentials) => {
    const res = await authApi.login(credentials)
    const { access } = res.data

    // Decode user_id from JWT payload (no crypto needed — just base64)
    const payload = JSON.parse(atob(access.split('.')[1]))
    localStorage.setItem('access_token', access)
    localStorage.setItem('user_id', payload.user_id)
    localStorage.setItem('username', payload.sub)
    setUserId(payload.user_id)
    setUsername(payload.sub)
    return payload
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_id')
    localStorage.removeItem('username')
    setUserId(null)
    setUsername(null)
  }, [])

  return (
    <AuthContext.Provider value={{ userId, username, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
