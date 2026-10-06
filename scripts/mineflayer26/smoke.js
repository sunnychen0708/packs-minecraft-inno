#!/usr/bin/env node
'use strict'

const fs = require('fs')
const path = require('path')

const here = __dirname
const repoRoot = path.resolve(here, '..', '..')
const stackRoot = path.resolve(process.env.MF26_STACK || path.join(repoRoot, 'dist', 'mineflayer-26.3-src'))
const mineflayer = require(path.join(stackRoot, 'mineflayer'))

const host = process.env.MF26_HOST || '127.0.0.1'
const port = Number(process.env.MF26_PORT || 25565)
const names = (process.env.MF26_BOTS || 'BotTester,BotOp,BotOp2').split(',').map(x => x.trim()).filter(Boolean)
const spawnTimeoutMs = Number(process.env.MF26_SPAWN_TIMEOUT_MS || 45000)
const dwellMs = Number(process.env.MF26_DWELL_MS || 7000)
const outPath = path.resolve(process.env.MF26_SMOKE_OUT || path.join(repoRoot, 'dist', 'mineflayer-26.3-smoke.json'))

const state = {
  target: { host, port, version: '26.3' },
  bots: {},
  checks: {},
  startedAt: new Date().toISOString()
}

function delay (ms) { return new Promise(resolve => setTimeout(resolve, ms)) }

function fail (name, detail) {
  state.checks[name] = { ok: false, detail }
  throw new Error(`${name}: ${detail}`)
}

function pass (name, detail = '') {
  state.checks[name] = { ok: true, detail }
}

function packetCounter (bot, s) {
  bot._client.on('packet', (_data, meta) => {
    s.packets[meta.name] = (s.packets[meta.name] || 0) + 1
  })
}

function createTrackedBot (username) {
  const s = state.bots[username] = { spawned: false, ended: false, packets: {}, errors: [], kicked: [] }
  const bot = mineflayer.createBot({ host, port, username, auth: 'offline', version: '26.3' })
  packetCounter(bot, s)
  bot.on('spawn', () => { s.spawned = true })
  bot.on('error', err => s.errors.push(String(err && err.stack ? err.stack : err)))
  bot.on('kicked', reason => s.kicked.push(typeof reason === 'string' ? reason : JSON.stringify(reason)))
  bot.on('end', reason => { s.ended = true; s.endReason = reason })
  return bot
}

async function waitForSpawn (bots) {
  const deadline = Date.now() + spawnTimeoutMs
  while (Date.now() < deadline) {
    if (bots.every(b => state.bots[b.username].spawned)) return
    if (bots.some(b => state.bots[b.username].ended)) break
    await delay(100)
  }
  const detail = bots.map(b => `${b.username}: spawned=${state.bots[b.username].spawned} ended=${state.bots[b.username].ended}`).join(', ')
  fail('all bots spawn', detail)
}

function verifyChunks (bots) {
  for (const bot of bots) {
    const p = bot.entity.position.floored()
    const block = bot.blockAt(p)
    if (!block) fail(`${bot.username} chunk loaded`, `blockAt(${p.x},${p.y},${p.z}) returned null`)
    const maps = state.bots[bot.username].packets.map_chunk || 0
    if (maps < 1) fail(`${bot.username} map_chunk packets`, `saw ${maps}`)
    pass(
      `${bot.username} chunk loaded`,
      `${block.name}; map_chunk=${maps}; update_light=${state.bots[bot.username].packets.update_light || 0}`
    )
  }
}

function verifyPlayerLists (bots) {
  for (const bot of bots) {
    const missing = bots.map(b => b.username).filter(name => !bot.players[name])
    if (missing.length) fail(`${bot.username} player list`, `missing ${missing.join(', ')}`)
    pass(`${bot.username} player list`, Object.keys(bot.players).sort().join(', '))
  }
}

async function verifyEntityMovement (bots) {
  if (bots.length < 2) {
    pass('entity movement', 'skipped: fewer than 2 bots')
    return
  }

  const observer = bots[0]
  const mover = bots[1]
  const tracked = () => observer.players[mover.username] && observer.players[mover.username].entity
  let entity = tracked()
  if (!entity) fail('entity movement', `${observer.username} has no entity for ${mover.username}`)
  const before = entity.position.clone()

  mover.setControlState('forward', true)
  await delay(1400)
  mover.setControlState('forward', false)
  await delay(900)

  entity = tracked()
  if (!entity) fail('entity movement', `${mover.username} entity disappeared`)
  const moved = entity.position.distanceTo(before)
  if (moved < 0.15) fail('entity movement', `observer saw only ${moved.toFixed(3)} blocks of movement`)
  pass('entity movement', `${observer.username} saw ${mover.username} move ${moved.toFixed(3)} blocks`)
}

function verifyConnectionsStillAlive (bots) {
  for (const bot of bots) {
    const s = state.bots[bot.username]
    if (s.ended) fail(`${bot.username} stays connected`, s.endReason || 'connection ended')
    if (s.errors.length) fail(`${bot.username} protocol errors`, s.errors.join('\n'))
    if (s.kicked.length) fail(`${bot.username} not kicked`, s.kicked.join('\n'))
    pass(`${bot.username} stays connected`, `position=${bot.entity.position}`)
  }
}

async function optionalMutationTests (bot) {
  if (process.env.MF26_MUTATION_TESTS !== '1') {
    pass('player-action mutation tests', 'skipped (set MF26_MUTATION_TESTS=1 on an OP test bot)')
    return
  }

  const base = bot.entity.position.floored()
  const target = base.offset(2, 0, 0)

  bot.chat(`/gamemode survival ${bot.username}`)
  bot.chat(`/setblock ${target.x} ${target.y} ${target.z} minecraft:dirt`)
  await delay(700)

  const block = bot.blockAt(target)
  if (!block || block.name !== 'dirt') fail('dig action ids', `fixture is ${block ? block.name : 'unloaded'}`)
  await bot.dig(block)
  await delay(350)

  const after = bot.blockAt(target)
  if (!after || after.name !== 'air') fail('dig action ids', `after dig: ${after ? after.name : 'unloaded'}`)
  pass('dig action ids', 'start/finish destroy removed the dirt fixture')

  bot.chat(`/item replace entity ${bot.username} weapon.mainhand with minecraft:bow`)
  await delay(700)
  const beforeBow = bot.heldItem && bot.heldItem.name
  if (beforeBow !== 'bow') fail('release-use action id', `expected bow in main hand, got ${beforeBow}`)

  bot.activateItem()
  await delay(350)
  bot.deactivateItem()
  await delay(700)

  const afterBow = bot.heldItem && bot.heldItem.name
  if (afterBow !== 'bow') {
    fail('release-use action id', `held item changed to ${afterBow || 'empty'} (old 26.2 id can drop it on 26.3)`)
  }
  pass('release-use action id', 'bow remained in main hand after deactivateItem()')
}

async function main () {
  fs.mkdirSync(path.dirname(outPath), { recursive: true })
  const bots = names.map(createTrackedBot)

  try {
    await waitForSpawn(bots)
    pass('all bots spawn', names.join(', '))

    await delay(2500)
    verifyChunks(bots)
    verifyPlayerLists(bots)
    await verifyEntityMovement(bots)

    await delay(dwellMs)
    verifyConnectionsStillAlive(bots)
    await optionalMutationTests(bots[0])
    state.ok = true
  } catch (err) {
    state.ok = false
    state.failure = String(err && err.stack ? err.stack : err)
    process.exitCode = 1
  } finally {
    for (const bot of bots) {
      try {
        bot.quit('26.3 smoke complete')
      } catch (_) {}
    }
    state.finishedAt = new Date().toISOString()
    fs.writeFileSync(outPath, JSON.stringify(state, null, 2) + '\n')
    console.log(JSON.stringify(state, null, 2))
  }
}

main().catch(err => {
  console.error(err)
  process.exitCode = 1
})
