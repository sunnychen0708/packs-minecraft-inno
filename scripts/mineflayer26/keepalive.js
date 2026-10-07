#!/usr/bin/env node
'use strict'

const path = require('path')

const repoRoot = path.resolve(__dirname, '..', '..')
const stackRoot = path.resolve(process.env.MF26_STACK || path.join(repoRoot, 'dist', 'mineflayer-26.3-src'))
const mineflayer = require(path.join(stackRoot, 'mineflayer'))
const { Vec3 } = require(require.resolve('vec3', { paths: [path.join(stackRoot, 'mineflayer')] }))

const TARGET = 'innotest.exaroton.me'
const host = String(process.env.MF26_HOST || TARGET).trim().toLowerCase().replace(/\.$/, '')
const port = Number(process.env.MF26_PORT || 25565)
const names = (process.env.MF26_BOTS || 'SunnyChen,penguin0531,geena0701,Felicitypeng').split(',').map(x => x.trim()).filter(Boolean)
const spawnTimeoutMs = Number(process.env.MF26_SPAWN_TIMEOUT_MS || 45000)
const durationMs = Number(process.env.MF26_DURATION_MS || 180000)

if (host !== TARGET) {
  console.error(`SAFETY LOCK: refusing Minecraft connection to ${host}; only ${TARGET} is allowed`)
  process.exit(2)
}
const allowedNames = new Set(['SunnyChen', 'penguin0531', 'geena0701', 'Felicitypeng'])
if (![1, 3, 4].includes(names.length) || new Set(names).size !== names.length ||
    names.some(name => !allowedNames.has(name)) || (names.length === 3 && names.includes('SunnyChen'))) {
  console.error('Use one allowed player, the three non-SunnyChen bots, or all four unique allowed players')
  process.exit(2)
}
if (!Number.isFinite(durationMs) || durationMs < 30000 || durationMs > 1500000) {
  console.error('MF26_DURATION_MS must be between 30000 and 1500000 for the GitHub smoke test')
  process.exit(2)
}

const states = new Map()
const bots = []

function delay (ms) { return new Promise(resolve => setTimeout(resolve, ms)) }

function createBot (username) {
  const state = { spawned: false, ended: false, errors: [], kicked: [] }
  states.set(username, state)
  const bot = mineflayer.createBot({ host, port, username, auth: 'offline', version: '26.3', physicsEnabled: false })
  bot.physicsEnabled = false

  // Idle test clients never need to originate movement. The current 26.3
  // protocol patch can emit an invalid move after a server-side teleport,
  // so suppress only movement packets while keeping teleport_confirm,
  // keepalive and all other protocol traffic intact.
  const rawWrite = bot._client.write.bind(bot._client)
  const movementPackets = new Set(['position', 'position_look', 'look', 'flying'])
  bot._client.write = (packet, data) => {
    const name = String(packet)
    if (movementPackets.has(name) || name.startsWith('move_player')) {
      state.suppressedMoves = (state.suppressedMoves || 0) + 1
      return
    }
    return rawWrite(packet, data)
  }

  attachDriver(bot, username)
  bots.push(bot)
  bot.once('spawn', () => {
    state.spawned = true
    console.log(`SPAWNED ${username}`)
  })
  bot.on('error', err => state.errors.push(String(err && err.stack ? err.stack : err)))
  bot.on('kicked', reason => state.kicked.push(typeof reason === 'string' ? reason : JSON.stringify(reason)))
  bot.on('end', reason => {
    state.ended = true
    state.endReason = reason
    console.log(`ENDED ${username}: ${reason || 'unknown'}`)
  })
  return bot
}

// Test driver. An innotest test datapack drives a bot with a system message
//   tellraw <bot> "MFBOT <name> <seq> <action> <args...>"
// and the bot acknowledges with its own /trigger mfack set <seq> when the
// action finished (or <seq>+100000 when it failed). Only system messages
// (tellraw, which needs OP) are read, and only a small fixed action set:
//   cmd trigger ...|function ...   send that command as this player
//   cmdx <n> <tok1..tokn> <command> send the command, then succeed only if one
//                                  chat/system/action-bar message or Dialog within 6 s
//                                  contains every token
//   dialog <command>               send trigger/function command and succeed only
//                                  after a clientbound show_dialog packet arrives
//   dig x y z                      survival-dig the block (real start/finish destroy)
//   sneak 0|1                      hold or release sneak
//   slot 0..8                      select a hotbar slot
//   use x y z                      right-click a block (e.g. open a chest)
//   close                          close the open container window
const COMMAND_PREFIXES = ['trigger ', 'function ']
function withTimeout (promise, ms, message) {
  let timer
  return Promise.race([promise, new Promise((resolve, reject) => { timer = setTimeout(() => reject(new Error(message)), ms) })])
    .finally(() => clearTimeout(timer))
}
function attachDriver (bot, username) {
  let queue = Promise.resolve()
  // Everything the player is shown (chat, system, action bar and Dialog
  // screens) as plain text, for cmdx token matching.
  bot.on('messagestr', text => bot.emit('mfbot_text', String(text)))
  bot.on('actionBar', msg => bot.emit('mfbot_text', msg && msg.toString ? msg.toString() : String(msg)))
  // 26.3 action bars arrive as set_action_bar_text or as system_chat with overlay=true; read the raw packets too.
  const rawText = packet => { try { return JSON.stringify(packet, (k, v) => typeof v === 'bigint' ? v.toString() : v) } catch (err) { return String(err) } }
  // The packet name differs between protocol versions, so match any action-bar/title/overlay packet by name.
  const seenNames = new Set()
  bot._client.on('packet', (packet, meta) => {
    const name = meta && meta.name ? meta.name : ''
    const overlay = name === 'system_chat' && packet && (packet.isActionBar || packet.overlay)
    if (!overlay && !/action_bar|title/.test(name)) return
    if (!seenNames.has(name)) { seenNames.add(name); console.log(`MFBOT_OVERLAY_PACKET ${username} ${name} ${rawText(packet).slice(0, 300)}`) }
    bot.emit('mfbot_text', rawText(packet))
  })
  bot._client.on('show_dialog', packet => {
    let text = ''
    try { text = JSON.stringify(packet, (k, v) => typeof v === 'bigint' ? v.toString() : v) } catch (err) { text = String(err) }
    console.log(`MFBOT_DIALOG ${username} ${text.slice(0, 300)}`)
    bot.emit('mfbot_text', text)
  })
  const ack = (seq, ok) => {
    try { bot.chat(`/trigger mfack set ${ok ? seq : seq + 100000}`) } catch (err) { console.log(`MFBOT_ACK_ERROR ${username} ${seq} ${err}`) }
  }
  const setSneak = on => {
    bot.setControlState('sneak', on)
    // With physics disabled the control state is not flushed by the physics
    // tick, so send the 26.3 player input packet directly as well.
    try { bot._client.write('player_input', { inputs: { shift: on } }) } catch (err) { console.log(`MFBOT_SNEAK_PACKET ${username} ${err}`) }
  }
  const run = async (action, args) => {
    const xyz = () => {
      const [x, y, z] = args.slice(0, 3).map(Number)
      if (![x, y, z].every(Number.isInteger)) throw new Error(`bad coordinates ${args.join(' ')}`)
      return new Vec3(x, y, z)
    }
    if (action === 'cmd') {
      const command = args.join(' ')
      if (!COMMAND_PREFIXES.some(p => command.startsWith(p))) throw new Error(`command not allowed: ${command}`)
      bot.chat(`/${command}`)
      await delay(250)
    } else if (action === 'cmdx') {
      const n = Number(args[0])
      if (!Number.isInteger(n) || n < 1 || n > 8) throw new Error(`bad token count ${args[0]}`)
      const tokens = args.slice(1, 1 + n)
      const command = args.slice(1 + n).join(' ')
      if (!COMMAND_PREFIXES.some(p => command.startsWith(p))) throw new Error(`command not allowed: ${command}`)
      let seen = null
      const listener = text => {
        const t = String(text)
        if (!seen && !t.startsWith('MFBOT ') && tokens.every(tok => t.includes(tok))) seen = t
      }
      bot.on('mfbot_text', listener)
      try {
        bot.chat(`/${command}`)
        const until = Date.now() + 6000
        while (!seen && Date.now() < until) await delay(100)
      } finally {
        bot.removeListener('mfbot_text', listener)
      }
      if (!seen) throw new Error(`no message containing ${JSON.stringify(tokens)}`)
      console.log(`MFBOT_SEEN ${username}: ${seen}`)
    } else if (action === 'dialog') {
      const command = args.join(' ')
      if (!COMMAND_PREFIXES.some(p => command.startsWith(p))) throw new Error(`command not allowed: ${command}`)
      let seen = null
      const listener = packet => {
        if (!seen) seen = packet
      }
      bot._client.on('show_dialog', listener)
      try {
        bot.chat(`/${command}`)
        const until = Date.now() + 6000
        while (!seen && Date.now() < until) await delay(100)
      } finally {
        bot._client.removeListener('show_dialog', listener)
      }
      if (!seen) throw new Error('no show_dialog packet received')
      let rendered
      try { rendered = JSON.stringify(seen) } catch (_) { rendered = String(seen) }
      console.log(`MFBOT_DIALOG ${username}: ${rendered.slice(0, 1200)}`)
    } else if (action === 'dig') {
      const pos = xyz()
      const block = bot.blockAt(pos)
      if (!block) throw new Error(`block not loaded at ${pos}`)
      if (block.name === 'air') throw new Error(`nothing to dig at ${pos}`)
      // Let the server time the break: send start and finish at once; vanilla
      // then completes the break itself (delayed destroy) as soon as the
      // player's real tool, effects and on-ground state allow. The client's
      // own estimate is wrong for a bot without physics (it is never on ground).
      const realDigTime = bot.digTime
      bot.digTime = () => 0
      try {
        await withTimeout(bot.dig(block, 'ignore'), 90000, `dig ${pos} did not finish`)
      } finally {
        bot.digTime = realDigTime
        try { bot.stopDigging() } catch (_) {}
      }
    } else if (action === 'sneak') {
      setSneak(args[0] === '1')
      await delay(150)
    } else if (action === 'slot') {
      const slot = Number(args[0])
      if (!Number.isInteger(slot) || slot < 0 || slot > 8) throw new Error(`bad slot ${args[0]}`)
      bot.setQuickBarSlot(slot)
      await delay(150)
    } else if (action === 'use') {
      const block = bot.blockAt(xyz())
      if (!block) throw new Error('block not loaded')
      await bot.activateBlock(block)
      await delay(250)
    } else if (action === 'close') {
      if (bot.currentWindow) bot.closeWindow(bot.currentWindow)
      await delay(150)
    } else {
      throw new Error(`unknown action ${action}`)
    }
  }
  bot.on('messagestr', (text, position) => {
    if (position !== 'system') return
    const parts = String(text).trim().split(/\s+/)
    if (parts[0] !== 'MFBOT' || parts[1] !== username) return
    const seq = Number(parts[2])
    const action = parts[3]
    const args = parts.slice(4)
    if (!Number.isInteger(seq) || seq < 1 || seq >= 100000) return
    queue = queue.then(async () => {
      try {
        await run(action, args)
        console.log(`MFBOT_DONE ${username} ${seq} ${action} ${args.join(' ')}`)
        ack(seq, true)
      } catch (err) {
        console.log(`MFBOT_FAIL ${username} ${seq} ${action} ${args.join(' ')}: ${err && err.message ? err.message : err}`)
        ack(seq, false)
      }
    })
  })
}

async function waitForSpawn (name) {
  const deadline = Date.now() + spawnTimeoutMs
  while (Date.now() < deadline) {
    const state = states.get(name)
    if (state && state.spawned && !state.ended) return
    if (state && state.ended) break
    await delay(100)
  }
  const state = states.get(name)
  throw new Error(`bot failed during serialized login: ${name} ${JSON.stringify(state)}`)
}

async function main () {
  // Minecraft 26.3 + the current Mineflayer patch has a race when several
  // clients perform initial position sync at once. Fully finish one login
  // before creating the next client, then leave a short quiet period.
  for (const name of names) {
    createBot(name)
    await waitForSpawn(name)
    if (names.length > 1) await delay(1500)
  }

  const failures = names.filter(name => {
    const s = states.get(name)
    return !s.spawned || s.ended || s.errors.length || s.kicked.length
  })

  if (failures.length) {
    for (const name of failures) {
      const s = states.get(name)
      console.error(JSON.stringify({ name, ...s }))
    }
    throw new Error(`failed to keep requested bot(s) online: ${failures.join(', ')}`)
  }

  console.log(`READY ${names.length}/${names.length} on ${TARGET}:${port} as ${names.join(',')}`)
  const endAt = Date.now() + durationMs
  while (Date.now() < endAt) {
    const ended = names.filter(name => states.get(name).ended)
    if (ended.length) throw new Error(`bots disconnected early: ${ended.join(', ')}`)
    await delay(Math.min(5000, endAt - Date.now()))
  }
  console.log('HOLD COMPLETE')
}

main()
  .then(() => { process.exitCode = 0 })
  .catch(err => {
    console.error(err && err.stack ? err.stack : String(err))
    process.exitCode = 1
  })
  .finally(async () => {
    for (const bot of bots) {
      try { bot.quit('keepalive smoke complete') } catch (_) {}
    }
    await delay(500)
  })
