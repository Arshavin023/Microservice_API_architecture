import { Link, useNavigate } from 'react-router-dom'
import { ShoppingCart, User, LogOut, Pizza } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function Navbar({ cartCount = 0 }) {
  const { isAuthenticated, username, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <nav className="bg-white border-b border-gray-100 sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 font-bold text-xl text-brand-600">
          <Pizza className="w-6 h-6" />
          Pizzasale
        </Link>

        <div className="flex items-center gap-2">
          {isAuthenticated ? (
            <>
              <Link to="/cart" className="relative btn-secondary flex items-center gap-2">
                <ShoppingCart className="w-4 h-4" />
                Cart
                {cartCount > 0 && (
                  <span className="absolute -top-1.5 -right-1.5 bg-brand-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {cartCount}
                  </span>
                )}
              </Link>
              <Link to="/orders" className="btn-secondary flex items-center gap-2">
                Orders
              </Link>
              <Link to="/profile" className="btn-secondary flex items-center gap-2">
                <User className="w-4 h-4" />
                {username}
              </Link>
              <button onClick={handleLogout} className="btn-secondary flex items-center gap-2 text-red-600 hover:text-red-700">
                <LogOut className="w-4 h-4" />
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn-secondary">Log in</Link>
              <Link to="/register" className="btn-primary">Sign up</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
