"""Architecture diagrams for agents 5-7 and the runner that draws all seven."""
import os
from diagram_lib import Diagram, frame
from diagrams_1_4 import ACT, simple_reflex, model_based, goal_based, utility_based


def learning(path):
    d = Diagram("Agent 5: Learning Agent", "Key components (purple): critic, learning element and problem generator - feedback improves future decisions")
    frame(d, "LEARNING AGENT", ["INPUT /", "PERCEPTION", "", "traffic, weather,", "distance, deadline"], ACT)
    d.box("critic", 48, 43, 21, 13, ["CRITIC", "", "compares actual", "delivery time with", "the expected time"], "key")
    d.box("learn", 74, 43, 21, 13, ["LEARNING ELEMENT", "", "updates learned", "delay factors for", "each route/weather"], "key")
    d.box("perf", 48, 26.5, 47, 11, ["PERFORMANCE ELEMENT", "", "best-utility route, using the learned delay factors"])
    d.box("pg", 58, 11, 28, 9, ["PROBLEM GENERATOR", "", "sometimes tries another route (training)"], "key")
    d.arrow((19.0, 50), (47.7, 50), "feedback: actual delivery result", dy=1.4)
    d.arrow(d.pt("critic", "r"), d.pt("learn", "l"), "error", dy=1.3)
    d.arrow((84.5, 42.7), (84.5, 37.8), "learned factors", dx=-9, dy=0)
    d.arrow((72, 20.3), (72, 26.2), "exploration", dx=8, dy=0)
    d.arrow(d.pt("perc", "r"), d.pt("perf", "l"), "percept")
    d.arrow(d.pt("perf", "r"), d.pt("act", "l"), "action")
    d.save(path)


def hierarchical(path):
    d = Diagram("Agent 6: Hierarchical Agent", "Key component (purple): main goal broken into subgoals, each with its own sub-controller and time budget")
    ys = {"s1": 44.2, "s2": 35.4, "s3": 26.6, "s4": 17.8, "s5": 9.0}
    frame(d, "HIERARCHICAL AGENT", ["INPUT /", "PERCEPTION", "", "traffic, weather,", "distance, deadline"], ACT,
          py=ys["s2"] + 2.9, ay=ys["s4"] + 2.9)
    d.box("goal", 48, 52.5, 47, 6, ["MAIN GOAL: deliver the order on time"], "key", fs=10)
    labels = {"s1": ["1. Accept order"], "s2": ["2. Choose route", "best utility in time budget"],
              "s3": ["3. Pick up food"], "s4": ["4. Deliver order"], "s5": ["5. Confirm delivery"]}
    for key, y in ys.items():
        d.box(key, 48, y, 26, 5.8, labels[key], "key" if key == "s2" else "dec", fs=9)
    d.arrow((61, 52.2), (61, 50.3), "decompose", dx=7, dy=0)
    for a, b in [("s1", "s2"), ("s2", "s3"), ("s3", "s4"), ("s4", "s5")]:
        d.arrow(d.pt(a, "b"), d.pt(b, "t"))
    d.box("mon", 79, 29, 17, 19, ["PLAN + MONITOR", "", "each subgoal has", "its own small", "controller and a", "time budget; the", "goal is flagged", "'at risk' if no", "route fits"], "dec", fs=8.5)
    d.arrow(d.pt("s2", "r"), (78.7, ys["s2"] + 2.9), both=True, ls="--")
    d.arrow(d.pt("perc", "r"), d.pt("s2", "l"), "percept")
    d.arrow(d.pt("s4", "r"), d.pt("act", "l"), "route taken", dy=1.5)
    d.save(path)


def contextual(path):
    d = Diagram("Agent 7: Contextual Agent", "Key component (purple): context - collected, interpreted, and used to adapt the decision")
    frame(d, "CONTEXTUAL AGENT", ["INPUT /", "PERCEPTION", "", "traffic, weather,", "distance, deadline"], ACT, py=26, ay=26)
    d.box("ctx", 48, 40, 47, 16, ["CONTEXT COLLECTOR", "", "time of day (rush hour) - customer type (VIP) - food type (hot)",
                                  "live road alerts - road attributes (underpass) + weather"], "key")
    d.box("interp", 48, 18, 21, 16, ["INTERPRET CONTEXT", "", "corrects each route's", "time (rain+underpass,", "rush hour, alerts) and", "re-weights the factors"], "key", fs=9)
    d.box("util", 74, 18, 21, 16, ["CONTEXT-AWARE", "UTILITY", "", "U(route) with adaptive", "weights; pick best U"])
    d.arrow((19.0, 50), (47.7, 50), "context", dy=1.4)
    d.arrow(d.pt("perc", "r"), d.pt("interp", "l"), "percept")
    d.arrow((58.5, 39.7), (58.5, 34.3), "context", dx=-6, dy=0)
    d.arrow(d.pt("interp", "r"), d.pt("util", "l"))
    d.arrow(d.pt("util", "r"), d.pt("act", "l"), "action")
    d.note(71.5, 12.5, "same utility idea as agent 4, but the situation around the order changes the numbers")
    d.save(path)


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagrams")
    os.makedirs(out, exist_ok=True)
    for i, (name, fn) in enumerate([("simple_reflex", simple_reflex), ("model_based_reflex", model_based),
                                    ("goal_based", goal_based), ("utility_based", utility_based),
                                    ("learning", learning), ("hierarchical", hierarchical),
                                    ("contextual", contextual)], 1):
        fn(os.path.join(out, f"agent{i}_{name}.png"))


if __name__ == "__main__":
    main()
