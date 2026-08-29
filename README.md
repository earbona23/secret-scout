# secret-scout

Finds secrets — API keys, tokens, private keys — that leaked into a git repository,
including ones **already deleted from the current files but still alive in history**.
It never prints the secret in full.

## The problem

Deleting a secret from a file and committing does not remove it. It stays in the earlier
commit forever, and anyone with a clone recovers it with `git show`. Scanning only the
current files is exactly why leaks survive for years. secret-scout walks every blob of
every commit, so a key that was "removed" last month still gets found.

## Try it in one command

```bash
git clone https://github.com/earbona23/secret-scout
cd secret-scout
python -m scout.cli --demo
```

`--demo` builds a throwaway repo with **fictional** secrets planted in its history — one of
them deleted in a later commit — and scans it, so you see the point immediately:

```
4 possible secret(s):

  Stripe live secret key
    .env:1
    sk_l…uvwx (sha256:1d420a5c0cf5)  ·  entropy 4.56
  AWS Access Key ID
    commit f31bb941: config.py:1        ← removed from the tree, still in history
    AKIA…MPLE (sha256:1a5d44a2dca1)  ·  entropy 3.68
```

## Scan a real repo

```bash
pip install -r requirements.txt
python -m scout.cli /path/to/repo               # working tree
python -m scout.cli /path/to/repo --historial   # + full commit history
python -m scout.cli /path/to/repo --historial --json report.json
```

It exits with code `1` when it finds anything, so it works as a CI step that blocks a
merge:

```yaml
- run: python -m scout.cli . --historial
```

## Two decisions that define the tool

**The secret is never printed in full.** A secrets scanner that dumps the secret into its
own report makes a second copy of the problem — in the CI log, in a shared terminal.
secret-scout shows a **fingerprint**: first and last few characters plus a short sha256.
That's enough to recognize and correlate a leak across commits without revealing it.

**Generic patterns require minimum entropy.** `password = "changeme"` is not a secret;
`password = "S9v!aX2p_Qz7Lm3RtWc8Yb1Nf6Kd0Hj"` is. Shannon entropy separates the two, and
it's what makes a generic pattern usable without drowning you in false positives. A tool
that cries wolf gets turned off — and a tool that's off finds nothing.

## Rules

Detection rules live in [`rules/rules.yaml`](rules/rules.yaml), editable so you can add the
providers your stack uses. Each rule carries a fictional example that a test asserts the
rule actually catches — so a rule can't silently rot into a pattern that matches nothing.

## Limitations — stated honestly

- It matches **patterns and entropy**, so it finds shapes of secrets, not proof. Expect
  false positives on high-entropy non-secrets (hashes, UUIDs in some formats) and false
  negatives on secrets with no distinctive shape. Treat output as leads to verify.
- Finding a leaked secret means **it must be rotated**, not just deleted. Removing it from
  history (e.g. `git filter-repo`) does not un-leak a key that was ever pushed — assume it's
  compromised and rotate it. This tool finds; it does not rotate.
- History scans of very large repos are proportionally slower; use `--max-commits` to bound.
- It is not a replacement for a pre-commit hook — it's the net that catches what already
  got through.

## Contributing

New rules are welcome — add a `patron` and a fictional `ejemplo`, and the test suite will
require the rule to catch its own example. Run `pytest -q` and `ruff check .`.

## License

MIT — see [LICENSE](LICENSE).
