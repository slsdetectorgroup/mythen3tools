"""Wall-clock timing of the trimming steps, to guide optimisation.

    from steptimer import timer

    with timer.step("threshold fit c0"):
        results = pool.map(...)
    ...
    timer.report("Trimming steps")

Each step prints its duration when it ends; report() prints all steps with
their share of the total.
"""

import time
from contextlib import contextmanager


class StepTimer:
    def __init__(self):
        self.steps = []   # (name, seconds) in the order they finished

    def reset(self):
        self.steps.clear()

    @contextmanager
    def step(self, name):
        t0 = time.perf_counter()
        try:
            yield
        finally:
            dt = time.perf_counter() - t0
            self.steps.append((name, dt))
            print(f"[{dt:8.2f} s] {name}")

    def total(self):
        return sum(dt for _, dt in self.steps)

    def report(self, title="Timing"):
        if not self.steps:
            return
        total = self.total()
        width = max(len(name) for name, _ in self.steps)
        print(f"\n{title}")
        for name, dt in self.steps:
            print(f"  {name:<{width}}  {dt:8.2f} s  {100 * dt / total:5.1f} %")
        print(f"  {'total':<{width}}  {total:8.2f} s")


timer = StepTimer()
