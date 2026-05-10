# SynthData Agent Handbook

This product inherits the company-wide agent operating standards from
[CreativeWare HQ Handbook](https://github.com/fratei/creative-ware-hq/blob/main/docs/agents/HANDBOOK.md).
The link currently uses `main` and should be switched to the `v1` reference when the framework tag is published.

## Product-Specific Overrides

### Sensitive paths (escalate to owner regardless of tier)
- `**/data/**` — synthetic data generation logic
- `**/synthetic-data/**` — outputs and templates
- `**/privacy/**` — privacy-related code paths

These are enforced via `config/agents.config.json#autonomy.tiers.high_extra_paths`.

### Higher SLA
SynthData uses a 72h decision SLA (vs HQ's 48h) because it's in `development` status
with no live customers.

## Linked Resources

- [Agent Charters](./charters/) — copied from framework main (switch to v1 after tag)
- [Framework Version](../../framework-version)
- [Local Config Overrides](../../config/agents.config.json)

## Human/Admin Actions Checklist

Use this checklist when enabling new autonomy stages for SynthData:

- [ ] Configure required repository secrets (`AGENT_PAT`, cloud/provider credentials, deploy credentials).
- [ ] Enable branch protection on `main` (required status checks + review policy).
- [ ] Enable auto-merge policy only after CI and PR pipeline are stable.
- [ ] Verify scheduled workflows are enabled in repository settings.
- [ ] Confirm incident routing (for `incident-detected` repository dispatch events).
- [ ] When framework `v1` is available, switch all `@main` reusable workflow references to `@v1`.
