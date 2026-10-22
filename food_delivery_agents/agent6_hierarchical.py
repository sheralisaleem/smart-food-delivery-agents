"""Agent 6 - Hierarchical Agent.
The main goal 'deliver the order on time' is broken into subgoals. A top-level controller runs the
subgoals in order; each subgoal has its own small sub-controller and its own time budget.
The 'Choose route' sub-controller must respect the time budget left after the other subgoals."""
from base import StatefulAgent, Decision, utility
from environment import nominal_eta, route_cost

SUBGOALS = ["Accept order", "Choose route", "Pick up food", "Deliver order", "Confirm delivery"]
RESERVED_MIN = {"Pick up food": 5, "Confirm delivery": 2}      # time kept for the other subgoals
SAFETY_MARGIN = 0.10                                           # keep 10 % of the deadline as a buffer


class HierarchicalAgent(StatefulAgent):
    name = "6. Hierarchical"

    # ---- sub-controllers: one per subgoal --------------------------------------------------
    def accept_order(self, p):
        return f"{p.order_id} accepted, deadline {p.deadline_min} min{' (URGENT)' if p.urgent else ''}"

    def choose_route(self, p):
        budget = p.deadline_min * (1 - SAFETY_MARGIN)          # total time we allow ourselves
        options = []
        for r in p.routes:
            traffic = self.traffic_of(r)
            eta = nominal_eta(r.distance_km, traffic, p.weather)
            u = utility(eta, r.distance_km, traffic, route_cost(r.distance_km, r.toll), p.deadline_min)
            options.append((u, r.name, eta))
        fits = [o for o in options if o[2] <= budget]
        flags = [] if fits else ["goal at risk"]
        u, name, eta = max(fits) if fits else min(options, key=lambda o: o[2])
        how = f"best utility among routes within the {budget:.0f}-min budget" if fits else "nothing fits the budget: fastest route"
        return name, eta, how, flags

    # ---- top-level controller -------------------------------------------------------------
    def decide(self, p):
        plan, route, eta, flags = [], None, None, []
        for i, goal in enumerate(SUBGOALS, 1):
            if goal == "Accept order":
                plan.append(f"{i}. {goal}: {self.accept_order(p)}")
            elif goal == "Choose route":
                route, eta, how, flags = self.choose_route(p)
                self.commit(route)
                plan.append(f"{i}. {goal}: route {route} ({how})")
            elif goal == "Pick up food":
                plan.append(f"{i}. {goal}: collect order at restaurant (budget {RESERVED_MIN[goal]} min)")
            elif goal == "Deliver order":
                plan.append(f"{i}. {goal}: ride via {route}, predicted total {eta:.1f} min")
            else:
                plan.append(f"{i}. {goal}: hand over and confirm (budget {RESERVED_MIN[goal]} min)")
        return Decision(route, f"Subgoal 2 chose {route}: {plan[1].split(': ', 1)[1]}", plan, flags)
