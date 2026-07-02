import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Trash2, ShoppingCart, Loader2, ExternalLink } from 'lucide-react'
import { ordersApi } from '../api'

export default function Cart({ onCartUpdate }) {
  const navigate = useNavigate()
  const [cart, setCart] = useState(null)
  const [loading, setLoading] = useState(true)
  const [removing, setRemoving] = useState({})
  const [checkingOut, setCheckingOut] = useState(false)
  const [checkoutResult, setCheckoutResult] = useState(null)
  const [error, setError] = useState('')

  const fetchCart = async () => {
    try {
      const res = await ordersApi.getCart()
      setCart(res.data)
    } catch {
      setError('Could not load cart.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchCart() }, [])

  const removeItem = async (itemId) => {
    setRemoving(r => ({ ...r, [itemId]: true }))
    try {
      await ordersApi.removeFromCart(itemId)
      await fetchCart()
      onCartUpdate?.()
    } catch {
      setError('Could not remove item.')
    } finally {
      setRemoving(r => ({ ...r, [itemId]: false }))
    }
  }

  const checkout = async () => {
    setCheckingOut(true)
    setError('')
    try {
      const res = await ordersApi.checkout()
      setCheckoutResult(res.data)
      onCartUpdate?.()
      // Open Paystack in a new tab so the user can complete payment
      if (res.data.authorization_url) {
        window.open(res.data.authorization_url, '_blank')
      }
    } catch (err) {
      const detail = err.response?.data?.detail
      setError(typeof detail === 'string' ? detail : 'Checkout failed. Please try again.')
    } finally {
      setCheckingOut(false)
    }
  }

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 className="w-8 h-8 animate-spin text-brand-500" />
    </div>
  )

  const items = cart?.items ?? []
  const total = items.reduce((sum, item) => sum + parseFloat(item.subtotal), 0)

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold mb-8">Your cart</h1>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg p-3 text-sm mb-4">
          {error}
        </div>
      )}

      {/* Checkout result */}
      {checkoutResult && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-5 mb-6">
          <h2 className="font-semibold text-green-800 mb-1">Order placed!</h2>
          <p className="text-sm text-green-700">
            Order ID: <code className="font-mono text-xs">{checkoutResult.id}</code>
          </p>
          <p className="text-sm text-green-700">Status: {checkoutResult.status}</p>
          {checkoutResult.authorization_url && (
            <a
              href={checkoutResult.authorization_url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 mt-3 btn-primary text-sm"
            >
              Complete payment on Paystack
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
          <button
            onClick={() => navigate('/orders')}
            className="mt-2 ml-3 btn-secondary text-sm"
          >
            View orders
          </button>
        </div>
      )}

      {items.length === 0 && !checkoutResult ? (
        <div className="text-center py-20 text-gray-400">
          <ShoppingCart className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p className="text-gray-500">Your cart is empty.</p>
          <button onClick={() => navigate('/')} className="btn-primary mt-4">Browse menu</button>
        </div>
      ) : (
        !checkoutResult && (
          <div className="card divide-y divide-gray-50">
            {items.map(item => (
              <div key={item.id} className="flex items-center justify-between p-4">
                <div>
                  <p className="font-medium">{item.product_name}</p>
                  <p className="text-sm text-gray-500 capitalize">{item.size} × {item.quantity}</p>
                </div>
                <div className="flex items-center gap-4">
                  <span className="font-medium">₦{parseFloat(item.subtotal).toFixed(2)}</span>
                  <button
                    onClick={() => removeItem(item.id)}
                    disabled={removing[item.id]}
                    className="text-gray-400 hover:text-red-500 transition-colors"
                  >
                    {removing[item.id]
                      ? <Loader2 className="w-4 h-4 animate-spin" />
                      : <Trash2 className="w-4 h-4" />
                    }
                  </button>
                </div>
              </div>
            ))}

            <div className="p-4 flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total</p>
                <p className="text-xl font-bold">₦{total.toFixed(2)}</p>
              </div>
              <button
                onClick={checkout}
                disabled={checkingOut || items.length === 0}
                className="btn-primary flex items-center gap-2"
              >
                {checkingOut && <Loader2 className="w-4 h-4 animate-spin" />}
                Checkout
              </button>
            </div>
          </div>
        )
      )}
    </div>
  )
}
