"""Agent 4 - Utility-Based Agent.
Compares ALL routes on delivery time, distance, traffic and cost, turns them into ONE utility
number per route, and selects the route with the best (highest) utility."""
from base import StatefulAgent, Decision, utility
from environment import nominal_eta, route_cost


class UtilityBasedAgent(StatefulAgent):
    name = "4. Utility-Based"

    def score(self, p, r):
        traffic = self.traffic_of(r)
        eta = nominal_eta(r.distance_km, traffic, p.weather)
        cost = route_cost(r.distance_km, r.toll)
        return utility(eta, r.distance_km, traffic, cost, p.deadline_min), eta, cost

    def decide(self, p):
        scores = {r.name: self.score(p, r) for r in p.routes}
        best = max(scores, key=lambda n: scores[n][0])
        table = ", ".join(f"{n}: U={scores[n][0]:.2f} ({scores[n][1]:.0f} min, Rs {scores[n][2]:.0f})"
                          for n in sorted(scores))
        self.commit(best)
        return Decision(best, f"Highest utility -> {best} | {table}")
