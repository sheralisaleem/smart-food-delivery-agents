"""Agent 1 - Simple Reflex Agent.
Decides ONLY from the current percept with fixed IF-THEN (condition-action) rules.
No memory, no deadline reasoning, no cost reasoning."""
from base import Agent, Decision
from environment import TRAFFIC_RANK


def shortest(p):
    return min(p.routes, key=lambda r: r.distance_km)


def lightest_alternative(p, avoid):
    """Lightest traffic among the OTHER routes whose live reading is available right now."""
    known = [r for r in p.routes if r.name != avoid.name and r.traffic is not None]
    return min(known, key=lambda r: (TRAFFIC_RANK[r.traffic], r.distance_km)) if known else avoid


# (rule text, condition(percept), action(percept) -> route); the first matching rule fires
RULES = [
    ("R1: IF shortest route is HEAVY THEN take the lightest-traffic alternative",
     lambda p: shortest(p).traffic == "heavy",
     lambda p: lightest_alternative(p, shortest(p))),
    ("R2: IF RAIN and shortest route is NORMAL and a LIGHT route exists THEN take the light route",
     lambda p: p.weather == "rain" and shortest(p).traffic == "normal"
               and any(r.traffic == "light" for r in p.routes),
     lambda p: min((r for r in p.routes if r.traffic == "light"), key=lambda r: r.distance_km)),
    ("R3: OTHERWISE take the shortest route",
     lambda p: True,
     shortest),
]


class SimpleReflexAgent(Agent):
    name = "1. Simple Reflex"

    def decide(self, p):
        for text, condition, action in RULES:
            if condition(p):
                return Decision(action(p).name, text)
