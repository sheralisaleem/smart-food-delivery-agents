"""Agent 2 - Model-Based Reflex Agent.
Same kind of IF-THEN rules, but they fire on an INTERNAL STATE (current route, traffic per route,
weather, order status) that is updated from every percept - so a missing live reading is
replaced by the last known value instead of being ignored."""
from base import StatefulAgent, Decision
from environment import TRAFFIC_RANK


class ModelBasedReflexAgent(StatefulAgent):
    name = "2. Model-Based Reflex"

    def decide(self, p):
        st = self.state                                           # 1) state was updated by observe()
        traffic = {r.name: self.traffic_of(r) for r in p.routes}  # 2) rules read the STATE, not the raw percept
        remembered = [r.name for r in p.routes if r.traffic is None]
        short = min(p.routes, key=lambda r: r.distance_km)
        lights = [r for r in p.routes if traffic[r.name] == "light"]

        if st["current_route"] and traffic[st["current_route"]] != "heavy":
            route, why = st["current_route"], "R0: already on a route that is not heavy -> keep it"
        elif traffic[short.name] == "heavy":
            alts = [r for r in p.routes if r.name != short.name]
            route = min(alts, key=lambda r: (TRAFFIC_RANK[traffic[r.name]], r.distance_km)).name
            why = f"R1: state says {short.name} is heavy -> lightest alternative"
        elif st["weather"] == "rain" and traffic[short.name] == "normal" and lights:
            route, why = min(lights, key=lambda r: r.distance_km).name, "R2: rain + normal traffic -> light route"
        else:
            route, why = short.name, "R3: otherwise shortest route"

        if remembered:
            why += f" (used REMEMBERED traffic for {', '.join(remembered)}: live feed down)"
        self.commit(route)                                        # 3) action updates the state
        return Decision(route, why + f" | state: status={st['order_status']}, weather={st['weather']}, traffic={traffic}")
