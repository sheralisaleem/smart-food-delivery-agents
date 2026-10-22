"""benchmark.py - robustness check beyond the 3 hand-made tests: 1000 unseen random deliveries.
'Urgent' = the tight-deadline subset, where choosing the right route matters most.
The learning agent is shown twice: before training and after training on 600 past deliveries."""
import os
import random

from environment import random_situation, execute
from run_tests import build_agents, run_one, OUT
from agent5_learning import LearningAgent

N = 1000
SEED = 2026                                   # different from the training seed, so situations are unseen


def evaluate(decide_route, situations):
    res = [(s.urgent, execute(s, decide_route(s))) for s in situations]
    everything, urgent = [o for _, o in res], [o for u, o in res if u]
    pct = lambda xs: 100 * sum(o.on_time for o in xs) / len(xs)
    return (pct(everything), pct(urgent), sum(o.minutes for o in everything) / len(everything),
            sum(o.cost for o in everything) / len(everything))


def main():
    rng = random.Random(SEED)
    situations = [random_situation(rng, i) for i in range(N)]
    n_urgent = sum(s.urgent for s in situations)
    rows = []
    untrained = LearningAgent()
    untrained.name = "5. Learning (untrained)"
    for a in [untrained] + build_agents():
        rows.append((a.name, evaluate(lambda s, a=a: run_one(a, s)[0].route, situations)))
    # hindsight reference: always take the truly fastest route (knows every hidden effect)
    rows.append(("Oracle (hindsight)", evaluate(
        lambda s: min(s.routes, key=lambda r: execute(s, r.name).minutes).name, situations)))
    lines = [f"Benchmark on {N} unseen random deliveries ({n_urgent} urgent)",
             f"{'Agent':<26}{'On time % (all)':<17}{'On time % (urgent)':<20}{'Avg min':<9}{'Avg cost Rs':<11}"]
    lines += [f"{n:<26}{r[0]:<17.1f}{r[1]:<20.1f}{r[2]:<9.1f}{r[3]:<11.0f}" for n, r in rows]
    text = "\n".join(lines)
    print(text)
    with open(os.path.join(OUT, "benchmark.txt"), "w") as f:
        f.write(text + "\n")


if __name__ == "__main__":
    main()
