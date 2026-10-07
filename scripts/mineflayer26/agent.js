#!/usr/bin/env node
'use strict'

// Four real test players for the live feature regression. Same safety rules as keepalive.js
// (innotest only, the four allowed names, serialized logins, no client-originated movement),
// plus a tiny directive channel so a server-side test can ask a player to do what only a client
// can do: sneak, dig a block, use (right-click) a block.
//
// The server sends   tellraw <player> "LIVEBOT <id> <action> [x y z]"
// and the player answers with   /trigger livebot_ack set <id>   once the action is done
// (or /trigger livebot_ack set -<id> when it failed).
//   actions: sneak_on | sneak_off | dig x y z | use x y z | respawn
// Like a person on the death screen, a dead agent player only respawns when asked (respawn).

const path = require('path')

const repoRoot = path.resolve(__dirname, '..', '..')
const stackRoot = path.resolve(process.env.MF26_STACK || path.join(repoRoot, 'dist', 'mineflayer-26.3-src'))
const mineflayer = require(path.join(stackRoot, 'mineflayer'))
const { Vec3 } = require(path.join(stackRoot, 'mineflayer', 'node_modules', 'vec3'))

const TARGET = 'innotest.exaroton.me'
const LOCAL = '127.0.0.1'
const host = String(process.env.MF26_HOST || TARGET).trim().toLowerCase().replace(/\.$/, '')
const port = Number(process.env.MF26_PORT || 25565)
const names = (process.env.MF26_BOTS || 'SunnyChen,penguin0531,geena0701,Felicitypeng').split(',').map(x => x.trim()).filter(Boolean)
const spawnTimeoutMs = Number(process.env.MF26_SPAWN_TIMEOUT_MS || 45000)
const durationMs = Number(process.env.MF26_DURATION_MS || 1800000)

if (host !== TARGET && !(host === LOCAL && process.env.MF26_ALLOW_LOCAL === '1')) {
  console.error(`SAFETY LOCK: refusing Minecraft connection to ${host}; only ${TARGET} is allowed`)
  process.exit(2)
}
const allowedNames = new Set(['SunnyChen', 'penguin0531', 'geena0701', 'Felicitypeng'])
if (![1, 4].includes(names.length) || new Set(names).size !== names.length || names.some(name => !allowedNames.has(name))) {
  console.error('Use either one allowed player or all four unique allowed players')
  process.exit(2)
}
if (!Number.isFinite(durationMs) || durationMs < 30000 || durationMs > 3600000) {
  console.error('MF26_DURATION_MS must be between 30000 and 3600000')
  process.exit(2)
}

const states = new Map()
const bots = []

function delay (ms) { return new Promise(resolve => setTimeout(resolve, ms)) }

async function act (bot, state, id, action, args) {
  if (action === 'sneak_on' || action === 'sneak_off') {
    bot.setControlState('sneak', action === 'sneak_on')
    await delay(300)
    return
  }
  if (action === 'respawn') {
    bot.respawn()
    await delay(1500)
    return
  }
  if (action === 'dig' || action === 'use') {
    const [x, y, z] = args.map(Number)
    if (![x, y, z].every(Number.isFinite)) throw new Error(`bad position ${args.join(' ')}`)
    const pos = new Vec3(x, y, z)
    let block = null
    for (let i = 0; i < 40 && !(block = bot.blockAt(pos)); i++) await delay(100)
    if (!block) throw new Error(`block ${x} ${y} ${z} is not loaded on the client`)
    if (action === 'dig') await bot.dig(block, 'ignore')
    else await bot.activateBlock(block)
    return
  }
  throw new Error(`unknown action ${action}`)
}

function createBot (username) {
  const state = { spawned: false, ended: false, errors: [], kicked: [], directives: 0 }
  states.set(username, state)
  const bot = mineflayer.createBot({ host, port, username, auth: 'offline', version: '26.3', physicsEnabled: false, respawn: false })
  bot.physicsEnabled = false

  // Same as keepalive.js: never originate movement packets (the 26.3 patch can send an invalid
  // move after a server-side teleport); teleport confirms, inputs and actions still go out.
  const rawWrite = bot._client.write.bind(bot._client)
  const movementPackets = new Set(['position', 'position_look', 'look', 'flying'])
  bot._client.write = (packet, data) => {
    const name = String(packet)
    if (movementPackets.has(name) || name.startsWith('move_player')) return
    return rawWrite(packet, data)
  }

  let queue = Promise.resolve()
  bot.on('message', (message, position) => {
    const text = message.toString()
    const m = /^LIVEBOT (\d+) (\w+)((?: -?\d+)*)$/.exec(text.trim())
    if (!m) {
      // what the datapacks tell this player (minus the coordinate action bar) - the evidence for failures
      if (position !== 'game_info' && text.trim()) console.log(`MSG ${username} ${text.replace(/\s+/g, ' ').slice(0, 300)}`)
      return
    }
    const [, id, action, rest] = m
    const args = rest.trim() ? rest.trim().split(/\s+/) : []
    state.directives++
    queue = queue.then(async () => {
      try {
        await act(bot, state, id, action, args)
        bot.chat(`/trigger livebot_ack set ${id}`)
        console.log(`ACT ${username} ${id} ${action} ${args.join(' ')} ok`)
      } catch (err) {
        bot.chat(`/trigger livebot_ack set -${id}`)
        console.log(`ACT ${username} ${id} ${action} ${args.join(' ')} FAILED ${err && err.message}`)
      }
    })
  })

  bots.push(bot)
  bot.once('spawn', () => { state.spawned = true; console.log(`SPAWNED ${username}`) })
  bot.on('death', () => console.log(`DIED ${username}`))
  bot.on('error', err => state.errors.push(String(err && err.stack ? err.stack : err)))
  bot.on('kicked', reason => state.kicked.push(typeof reason === 'string' ? reason : JSON.stringify(reason)))
  bot.on('end', reason => { state.ended = true; state.endReason = reason; console.log(`ENDED ${username}: ${reason || 'unknown'}`) })
  return bot
}

async function waitForSpawn (name) {
  const deadline = Date.now() + spawnTimeoutMs
  while (Date.now() < deadline) {
    const state = states.get(name)
    if (state && state.spawned && !state.ended) return
    if (state && state.ended) break
    await delay(100)
  }
  throw new Error(`bot failed during serialized login: ${name} ${JSON.stringify(states.get(name))}`)
}

async function main () {
  for (const name of names) {
    createBot(name)
    await waitForSpawn(name)
    if (names.length > 1) await delay(1500)
  }
  const failures = names.filter(name => { const s = states.get(name); return !s.spawned || s.ended || s.errors.length || s.kicked.length })
  if (failures.length) {
    for (const name of failures) console.error(JSON.stringify({ name, ...states.get(name) }))
    throw new Error(`failed to bring bot(s) online: ${failures.join(', ')}`)
  }
  console.log(`READY ${names.length}/${names.length} on ${host}:${port} as ${names.join(',')} (agent)`)
  const endAt = Date.now() + durationMs
  while (Date.now() < endAt) {
    const ended = names.filter(name => states.get(name).ended)
    if (ended.length) throw new Error(`bots disconnected early: ${ended.join(', ')} ${JSON.stringify(ended.map(n => states.get(n)))}`)
    await delay(Math.min(5000, endAt - Date.now()))
  }
  console.log('HOLD COMPLETE')
}

main()
  .then(() => { process.exitCode = 0 })
  .catch(err => { console.error(err && err.stack ? err.stack : String(err)); process.exitCode = 1 })
  .finally(async () => {
    for (const bot of bots) { try { bot.quit('agent session complete') } catch (_) {} }
    await delay(500)
  })
