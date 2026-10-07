<!--
Base branch: the work branch, never production. The exceptions: a stacked PR targets its parent's branch, and a hotfix targets production (the contributing guide, "Production problems"); its author opens the merge-back PR to the work branch the same day.
Title: type(scope): subject, where scope is the main area; add the migration number if the slice adds one. Refer to other PRs and issues as "Refs #N".
Open it as a draft as soon as you start: the draft is your claim.
-->

## What and why

<!-- Refs #<issue> if it came from one. The spec, issue or decision this implements, and what changes for the user. -->

## Areas

<!-- The areas this touches (from the areas file). A path with no area means this PR adds its line. -->

## Migrations

<!-- "None", or <app>/<NNNN> and why it is backward compatible. -->

## Impact on other areas and shared contracts

<!-- API shapes, permission codes, error codes, job payloads, event names. "None" if none. -->

## Assumptions

<!-- Questions still open in collaboration issues, and the default you built on. "None" if none. -->

## Tests

<!-- What you ran and the result. -->

## Definition of done

<!-- Tick what applies from the definition of done; write "n/a" and why for the rest. -->

- [ ] Tests and lint pass
- [ ] The spec or doc that owns the changed behaviour, and the area's status file, are updated in this PR
- [ ] Reviews sized by risk
- [ ] If there's a UI: touched screens checked on your users' devices

## Decisions

<!--
"None" if none. Otherwise one table row per new owner decision, with the columns Date | Decision | Notes | Source.
Source holds the owner's exact words and where they said them (chat name, date). The coordinator appends the rows to
the decisions log when it merges, so never edit the log in this PR.
-->
