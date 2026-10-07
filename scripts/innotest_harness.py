"""Shared builder for innotest live-test datapacks.

A suite is a chain of steps. Each step is one function that schedules the next
one. A check counts PASS/FAIL and prints `<PREFIX>_CHECK PASS|FAIL <label>`;
a failing condition with a diff text also prints `<PREFIX>_DIFF <label> <text>`.
At the end the suite prints `<PREFIX>_RESULT PASS|FAIL`.

Bots are driven with the Mineflayer test driver (scripts/mineflayer26/keepalive.js):
`bot(p, action, *args)` sends `tellraw <bot> "MFBOT <name> <seq> <action> ..."` and
waits until the bot acknowledges with `/trigger mfack set <seq>`.

Conditions are execute sub-commands. Chains that start with `in ` or `positioned `
are used as is ("in minecraft:overworld if block ..."); bare conditions get `if`
("score @s x matches 1").
"""
from __future__ import annotations

from pathlib import Path
import json
import shutil

ALLOWED_BOTS = ('SunnyChen', 'penguin0531', 'geena0701', 'Felicitypeng')
# /tick needs permission level 3 and datapack functions run at level 2, so the suite asks the
# runner (console) to change the tick rate: speed() prints <PREFIX>_SPEED <seq> <rate> and waits
# until the runner sets #speed htest to <seq>. Only stretches that do not wait for a bot reply
# may run fast: tick-counted waits would otherwise time out before the bot answers.
FAST_TICK_RATE = 10000


def chained(cond: str) -> str:
    return cond if cond.startswith(('in ', 'positioned ', 'as ', 'at ')) else 'if ' + cond


def negate(cond: str) -> str:
    if not cond.startswith(('in ', 'positioned ', 'as ', 'at ')):
        return 'unless ' + cond
    for a, b in ((' if ', ' unless '), (' unless ', ' if ')):
        if a in cond:
            return cond.replace(a, b, 1)
    raise ValueError(f'cannot negate execute condition: {cond}')


class Suite:
    def __init__(self, ns: str, prefix: str, players: dict[str, str], description: str):
        """players: role -> bot name, e.g. {'a': 'penguin0531'}."""
        assert all(n in ALLOWED_BOTS for n in players.values())
        self.ns = ns
        self.prefix = prefix
        self.players = players
        self.description = description
        self.steps: list[tuple] = []
        self.seq = 0
        self.cleanup_cmds: list[str] = []
        self.default_delay = 10
        self.realtime: list[bool] = []
        self.speed_seq = 0
        self._fast = False
        self._in_bot = False

    # ---- selectors -------------------------------------------------------
    def sel(self, p: str) -> str:
        return f'@a[name={self.players[p]},limit=1]'

    # ---- steps -------------------------------------------------------------
    def step(self, *commands: str, delay: int | None = None, realtime: bool = False) -> None:
        delay = self.default_delay if delay is None else delay
        self.steps.append(('cmd', list(commands), delay))
        self.realtime.append(realtime or self._in_bot)

    def wait(self, label: str, ready: list[str], fail: list[str] | None = None, tries: int = 80, realtime: bool = False) -> None:
        """Poll every 5 ticks until all `ready` conditions hold. Any `fail` condition, or `tries` polls, counts a FAIL."""
        self.steps.append(('wait', label, list(ready), list(fail or []), tries))
        self.realtime.append(realtime or self._in_bot)

    def check(self, label: str, *conditions) -> None:
        """Each condition is a string, or (condition, diff text) to print when it fails."""
        tag = label.replace(' ', '_')
        cmds = ['scoreboard players set #ok htest 1']
        for c in conditions:
            cond, diff = (c if isinstance(c, tuple) else (c, None))
            cmds.append(f'execute {negate(cond)} run scoreboard players set #ok htest 0')
            if diff:
                cmds.append(f'execute {negate(cond)} run say {self.prefix}_DIFF {tag} {diff}')
        cmds += [
            f'execute if score #ok htest matches 1 run say {self.prefix}_CHECK PASS {tag}',
            f'execute unless score #ok htest matches 1 run say {self.prefix}_CHECK FAIL {tag}',
            'execute if score #ok htest matches 1 run scoreboard players add #pass htest 1',
            'execute unless score #ok htest matches 1 run scoreboard players add #fail htest 1',
        ]
        self.step(*cmds)

    def bot(self, p: str, action: str, *args, tries: int = 120, label: str | None = None) -> None:
        """Have bot `p` perform an action itself and wait for its acknowledgement."""
        self.seq += 1
        seq = self.seq
        text = ' '.join(['MFBOT', self.players[p], str(seq), action, *map(str, args)])
        quoted = text.replace('\\', '\\\\').replace('"', '\\"')
        self._in_bot = True
        self.step(f'scoreboard players enable {self.sel(p)} mfack',
                  f'scoreboard players set {self.sel(p)} mfack 0',
                  f'tellraw {self.sel(p)} "{quoted}"', delay=1)
        lab = label or f'{p} {action} {" ".join(map(str, args))}'.strip()
        self.wait(f'bot {lab}', [f'score {self.sel(p)} mfack matches {seq}'],
                  fail=[f'score {self.sel(p)} mfack matches {seq + 100000}'], tries=tries)
        self._in_bot = False

    def speed(self, fast: bool) -> None:
        """Ask the runner to switch the tick rate (fastest or 20) and wait until it has."""
        self.speed_seq += 1
        rate = FAST_TICK_RATE if fast else 20
        self.step(f'say {self.prefix}_SPEED {self.speed_seq} {rate}', delay=1)
        self.wait(f'tick rate {rate}', [f'score #speed htest matches {self.speed_seq}'], tries=1000000)
        self._fast = fast

    def trigger(self, p: str, objective: str, value: int | None = None) -> None:
        """The bot sends /trigger itself, like a player typing it."""
        args = ['trigger', objective] + (['set', str(value)] if value is not None else [])
        self.bot(p, 'cmd', *args)

    def cmdx(self, p: str, tokens: list[str], command: str, label: str | None = None) -> None:
        """The bot sends a command and must then receive a message containing every token."""
        assert all(' ' not in t for t in tokens)
        self.bot(p, 'cmdx', len(tokens), *tokens, command, label=label or f'{p} {command} sees {"+".join(tokens)}')

    def dialog(self, p: str, command: str, label: str | None = None) -> None:
        """Have the bot send a trigger/function command and require a real show_dialog packet."""
        assert command.startswith(('trigger ', 'function '))
        self.bot(p, 'dialog', *command.split(), label=label or f'{p} {command} receives Dialog')

    def tp(self, p: str, x: float, y: float, z: float, yaw: float = 0, pitch: float = 0, dim: str = 'overworld') -> None:
        self.step(f'execute in minecraft:{dim} run tp {self.sel(p)} {x} {y} {z} {yaw} {pitch}', delay=5)

    def cleanup(self, *commands: str) -> None:
        self.cleanup_cmds.extend(commands)

    # ---- write -----------------------------------------------------------
    def write(self, out: Path) -> int:
        if out.exists():
            shutil.rmtree(out)
        fn = out / f'data/{self.ns}/function'
        fn.mkdir(parents=True)
        (out / 'pack.mcmeta').write_text(json.dumps(
            {'pack': {'description': self.description, 'min_format': 121, 'max_format': 121}},
            ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        if self.speed_seq and self._fast:
            self.speed(False)
        self.step(f'execute if score #fail htest matches 0 run say {self.prefix}_RESULT PASS',
                  f'execute unless score #fail htest matches 0 run say {self.prefix}_RESULT FAIL')
        n = len(self.steps)
        for i, s in enumerate(self.steps):
            nxt = f'{self.ns}:step_{i+1}' if i + 1 < n else None
            if s[0] == 'cmd':
                _, commands, delay = s
                lines = list(commands)
                if nxt:
                    lines.append(f'schedule function {nxt} {delay}t replace')
            else:
                _, label, ready, fail, tries = s
                tag = label.replace(' ', '_')
                ok = 'execute ' + ' '.join(chained(c) for c in ready)
                lines = ['scoreboard players add #wait htest 1']
                for f in fail:
                    lines += [f'execute {chained(f)} run say {self.prefix}_CHECK FAIL {tag}',
                              f'execute {chained(f)} run scoreboard players add #fail htest 1',
                              f'execute {chained(f)} run scoreboard players set #wait htest 0',
                              f'execute {chained(f)} run return run schedule function {nxt} 5t replace']
                lines += [f'{ok} run scoreboard players set #wait htest 0',
                          f'{ok} run return run schedule function {nxt} 5t replace',
                          f'execute if score #wait htest matches {tries}.. run say {self.prefix}_CHECK FAIL {tag}_timeout',
                          f'execute if score #wait htest matches {tries}.. run scoreboard players add #fail htest 1',
                          f'execute if score #wait htest matches {tries}.. run scoreboard players set #wait htest 0',
                          f'execute if score #wait htest matches 0 run return run schedule function {nxt} 5t replace',
                          f'schedule function {self.ns}:step_{i} 5t replace']
            (fn / f'step_{i}.mcfunction').write_text('\n'.join(lines) + '\n', encoding='utf-8')
        start = ['scoreboard objectives remove htest', 'scoreboard objectives add htest dummy',
                 'scoreboard objectives add mfack trigger',
                 'scoreboard players set #pass htest 0', 'scoreboard players set #fail htest 0',
                 'scoreboard players set #wait htest 0', 'scoreboard players set #speed htest 0']
        for p in self.players:
            start.append(f'execute unless entity {self.sel(p)} run say {self.prefix}_RESULT FAIL missing_player_{self.players[p]}')
            start.append(f'execute unless entity {self.sel(p)} run return fail')
        start.append(f'function {self.ns}:step_0')
        (fn / 'start.mcfunction').write_text('\n'.join(start) + '\n', encoding='utf-8')
        cleanup = [f'schedule clear {self.ns}:step_{i}' for i in range(n)]
        cleanup += self.cleanup_cmds
        cleanup += ['scoreboard objectives remove mfack', 'scoreboard objectives remove htest',
                    f'say {self.prefix}_CLEANUP DONE']
        (fn / 'cleanup.mcfunction').write_text('\n'.join(cleanup) + '\n', encoding='utf-8')
        return n

    def extra_function(self, out: Path, name: str, lines: list[str]) -> None:
        path = out / f'data/{self.ns}/function/{name}.mcfunction'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
