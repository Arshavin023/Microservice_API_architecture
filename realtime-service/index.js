'use strict';

/**
 * realtime-service — Node.js + Socket.io + RabbitMQ
 *
 * Consumes shipping and order events from RabbitMQ and pushes live
 * status updates to connected browser clients via WebSocket.
 *
 * Each browser subscribes to a room named after their order ID.
 * When an event arrives for that order, the server emits to the room.
 * The frontend updates the tracking timeline without a page refresh.
 *
 * Events handled:
 *   shipment.dispatched       → order status: shipped
 *   shipment.delivery_pending → order status: awaiting_confirmation
 *   shipment.delivered        → order status: delivered
 *   payment.succeeded         → order status: paid
 */

const express   = require('express');
const http      = require('http');
const { Server} = require('socket.io');
const amqplib   = require('amqplib');

const PORT         = process.env.PORT         || 8007;
const RABBITMQ_URL = process.env.RABBITMQ_URL || 'amqp://guest:guest@rabbitmq:5672';
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';

// ── Express + Socket.io setup ──────────────────────────────────────────────
const app    = express();
const server = http.createServer(app);
const io     = new Server(server, {
  cors: {
    origin:  [FRONTEND_URL, 'http://localhost:3000'],
    methods: ['GET', 'POST'],
  },
  path: '/socket.io',
});

app.get('/health', (_, res) => res.json({ status: 'ok', service: 'realtime-service' }));

// ── Socket.io connection ───────────────────────────────────────────────────
io.on('connection', (socket) => {
  console.log(`[socket] client connected: ${socket.id}`);

  // Client subscribes to a specific order room
  socket.on('subscribe:order', (orderId) => {
    if (!orderId || typeof orderId !== 'string') return;
    socket.join(`order:${orderId}`);
    console.log(`[socket] ${socket.id} subscribed to order:${orderId}`);
  });

  socket.on('unsubscribe:order', (orderId) => {
    socket.leave(`order:${orderId}`);
  });

  socket.on('disconnect', () => {
    console.log(`[socket] client disconnected: ${socket.id}`);
  });
});

// ── Status mapping — RabbitMQ event → order status ────────────────────────
const EVENT_STATUS_MAP = {
  'payment.succeeded':         'paid',
  'shipment.dispatched':       'shipped',
  'shipment.delivery_pending': 'awaiting_confirmation',
  'shipment.delivered':        'delivered',
};

// ── RabbitMQ consumer ──────────────────────────────────────────────────────
async function startConsumer() {
  let retries = 0;

  while (true) {
    try {
      console.log('[amqp] connecting to RabbitMQ...');
      const conn    = await amqplib.connect(RABBITMQ_URL);
      const channel = await conn.createChannel();

      // Declare the exchanges we need (idempotent)
      await channel.assertExchange('payment_events',  'topic', { durable: true });
      await channel.assertExchange('shipping_events', 'topic', { durable: true });

      // Exclusive queue — auto-deleted when this service disconnects
      const { queue } = await channel.assertQueue('', { exclusive: true });

      // Bind to all relevant events
      const bindings = [
        ['payment_events',  'payment.succeeded'],
        ['shipping_events', 'shipment.dispatched'],
        ['shipping_events', 'shipment.delivery_pending'],
        ['shipping_events', 'shipment.delivered'],
      ];

      for (const [exchange, routingKey] of bindings) {
        await channel.bindQueue(queue, exchange, routingKey);
      }

      console.log('[amqp] realtime-service listening for order/shipping events');
      retries = 0;

      channel.consume(queue, (msg) => {
        if (!msg) return;

        try {
          const data     = JSON.parse(msg.content.toString());
          const event    = data.event;
          const orderId  = data.order_id;
          const newStatus = EVENT_STATUS_MAP[event];

          if (!orderId || !newStatus) {
            channel.ack(msg);
            return;
          }

          console.log(`[amqp] ${event} → order:${orderId} → ${newStatus}`);

          // Push to all browser clients watching this order
          io.to(`order:${orderId}`).emit('order:status', {
            orderId,
            status:    newStatus,
            event,
            timestamp: new Date().toISOString(),
          });

          channel.ack(msg);
        } catch (err) {
          console.error('[amqp] error processing message:', err.message);
          channel.nack(msg, false, false);
        }
      });

      // Handle connection close
      conn.on('close', () => {
        console.warn('[amqp] connection closed — reconnecting...');
        setTimeout(startConsumer, 3000);
      });

      conn.on('error', (err) => {
        console.error('[amqp] connection error:', err.message);
      });

      break; // exit retry loop on success

    } catch (err) {
      retries++;
      const delay = Math.min(1000 * 2 ** retries, 30000);
      console.error(`[amqp] failed to connect (attempt ${retries}): ${err.message}`);
      console.log(`[amqp] retrying in ${delay / 1000}s...`);
      await new Promise(r => setTimeout(r, delay));
    }
  }
}

// ── Start ──────────────────────────────────────────────────────────────────
server.listen(PORT, () => {
  console.log(`[http] realtime-service listening on port ${PORT}`);
});

startConsumer().catch((err) => {
  console.error('[fatal] could not start consumer:', err);
  process.exit(1);
});
