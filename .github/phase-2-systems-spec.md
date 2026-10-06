# Sunday League Manager: Phase 2 Systems Spec

## Purpose

Phase 2 defines the first production-level layer of the game beyond the prototype shell. The goal is to make the weekly management loop feel complete: matches tell a story, the season progresses through a league, and off-pitch chaos has mechanical consequences.

This spec should be read alongside [brief.md](../brief.md), [content-bible.md](../content-bible.md), [roadmap.md](../roadmap.md), and [README.md](../README.md).

## Phase 2 Scope

Build these systems in Phase 2:

- Match commentary
- Weekly events
- League system
- Finances

Do not treat this spec as a request for transfers, cup competitions, training, or a full art/audio pass. Those remain later-phase systems unless the roadmap changes.

## Match Commentary

Match commentary is the main in-match delivery surface. It should turn the result into a readable Sunday-league story.

### Commentary Required Behaviour

- Commentary should advance in a clear chronological order.
- Each key event should include a minute marker and a short plain-language description.
- The feed should highlight goals, cards, injuries, weather chaos, referee mistakes, and major momentum swings.
- Commentary should feed the post-match summary so the same match can be understood at a glance or read in detail.

### Commentary Tone Rules

- Keep the language blunt, compact, and football-specific.
- Lean into the absurdity of grassroots football without turning the tone nasty or cruel.
- Treat player complaints and referee arguments as part of the comedy, not filler.

### Commentary Acceptance Criteria

- A player can read the match from commentary alone and understand what changed in the game.
- The summary view surfaces the key moments without repeating every line verbatim.

## Weekly Events

Weekly events are the glue between matches. They should make the squad feel unreliable, alive, and slightly impossible to manage.

### Weekly Events Required Behaviour

- Events can occur before a fixture, between fixtures, or after a match.
- Events should be delivered through chat, notifications, or diary-style updates.
- Events should create a visible consequence such as a morale shift, an availability change, a fine, or a small financial impact.

### Weekly Event Buckets

- Availability chaos: dropouts, late arrivals, work shifts, and hangovers.
- Squad drama: arguments, passive-aggressive messages, and player mood swings.
- Match fallout: blame, excuses, praise, and injuries.
- Club admin: kit problems, fines, and weekly reminders.

### Weekly Events Acceptance Criteria

- A week can include at least one meaningful event before or after a fixture.
- The player can tell why a squad state changed, not just that it changed.

## League System

The league system gives the game long-term structure and a reason for every result to matter.

### League Required Behaviour

- The game should track the team within a division and update the table after each completed fixture.
- The fixture list should support a repeatable weekly progression.
- Promotion and relegation pressure should be visible in the season structure, even if the exact rules are tuned later.

### League Presentation Rules

- Division, table position, points, and recent form should be easy to scan.
- The fixtures/results surface should make it obvious whether the next game is pending or already played.
- Results should stay tied to the same league context so the season reads as one connected arc.

### League Acceptance Criteria

- A player can see where the team sits in the league and what the next fixture is.
- Completed matches visibly affect table position or season state.

## Finances

Finances are intentionally small-scale. They should feel like club admin, not a spreadsheet sim.

### Finance Required Behaviour

- Track basic weekly income and spending.
- Include subs, fines, pitch fees, and referee fees as recurring items.
- Make kit or equipment costs visible when they occur.

### Finance Presentation Rules

- Keep the financial view readable in plain language.
- Show whether the club has money, is breaking even, or is short.
- Connect financial events to mood or availability when that helps the story make sense.

### Finance Acceptance Criteria

- The player can tell what money came in, what money went out, and why.
- A financial event can affect the next week without needing a separate explanation screen.

## Open Documentation Items

- Exact data model for season progression and promotion rules.
- Exact balance-sheet format for club finances.
- Whether commentary is generated from templates, a rule engine, or a hybrid approach.
- Whether weekly events are authored as fixed narrative beats, weighted pools, or both.
