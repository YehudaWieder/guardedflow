---
name: review-diff
description: Senior self-review of a change before calling it done — catches overengineering, workaround fixes, redundant checks, unused parameters, narrating comments, scope creep, and other marks of careless or machine-generated code. Use at the end of every coding task in this repo, and whenever asked to review a diff or PR.
---

# Review the diff

Read `git diff` as the skeptical senior who will maintain it. When an item fails, fix the code — don't explain it away.

1. **Cause or symptom?** Does the change fix the root cause, or add a branch, flag, or fallback around it? If a foundation (model, signature, invariant) was wrong, the diff changes the foundation.
2. **What can be deleted?** Checks the types already guarantee, `try` blocks that can't trigger or only re-raise, single-use variables, wrappers that only forward.
3. **Parameters:** is each one used? Derivable from another? Passed through layers that ignore it?
4. **New abstractions:** does every new class, interface, or file have at least two real uses today? If not, inline it.
5. **Errors:** anything swallowed, defaulted to empty, or logged-and-continued where it should fail?
6. **Comments and names:** delete narrating comments; rename instead. Replace generic names (`data`, `result`, `handle`, `manager`, `utils`).
7. **Scope:** revert edits unrelated to the task.
8. **Tests:** would each new test fail if the feature were deleted? If not, it tests nothing.
9. **Leftovers:** debug prints, commented-out code, unused imports, TODOs.

Then run the area's checks. Report in two or three lines what review changed; say nothing if it changed nothing.
