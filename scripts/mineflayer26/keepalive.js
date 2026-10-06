#!/usr/bin/env node
'use strict'

const path = require('path')

const repoRoot = path.resolve(__dirname, '..', '..')
const stackRoot = path.resolve(process.env.MF26_STACK || path.join(repoRoot, 'dist', 'mineflayer-26.3-src'))
const mineflayer = require(path.join(stackRoot, 'mineflayer'))

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
if (names.length !== 4 || new Set(names).size !== 4) {
  console.error('Exactly four unique bot names are required')
  process.exit(2)
}
if (!Number.isFinite(durationMs) || durationMs < 30000 || durationMs > 300000) {
  console.error('MF26_DURATION_MS must be between 30000 and 300000 for the GitHub smoke test')
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

async function main () {
  names.forEach(createBot)
  const deadline = Date.now() + spawnTimeoutMs

  while (Date.now() < deadline) {
    if (names.every(name => states.get(name).spawned && !states.get(name).ended)) break
    if (names.some(name => states.get(name).ended)) break
    await delay(100)
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
    throw new Error(`failed to keep all four bots online: ${failures.join(', ')}`)
  }

  console.log(`READY 4/4 on ${TARGET}:${port} as ${names.join(',')}`)
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
