# Security policy

## Reporting a vulnerability

Open a [private security advisory](https://github.com/earbona23/secret-scout/security/advisories/new)
on this repository. Please do not open a public issue for a vulnerability.

You will get an acknowledgement within 72 hours and an assessment within seven days. There
is no bounty programme — this is a single-maintainer project — but every report is credited
in the advisory unless you ask me not to.

## What counts as a vulnerability here

`secret-scout` finds secrets committed into a git repository, including secrets already
deleted from the working tree but still alive in history.

The threat model is unusual: **the tool handles live secrets by design**, and it is pointed
at repositories it does not trust. These are in scope, in rough order of severity.

| Class | Why it matters |
|---|---|
| **Printing a secret in full** | The tool redacts every match to a prefix/suffix fingerprint plus a hash. A path that emits the whole value creates another copy of the secret — in a terminal, a CI log, a ticket, a screenshot. This is the most serious bug this project can have. |
| **A secret written unredacted to a report or log** | Same class, different destination, and worse: it persists. |
| **A false clean on a supported pattern** | A secret of a documented, supported format that the scanner walks past. Someone shipped on the strength of a green run. |
| **A crafted repository hanging or crashing the scan** | A pathological regex input, a decompression bomb, or a history walk that never terminates. Denial of service against a security gate is a way to disable it. |
| **Escaping the scanned tree** | A crafted path, symlink or ref name that causes reads or writes outside the repository under examination. |
| **Any outbound network call** | The scanner is local. A secret leaving the machine, for any reason including telemetry, would be the exact harm it exists to prevent. |

## If you find a secret with it

Rotate first, then clean history. Removing the file and committing does not remove the
secret — that is the premise of this tool. Treat any secret that ever reached a shared
remote as compromised regardless of what the history looks like afterwards.

## Out of scope

- False positives. Tune `.secretscout.yaml` and open a normal issue; the entropy gate and
  the rule set are data you are meant to adjust.
- Unsupported secret formats. That is a feature request — new rules are welcome.
