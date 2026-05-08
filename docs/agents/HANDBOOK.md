# SynthData Agent Handbook

This product inherits the company-wide agent operating standards from
[CreativeWare HQ Handbook](https://github.com/fratei/creative-ware-hq/blob/main/docs/agents/HANDBOOK.md).

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
