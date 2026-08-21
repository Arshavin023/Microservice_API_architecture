import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Trash2, ShoppingBag, Loader2, ExternalLink, ArrowRight } from 'lucide-react'
import { ordersApi } from '../api'

export default function Cart({ onCartUpdate }) {
  const navigate = useNavigate()
  const [cart,           setCart]           = useState(null)
  const [loading,        setLoading]        = useState(true)
  const [removing,       setRemoving]       = useState({})
  const [checkingOut,    setCheckingOut]    = useState(false)
  const [checkoutResult, setCheckoutResult] = useState(null)
  const [error,          setError]          = useState('')

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
      <Loader2 className="w-8 h-8 animate-spin text-[#FF6B35]" />
    </div>
  )

  const items = cart?.items ?? []
  const total = items.reduce((sum, item) => sum + parseFloat(item.unit_price ?? 0) * (item.quantity ?? 1), 0)

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold text-[#1A1A2E] mb-2">Your cart</h1>
      <p className="text-gray-500 mb-8">{items.length} item{items.length !== 1 ? 's' : ''}</p>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 text-sm mb-5">
          {error}
        </div>
      )}

      {/* Post-checkout state */}
      {checkoutResult && (
        <div className="card p-6 bg-green-50 border-green-200 mb-6">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-xl flex items-center justify-center text-xl">🎉</div>
            <div className="flex-1">
              <h2 className="font-bold text-green-800 mb-1">Order placed!</h2>
              <p className="text-sm text-green-700 mb-3">
                Order <code className="font-mono bg-green-100 px-1 rounded">{checkoutResult.id?.slice(0, 8)}…</code> is being processed.
              </p>
              <div className="flex gap-2 flex-wrap">
                {checkoutResult.authorization_url && (
                  <a
                    href={checkoutResult.authorization_url}
                    target="_blank"
                    rel="noreferrer"
                    className="btn-primary text-sm flex items-center gap-1.5"
                  >
                    Pay on Paystack <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                )}
                <button onClick={() => navigate('/orders')} className="btn-secondary text-sm">
                  View orders
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {items.length === 0 && !checkoutResult ? (
        <div className="text-center py-20">
          <span className="text-6xl">🛒</span>
          <p className="text-gray-500 mt-4 mb-6">Your cart is empty</p>
          <button onClick={() => navigate('/')} className="btn-primary">
            Browse menu
          </button>
        </div>
      ) : !checkoutResult && (
        <div className="space-y-4">
          {/* Items */}
          <div className="card divide-y divide-gray-50">
            {items.map(item => (
              <div key={item.id} className="flex items-center justify-between p-4">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">🍕</span>
                  <div>
                    <p className="font-semibold text-[#1A1A2E]">{item.product_name}</p>
                    <p className="text-sm text-gray-500 capitalize">{item.size} × {item.quantity}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="font-bold text-[#1A1A2E]">₦{(parseFloat(item.unit_price ?? 0) * (item.quantity ?? 1)).toFixed(2)}</span>
                  <button
                    onClick={() => removeItem(item.id)}
                    disabled={removing[item.id]}
                    className="text-gray-300 hover:text-red-500 transition-colors p-1"
                  >
                    {removing[item.id]
                      ? <Loader2 className="w-4 h-4 animate-spin" />
                      : <Trash2 className="w-4 h-4" />
                    }
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Summary */}
          <div className="card p-5">
            <div className="flex justify-between items-center mb-1">
              <span className="text-gray-500 text-sm">Subtotal</span>
              <span className="font-semibold">₦{total.toFixed(2)}</span>
            </div>
            <div className="flex justify-between items-center mb-5">
              <span className="text-gray-500 text-sm">Delivery</span>
              <span className="text-green-600 text-sm font-medium">Free</span>
            </div>
            <div className="flex justify-between items-center mb-5 pt-3 border-t border-gray-100">
              <span className="font-bold text-[#1A1A2E]">Total</span>
              <span className="text-2xl font-bold text-[#FF6B35]">₦{total.toFixed(2)}</span>
            </div>
            <button
              onClick={checkout}
              disabled={checkingOut || items.length === 0}
              className="btn-primary w-full flex items-center justify-center gap-2 py-3"
            >
              {checkingOut
                ? <Loader2 className="w-4 h-4 animate-spin" />
                : <ArrowRight className="w-4 h-4" />
              }
              {checkingOut ? 'Processing…' : 'Place order'}
            </button>
            <p className="text-xs text-gray-400 text-center mt-3">
              You'll be redirected to Paystack to complete payment
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
