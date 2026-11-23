"""Deterministic model of two consumers. Run with Python 3.8 or later."""
from collections import Counter
from dataclasses import dataclass

@dataclass
class Event:
    version: int
    state: str
    template: int = 1
    attempts: int = 0
    visible_at: int = 0
    delivery: str = "ready"

events = [Event(1, "accepted"), Event(2, "packed"), Event(3, "shipped", 2)]
ledger = {}
attempts = Counter()
supported = {1}

def receive(event, worker, now, crash=False, pause=False):
    assert event.delivery == "ready" and now >= event.visible_at
    event.attempts += 1
    attempts[event.version] += 1
    event.visible_at = now + 5
    print(f"t={now:02} {worker} receives e{event.version}, attempt {event.attempts}")
    if pause or event.template not in supported:
        return
    # A single insertion models a conditional write keyed by stable event ID.
    key = ("O-17", event.version)
    existed = key in ledger
    ledger.setdefault(key, event.state)
    print("  existing ledger row" if existed else "  inserted ledger row")
    if not crash:
        event.delivery = "acked"

def expire(now):
    for event in events:
        if event.delivery == "ready" and event.attempts >= 3 and now >= event.visible_at:
            event.delivery = "dead"
            print(f"t={now:02} e{event.version} enters dead-letter state")

projection = []
for event in events:
    assert event.version == len(projection) + 1
    projection.append(event.state)
print("Shard reader:", " -> ".join(projection))
first, second, third = events
receive(second, "A", 0, crash=True)
receive(first, "B", 1, pause=True)
receive(third, "B", 2)
receive(second, "B", 5)
receive(first, "A", 6)
receive(third, "A", 7)
receive(third, "B", 12)
expire(17)
assert third.delivery == "dead" and len(ledger) == 2
supported.add(2)
third.delivery, third.attempts = "ready", 0
receive(third, "A", 18)
assert all(e.delivery == "acked" for e in events)
assert len(ledger) == 3 and attempts == {1: 2, 2: 2, 3: 4}
print("PASS: ordered projection, three unique rows, seven delivery attempts")
