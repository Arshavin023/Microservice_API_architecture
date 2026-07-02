import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Loader2, Package, ChevronRight, CheckCircle, Clock, XCircle, Truck } from 'lucide-react'
import { ordersApi, paymentsApi } from '../api'

const STATUS_CONFIG = {
  draft:           { label: 'Draft',           icon: Clock,         color: 'bg-gray-100 text-gray-600' },
  pending_payment: { label: 'Awaiting payment', icon: Clock,         color: 'bg-yellow-100 text-yellow-700' },
  confirmed:       { label: 'Confirmed',        icon: CheckCircle,   color: 'bg-blue-100 text-blue-700' },
  paid:            { label: 'Paid',             icon: CheckCircle,   color: 'bg-green-100 text-green-700' },
  shipped:         { label: 'Shipped',          icon: Truck,         color: 'bg-purple-100 text-purple-700' },
  delivered:       { label: 'Delivered',        icon: CheckCircle,   color: 'bg-emerald-100 text-emerald-700' },
  cancelled:       { label: 'Cancelled',        icon: XCircle,       color: 'bg-red-100 text-red-700' },
}

function StatusBadge({ status }) {
  const config = STATUS_CONFIG[status] ?? { label: status, icon: Clock, color: 'bg-gray-100 text-gray-600' }
  const Icon = config.icon
  return (
    <span className={`badge gap-1 ${config.color}`}>
      <Icon className="w-3 h-3" />
      {config.label}
    </span>
  )
}

// ── Order list ────────────────────────────────────────────────────
export function Orders() {
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    ordersApi.listOrders()
      .then(res => setOrders(res.data))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 className="w-8 h-8 animate-spin text-brand-500" />
    </div>
  )

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold mb-8">Orders</h1>

      {orders.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <Package className="w-12 h-12 mx-auto mb-3 opacity-30" />
          <p className="text-gray-500">No orders yet.</p>
          <Link to="/" className="btn-primary mt-4 inline-block">Browse menu</Link>
        </div>
      ) : (
        <div className="card divide-y divide-gray-50">
          {orders.map(order => (
            <Link
              key={order.id}
              to={`/orders/${order.id}`}
              className="flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
            >
              <div>
                <p className="font-medium text-sm font-mono text-gray-500">{order.id.slice(0, 8)}…</p>
                <p className="text-lg font-semibold mt-0.5">₦{parseFloat(order.total_amount).toFixed(2)}</p>
                <p className="text-xs text-gray-400 mt-0.5">
                  {new Date(order.created_at).toLocaleDateString('en-GB', {
                    day: 'numeric', month: 'short', year: 'numeric',
                    hour: '2-digit', minute: '2-digit'
                  })}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <StatusBadge status={order.status} />
                <ChevronRight className="w-4 h-4 text-gray-400" />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}

// ── Order detail ──────────────────────────────────────────────────
export function OrderDetail() {
  const { id } = useParams()
  const [order, setOrder] = useState(null)
  const [payment, setPayment] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.allSettled([
      ordersApi.getOrder(id),
      paymentsApi.getPaymentByOrder(id),
    ]).then(([orderRes, paymentRes]) => {
      if (orderRes.status === 'fulfilled') setOrder(orderRes.value.data)
      if (paymentRes.status === 'fulfilled') setPayment(paymentRes.value.data)
    }).finally(() => setLoading(false))
  }, [id])

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 className="w-8 h-8 animate-spin text-brand-500" />
    </div>
  )

  if (!order) return (
    <div className="text-center py-20 text-gray-400">
      <Package className="w-12 h-12 mx-auto mb-3 opacity-30" />
      <p>Order not found.</p>
    </div>
  )

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <Link to="/orders" className="text-sm text-gray-400 hover:text-gray-600 mb-1 block">← Back to orders</Link>
          <h1 className="text-2xl font-bold">Order detail</h1>
          <p className="text-xs text-gray-400 font-mono mt-1">{order.id}</p>
        </div>
        <StatusBadge status={order.status} />
      </div>

      {/* Items */}
      <div className="card divide-y divide-gray-50 mb-6">
        <div className="p-4 bg-gray-50 rounded-t-xl">
          <p className="text-sm font-medium text-gray-500">Items</p>
        </div>
        {order.items?.map(item => (
          <div key={item.id} className="flex justify-between items-center p-4">
            <div>
              <p className="font-medium">{item.product_name}</p>
              <p className="text-sm text-gray-500 capitalize">{item.size} × {item.quantity}</p>
            </div>
            <p className="font-medium">₦{parseFloat(item.subtotal).toFixed(2)}</p>
          </div>
        ))}
        <div className="flex justify-between items-center p-4 font-semibold">
          <p>Total</p>
          <p className="text-xl">₦{parseFloat(order.total_amount).toFixed(2)}</p>
        </div>
      </div>

      {/* Payment info */}
      {payment && (
        <div className="card p-5">
          <p className="text-sm font-medium text-gray-500 mb-3">Payment</p>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Status</span>
              <span className={`font-medium ${payment.status === 'succeeded' ? 'text-green-600' : payment.status === 'failed' ? 'text-red-600' : 'text-yellow-600'}`}>
                {payment.status}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Reference</span>
              <span className="font-mono text-xs">{payment.paystack_reference}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Amount</span>
              <span>₦{parseFloat(payment.amount).toFixed(2)}</span>
            </div>
          </div>
        </div>
      )}

      {/* Pending payment CTA */}
      {order.status === 'pending_payment' && order.authorization_url && (
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-xl">
          <p className="text-sm text-yellow-800 font-medium mb-2">Payment not yet completed</p>
          <a
            href={order.authorization_url}
            target="_blank"
            rel="noreferrer"
            className="btn-primary text-sm inline-flex items-center gap-1.5"
          >
            Complete payment on Paystack
          </a>
        </div>
      )}
    </div>
  )
}
