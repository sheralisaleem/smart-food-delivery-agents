"""base.py - common agent interface, internal-state helper and the shared utility function."""
from __future__ import annotations
from dataclasses import dataclass, field
from environment import TRAFFIC_SCORE

DEFAULT_WEIGHTS = {"time": 0.50, "distance": 0.15, "traffic": 0.15, "cost": 0.20}
LATE_PENALTY = 3.0


@dataclass
class Decision:
    route: str                                   # the action: which route to take
    reason: str                                  # one-line explanation of why
    plan: list = field(default_factory=list)     # ordered subtasks (hierarchical agent)
    flags: list = field(default_factory=list)    # warnings, e.g. "goal at risk"


class Agent:
    name = "Agent"

    def reset(self):                             # clear short-term memory before each delivery
        pass

    def observe(self, percept):                  # perception update
        pass

    def decide(self, percept) -> Decision:       # choose the action
        raise NotImplementedError

    def learn(self, percept, decision, outcome):  # feedback after the delivery
        pass


class StatefulAgent(Agent):
    """Keeps an internal state: order status, current route, weather and the LAST KNOWN traffic
    of every route (so a missing live reading does not blind the agent)."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = {"order_status": "new", "current_route": None, "weather": None, "traffic": {}}

    def observe(self, p):
        st = self.state
        st["weather"] = p.weather
        for r in p.routes:
            if r.traffic is not None:
                st["traffic"][r.name] = r.traffic
        st["order_status"] = {"accept": "accepted", "pickup": "picked_up"}.get(p.stage, st["order_status"])

    def traffic_of(self, r):
        """Live reading if available, otherwise the remembered one, otherwise assume 'normal'."""
        return r.traffic or self.state["traffic"].get(r.name, "normal")

    def commit(self, route):
        self.state["current_route"] = route
        self.state["order_status"] = "en_route"


def utility(eta, distance_km, traffic, cost, deadline, w=DEFAULT_WEIGHTS, late_penalty=LATE_PENALTY):
    """Higher is better. Every factor is scaled to about 0..1, weighted, and subtracted;
    arriving after the deadline adds a large extra penalty that grows with the lateness."""
    loss = (w["time"] * eta / deadline + w["distance"] * distance_km / 10
            + w["traffic"] * TRAFFIC_SCORE[traffic] + w["cost"] * cost / 100)
    if eta > deadline:
        loss += late_penalty * (1 + (eta - deadline) / deadline)
    return -loss
