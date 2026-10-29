# Lexicon
A local-first Python vocabulary dictionary for Windows and macOS.

## Files
- lexicon.py: runnable desktop application.
- README.md: installation and mechanics.
- BLUEPRINT.md: architecture and coding plan.
- Your chosen .json file: your dictionary, schedule and review history.

## Installation
1. Install Python 3.10+ from https://www.python.org/downloads/.
   Windows: enable "Add Python to PATH" during installation.
   macOS: the official installer includes Tcl/Tk; avoid relying on system Python.
2. Place lexicon.py in a writable folder.
3. In a terminal in that folder, run:
   Windows: python lexicon.py
   macOS: python3 lexicon.py
4. At setup choose Yes and select a name/location for your blank JSON dictionary,
   or No to open an existing Lexicon JSON file.
No pip dependencies are needed. Verify Tk with python -m tkinter
(or python3 -m tkinter). If that fails, install a Python distribution with Tk support.

## Everyday use
Add a source item and a translation. Direct translation is selected by default.
- direct: one source item maps to one meaning; phrases and unequal token counts
  are allowed. Example: look at = bakmak.
- aligned: match each source token to a target token using dropdowns.
  Several source tokens may map to one target; "No direct match" is allowed.
  Edit the text before assigning positions: editing rebuilds alignment controls.
- expression: preserve an idiom as a whole, without pretending its components
  translate independently. Example: take someone for granted =
  birisini çantada keklik görmek.

These are semantic connection types, not three different dictionaries.
Tokenization uses whitespace; punctuation stays attached to its word.
Word count rules in the original brief were ambiguous: direct translation does
not enforce equal counts, which would reject its own "look at = bakmak" example.
Aligned mode makes word positioning explicit instead.

## Review mechanics
Creation times and every review are recorded as Unix milliseconds.
New entries are due immediately. Open "Review due", recall the translation,
reveal it, then honestly select Again (quality 1), Hard (3), Good (4), or Easy (5).
The scheduler is inspired by SM-2:
ease = max(1.3, ease + 0.1 - (5-q)*(0.08 + (5-q)*0.02)).
Failure resets successful repetitions and schedules a retry in 10 minutes.
Success schedules 1 day, then 6 days, then previous interval multiplied by ease.
Ratings affect ease, including during the initial fixed intervals.
Intervals use elapsed 24-hour days, not local calendar midnights.
This uses spaced repetition and retrieval practice, but is not a clinical or
scientifically validated implementation of a specific learning protocol.
The review itself is a self-assessed test; no separate exam or automated
translation grading is implemented. Longer-term tests happen as items become due.
The app refreshes its due count every minute while open.
It does not run in the background or issue operating-system notifications.

## Data and privacy
No accounts, network requests, or remote storage in the Python app.
Every successful addition/deletion/review is saved to your selected JSON file.
Writes use a temporary sibling file and atomic replacement.
Do not open the same dictionary simultaneously in multiple app instances.
Back up the JSON file regularly. Deletion has confirmation but no undo.
The browser preview uses localStorage; export its JSON and open it in Python.
Browser storage is not the downloaded file and may be cleared by the browser.
Google Fonts are loaded by the preview page, not by the Python app.

## Limitations
Tk provides native-style controls, not the browser preview's exact appearance.
No audio, automatic translations, background notifications, separate exam engine,
file locking, encryption or automatic backups. Editing existing entries is not
implemented; delete/re-add only if resetting its review history is acceptable.
A frozen executable is not included; Python must be installed.
