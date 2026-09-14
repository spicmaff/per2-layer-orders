from __future__ import annotations

from dataclasses import asdict, dataclass

from .row_forms import column_word


@dataclass(frozen=True)
class StackEvent:
    step: int
    face: str
    column: int
    action: str
    stack_before: tuple[int, ...]
    stack_after: tuple[int, ...]
    status: str
    reason_code: str | None = None
    requested_closer: int | None = None
    blocking_label: int | None = None

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class StackTrace:
    k: int
    upper_pivot: int
    lower_pivot: int
    upper_stream: tuple[int, ...]
    lower_closer_stream: tuple[int, ...]
    compatible: bool
    events: tuple[StackEvent, ...]
    failure: dict | None

    def as_dict(self) -> dict:
        return {
            "k": self.k,
            "upper_pivot": self.upper_pivot,
            "lower_pivot": self.lower_pivot,
            "upper_stream": list(self.upper_stream),
            "lower_closer_stream": list(self.lower_closer_stream),
            "compatible": self.compatible,
            "events": [e.as_dict() for e in self.events],
            "failure": self.failure,
        }


def mvmmmm_lifo_trace(k: int, a: int, b: int) -> StackTrace:
    """Deterministic horizontal reconstruction from Appendix E.2.

    Upper A-events push horizontal labels in W_a order. Lower B-events request
    closers in reverse(W_b). If the requested label is unopened, the upper
    stream advances. If it is stack-top, it closes. If buried, completion is
    impossible and the trace stops immediately.
    """
    upper = column_word(k, a)
    lower = tuple(reversed(column_word(k, b)))
    stack: list[int] = []
    ui = 0
    li = 0
    events: list[StackEvent] = []
    step = 1
    while li < len(lower):
        requested = lower[li]
        if requested in stack:
            if stack[-1] == requested:
                before = tuple(stack)
                stack.pop()
                events.append(
                    StackEvent(step, f"B{requested}", requested, "POP", before, tuple(stack), "COMMITTED", requested_closer=requested)
                )
                li += 1
                step += 1
                continue
            failure = {
                "type": "BURIED_CLOSER",
                "requested_closer": requested,
                "blocking_label": stack[-1],
                "stack": list(stack),
            }
            events.append(
                StackEvent(
                    step,
                    f"B{requested}",
                    requested,
                    "STOP",
                    tuple(stack),
                    tuple(stack),
                    "FAILED_CANDIDATE",
                    "BURIED_CLOSER",
                    requested,
                    stack[-1],
                )
            )
            return StackTrace(k, a, b, upper, lower, False, tuple(events), failure)

        if ui >= len(upper):
            failure = {"type": "UNOPENED_CLOSER", "requested_closer": requested, "stack": list(stack)}
            events.append(
                StackEvent(
                    step,
                    f"B{requested}",
                    requested,
                    "STOP",
                    tuple(stack),
                    tuple(stack),
                    "FAILED_CANDIDATE",
                    "UNOPENED_CLOSER",
                    requested,
                    None,
                )
            )
            return StackTrace(k, a, b, upper, lower, False, tuple(events), failure)

        col = upper[ui]
        before = tuple(stack)
        stack.append(col)
        events.append(StackEvent(step, f"A{col}", col, "PUSH", before, tuple(stack), "COMMITTED", requested_closer=requested))
        ui += 1
        step += 1

    compatible = ui == len(upper) and not stack
    failure = None if compatible else {"type": "INCOMPLETE_TRACE", "upper_index": ui, "stack": list(stack)}
    return StackTrace(k, a, b, upper, lower, compatible, tuple(events), failure)
