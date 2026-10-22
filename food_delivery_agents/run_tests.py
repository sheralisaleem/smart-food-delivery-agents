"""run_tests.py - runs all seven agents on the three required delivery situations.
Usage:  python run_tests.py          (compact tables)
        python run_tests.py --why    (also print each agent's reasoning and the hierarchical plan)
Files are written to results/ (test_results.txt, test_results.csv, decision_log.txt, learned_factors.txt)."""
import csv
import os
import sys

from environment import test_situations, execute
from agent1_simple_reflex import SimpleReflexAgent
from agent2_model_based import ModelBasedReflexAgent
from agent3_goal_based import GoalBasedAgent
from agent4_utility_based import UtilityBasedAgent
from agent5_learning import LearningAgent
from agent6_hierarchical import HierarchicalAgent
from agent7_contextual import ContextualAgent

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def build_agents(train=True):
    learner = LearningAgent()
    if train:
        learner.train()                      # experience from 600 simulated past deliveries
    return [SimpleReflexAgent(), ModelBasedReflexAgent(), GoalBasedAgent(), UtilityBasedAgent(),
            learner, HierarchicalAgent(), ContextualAgent()]


def run_one(agent, s):
    """Perceive -> decide -> act in the environment. Returns (decision, true outcome)."""
    agent.reset()
    agent.observe(s.percept("accept"))       # order arrives
    p = s.percept("pickup")                  # decision time (a traffic feed may be down)
    agent.observe(p)
    d = agent.decide(p)
    return d, execute(s, d.route)


def conditions(s):
    traffic = " ".join(f"{r.name}={r.traffic}" for r in s.routes)
    extra = []
    if s.context.alerts:
        extra.append("alerts: " + ", ".join(f"{n} {a}" for n, a in s.context.alerts))
    if s.feed_down_at_pickup:
        extra.append("live feed down: " + ",".join(s.feed_down_at_pickup))
    c = s.context
    return (f"weather={s.weather} | urgent={'yes' if s.urgent else 'no'} | deadline={s.deadline_min} min | "
            f"traffic {traffic} | {c.time_of_day}, {c.customer}, {c.food} food" + "".join(" | " + e for e in extra))


def fmt(route, o):
    return f"{route} {o.minutes:.1f} min ({'on time' if o.on_time else 'LATE'})"


def main():
    why = "--why" in sys.argv
    os.makedirs(OUT, exist_ok=True)
    agents = build_agents()
    table, log, rows, summary, trained = [], [], [], {a.name: [] for a in agents}, {}
    for s in test_situations():
        table += [f"\n=== {s.name} ===", conditions(s),
                  f"{'Agent':<24}{'Route':<7}{'Time(min)':<11}{'On time':<9}{'Cost(Rs)':<9}"]
        log.append(f"\n=== {s.name} ===")
        for a in agents:
            d, o = run_one(a, s)
            table.append(f"{a.name:<24}{d.route:<7}{o.minutes:<11.1f}{'yes' if o.on_time else 'NO':<9}{o.cost:<9.0f}")
            log.append(f"[{a.name}] -> {d.route}: {d.reason}" + (f"  FLAGS: {d.flags}" if d.flags else ""))
            log += [f"      {step}" for step in d.plan]
            rows.append([s.name, a.name, d.route, round(o.minutes, 1), o.on_time, round(o.cost)])
            summary[a.name].append((d.route, o.on_time))
            if isinstance(a, LearningAgent):
                trained[s.name] = (d.route, o)
    table += ["\n=== Summary: route chosen in Test 1 / 2 / 3 and deliveries on time ===",
              f"{'Agent':<24}{'T1':<5}{'T2':<5}{'T3':<5}{'On time':<8}"]
    for name, res in summary.items():
        table.append(f"{name:<24}" + "".join(f"{r:<5}" for r, _ in res) + f"{sum(ok for _, ok in res)}/3")
    table.append("\n=== Learning agent: before vs after training on 600 past deliveries ===")
    before = LearningAgent()
    for s in test_situations():
        d0, o0 = run_one(before, s)
        table.append(f"{s.name[:6]}: before -> {fmt(d0.route, o0)} | after -> {fmt(*trained[s.name])}")
    text = "\n".join(table)
    print(text)
    if why:
        print("\n".join(log))
    learner = next(a for a in agents if isinstance(a, LearningAgent))
    for fname, content in [("test_results.txt", text), ("decision_log.txt", "\n".join(log)),
                           ("learned_factors.txt", learner.learned_table())]:
        with open(os.path.join(OUT, fname), "w") as f:
            f.write(content + "\n")
    with open(os.path.join(OUT, "test_results.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["test", "agent", "route", "minutes", "on_time", "cost_rs"])
        w.writerows(rows)


if __name__ == "__main__":
    main()
