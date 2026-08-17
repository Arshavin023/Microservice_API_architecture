import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Loader2, Package, ChevronRight, CheckCircle, Clock, XCircle, Truck, MapPin } from 'lucide-react'
import { ordersApi, paymentsApi, shippingApi } from '../api'

const STATUS_CONFIG = {
  draft:           { label: 'Draft',            color: 'bg-gray-100 text-gray-600',      dot: 'bg-gray-400' },
  pending_payment: { label: 'Awaiting payment',  color: 'bg-amber-100 text-amber-700',    dot: 'bg-amber-400' },
  paid:            { label: 'Paid',              color: 'bg-green-100 text-green-700',    dot: 'bg-green-500' },
  shipped:         { label: 'On the way',        color: 'bg-blue-100 text-blue-700',      dot: 'bg-blue-500' },
  delivered:       { label: 'Delivered',         color: 'bg-emerald-100 text-emerald-700', dot: 'bg-emerald-500' },
  cancelled:       { label: 'Cancelled',         color: 'bg-red-100 text-red-700',        dot: 'bg-red-400' },
}

function StatusBadge({ status }) {
  const cfg = STATUS_CONFIG[status] ?? { label: status, color: 'bg-gray-100 text-gray-600', dot: 'bg-gray-400' }
  return (
    <span className={`badge ${cfg.color}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
      {cfg.label}
    </span>
  )
}

// ── Tracking timeline ─────────────────────────────────────────────
const STEPS = [
  { key: 'ordered',    label: 'Order placed',      icon: Package },
  { key: 'paid',       label: 'Payment confirmed',  icon: CheckCircle },
  { key: 'preparing',  label: 'Being prepared',     icon: Clock },
  { key: 'shipped',    label: 'Out for delivery',   icon: Truck },
  { key: 'delivered',  label: 'Delivered',          icon: MapPin },
]

function getActiveStep(orderStatus, shipmentStatus) {
  if (orderStatus === 'delivered') return 5
  if (orderStatus === 'shipped')   return 4
  if (shipmentStatus === 'pending') return 3
  if (orderStatus === 'paid')      return 3
  if (orderStatus === 'pending_payment') return 1
  return 0
}

function TrackingTimeline({ order, shipment }) {
  const activeStep = getActiveStep(order.status, shipment?.status)

  return (
    <div className="card p-5 mb-6">
      <h3 className="font-bold text-[#1A1A2E] mb-5">Order tracking</h3>
      <div className="relative">
        {/* Connector line */}
        <div className="absolute left-4 top-4 bottom-4 w-0.5 bg-gray-100" />
        <div
          className="absolute left-4 top-4 w-0.5 bg-[#FF6B35] transition-all duration-500"
          style={{ height: `${Math.min((activeStep / (STEPS.length - 1)) * 100, 100)}%` }}
        />

        <div className="space-y-6">
          {STEPS.map((step, i) => {
            const Icon    = step.icon
            const done    = i < activeStep
            const current = i === activeStep - 1 || (i === 0 && activeStep === 0)

            return (
              <div key={step.key} className="flex items-start gap-4 relative">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 z-10 transition-all ${
                  done    ? 'bg-[#FF6B35] text-white' :
                  current ? 'bg-[#FF6B35] text-white ring-4 ring-orange-100' :
                            'bg-gray-100 text-gray-400'
                }`}>
                  <Icon className="w-4 h-4" />
                </div>
                <div className="pt-1">
                  <p className={`text-sm font-semibold ${done || current ? 'text-[#1A1A2E]' : 'text-gray-400'}`}>
                    {step.label}
                  </p>
                  {/* Shipment detail on out-for-delivery step */}
                  {step.key === 'shipped' && shipment?.status === 'dispatched' && (
                    <p className="text-xs text-gray-500 mt-0.5">
                      {shipment.driver_name && `Driver: ${shipment.driver_name}`}
                      {shipment.driver_phone && ` · ${shipment.driver_phone}`}
                    </p>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Delivery address */}
      {shipment?.delivery_address && (
        <div className="mt-5 pt-5 border-t border-gray-50 flex items-start gap-2 text-sm text-gray-600">
          <MapPin className="w-4 h-4 text-[#FF6B35] flex-shrink-0 mt-0.5" />
          <span>{shipment.delivery_address}</span>
        </div>
      )}
    </div>
  )
}

// ── Order list ────────────────────────────────────────────────────
export function Orders() {
  const [orders,  setOrders]  = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    ordersApi.listOrders()
      .then(res => setOrders(res.data))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 className="w-8 h-8 animate-spin text-[#FF6B35]" />
    </div>
  )

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold text-[#1A1A2E] mb-2">My Orders</h1>
      <p className="text-gray-500 mb-8">Track and manage your pizza orders</p>

      {orders.length === 0 ? (
        <div className="text-center py-20">
          <span className="text-6xl">🍕</span>
          <p className="text-gray-500 mt-4 mb-6">No orders yet — your first pizza is waiting!</p>
          <Link to="/" className="btn-primary">Browse menu</Link>
        </div>
      ) : (
        <div className="space-y-3">
          {orders.map(order => (
            <Link
              key={order.id}
              to={`/orders/${order.id}`}
              className="card flex items-center justify-between p-4 hover:shadow-card transition-shadow group"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-orange-50 rounded-xl flex items-center justify-center text-2xl">
                  🍕
                </div>
                <div>
                  <p className="font-semibold text-[#1A1A2E]">
                    ₦{parseFloat(order.total_amount).toFixed(2)}
                  </p>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {new Date(order.created_at).toLocaleDateString('en-GB', {
                      day: 'numeric', month: 'short', year: 'numeric',
                    })} · {order.items?.length ?? 0} item{order.items?.length !== 1 ? 's' : ''}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <StatusBadge status={order.status} />
                <ChevronRight className="w-4 h-4 text-gray-300 group-hover:text-gray-500 transition-colors" />
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
  const [order,    setOrder]    = useState(null)
  const [payment,  setPayment]  = useState(null)
  const [shipment, setShipment] = useState(null)
  const [loading,  setLoading]  = useState(true)

  useEffect(() => {
    Promise.allSettled([
      ordersApi.getOrder(id),
      paymentsApi.getPaymentByOrder(id),
      shippingApi.getShipmentByOrder(id),
    ]).then(([orderRes, paymentRes, shipmentRes]) => {
      if (orderRes.status   === 'fulfilled') setOrder(orderRes.value.data)
      if (paymentRes.status === 'fulfilled') setPayment(paymentRes.value.data)
      if (shipmentRes.status === 'fulfilled') setShipment(shipmentRes.value.data)
    }).finally(() => setLoading(false))
  }, [id])

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <Loader2 className="w-8 h-8 animate-spin text-[#FF6B35]" />
    </div>
  )

  if (!order) return (
    <div className="text-center py-20">
      <Package className="w-12 h-12 mx-auto mb-3 text-gray-300" />
      <p className="text-gray-500">Order not found.</p>
    </div>
  )

  const showTracking = ['paid', 'shipped', 'delivered'].includes(order.status)

  return (
    <div className="max-w-2xl mx-auto px-4 py-10">
      {/* Header */}
      <Link to="/orders" className="flex items-center gap-1 text-sm text-gray-400 hover:text-gray-600 mb-6">
        ← Back to orders
      </Link>

      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-[#1A1A2E]">Order details</h1>
          <p className="text-xs text-gray-400 font-mono mt-1">{order.id}</p>
        </div>
        <StatusBadge status={order.status} />
      </div>

      {/* Tracking timeline for paid+ orders */}
      {showTracking && (
        <TrackingTimeline order={order} shipment={shipment} />
      )}

      {/* Pending payment CTA */}
      {order.status === 'pending_payment' && order.authorization_url && (
        <div className="card p-5 mb-6 border-amber-200 bg-amber-50">
          <p className="font-semibold text-amber-800 mb-1">Payment pending</p>
          <p className="text-sm text-amber-700 mb-3">Complete your payment to confirm this order.</p>
          <a
            href={order.authorization_url}
            target="_blank"
            rel="noreferrer"
            className="btn-primary text-sm inline-flex"
          >
            Complete payment on Paystack
          </a>
        </div>
      )}

      {/* Items */}
      <div className="card divide-y divide-gray-50 mb-5">
        <div className="p-4">
          <p className="text-sm font-semibold text-gray-500">Items ordered</p>
        </div>
        {order.items?.map(item => (
          <div key={item.id} className="flex justify-between items-center p-4">
            <div className="flex items-center gap-3">
              <span className="text-2xl">🍕</span>
              <div>
                <p className="font-semibold text-[#1A1A2E]">{item.product_name}</p>
                <p className="text-sm text-gray-500 capitalize">{item.size} × {item.quantity}</p>
              </div>
            </div>
            <p className="font-semibold">₦{parseFloat(item.subtotal).toFixed(2)}</p>
          </div>
        ))}
        <div className="flex justify-between items-center p-4 bg-gray-50">
          <p className="font-bold text-[#1A1A2E]">Total</p>
          <p className="text-xl font-bold text-[#FF6B35]">₦{parseFloat(order.total_amount).toFixed(2)}</p>
        </div>
      </div>

      {/* Payment info */}
      {payment && (
        <div className="card p-5">
          <p className="text-sm font-semibold text-gray-500 mb-3">Payment</p>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Status</span>
              <span className={`font-semibold ${
                payment.status === 'succeeded' ? 'text-green-600' :
                payment.status === 'failed'    ? 'text-red-600'   : 'text-amber-600'
              }`}>{payment.status}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Reference</span>
              <span className="font-mono text-xs text-gray-700">{payment.paystack_reference}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
