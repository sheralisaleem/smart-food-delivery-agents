"""Agent 7 - Contextual Agent.
Collects CONTEXT (time of day, customer type, food type, live road alerts, road attributes + weather),
interprets it, and lets it change both the predicted delivery time and the importance of each factor
before choosing a route with the utility function."""
from base import StatefulAgent, Decision, utility, DEFAULT_WEIGHTS, LATE_PENALTY
from environment import OVERHEAD_MIN, travel_minutes, route_cost

EXPECTED_ALERT_DELAY = {"accident": 10, "road_works": 6, "procession": 12}   # what the agent believes an alert costs


class ContextualAgent(StatefulAgent):
    name = "7. Contextual"

    def decide(self, p):
        c = p.context
        # 1) collect + interpret context -> adapt the weights (what matters in THIS delivery)
        w, late_penalty, notes = dict(DEFAULT_WEIGHTS), LATE_PENALTY, []
        if c.food == "hot":
            w["time"] *= 1.5
            notes.append("hot food: time weighs more")
        if c.customer == "vip":
            w["cost"] *= 0.3
            late_penalty *= 2
            notes.append("VIP: cost matters less, lateness penalised x2")
        # 2) use context to correct the predicted travel time of every route
        scores = {}
        for r in p.routes:
            traffic = self.traffic_of(r)
            tt = travel_minutes(r.distance_km, traffic, p.weather)
            if p.weather == "rain" and r.underpass:
                tt *= 1.30
                notes.append(f"rain + underpass on {r.name}: x1.3")
            if c.time_of_day == "rush_hour" and traffic != "light":
                tt *= 1.10
            tt += sum(EXPECTED_ALERT_DELAY[a] for n, a in c.alerts if n == r.name)
            eta = OVERHEAD_MIN + tt
            scores[r.name] = (utility(eta, r.distance_km, traffic, route_cost(r.distance_km, r.toll),
                                      p.deadline_min, w, late_penalty), eta)
        if c.time_of_day == "rush_hour":
            notes.append("rush hour: +10% on busy routes")
        notes += [f"alert on {n}: {a}" for n, a in c.alerts]
        best = max(scores, key=lambda n: scores[n][0])
        self.commit(best)
        etas = ", ".join(f"{n}={scores[n][1]:.1f}" for n in sorted(scores))
        return Decision(best, f"Context-adjusted ETA ({etas} min) -> {best} | context used: "
                              + ("; ".join(dict.fromkeys(notes)) or "none"))
