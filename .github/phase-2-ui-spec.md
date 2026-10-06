# Sunday League Manager: Phase 2 UI Spec

## Purpose

Phase 2 starts turning the phone shell into a proper club-management loop. This first slice keeps the existing mobile phone metaphor, but expands the fixtures/result area into a compact club hub that can carry full match commentary, weekly events, league context, and finances without adding a crowded launcher.

This UI spec should be read alongside [brief.md](../brief.md), [content-bible.md](../content-bible.md), [roadmap.md](../roadmap.md), and [.github/phase-2-systems-spec.md](phase-2-systems-spec.md).

## Phase 2 Slice 1

Build only the first coherent slice of Phase 2:

- Match Centre with full commentary
- Weekly Events inbox
- League System summary
- Finances ledger

Keep the current Phase 1 shell, chat, and team sheet patterns intact. Do not redesign the whole phone yet. The goal is to prove the new weekly loop, not the complete content depth.

## Visual Direction

The visual language should stay aligned with the Phase 1 spec: a slightly scruffy football-manager phone, clear enough to scan quickly, but denser than a simple menu app.

- Reference mood: WhatsApp-style urgency, Notes-style utility, and a dodgy FA Full-Time style league view.
- Surface treatment: compact cards, pill filters, thin dividers, and a subtle mud-stained accent palette.
- Hierarchy: one dominant section per screen, then secondary cards and compact lists beneath it.
- Motion: minimal and functional, such as new-event emphasis, live-commentary reveal, and small badge updates.

## Mobile Interaction Rules

This phase should feel like a real phone, not a desktop app shrunk down.

- One primary action per screen. Secondary actions stay in overflow chips or compact footer controls.
- Single-column layout only. No side-by-side panels on mobile.
- Tap targets should be large enough for thumb use, with 44px minimum touch areas.
- Navigation must always offer a visible back path to the phone home.
- Content should scroll vertically in one place per screen. Avoid nested scroll regions unless the content is obviously long, such as commentary.
- Use chips or segmented controls for mode changes, not hidden gestures.
- Keep status and read-state visible without relying on colour alone.

## Phone Shell Update

The shell itself should remain recognisable, but the bottom of the phone needs a stronger Phase 2 navigation model.

- Keep the top status area and shell frame from Phase 1.
- Introduce a compact, persistent club-level footer on Phase 2 screens only.
- The footer should switch between the Phase 2 hub sections rather than opening new modal layers.
- Home remains the root launcher. All deeper screens must return there in one tap.

### Acceptance Criteria

- A player can reach the new club hub from the existing phone flow without losing the Phase 1 launcher.
- Every Phase 2 screen still feels like it lives inside the same phone shell.

## Phase 2 Hub Flow

The smallest coherent first pass is a club hub entered from the current fixtures/results area.

### Entry Point

- Tapping Fixtures & Results should open the new Match Centre hub.
- The Match Centre becomes the default landing view for Phase 2 content.
- The existing summary screen becomes a post-match view inside Match Centre rather than a separate dead-end result page.

### Internal Sections

- Match Centre
- Weekly Events
- League System
- Finances

### Behaviour

- The current screen stays in place while the player switches sections.
- Section changes should feel like moving between phone app pages, not a full reload.
- If the screen is showing live commentary, the Match Centre remains the primary context and the other sections become quick-swap views.

## Match Centre

This is the main Phase 2 screen and the first place to prove the expanded weekly loop.

### Layout

- Top block: scoreline or fixture header, with opponent, competition, and state such as live, pre-match, or full time.
- Middle block: full commentary feed, stacked chronologically with time stamps.
- Secondary block: key match moments surfaced as compact chips or callouts.
- Footer actions: quick switch to Weekly Events, League System, and Finances.

### Content Rules

- Commentary should read as a continuous narrative, not a list of disconnected updates.
- The newest event should always be easy to spot.
- Commentary lines should stay short enough to scan on a phone.
- Use tone from the brief and content bible: dry, chaotic, and rooted in Sunday-league nonsense.

### Behaviour

- Pre-match state shows the fixture header and any late availability chaos.
- Live state shows a running commentary feed and can surface momentum changes or red-card style events.
- Full-time state swaps the top block to result mode while keeping the commentary intact below it.

### Acceptance Criteria

- The player can read the whole match flow from pre-match to full-time without leaving the screen.
- The layout still works when commentary becomes much longer than Phase 1’s short recap.

## Weekly Events

Weekly events are the narrative glue between matches and should feel like a chaotic inbox.

### Layout

- A chronological feed of event cards.
- Each card should show source, short description, and gameplay impact.
- Grouping labels such as pre-match, match-day, and post-match can be used if they improve readability.

### Content Rules

- Keep event copy brief and plausible.
- Avoid making events feel like system logs; they should read like club drama.
- Use different visual emphasis for availability issues, morale drops, financial hits, and harmless banter.

### Behaviour

- New weekly events should appear at the top with a clear unread state.
- Tapping an event can reveal a compact detail card, but it should not require a separate detail page in this slice.
- Weekly events should be readable even when multiple things happen in the same week.

### Acceptance Criteria

- A player can quickly understand what changed during the week and why it matters.
- The feed supports stacked updates without becoming visually noisy.

## League System

The league view should establish progression without forcing the player into a dense stats wall.

### Layout

- Top summary: current division, position, and promotion status.
- Middle: compact table with nearby teams and points gap.
- Lower area: simple progress markers for promotion or relegation pressure.

### Behaviour

- The player should instantly know where the club sits in the division.
- The table must remain readable on a narrow screen, even if only the top few rows are shown at first.
- If the team is in promotion contention, that state should be more prominent than the table chrome.

### Acceptance Criteria

- The player can tell at a glance whether the club is safe, chasing promotion, or in trouble.
- The league view remains compact enough to live inside the phone shell.

## Finances

Finances should feel like a practical club ledger, not an accounting spreadsheet.

### Layout

- Top summary: current club balance and weekly cash movement.
- Middle: a list of line items such as subs, fines, pitch fees, and ref fees.
- Lower area: outstanding payments or warnings if the club is running low.

### Behaviour

- Positive and negative movements should be easy to distinguish.
- Financial hits should feel like part of Sunday-league chaos, not a separate management sim.
- The first pass can stay read-only, with no editing flow yet.

### Acceptance Criteria

- The player can understand where money is coming from and where it is going.
- The design clearly leaves room for later warnings, reminders, and payment collection flows.

## Screen-Level Changes From Phase 1

- Fixtures & Results evolves into the Phase 2 Match Centre entry point.
- Match summary becomes a state inside the Match Centre instead of a separate end screen.
- Weekly Events, League System, and Finances are presented as first-class hub sections rather than separate large app launches.
- The home launcher remains simple and does not grow into a crowded dashboard in this slice.

## Brief Mismatches To Avoid

- Do not turn the phone into a desktop-style multi-pane dashboard.
- Do not introduce deep routing that hides the current state of play.
- Do not add large editable forms for finances in the first pass.
- Do not over-focus on long tables at the cost of readability on mobile.

## Implementation Notes For Frontend

- Reuse the existing phone shell, card, and footer language from Phase 1.
- Treat the Phase 2 hub as a set of stacked mobile sections with quick section switching.
- Keep commentary and weekly events as vertically scrolling lists with compact cards.
- Use the existing badge and pill patterns for unread states, division state, and finance warnings.
- Prefer one clearly visible state per screen, with the rest collapsed into supporting context.

## Phase 2 Success Test

If a player can open the phone, follow a full commentary sequence, see what happened during the week, understand the league position, and check the club balance without feeling lost, the first Phase 2 slice is doing its job.