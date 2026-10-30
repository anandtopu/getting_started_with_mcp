# Extend it

1. Introduce one realistic failure and prove the failure is contained.
2. Add an independently checked evaluation case with a negative control.
3. Design shared state and recovery before introducing a second worker.
4. Add a new capability only after updating its capture, permission policy and tests.
5. Document a threat model for real data; keep the course fixture as a safe test environment.
