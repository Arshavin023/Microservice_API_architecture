import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ShoppingBag, Loader2, Star, Clock, ChevronRight } from 'lucide-react'
import { productsApi, ordersApi } from '../api'
import { useAuth } from '../context/AuthContext'

const PIZZA_EMOJI = { classic: '🍕', vegetarian: '🥦', meat: '🥩', special: '⭐' }

export default function Menu({ onCartUpdate }) {
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [categories, setCategories]   = useState([])
  const [products,   setProducts]     = useState([])
  const [selected,   setSelected]     = useState(null)
  const [loading,    setLoading]      = useState(true)
  const [adding,     setAdding]       = useState({})
  const [toast,      setToast]        = useState('')
  const [toastType,  setToastType]    = useState('success')

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

  const showToast = (msg, type = 'success') => {
    setToast(msg)
    setToastType(type)
    setTimeout(() => setToast(''), 2500)
  }

  const addToCart = async (product, variant) => {
    if (!isAuthenticated) { navigate('/login'); return }
    setAdding(a => ({ ...a, [variant.id]: true }))
    try {
      await ordersApi.addToCart({
        product_id:   product.id,
        variant_id:   variant.id,
        product_name: product.name,
        size:         variant.size,
        unit_price:   parseFloat(variant.price),
        quantity:     1,
      })
      showToast(`${product.name} added to cart 🛒`)
      onCartUpdate?.()
    } catch {
      showToast('Could not add to cart', 'error')
    } finally {
      setAdding(a => ({ ...a, [variant.id]: false }))
    }
  }

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 className="w-8 h-8 animate-spin text-[#FF6B35]" />
    </div>
  )

  return (
    <div className="min-h-screen bg-[#FFF8F0]">
      {/* Hero */}
      <div className="bg-[#1A1A2E] text-white">
        <div className="max-w-6xl mx-auto px-4 py-14 flex flex-col md:flex-row items-center gap-8">
          <div className="flex-1">
            <p className="text-[#FF6B35] font-semibold text-sm uppercase tracking-wider mb-3">Fresh from the oven</p>
            <h1 className="font-display text-4xl md:text-5xl font-bold leading-tight mb-4">
              Handcrafted pizzas,<br />
              <span className="text-[#FF6B35]">delivered fast.</span>
            </h1>
            <p className="text-gray-400 mb-6 max-w-md">
              Choose from our wood-fired selection. Order in seconds, track in real time.
            </p>
            <div className="flex items-center gap-6 text-sm">
              <div className="flex items-center gap-1.5 text-gray-300">
                <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
                <span>4.8 rating</span>
              </div>
              <div className="flex items-center gap-1.5 text-gray-300">
                <Clock className="w-4 h-4 text-[#FF6B35]" />
                <span>20–35 min delivery</span>
              </div>
            </div>
          </div>
          <div className="text-8xl select-none hidden md:block">🍕</div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Category pills */}
        <div className="flex gap-2 mb-8 overflow-x-auto pb-2 scrollbar-hide">
          <button
            onClick={() => filterByCategory(null)}
            className={`pill whitespace-nowrap flex-shrink-0 ${!selected ? 'pill-active' : 'pill-inactive'}`}
          >
            🍕 All pizzas
          </button>
          {categories.map(cat => (
            <button
              key={cat.id}
              onClick={() => filterByCategory(cat.id)}
              className={`pill whitespace-nowrap flex-shrink-0 ${selected === cat.id ? 'pill-active' : 'pill-inactive'}`}
            >
              {PIZZA_EMOJI[cat.name?.toLowerCase()] ?? '🍕'} {cat.name}
            </button>
          ))}
        </div>

        {/* Section header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-[#1A1A2E]">
            {selected ? categories.find(c => c.id === selected)?.name : 'All pizzas'}
            <span className="text-gray-400 font-normal text-base ml-2">({products.length})</span>
          </h2>
        </div>

        {/* Product grid */}
        {products.length === 0 ? (
          <div className="text-center py-20 text-gray-400">
            <span className="text-5xl">🍕</span>
            <p className="mt-4 text-gray-500">No pizzas in this category yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {products.map(product => (
              <ProductCard
                key={product.id}
                product={product}
                adding={adding}
                onAdd={addToCart}
              />
            ))}
          </div>
        )}
      </div>

      {/* Toast */}
      {toast && (
        <div className={`fixed bottom-6 left-1/2 -translate-x-1/2 px-5 py-3 rounded-2xl shadow-float text-sm font-medium z-50 transition-all ${
          toastType === 'error' ? 'bg-red-600 text-white' : 'bg-[#1A1A2E] text-white'
        }`}>
          {toast}
        </div>
      )}
    </div>
  )
}

function ProductCard({ product, adding, onAdd }) {
  const [selectedSize, setSelectedSize] = useState(0)
  const variants = product.variants ?? []
  const variant  = variants[selectedSize]

  if (!variant) return null

  return (
    <div className="card overflow-hidden hover:shadow-card transition-shadow group">
      {/* Image placeholder with gradient */}
      <div className="h-44 bg-gradient-to-br from-orange-50 to-amber-100 flex items-center justify-center relative">
        <span className="text-7xl group-hover:scale-110 transition-transform duration-300">🍕</span>
        {product.is_available === false && (
          <div className="absolute inset-0 bg-white/70 flex items-center justify-center">
            <span className="text-sm font-semibold text-gray-500">Unavailable</span>
          </div>
        )}
      </div>

      <div className="p-4">
        <h3 className="font-bold text-[#1A1A2E] text-lg mb-1">{product.name}</h3>
        {product.description && (
          <p className="text-gray-500 text-sm mb-3 line-clamp-2">{product.description}</p>
        )}

        {/* Size selector */}
        {variants.length > 1 && (
          <div className="flex gap-1.5 mb-4">
            {variants.map((v, i) => (
              <button
                key={v.id}
                onClick={() => setSelectedSize(i)}
                className={`px-3 py-1 rounded-lg text-xs font-semibold border transition-all capitalize ${
                  selectedSize === i
                    ? 'bg-[#1A1A2E] text-white border-[#1A1A2E]'
                    : 'border-gray-200 text-gray-600 hover:border-gray-400'
                }`}
              >
                {v.size}
              </button>
            ))}
          </div>
        )}

        <div className="flex items-center justify-between">
          <div>
            <span className="text-xl font-bold text-[#1A1A2E]">
              ₦{parseFloat(variant.price).toFixed(2)}
            </span>
            {variants.length === 1 && (
              <span className="text-xs text-gray-400 ml-1 capitalize">{variant.size}</span>
            )}
          </div>
          <button
            onClick={() => onAdd(product, variant)}
            disabled={adding[variant.id] || product.is_available === false}
            className="flex items-center gap-1.5 bg-[#FF6B35] hover:bg-[#e55a24] text-white px-4 py-2 rounded-xl text-sm font-semibold transition-all disabled:opacity-50 active:scale-95"
          >
            {adding[variant.id]
              ? <Loader2 className="w-4 h-4 animate-spin" />
              : <ShoppingBag className="w-4 h-4" />
            }
            Add
          </button>
        </div>
      </div>
    </div>
  )
}
