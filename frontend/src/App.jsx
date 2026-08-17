import { useState, useEffect, useCallback } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'
import Menu from './pages/Menu'
import Login from './pages/Login'
import Register from './pages/Register'
import Cart from './pages/Cart'
import { Orders, OrderDetail } from './pages/Orders'
import Profile from './pages/Profile'
import StaffDashboard from './pages/StaffDashboard'
import { ordersApi } from './api'
import { useAuth } from './context/AuthContext'

function AppShell() {
  const { isAuthenticated } = useAuth()
  const [cartCount, setCartCount] = useState(0)

  const refreshCartCount = useCallback(async () => {
    if (!isAuthenticated) { setCartCount(0); return }
    try {
      const res = await ordersApi.getCart()
      setCartCount(res.data?.items?.length ?? 0)
    } catch {
      setCartCount(0)
    }
  }, [isAuthenticated])

  useEffect(() => { refreshCartCount() }, [refreshCartCount])

  return (
    <div className="min-h-screen bg-[#FFF8F0]">
      <Navbar cartCount={cartCount} />
      <Routes>
        <Route path="/"          element={<Menu onCartUpdate={refreshCartCount} />} />
        <Route path="/login"     element={<Login />} />
        <Route path="/register"  element={<Register />} />
        <Route path="/cart"      element={<ProtectedRoute><Cart onCartUpdate={refreshCartCount} /></ProtectedRoute>} />
        <Route path="/orders"    element={<ProtectedRoute><Orders /></ProtectedRoute>} />
        <Route path="/orders/:id" element={<ProtectedRoute><OrderDetail /></ProtectedRoute>} />
        <Route path="/profile"   element={<ProtectedRoute><Profile /></ProtectedRoute>} />
        <Route path="/staff"     element={<ProtectedRoute><StaffDashboard /></ProtectedRoute>} />
        <Route path="*"          element={<Navigate to="/" replace />} />
      </Routes>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppShell />
      </AuthProvider>
    </BrowserRouter>
  )
}
