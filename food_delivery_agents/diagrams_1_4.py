"""Architecture diagrams for agents 1-4."""
from diagram_lib import Diagram, frame

ACT = ["ACTION", "", "ride the", "selected route"]


def simple_reflex(path):
    d = Diagram("Agent 1: Simple Reflex Agent", "Key component (purple): condition-action rules (IF-THEN) on the current percept only")
    frame(d, "SIMPLE REFLEX AGENT", ["INPUT /", "PERCEPTION", "", "current percept", "only: traffic,", "weather, routes"], ACT)
    d.box("rules", 48, 17, 47, 30, ["CONDITION-ACTION RULES (IF-THEN)", "",
          "R1  IF the shortest route is HEAVY", "      THEN take the lightest-traffic route",
          "R2  IF RAIN and shortest route is NORMAL", "      and a LIGHT route exists",
          "      THEN take the light route", "R3  OTHERWISE take the shortest route", "",
          "the first matching rule fires"], "key", align="left")
    d.arrow(d.pt("perc", "r"), d.pt("rules", "l"), "percept")
    d.arrow(d.pt("rules", "r"), d.pt("act", "l"), "action")
    d.note(71.5, 12.5, "no memory - no deadline reasoning - no cost reasoning")
    d.save(path)


def model_based(path):
    d = Diagram("Agent 2: Model-Based Reflex Agent", "Key component (purple): internal state, updated before every decision")
    frame(d, "MODEL-BASED REFLEX AGENT", ["INPUT /", "PERCEPTION", "", "traffic, weather,", "order status", "(a feed may be", "missing)"], ACT, py=26, ay=26)
    d.box("state", 48, 40, 47, 16, ["INTERNAL STATE", "", "current route - traffic of every route (last known)",
                                    "weather - order status (accepted > picked up > en route)"], "key")
    d.box("upd", 48, 18, 21, 16, ["UPDATE STATE", "", "how the world", "evolves + what my", "actions do"])
    d.box("rules", 74, 18, 21, 16, ["RULES ON STATE", "", "R0 keep a good route", "R1 heavy: go around", "R2 rain: light route", "R3 else: shortest"])
    d.arrow(d.pt("perc", "r"), d.pt("upd", "l"), "percept")
    d.arrow((58.5, 34.3), (58.5, 39.7), both=True, dx=8, dy=0)
    d.arrow((84.5, 39.7), (84.5, 34.3), "read state", dx=-7, dy=0)
    d.arrow(d.pt("rules", "r"), d.pt("act", "l"), "action")
    d.note(71.5, 12.5, "remembers the last known traffic when a live reading is missing")
    d.save(path)


def goal_based(path):
    d = Diagram("Agent 3: Goal-Based Agent", "Key component (purple): the goal - deliver the order successfully within the required time")
    frame(d, "GOAL-BASED AGENT", ["INPUT /", "PERCEPTION", "", "traffic, weather,", "distance, deadline"], ACT, py=26, ay=26)
    d.box("goal", 48, 40, 47, 16, ["GOAL", "", "deliver the order successfully within the required time",
                                   "(deadline taken from the order)"], "key")
    d.box("pred", 48, 18, 21, 16, ["PREDICT RESULTS", "", "estimate the delivery", "time (ETA) of each", "route from the state"])
    d.box("test", 74, 18, 21, 16, ["GOAL TEST", "", "ETA <= deadline ?", "take 1st route that", "achieves the goal,", "else fastest + warn"])
    d.arrow(d.pt("perc", "r"), d.pt("pred", "l"), "percept")
    d.arrow(d.pt("pred", "r"), d.pt("test", "l"), "ETAs", dy=1.5)
    d.arrow((84.5, 39.7), (84.5, 34.3), "goal", dx=-4, dy=0)
    d.arrow(d.pt("test", "r"), d.pt("act", "l"), "action")
    d.note(71.5, 12.5, "goal = yes/no only: the first route that makes the deadline is good enough")
    d.save(path)


def utility_based(path):
    d = Diagram("Agent 4: Utility-Based Agent", "Key component (purple): utility function - one score per route, best score wins")
    frame(d, "UTILITY-BASED AGENT", ["INPUT /", "PERCEPTION", "", "traffic, weather,", "distance, toll,", "deadline"], ACT, py=26, ay=26)
    d.box("util", 48, 40, 47, 16, ["UTILITY FUNCTION", "", "U(route) = -( w1×time + w2×distance + w3×traffic + w4×cost )",
                                   "- extra penalty if later than the deadline", "higher U = better trade-off"], "key")
    d.box("pred", 48, 18, 21, 16, ["PREDICT OUTCOMES", "", "time, distance,", "traffic and cost", "of EVERY route"])
    d.box("sel", 74, 18, 21, 16, ["SELECT", "", "route with the", "highest utility", "(argmax U)"])
    d.arrow(d.pt("perc", "r"), d.pt("pred", "l"), "percept")
    d.arrow((58.5, 34.3), (58.5, 39.7), "outcomes", dx=-6, dy=0)
    d.arrow((84.5, 39.7), (84.5, 34.3), "U of each route", dx=-8.5, dy=0)
    d.arrow(d.pt("sel", "r"), d.pt("act", "l"), "action")
    d.note(71.5, 12.5, "trades time against distance, traffic and cost instead of a yes/no goal test")
    d.save(path)
