"""Agent 3 - Goal-Based Agent.
GOAL: deliver the order successfully within the required time.
For each candidate route it PREDICTS the delivery time and TESTS it against the goal.
It is a satisficer: the first route that achieves the goal is good enough (cost/comfort are ignored)."""
from base import StatefulAgent, Decision
from environment import nominal_eta


class GoalBasedAgent(StatefulAgent):
    name = "3. Goal-Based"

    def decide(self, p):
        tried = []
        for r in sorted(p.routes, key=lambda r: r.distance_km):          # simplest (shortest) route first
            eta = nominal_eta(r.distance_km, self.traffic_of(r), p.weather)   # predict the result
            tried.append((r.name, eta))
            if eta <= p.deadline_min:                                    # goal test
                self.commit(r.name)
                return Decision(r.name, f"Goal test passed: predicted {eta:.1f} min <= {p.deadline_min} min "
                                        f"(checked {', '.join(f'{n}={e:.1f}' for n, e in tried)})")
        name, eta = min(tried, key=lambda t: t[1])                       # no route achieves the goal
        self.commit(name)
        return Decision(name, f"No route meets {p.deadline_min} min; fastest predicted is {eta:.1f} min",
                        flags=["goal at risk"])
