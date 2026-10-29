# Lexicon — implementation blueprint

## 1. Scope and decisions
Deliver a runnable, dependency-free Python 3.10+ Tkinter app for Windows/macOS.
Persist vocabulary in a user-created JSON file rather than an opaque database.
Support direct, aligned and whole-expression translation.
Use self-assessed retrieval practice with an SM-2-inspired schedule.
Treat "one word" as one vocabulary item, which may contain several tokens.
Keep alignment optional and explicit; do not infer linguistically incorrect links.

## 2. Data model
Dictionary: {version:1, name:string, items:[Entry]}.
Entry:
- id: UUID string
- source, target: original text
- mode: direct | aligned | expression
- alignment: target token indexes for source tokens; -1 = unmatched
- created, due: Unix timestamp in milliseconds
- interval: elapsed days; 0 for new/failed items
- ease: numeric factor, starts at 2.5, floor 1.3
- repetitions: successful review streak
- history: [{at, quality, interval}]
Whitespace tokenization deliberately avoids language-specific assumptions.
Production expansion should use a formal schema, duplicate-ID detection, input
size limits and migrations before accepting untrusted dictionary files.

## 3. Modules in the supplied single-file implementation
validate: checks imported dictionaries and required schedule fields.
schedule: modifies one entry from a recall quality, appends history.
Lexicon: GUI controller, file ownership, editor, table and review session.
write: UTF-8 JSON to sibling .tmp file, os.replace into selected file.
now: common millisecond clock.
For a larger codebase split these into model.py, storage.py, scheduler.py,
ui/editor.py, ui/review.py and app.py.

## 4. Coding sequence
A. Establish Tk root, shared style and initial setup dialog.
B. Implement new/open operations and atomic persistence.
C. Add sortable-by-insertion vocabulary display, search, delete confirmation.
D. Build direct/expression editor and dynamic word-position selectors.
E. Implement scheduler as a pure function where practical.
F. Build a reveal-then-rate review session over a snapshot of due entries.
G. Refresh due count every 60 seconds with Tk.after.
H. Interoperate with browser-exported version 1 JSON files.
I. Test both OS platforms and disk-failure paths.

## 5. Review state machine
Ready -> show source -> reveal target/alignment -> rating -> persist -> next.
Closing before rating leaves an entry unchanged.
Failed items return after 10 minutes, not immediately within the session snapshot.
A failed save restores the pre-rating in-memory entry.
No automated grading: paraphrases and idioms make exact matching misleading.

## 6. Manual acceptance tests
- First run can create an empty file and reopen it.
- Cancel setup leaves a usable window; Add asks for setup.
- Unicode Turkish vocabulary survives save/open without corruption.
- Blank source/target is rejected.
- Direct handles "look at = bakmak" without equal-token constraints.
- Aligned permits nonsequential positioning, repeated target indexes and -1.
- Expression retains idiom text verbatim.
- New entries are immediately due.
- Good gives 1 day, then 6 days; Again gives 10 minutes.
- Ease never falls below 1.3.
- Review history contains every committed rating.
- Search matches source or target; delete needs confirmation.
- Invalid files do not replace the active dictionary.
- Write failure is reported; additions/deletions/reviews roll back.
- Browser export opens in Python and Python JSON imports in browser.
- Due count updates while open.

## 7. Recommended next iteration
Add automated unittest coverage with an injected clock; entry editing that
preserves history; alignment schema validation in both clients; file locking;
dated rotating backups; keyboard review shortcuts; screen-reader testing;
calendar review view; an optional separate delayed assessment mode.
For genuine OS reminders, add platform-specific notification integration and a
clearly consented background agent. Do not claim reminders work when closed
until that feature is implemented.
Package using PyInstaller only after platform-specific testing; sign Windows
binaries and notarize macOS builds. These are not included in this prototype.
