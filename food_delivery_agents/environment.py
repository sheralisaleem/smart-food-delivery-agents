"""environment.py - the shared world used by all seven agents.

Two views of the world are kept apart on purpose:
  * Situation = the TRUE world (only the simulator uses it, to judge a decision afterwards)
  * Percept   = what an agent is allowed to SENSE (a live traffic reading can be missing)
"""
from __future__ import annotations
from dataclasses import dataclass

# ---- nominal model: what the live traffic feed lets an agent predict -------------------------
SPEED_KMH = {"light": 40, "normal": 30, "heavy": 12}    # km/h for each traffic level
RAIN_FACTOR = 0.8                                        # rain slows every route by 20 %
OVERHEAD_MIN = 7                                         # pick-up wait (5) + hand-over/confirm (2)
FUEL_RS_PER_KM = 8
TRAFFIC_SCORE = {"light": 0.0, "normal": 0.5, "heavy": 1.0}
TRAFFIC_RANK = {"light": 0, "normal": 1, "heavy": 2}


def travel_minutes(distance_km, traffic, weather):
    speed = SPEED_KMH[traffic] * (RAIN_FACTOR if weather == "rain" else 1.0)
    return distance_km / speed * 60


def nominal_eta(distance_km, traffic, weather):
    return OVERHEAD_MIN + travel_minutes(distance_km, traffic, weather)


def route_cost(distance_km, toll):
    return distance_km * FUEL_RS_PER_KM + toll


# ---- what an agent can perceive ---------------------------------------------------------------
@dataclass(frozen=True)
class Context:
    time_of_day: str = "afternoon"     # "rush_hour" | "afternoon" | "night"
    customer: str = "regular"          # "regular" | "vip"
    food: str = "standard"             # "standard" | "hot"
    alerts: tuple = ()                 # live road alerts, e.g. (("C", "accident"),)


@dataclass(frozen=True)
class Route:                           # TRUE state of a route
    name: str
    distance_km: float
    traffic: str                       # "light" | "normal" | "heavy"
    toll: int = 0                      # Rs
    underpass: bool = False            # static road attribute (floods when it rains)


@dataclass(frozen=True)
class RouteView:                       # what an agent senses; traffic is None if the feed is down
    name: str
    distance_km: float
    traffic: str | None
    toll: int
    underpass: bool


@dataclass(frozen=True)
class Percept:
    stage: str                         # "accept" (order arrives) or "pickup" (decision time)
    order_id: str
    urgent: bool
    deadline_min: int
    weather: str                       # "clear" | "rain"
    routes: tuple
    context: Context


@dataclass(frozen=True)
class Situation:                       # the TRUE world for one delivery
    name: str
    order_id: str
    weather: str
    urgent: bool
    deadline_min: int
    routes: tuple
    context: Context
    feed_down_at_pickup: tuple = ()    # routes whose live traffic feed is down at decision time

    def percept(self, stage):
        down = self.feed_down_at_pickup if stage == "pickup" else ()
        views = tuple(RouteView(r.name, r.distance_km, None if r.name in down else r.traffic,
                                r.toll, r.underpass) for r in self.routes)
        return Percept(stage, self.order_id, self.urgent, self.deadline_min,
                       self.weather, views, self.context)


# ---- ground truth: the simulator that judges every decision -----------------------------------
ALERT_DELAY_MIN = {"accident": 12, "road_works": 8, "procession": 15}   # true extra minutes


def hidden_factor(route, weather):
    """Real effects the live traffic feed does NOT show. Agents can only discover them from
    history (learning agent) or infer them from road attributes (contextual agent)."""
    f = 1.0
    if route.name == "A" and route.traffic == "heavy":
        f *= 1.30                      # market spill-over: jams are worse than reported
    if route.underpass and weather == "rain":
        f *= 1.40                      # underpass waterlogs in rain
    if route.toll:
        f *= 0.95                      # toll road is slightly faster than reported
    return f


@dataclass(frozen=True)
class Outcome:
    route: str
    minutes: float                     # true total delivery time
    on_time: bool
    late_by: float
    cost: float


def execute(s: Situation, route_name, rng=None) -> Outcome:
    """Carry out the delivery on the chosen route and report what really happened."""
    r = next(x for x in s.routes if x.name == route_name)
    t = travel_minutes(r.distance_km, r.traffic, s.weather) * hidden_factor(r, s.weather)
    if s.context.time_of_day == "rush_hour" and r.traffic != "light":
        t *= 1.10
    t += sum(ALERT_DELAY_MIN[a] for n, a in s.context.alerts if n == route_name)
    if rng is not None:                # noise is used for past deliveries, not for the 3 tests
        t *= rng.gauss(1.0, 0.05)
    total = OVERHEAD_MIN + t
    return Outcome(route_name, total, total <= s.deadline_min,
                   max(0.0, total - s.deadline_min), route_cost(r.distance_km, r.toll))


# ---- the three required test situations (same road network, different conditions) ------------
def _net(a, b, c):
    return (Route("A", 3.5, a), Route("B", 5.5, b, 0, True), Route("C", 4.5, c, 60))


def test_situations():
    return [
        Situation("Test 1 - normal traffic, good weather", "ORD-101", "clear", False, 35,
                  _net("normal", "normal", "normal"), Context()),
        Situation("Test 2 - heavy traffic, multiple routes", "ORD-102", "clear", False, 30,
                  _net("heavy", "light", "normal"), Context(alerts=(("C", "accident"),)),
                  feed_down_at_pickup=("B",)),
        Situation("Test 3 - heavy traffic, rain, urgent", "ORD-103", "rain", True, 20,
                  _net("heavy", "light", "normal"), Context("rush_hour", "vip", "hot")),
    ]


# ---- random situations: past deliveries for training and a held-out benchmark ----------------
ROAD_NETWORK = (("A", 3.5, 0, False), ("B", 5.5, 0, True), ("C", 4.5, 60, False))


def random_situation(rng, i=0) -> Situation:
    urgent = rng.random() < 0.3
    routes = tuple(Route(n, km, rng.choices(["light", "normal", "heavy"], [0.3, 0.4, 0.3])[0], toll, up)
                   for n, km, toll, up in ROAD_NETWORK)
    ctx = Context(rng.choice(["rush_hour", "afternoon", "night"]),
                  "vip" if rng.random() < 0.15 else "regular",
                  "hot" if rng.random() < 0.4 else "standard",
                  ((rng.choice("ABC"), rng.choice(list(ALERT_DELAY_MIN))),) if rng.random() < 0.25 else ())
    return Situation(f"random-{i}", f"ORD-{i}", "rain" if rng.random() < 0.3 else "clear", urgent,
                     rng.randint(18, 24) if urgent else rng.randint(28, 40), routes, ctx,
                     (rng.choice("ABC"),) if rng.random() < 0.2 else ())
