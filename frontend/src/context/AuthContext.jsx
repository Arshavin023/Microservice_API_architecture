import { createContext, useContext, useState, useCallback } from 'react'
import { authApi } from '../api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [userId,   setUserId]   = useState(() => localStorage.getItem('user_id'))
  const [username, setUsername] = useState(() => localStorage.getItem('username'))
  const [isStaff,  setIsStaff]  = useState(() => localStorage.getItem('is_staff') === 'true')
  const isAuthenticated = !!userId

  const login = useCallback(async (credentials) => {
    const res = await authApi.login(credentials)
    const { access } = res.data
    const payload = JSON.parse(atob(access.split('.')[1]))
    localStorage.setItem('access_token', access)
    localStorage.setItem('user_id',  payload.user_id)
    localStorage.setItem('username', payload.sub)
    localStorage.setItem('is_staff', payload.is_staff ? 'true' : 'false')
    setUserId(payload.user_id)
    setUsername(payload.sub)
    setIsStaff(!!payload.is_staff)
    return payload
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_id')
    localStorage.removeItem('username')
    localStorage.removeItem('is_staff')
    setUserId(null)
    setUsername(null)
    setIsStaff(false)
  }, [])

  return (
    <AuthContext.Provider value={{ userId, username, isAuthenticated, isStaff, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
