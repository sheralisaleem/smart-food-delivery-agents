"""diagram_lib.py - small helper for drawing consistent architecture diagrams with matplotlib.
Every diagram has the same frame: Environment -> Perception -> Decision Process -> Action -> Environment."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

COLORS = {"env": "#E5E7EB", "perc": "#DBEAFE", "dec": "#FEF3C7", "act": "#D1FAE5", "key": "#EDE9FE"}
INK = "#111827"


class Diagram:
    def __init__(self, title, subtitle):
        self.fig, self.ax = plt.subplots(figsize=(12, 6.6))
        self.fig.subplots_adjust(0, 0, 1, 1)
        self.ax.set_xlim(0, 120)
        self.ax.set_ylim(0, 66)
        self.ax.axis("off")
        self.ax.text(60, 64.2, title, ha="center", va="center", fontsize=16, fontweight="bold", color=INK)
        self.ax.text(60, 61.6, subtitle, ha="center", va="center", fontsize=10.5, color="#4B5563")
        self.b = {}

    def box(self, key, x, y, w, h, lines, kind="dec", fs=9.5, align="center"):
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.0",
                                         fc=COLORS[kind], ec=INK, lw=1.4, zorder=2))
        lh = fs * 0.185                                   # line height in axis units
        top = y + h / 2 + (len(lines) - 1) * lh / 2
        for i, line in enumerate(lines):
            first = i == 0
            left = align == "left" and not first
            self.ax.text(x + 1.6 if left else x + w / 2, top - i * lh, line, ha="left" if left else "center",
                         va="center", fontsize=fs, fontweight="bold" if first else "normal", color=INK, zorder=3)
        self.b[key] = (x, y, w, h)

    def pt(self, key, side):
        x, y, w, h = self.b[key]
        return {"l": (x - 0.3, y + h / 2), "r": (x + w + 0.3, y + h / 2),
                "t": (x + w / 2, y + h + 0.3), "b": (x + w / 2, y - 0.3)}[side]

    def arrow(self, p, q, label=None, both=False, dx=0.0, dy=1.1, rad=0.0, ls="-"):
        self.ax.add_patch(FancyArrowPatch(p, q, arrowstyle="<|-|>" if both else "-|>", mutation_scale=14, lw=1.6,
                                          color=INK, connectionstyle=f"arc3,rad={rad}", linestyle=ls, zorder=4))
        if label:
            self.ax.text((p[0] + q[0]) / 2 + dx, (p[1] + q[1]) / 2 + dy, label, ha="center", va="center",
                         fontsize=8.5, style="italic", color=INK, zorder=5,
                         bbox=dict(fc="white", ec="none", pad=0.6))

    def note(self, x, y, text):
        self.ax.text(x, y, text, ha="center", va="center", fontsize=9, style="italic", color="#4B5563")

    def save(self, path):
        self.fig.savefig(path, dpi=170, facecolor="white")
        plt.close(self.fig)


def frame(d, name, perc_lines, act_lines, py=32, ay=32):
    """Environment (left), dashed agent boundary, Perception and Action boxes, and the loop back."""
    d.box("env", 1.5, 12, 17, 40, ["ENVIRONMENT", "", "order", "routes", "traffic", "weather", "deadline", "context"], "env")
    d.ax.add_patch(FancyBboxPatch((22, 7.5), 96, 52, boxstyle="round,pad=0.3,rounding_size=1.5",
                                  fc="white", ec=INK, lw=1.4, ls="--", zorder=0))
    d.ax.text(24, 57.6, name, fontsize=9.5, fontweight="bold", color="#4B5563", va="center")
    d.box("perc", 25, py - 7, 17, 14, perc_lines, "perc", fs=9)
    d.box("act", 100, ay - 5, 16, 10, act_lines, "act", fs=9)
    d.arrow((19.0, py), (24.7, py), "percepts", dy=1.6)
    d.ax.plot([108, 108, 10], [ay - 5.3, 3.4, 3.4], color=INK, lw=1.6, zorder=1)
    d.arrow((10, 3.4), (10, 11.6))
    d.ax.text(59, 4.9, "ACTION changes the ENVIRONMENT: route is ridden, order is delivered (outcome = feedback)",
              ha="center", va="center", fontsize=9, style="italic", color=INK)
