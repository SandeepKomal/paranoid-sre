# Privacy and India's DPDP Act

paranoid-sre is a Claude skill: Markdown instructions that Claude reads. It
has no code that runs, keeps no data, and sends nothing to the project or
anyone else. So it is never a Data Fiduciary or Data Processor under India's
**Digital Personal Data Protection Act, 2023** (DPDP Act).

What it does is shape how an AI agent handles personal data while it works
on your infrastructure and databases. Those habits help your organisation,
which *is* the Data Fiduciary, meet its duties.

> This page explains what the skill asks Claude to do. It is not legal
> advice. Check the current notified DPDP Rules and your own legal team
> before relying on it.

## What the skill tells Claude to do with personal data

From the "Personal data and secrets" section of
[SKILL.md](../skills/paranoid/SKILL.md):

| Habit | Why it matters under DPDP |
| --- | --- |
| Count rows or select only the needed columns with a `LIMIT`; don't print whole tables of customer data | Purpose limitation and data minimisation (Sec. 4, 6): the agent sees no more personal data than the task needs, and less ends up in its context and logs. |
| Don't copy production personal data into other environments, local files, tickets, commit messages or logs; use masked or synthetic data | Reasonable security safeguards (Sec. 8(5)) and storage limitation (Sec. 8(7)): every copy is another place to secure and later erase. |
| Never print secrets; use the tool's own prompt instead of `--password=...` | Security safeguards: credentials in transcripts and shell history are a common breach path. |
| Treat deleting personal data as irreversible, name it under "Data loss" and wait for a clear yes | Erasure can be a legal duty (Sec. 12, an erasure request) or a breach (a retention obligation). A person decides, not the agent. |
| Preview `DELETE` and `UPDATE` with `SELECT count(*)` first, and back up before irreversible changes | Accuracy (Sec. 8(3)) and avoiding accidental loss, which can be a personal data breach (Sec. 8(6)). |

## Checklist

✅ the skill does this · 🟡 the skill helps, your organisation completes it ·
🏢 your organisation's responsibility · ➖ does not apply

| # | Requirement | Status | How |
| --- | --- | --- | --- |
| 1 | The tool itself collects or transfers no personal data | ✅ | Instructions only; no code, telemetry or network access. |
| 2 | Data minimisation when the agent works with personal data | ✅ | Counts and limited selects instead of full dumps. |
| 3 | No copies of production personal data in other places | ✅ | Explicit rule in the skill. |
| 4 | No secrets in commands, logs or transcripts | ✅ | Explicit rule in the skill. blast-radius also masks secrets in its activity log. |
| 5 | Human approval before destroying personal data | ✅ | Step 6: target, change, data loss, way back and exact command, then a clear yes. |
| 6 | A record of what the agent did | 🟡 | Install blast-radius with its activity log, which records commands and paranoid-sre's steps with personal data masked, and supports retention, access and erasure. |
| 7 | Lawful basis, notice and consent for the agent's access to personal data | 🏢 | Decide which systems an AI agent may touch and tell the people concerned. |
| 8 | Least-privilege access for the agent | 🏢 | Give the agent read-only or narrowly scoped credentials. The skill forbids widening its own access. |
| 9 | Breach detection and notification | 🏢 | Include AI agent activity in your incident response plan. |
| 10 | Cross-border transfer | ➖ | The skill transfers nothing. What Claude Code sends to Anthropic is governed by your agreement with Anthropic. |
