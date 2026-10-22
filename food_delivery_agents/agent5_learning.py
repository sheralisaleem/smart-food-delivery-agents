"""Agent 5 - Learning Agent (classic four-part structure).
  Performance element : picks the best-utility route using its LEARNED delay factors
  Critic              : compares what really happened with what it expected
  Learning element    : updates the learned factor for that (route, traffic, weather)
  Problem generator   : while training, sometimes tries another route to gain new experience
Learned knowledge = a multiplier on the published travel time, e.g. 'route B in rain is x1.4'."""
import random
from base import StatefulAgent, Decision, utility
from environment import OVERHEAD_MIN, travel_minutes, route_cost, execute, random_situation


class LearningAgent(StatefulAgent):
    name = "5. Learning"
    EPSILON = 0.25                      # exploration rate (training only)

    def __init__(self, seed=0):
        super().__init__()
        self.factor = {}                # (route, traffic, weather) -> learned multiplier (starts at 1.0)
        self.count = {}
        self.explore = False
        self.rng = random.Random(seed)

    def predicted_eta(self, p, r):
        traffic = self.traffic_of(r)
        f = self.factor.get((r.name, traffic, p.weather), 1.0)
        return OVERHEAD_MIN + travel_minutes(r.distance_km, traffic, p.weather) * f, traffic, f

    def decide(self, p):                # performance element (+ problem generator)
        if self.explore and self.rng.random() < self.EPSILON:
            r = self.rng.choice(p.routes)
            self.commit(r.name)
            return Decision(r.name, "Exploring (problem generator): trying a route to gain experience")
        scores, factors = {}, {}
        for r in p.routes:
            eta, traffic, f = self.predicted_eta(p, r)
            scores[r.name] = utility(eta, r.distance_km, traffic, route_cost(r.distance_km, r.toll), p.deadline_min)
            factors[r.name] = f
        best = max(scores, key=scores.get)
        self.commit(best)
        learned = ", ".join(f"{n} x{factors[n]:.2f}" for n in sorted(factors))
        return Decision(best, f"Best utility with learned delay factors ({learned}) -> {best}")

    def learn(self, p, decision, outcome):          # critic + learning element
        r = next(x for x in p.routes if x.name == outcome.route)
        traffic = self.traffic_of(r)
        expected = travel_minutes(r.distance_km, traffic, p.weather)
        observed = (outcome.minutes - OVERHEAD_MIN) / expected          # critic: reality / expectation
        key = (r.name, traffic, p.weather)
        n = self.count.get(key, 0)
        old = self.factor.get(key, 1.0)
        self.factor[key] = old + (observed - old) / (n + 3)             # learning element: running average
        self.count[key] = n + 1

    def learned_table(self):
        """What the agent has learned: multiplier on the published travel time per situation."""
        lines = [f"{'Route':<7}{'Traffic':<9}{'Weather':<9}{'Learned x':<11}{'Samples':<8}"]
        for key, f in sorted(self.factor.items()):
            lines.append(f"{key[0]:<7}{key[1]:<9}{key[2]:<9}{f:<11.2f}{self.count[key]:<8}")
        return "\n".join(lines)

    def train(self, episodes=600, seed=1):
        """Gain experience from simulated PAST deliveries (with natural randomness)."""
        rng = random.Random(seed)
        self.explore = True
        for i in range(episodes):
            s = random_situation(rng, i)
            self.reset()
            self.observe(s.percept("accept"))
            p = s.percept("pickup")
            self.observe(p)
            d = self.decide(p)
            self.learn(p, d, execute(s, d.route, rng))
        self.explore = False
        self.reset()
