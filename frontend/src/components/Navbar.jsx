import { Link, useNavigate, useLocation } from 'react-router-dom'
import { ShoppingBag, User, LogOut, Pizza, ChefHat, Package } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function Navbar({ cartCount = 0 }) {
  const { isAuthenticated, username, isStaff, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => { logout(); navigate('/login') }

  const isActive = (path) => location.pathname === path

  return (
    <nav className="bg-white border-b border-gray-100 sticky top-0 z-50 shadow-sm">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">

        {/* Logo */}
        <Link to="/" className="flex items-center gap-2.5">
          <div className="w-9 h-9 bg-[#FF6B35] rounded-xl flex items-center justify-center">
            <Pizza className="w-5 h-5 text-white" />
          </div>
          <span className="font-display font-bold text-xl text-[#1A1A2E]">Pizzasale</span>
        </Link>

        {/* Nav links — desktop */}
        <div className="hidden md:flex items-center gap-1">
          <Link to="/" className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            isActive('/') ? 'bg-orange-50 text-[#FF6B35]' : 'text-gray-600 hover:text-[#1A1A2E] hover:bg-gray-50'
          }`}>Menu</Link>
          {isAuthenticated && (
            <Link to="/orders" className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              isActive('/orders') ? 'bg-orange-50 text-[#FF6B35]' : 'text-gray-600 hover:text-[#1A1A2E] hover:bg-gray-50'
            }`}>My Orders</Link>
          )}
          {isStaff && (
            <Link to="/staff" className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5 ${
              isActive('/staff') ? 'bg-orange-50 text-[#FF6B35]' : 'text-gray-600 hover:text-[#1A1A2E] hover:bg-gray-50'
            }`}>
              <ChefHat className="w-4 h-4" />
              Staff
            </Link>
          )}
        </div>

        {/* Right actions */}
        <div className="flex items-center gap-2">
          {isAuthenticated ? (
            <>
              {/* Cart button */}
              <Link to="/cart" className="relative flex items-center gap-2 bg-[#1A1A2E] hover:bg-[#2d2d4e] text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors">
                <ShoppingBag className="w-4 h-4" />
                <span className="hidden sm:inline">Cart</span>
                {cartCount > 0 && (
                  <span className="absolute -top-2 -right-2 bg-[#FF6B35] text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                    {cartCount > 9 ? '9+' : cartCount}
                  </span>
                )}
              </Link>

              {/* Profile */}
              <Link to="/profile" className="flex items-center gap-2 btn-ghost text-sm">
                <div className="w-7 h-7 bg-orange-100 rounded-full flex items-center justify-center">
                  <User className="w-3.5 h-3.5 text-[#FF6B35]" />
                </div>
                <span className="hidden sm:inline text-sm font-medium">{username}</span>
              </Link>

              {/* Logout */}
              <button onClick={handleLogout} className="btn-ghost text-gray-400 hover:text-red-500">
                <LogOut className="w-4 h-4" />
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn-secondary text-sm">Log in</Link>
              <Link to="/register" className="btn-primary text-sm">Sign up</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
