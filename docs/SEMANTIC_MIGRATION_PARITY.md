# Semantic migration parity

The historical `vendor/per2ref` implementation was characterized before removal from the live public tree.

The refactored `per2.semantics` implementation was compared against the historical oracle on the exact state sets of:

- all 64 formal words at `k=1`;
- all 64 formal words at `k=2`.

Total exact set comparisons: **128**. Mismatches: **0**.

The historical code remains available only inside the immutable canonical submission archive, not as a second active implementation.
