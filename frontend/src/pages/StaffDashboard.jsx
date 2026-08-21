import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2, Truck, Package, CheckCircle, ChevronDown, ChevronUp, Clock, AlertTriangle } from 'lucide-react'
import { ordersApi, shippingApi } from '../api'
import { useAuth } from '../context/AuthContext'

const SHIPMENT_STATUS_COLOR = {
  pending:    'bg-amber-100 text-amber-700',
  dispatched: 'bg-blue-100 text-blue-700',
  delivered:  'bg-emerald-100 text-emerald-700',
}

function ShipmentCard({ order, shipment, onRefresh }) {
  const [expanded, setExpanded] = useState(false)
  const [working,  setWorking]  = useState(false)
  const [form,     setForm]     = useState({ driver_name: '', driver_phone: '', tracking_note: '' })
  const [error,    setError]    = useState('')

  const isDisputed = order.status === 'disputed'

  const dispatch = async () => {
    setWorking(true); setError('')
    try {
      await shippingApi.dispatchShipment(shipment.id, {
        driver_name:   form.driver_name  || undefined,
        driver_phone:  form.driver_phone || undefined,
        tracking_note: form.tracking_note || undefined,
      })
      onRefresh()
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Failed to dispatch')
    } finally {
      setWorking(false)
    }
  }

  const notifyCustomer = async () => {
    setWorking(true); setError('')
    try {
      await shippingApi.notifyCustomer(shipment.id, {
        tracking_note: form.tracking_note || undefined,
      })
      onRefresh()
    } catch (err) {
      setError(err.response?.data?.detail ?? 'Failed to notify customer')
    } finally {
      setWorking(false)
    }
  }

  return (
    <div className={`card overflow-hidden ${isDisputed ? 'border-red-300 bg-red-50/30' : ''}`}>
      <button
        onClick={() => setExpanded(e => !e)}
        className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3 text-left">
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-xl ${
            isDisputed ? 'bg-red-100' : 'bg-orange-50'
          }`}>
            {isDisputed ? <AlertTriangle className="w-5 h-5 text-red-600" /> : '🍽️'}
          </div>
          <div>
            <p className="font-semibold text-[#1A1A2E] text-sm">
              ₦{parseFloat(order.total_amount).toFixed(2)}
            </p>
            <p className="text-xs text-gray-400 font-mono">{order.id.slice(0, 12)}…</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {isDisputed ? (
            <span className="badge bg-red-100 text-red-700 flex items-center gap-1">
              <AlertTriangle className="w-3 h-3" /> Disputed
            </span>
          ) : shipment ? (
            <span className={`badge ${SHIPMENT_STATUS_COLOR[shipment.status]}`}>
              {shipment.status}
            </span>
          ) : (
            <span className="badge bg-amber-100 text-amber-600 flex items-center gap-1">
              <Clock className="w-3 h-3" /> Awaiting shipment
            </span>
          )}
          {expanded
            ? <ChevronUp className="w-4 h-4 text-gray-400" />
            : <ChevronDown className="w-4 h-4 text-gray-400" />
          }
        </div>
      </button>

      {expanded && (
        <div className="border-t border-gray-50 p-4 space-y-4">
          {error && (
            <div className="bg-red-50 text-red-700 text-sm p-3 rounded-lg">{error}</div>
          )}

          {isDisputed ? (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4">
              <p className="font-semibold text-red-800 text-sm mb-1">
                Customer reports non-delivery
              </p>
              <p className="text-red-700 text-sm mb-3">
                This customer said they did not receive their order.
                Please contact the delivery rider to investigate before
                taking further action.
              </p>
              {shipment?.driver_name && (
                <p className="text-xs text-red-600">
                  Driver: <strong>{shipment.driver_name}</strong>
                  {shipment.driver_phone && ` · ${shipment.driver_phone}`}
                </p>
              )}
              {shipment?.delivery_address && (
                <p className="text-xs text-red-600 mt-1">
                  Delivery address: {shipment.delivery_address}
                </p>
              )}
            </div>
          ) : !shipment ? (
            <div className="text-center py-4 text-gray-500 text-sm">
              <Clock className="w-5 h-5 mx-auto mb-2 text-amber-400" />
              Shipment is being created automatically.<br />
              Refresh in a moment.
            </div>
          ) : shipment.status === 'delivered' ? (
            <div className="flex items-center gap-2 text-emerald-600 text-sm font-medium py-2">
              <CheckCircle className="w-4 h-4" /> Delivered ✓
            </div>
          ) : (
            <>
              {shipment.status === 'pending' && (
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="text-xs font-medium text-gray-500 mb-1 block">Driver name</label>
                    <input
                      className="input text-sm"
                      placeholder="Emeka Obi"
                      value={form.driver_name}
                      onChange={e => setForm(f => ({ ...f, driver_name: e.target.value }))}
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium text-gray-500 mb-1 block">Driver phone</label>
                    <input
                      className="input text-sm"
                      placeholder="+234..."
                      value={form.driver_phone}
                      onChange={e => setForm(f => ({ ...f, driver_phone: e.target.value }))}
                    />
                  </div>
                </div>
              )}

              <div>
                <label className="text-xs font-medium text-gray-500 mb-1 block">Note (optional)</label>
                <input
                  className="input text-sm"
                  placeholder="e.g. Call customer on arrival"
                  value={form.tracking_note}
                  onChange={e => setForm(f => ({ ...f, tracking_note: e.target.value }))}
                />
              </div>

              <div className="flex gap-2 pt-1">
                {shipment.status === 'pending' && (
                  <button onClick={dispatch} disabled={working}
                    className="btn-primary text-sm flex items-center gap-1.5 flex-1 justify-center">
                    {working ? <Loader2 className="w-4 h-4 animate-spin" /> : <Truck className="w-4 h-4" />}
                    Dispatch to customer
                  </button>
                )}
                {shipment.status === 'dispatched' && (
                  <button onClick={notifyCustomer} disabled={working}
                    className="bg-[#2D6A4F] hover:bg-[#235a40] text-white font-semibold px-5 py-2.5 rounded-xl transition-all text-sm flex items-center gap-1.5 flex-1 justify-center disabled:opacity-50">
                    {working ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle className="w-4 h-4" />}
                    Notify customer to confirm
                  </button>
                )}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  )
}

export default function StaffDashboard() {
  const { isStaff, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [paidOrders, setPaidOrders] = useState([])
  const [shipments,  setShipments]  = useState({})
  const [loading,    setLoading]    = useState(true)

  useEffect(() => {
    if (!isAuthenticated || !isStaff) { navigate('/'); return }
    loadData()
  }, [isAuthenticated, isStaff])

  const loadData = async () => {
    setLoading(true)
    try {
      const ordersRes = await ordersApi.listAllOrders()
      const active = ordersRes.data
      setPaidOrders(active)

      const shipmentMap = {}
      await Promise.allSettled(
        active.map(async (order) => {
          try {
            const res = await shippingApi.getShipmentByOrderStaff(order.id)
            shipmentMap[order.id] = res.data
          } catch {
            shipmentMap[order.id] = null
          }
        })
      )
      setShipments(shipmentMap)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  if (!isStaff) return null

  const inTransit  = Object.values(shipments).filter(s => s?.status === 'dispatched').length
  const pending    = Object.values(shipments).filter(s => s?.status === 'pending').length
  const disputed   = paidOrders.filter(o => o.status === 'disputed').length

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-[#1A1A2E] rounded-xl flex items-center justify-center">
            <Truck className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-[#1A1A2E]">Staff Dashboard</h1>
            <p className="text-gray-500 text-sm">Shipments are created automatically when payment is confirmed</p>
          </div>
        </div>
        <button onClick={loadData} className="btn-secondary text-sm">Refresh</button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-3 mb-8">
        <div className="card px-4 py-3 text-center">
          <p className="text-2xl font-bold text-[#1A1A2E]">{paidOrders.length}</p>
          <p className="text-xs text-gray-500 mt-0.5">Active orders</p>
        </div>
        <div className="card px-4 py-3 text-center">
          <p className="text-2xl font-bold text-amber-500">{pending}</p>
          <p className="text-xs text-gray-500 mt-0.5">Ready to dispatch</p>
        </div>
        <div className="card px-4 py-3 text-center">
          <p className="text-2xl font-bold text-[#FF6B35]">{inTransit}</p>
          <p className="text-xs text-gray-500 mt-0.5">In transit</p>
        </div>
        <div className={`card px-4 py-3 text-center ${disputed > 0 ? 'border-red-300 bg-red-50' : ''}`}>
          <p className={`text-2xl font-bold ${disputed > 0 ? 'text-red-600' : 'text-gray-300'}`}>{disputed}</p>
          <p className={`text-xs mt-0.5 ${disputed > 0 ? 'text-red-500' : 'text-gray-500'}`}>Disputed</p>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-32">
          <Loader2 className="w-6 h-6 animate-spin text-[#FF6B35]" />
        </div>
      ) : paidOrders.length === 0 ? (
        <div className="text-center py-16">
          <span className="text-5xl">✅</span>
          <p className="text-gray-500 mt-4">No active orders right now</p>
        </div>
      ) : (
        <div className="space-y-3">
          {[...paidOrders]
            .sort((a, b) => (a.status === 'disputed' ? -1 : 1) - (b.status === 'disputed' ? -1 : 1))
            .map(order => (
              <ShipmentCard
                key={order.id}
                order={order}
                shipment={shipments[order.id]}
                onRefresh={loadData}
              />
            ))}
        </div>
      )}
    </div>
  )
}
