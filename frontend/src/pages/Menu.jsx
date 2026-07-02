import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ShoppingCart, Loader2, Pizza } from 'lucide-react'
import { productsApi, ordersApi } from '../api'
import { useAuth } from '../context/AuthContext'

const STATUS_COLORS = {
  pending_payment: 'bg-yellow-100 text-yellow-700',
  confirmed:       'bg-blue-100 text-blue-700',
  paid:            'bg-green-100 text-green-700',
  shipped:         'bg-purple-100 text-purple-700',
  delivered:       'bg-gray-100 text-gray-700',
  cancelled:       'bg-red-100 text-red-700',
}

export default function Menu({ onCartUpdate }) {
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [categories, setCategories] = useState([])
  const [products, setProducts] = useState([])
  const [selected, setSelected] = useState(null) // selected category
  const [loading, setLoading] = useState(true)
  const [adding, setAdding] = useState({}) // { [variantId]: bool }
  const [toast, setToast] = useState('')

  useEffect(() => {
    Promise.all([
      productsApi.listCategories(),
      productsApi.listProducts(),
    ]).then(([catRes, prodRes]) => {
      setCategories(catRes.data)
      setProducts(prodRes.data)
    }).finally(() => setLoading(false))
  }, [])

  const filterByCategory = async (catId) => {
    setSelected(catId)
    const res = await productsApi.listProducts(catId)
    setProducts(res.data)
  }

  const addToCart = async (product, variant) => {
    if (!isAuthenticated) { navigate('/login'); return }
    setAdding(a => ({ ...a, [variant.id]: true }))
    try {
      await ordersApi.addToCart({
        product_id: product.id,
        variant_id: variant.id,
        product_name: product.name,
        size: variant.size,
        unit_price: parseFloat(variant.price),
        quantity: 1,
      })
      setToast(`${product.name} (${variant.size}) added to cart`)
      onCartUpdate?.()
      setTimeout(() => setToast(''), 2500)
    } catch {
      setToast('Could not add to cart. Please try again.')
      setTimeout(() => setToast(''), 2500)
    } finally {
      setAdding(a => ({ ...a, [variant.id]: false }))
    }
  }

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 className="w-8 h-8 animate-spin text-brand-500" />
    </div>
  )

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      {/* Hero */}
      <div className="mb-10">
        <h1 className="text-4xl font-bold text-gray-900">
          Fresh from the oven 🍕
        </h1>
        <p className="text-gray-500 mt-2">
          Handcrafted pizzas, delivered fast. Browse the menu and order in seconds.
        </p>
      </div>

      {/* Category filter */}
      <div className="flex gap-2 mb-8 flex-wrap">
        <button
          onClick={() => filterByCategory(null)}
          className={`px-4 py-1.5 rounded-full text-sm font-medium border transition-colors ${
            !selected ? 'bg-brand-600 text-white border-brand-600' : 'bg-white text-gray-600 border-gray-200 hover:border-brand-400'
          }`}
        >
          All
        </button>
        {categories.map(cat => (
          <button
            key={cat.id}
            onClick={() => filterByCategory(cat.id)}
            className={`px-4 py-1.5 rounded-full text-sm font-medium border transition-colors ${
              selected === cat.id ? 'bg-brand-600 text-white border-brand-600' : 'bg-white text-gray-600 border-gray-200 hover:border-brand-400'
            }`}
          >
            {cat.name}
          </button>
        ))}
      </div>

      {/* Product grid */}
      {products.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <Pizza className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p>No pizzas in this category yet.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map(product => (
            <div key={product.id} className="card p-6 flex flex-col">
              <div className="flex-1">
                <h3 className="font-semibold text-lg text-gray-900">{product.name}</h3>
                {product.description && (
                  <p className="text-gray-500 text-sm mt-1 leading-relaxed">{product.description}</p>
                )}
              </div>

              <div className="mt-4 space-y-2">
                {product.variants?.map(variant => (
                  <div key={variant.id} className="flex items-center justify-between">
                    <div>
                      <span className="text-sm font-medium capitalize text-gray-700">{variant.size}</span>
                      <span className="text-sm text-gray-500 ml-2">₦{parseFloat(variant.price).toFixed(2)}</span>
                    </div>
                    <button
                      onClick={() => addToCart(product, variant)}
                      disabled={adding[variant.id]}
                      className="flex items-center gap-1.5 text-sm btn-primary py-1.5 px-3"
                    >
                      {adding[variant.id]
                        ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        : <ShoppingCart className="w-3.5 h-3.5" />
                      }
                      Add
                    </button>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Toast */}
      {toast && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-gray-900 text-white px-5 py-3 rounded-xl shadow-lg text-sm z-50 transition-all">
          {toast}
        </div>
      )}
    </div>
  )
}
