# Offline evidence report

## Purpose and boundary

Make one acceptance decision easy to inspect. The UI reads saved workflow JSON, per-attempt records and preserved source snapshots. It never runs an agent, approves a patch or applies a change. CSS and JavaScript are embedded with no external fonts, requests or build dependencies. Raw links require keeping the report beside its evidence folder. Copying only report.html retains the displayed view but loses the linked raw artifacts.

The supplied renderer is specific to the R3 checkout replay. It does not yet render arbitrary pilot tasks or Petclinic evidence. A verified label describes the recorded runner decision, not authenticated proof or a fresh verification at page load. Synthetic challenges are explicitly labelled; absent stages say Not run. Command/source text is HTML-escaped, and attempt paths cannot escape the run folder. Hashes are traceability aids, not tamper-proof signatures.

## Design decisions

Outcome, pending developer review and scope appear before implementation details. Closely grouped counts and stages follow [Laws of UX](https://lawsofux.com/) proximity principles. Readable numbers, wrapping source text, visible focus and reduced motion follow the [Interfaces checklist](https://www.interfaces.dev/cheat-sheet). Expandable execution records apply progressive disclosure, with [Detail](https://www.detail.design/) as an interaction reference. No fake live progress or animated execution is shown.

## Validation

35 Python checks pass, including five report-specific checks. Headless Edge inspected the actual saved Java report at 1440 by 1100 and 390 by 844. Side-by-side/unified switching and fingerprint expansion work; mobile has no document overflow and retains the explanatory panel. The report was visually inspected at both sizes. Browser tests are functional/layout checks, not a complete accessibility audit. Print is a convenience using the browser dialog; a final PDF layout has not been reviewed.

Regenerate with `python -m vesper report <run-directory>`. New R3 workflows produce Markdown and HTML automatically. Historical run timestamps, duration and execution records remain historical.

## Vesper identity refinement

The reusable vector mark is `vesper/assets/vesper-mark.svg`: a ladybug with exactly four five-point stars as wing markings. The team confirmed their meaning on 26 September: requirement, reproduction, verification, human review. This is a brand metaphor, not four completed checks or a rating. The ladybug connects the identity to investigating software bugs; the dark dusk-colored navigation gives the name a visual setting without asserting an unconfirmed origin story.

The report uses warm paper, plum-black navigation, restrained terracotta branding and separate green/ochre evidence states. Georgia headings and system sans-serif labels work offline without font downloads. Actual finding names replace promotional headlines. A simple reading order and grouped execution records draw on Laws of UX proximity; tabular figures, wrapping and optical icon alignment draw on Interfaces. Detail's underlying-details example informed keeping raw evidence expandable, adapted to explicit keyboard-accessible controls rather than a hidden modifier key.

References: https://lawsofux.com/law-of-proximity/ · https://interfaces.dev/cheat-sheet · https://detail.design/detail/hold-option-for-underlying-details

The four stars remain part of the mark on narrow screens: mobile has its own visible wordmark instead of losing the brand when the desktop navigation is hidden. No gradients, live activity indicators or ornamental animation are used. The SVG is original project artwork and can be reused in the cover and slides.


The refined report was checked at 1440, 768, 390 and 320 pixels: no horizontal overflow, exactly four stars in the visible logo, working patch views and provenance disclosure, keyboard skip link, zero remote requests and no browser script errors. Both verified and synthetic-blocked records were inspected. Blocked records direct the primary action to the execution evidence and distinguish reported test counts from gate acceptance.
