# Sunday League Manager: Phase 1 UI Spec

## Purpose

Phase 1 proves the core fantasy: the player manages a chaotic Sunday-league team through a fictional phone. This spec defines the first buildable UI slice for frontend and backend teams, based on the brief, content bible, prototype plan, and roadmap.

## Phase 1 Scope

Build only these surfaces in this phase:

- Phone shell and app launcher
- Squad Chat
- Fixtures & Results
- Team Sheet stub
- Match summary

Do not design or build later-phase systems in this spec, including transfers, club finances, multi-division progression, cup runs, training, or full art/audio polish.

## Visual Tone

The interface should feel like a slightly scruffy football manager phone: clean enough to read quickly, but full of Sunday-league personality.

- Reference mood: WhatsApp-style chat, Notes-like utility screens, and a dubious FA Full-Time-style results app.
- Surface treatment: light phone UI with mud-splattered accents, soft shadows, rounded cards, and a touch of low-fidelity charm.
- Typography: use a highly legible mobile-first system with clear hierarchy; headers can feel a little playful, but body text must stay compact and readable.
- Colour: mostly neutral UI with one strong accent for active states and status badges; use warning colours sparingly for chaos events, dropouts, and match losses.
- Motion: keep motion subtle and functional, such as app open transitions, badge pulses, and match-result reveal.

## Phone Shell Layout

The phone shell is the persistent frame for all Phase 1 screens.

- Top status area: time, signal/battery style indicators, and a compact club state marker if needed.
- Main content area: swaps between launcher and app screens without leaving the phone frame.
- Bottom navigation zone: a simple back control plus one primary shortcut to the home screen.
- Safe area: all content must remain readable on a narrow mobile viewport first, then scale up gracefully on desktop.

### Acceptance Criteria

- The phone shell is visible on every Phase 1 screen and keeps a consistent frame, spacing, and safe area.
- A user can return to the home launcher from any app view in one tap.

## Home / App Grid

The home screen is the default landing view and acts as the main launcher.

### Layout

- Use a 2-column phone grid on mobile, expanding to a compact centered grid on larger screens.
- Each app tile includes an icon, label, and optional small badge for unread items or urgent events.
- Keep the number of visible apps limited to the Phase 1 set so the launcher feels focused, not crowded.

### Required Apps

- Squad Chat
- Fixtures & Results
- Team Sheet

### Behaviour

- Tapping a tile opens the app full-screen inside the phone shell.
- Notification badges should signal unread chat or new match results without overwhelming the grid.

### Acceptance Criteria

- All Phase 1 apps are reachable from the home grid with no extra navigation.
- At least one app tile can show a badge state for unread or new content.

## Squad Chat View

This is the most character-led surface and should feel like a group chat full of excuses, arguments, and last-minute chaos.

### Layout

- Header: chat title, squad identity, and a compact status line such as pre-match, post-match, or midweek.
- Message feed: stacked left/right chat bubbles with timestamps, sender names, and occasional system-style notices.
- Composer area: Phase 1 can use a stubbed input row or a disabled send bar if live messaging is not part of the build.

### Content Rules

- Messages should be short, colloquial, and plausible for Sunday league culture.
- System messages should clearly separate availability updates, lateness, or match-day announcements from player banter.
- Use visual distinction for different message types: player chat, manager notices, and automated event messages.

### Acceptance Criteria

- The chat feed clearly differentiates at least three message types: player message, manager/system notice, and event message.
- The feed supports timestamped, vertically scrollable conversation history on a small screen.

## Fixtures / Results View

This surface is the clearest “league app” view and should feel like a readable match-and-table dashboard.

### Layout

- Top section: upcoming fixture or latest result card with opponent, date/day, venue, and a prominent score state when available.
- Middle section: brief match report or preview summary, kept to one screen’s worth of content.
- Bottom section: league table or compact results list, depending on the current state.

### Behaviour

- Before a match, show fixture details and a clear “match pending” state.
- After a match, swap the top card to result mode and surface the score first, summary second.
- If only one division is present in Phase 1, the table should stay concise and readable rather than dense.

### Acceptance Criteria

- The view can represent both pre-match and post-match states without changing screen structure.
- The latest result is visually more prominent than older fixtures or table rows.

## Team Sheet Stub

The Phase 1 team sheet does not need full drag-and-drop depth, but it must prove the lineup-building concept.

### Layout

- Formation selector at the top using a small set of permitted shapes such as 4-4-2 and 4-3-3.
- Pitch/grid area in the centre showing positions and player slots.
- Bench/reserve strip below the pitch with compact player chips.
- Simple player detail panel or tooltip area for trait previews.

### Behaviour

- The stub should allow selection and placement of players into positions in a clearly understandable way.
- Selected players should expose key traits in a small, readable summary, not a full stat sheet.
- The UI must make it obvious when a position is unfilled or a choice is invalid.

### Acceptance Criteria

- A user can see the chosen formation and understand which positions are occupied at a glance.
- Empty, selected, and invalid placement states are visually distinct.

## Match Summary

The match summary is the payoff screen for the weekly loop and should feel punchy, readable, and a little cheeky.

### Layout

- Primary result block: scoreline, opponent, and outcome state.
- Secondary block: short commentary recap or three to five highlighted events.
- Tertiary block: player impact notes such as morale changes, standout performers, or chaos events.

### Behaviour

- The scoreline must dominate the hierarchy.
- Supporting details should be scan-friendly and never bury the result.
- The summary should support both good and bad outcomes without changing the core layout.

### Acceptance Criteria

- The result is readable within one glance on a phone-sized layout.
- At least one noteworthy match event is surfaced beneath the scoreline.

## Navigation Rules

- Home launcher is the root destination for Phase 1.
- App screens must allow back navigation to the launcher without dead ends.
- Internal deep links should be minimal; Phase 1 should favor simple forward/back movement over complex routing.
- State changes such as unread chat, new result, or match completion should update the relevant launcher badge or screen state.

## Cross-Surface Requirements

- Use the same shell and spacing system across every app surface.
- Keep text dense but not cramped; football-management players will tolerate detail, but the phone metaphor must stay usable.
- Design for fast scanning first, detail second.
- Ensure the UI remains understandable without colour alone doing all the work.

## Unresolved Decisions For Implementation

- Whether the chat composer is interactive in Phase 1 or purely decorative/stubbed.
- Whether the fixtures/results surface shows a league table, a recent-results list, or both in the initial build.
- Whether the team sheet supports true drag-and-drop or a simpler tap-to-place interaction for the prototype.

## Phase 1 Success Test

If a player can open the phone, find the squad chat, inspect fixtures/results, set a basic lineup, and read a match summary without confusion, Phase 1 is doing its job.