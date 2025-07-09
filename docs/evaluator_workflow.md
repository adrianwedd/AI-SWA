# Evaluator Workflow

The Evaluator scores completed tasks and stores short critiques in
`critiques.yml`. Each task receives a numeric score and optional notes.
The Reflector and Planner can later consult these critiques when
prioritising work.

During memory reconciliation the `Memory.reconcile_tasks` method accepts
these scores to decide which version of a task to keep if multiple
entries exist. The task with the higher critique score is preserved.
