# {{PRODUCT_NAME}} — Agent Handbook

> Product-level agent operating standards. See also the [company-wide handbook](https://github.com/fratei/creative-ware-hq/blob/main/docs/agents/HANDBOOK.md).

## Product Agents

| Agent | Role |
|-------|------|
| 📦 CPO | Product roadmap, feature prioritization |
| 🔧 CTO | Technical architecture, tech debt |
| 💰 CFO | Financial analysis |
| 💻 Engineering | Implementation via @copilot |
| 🧪 QA | Testing, quality gates |
| ⚙️ DevOps | CI/CD, monitoring |

## Operating Rules

- Follow the [company-wide handbook](https://github.com/fratei/creative-ware-hq/blob/main/docs/agents/HANDBOOK.md)
- Auto-approve safe changes (src/, docs/, tests/)
- Escalate risky changes (workflows, infra, billing, auth)
- Max 5 auto-merges per day
- State persists in `strategy/agent-state/`
- Outcomes tracked in `strategy/outcomes/`
