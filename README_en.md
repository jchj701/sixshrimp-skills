# sixshrimp-skills

English | [中文](./README.md)

My [Claude Code](https://docs.anthropic.com/en/docs/claude-code) custom skills collection.

## Installation

Using [skills CLI](https://github.com/vercel-labs/skills) (via `npx`):

```bash
# Install all skills (global)
npx skills add jchj701/sixshrimp-skills -g --all

# Install a single skill
npx skills add jchj701/sixshrimp-skills -g --skill skill-quality-rater

# List available skills
npx skills add jchj701/sixshrimp-skills -l
```

Or manually:

```bash
git clone https://github.com/jchj701/sixshrimp-skills.git
cp -r sixshrimp-skills/skills/* ~/.claude/skills/
```

## Skills

| Skill | Version | Description | Dependencies |
|:---|:---:|:---|:---|
| **skill-quality-rater** | 0.1.0 | 8-dimension skill quality rater | Python 3 |
| **browser-learn-skill** | 0.1.0 | Browser operation recording & AI self-learning | Python 3, browser-use SDK |

## ⚠️ Status: Untested

These skills are **work-in-progress and have NOT been tested in a real Claude Code environment yet**. They are shared as-is for:

- Reference and inspiration for skill design patterns
- Community feedback and collaboration
- Iterative improvement before production use

Expect rough edges. Use at your own risk. Issues and PRs welcome.

---

## skill-quality-rater

An 8-dimension skill quality evaluator that systematizes design principles from Anthropic, OpenAI, Google, and others into an executable assessment framework.

### Concept Attribution

The evaluation dimensions are not invented from scratch. They originate from established industry practices:

| Dimension | Source | Notes |
|:---|:---|:---|
| Freedom Spectrum | [Anthropic "Degrees of Freedom"](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/skill-authoring-best-practices) | High/Medium/Low freedom classification |
| Layered Architecture L1/L2/L3 | [Anthropic "Progressive Disclosure"](https://www.anthropic.com/news/equipping-agents-for-the-real-world-with-agent-skills) (2025-10-16) | Also adopted by [OpenAI skill-creator](https://github.com/openai/skills) and [Google ADK](https://cloud.google.com/blog/topics/developers-practitioners/5-agent-skill-design-patterns-every-adk-developer-should-know) |
| Inversion Test | Inspired by [OpenAI skill-creator](https://github.com/openai/skills) "inversion test" | skill-creator mentions rewriting positive guidance as "don't do X"; this skill **systematizes it as a formal evaluation dimension** |
| Negative Triggers | [Anthropic best practices](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/skill-authoring-best-practices) + [Google ADK Inversion Pattern](https://cloud.google.com/blog/topics/developers-practitioners/5-agent-skill-design-patterns-every-adk-developer-should-know) | Consensus solution for over-triggering |

**This skill's innovation**: Integrating the above scattered design principles into an executable 8-dimension scoring framework, with automated detection scripts (trigger collision, sensitive info leakage, freedom level suggestions).

### 8-Dimension Scoring Framework

| Dimension | Weight | Core Check |
|:---|:---:|:---|
| D1 Trigger Precision | 15% | Description includes "when to use", no trigger conflicts |
| D2 Layer Rationality | 20% | L1/L2/L3 each in its place, scripts executed not read |
| D3 Freedom Matching | 20% | Fragile ops → scripts, creative → free-form text |
| D4 Concise Constraints | 15% | No README/CHANGELOG bloat, every sentence earns its tokens |
| D5 Anti-pattern Expression | 10% | "Don't do X" is more precise than "do Y" |
| D6 Resource Organization | 10% | scripts/references/assets properly separated |
| D7 Domain Adaptation | 5% | Follows domain-specific best practices |
| D8 Security Boundary | 5% | No dangerous commands, no sensitive info leakage |

### File Structure

```
skill-quality-rater/
├── SKILL.md                      # Main skill definition
├── references/
│   ├── dimension_rubric.md       # Detailed scoring rubric per dimension
│   ├── freedom_spectrum.md       # Freedom spectrum decision guide
│   ├── layer_architecture.md     # L1/L2/L3 layer architecture spec
│   ├── antipattern_library.md    # Anti-pattern catalog
│   ├── forbidden_files.md        # Files that should never appear in a skill
│   └── domain_rules/             # Domain-specific rule libraries
│       ├── document-processing.yaml
│       ├── data-analysis.yaml
│       └── code-development.yaml
├── scripts/
│   ├── trigger_collision.py      # Trigger word collision detection
│   ├── leakage_detector.py       # Sensitive information leakage detection
│   └── suggest_freedom.py        # Freedom level suggestion generator
└── templates/
    ├── eval_report.md            # Evaluation report template
    ├── improvement_plan.md       # Improvement plan template
    └── batch_summary.md          # Batch evaluation summary template
```

---

## browser-learn-skill

A skill for browser operation recording and AI self-learning execution. Defines the complete pipeline from human demonstration to automated execution.

### Core Principle

> **"AI should never make uncertain decisions. One-time operations must be flagged. If the environment isn't ready, don't proceed."**

### 5 Execution Phases

| Phase | Name | What It Does |
|:---:|:---|:---|
| 1 | Reproducibility Check | Determine if an operation can be scripted |
| 2 | Environment Readiness | Verify dependencies, permissions, network status |
| 3 | Recording Interpretation | Parse human operation sequences |
| 4 | Confidence Scoring | Self-assess certainty before execution |
| 5 | Script Solidification | Convert high-confidence operations into reusable scripts |

### 7 AI Boundary Constraints

The skill enforces strict boundaries on AI autonomy:
- No executing irreversible actions without confirmation
- No proceeding when environment checks fail
- No skipping anomaly reporting
- No fabricating confidence scores

### File Structure

```
browser-learn-skill/
├── SKILL.md                      # Main skill definition (446 lines)
├── references/
│   ├── reproducibility-checklist.md  # Reproducibility判定标准
│   ├── script-format-spec.md         # Script format specification
│   ├── confidence-scoring.md         # Confidence scoring criteria
│   └── solidification-criteria.md    # Script solidification criteria
└── scripts/
    ├── env_readiness_check.py    # Environment readiness checker
    └── script_sanitize.py        # Recorded script sanitizer
```

---

## References

- [Anthropic: Equipping agents for the real world with Agent Skills](https://www.anthropic.com/news/equipping-agents-for-the-real-world-with-agent-skills) (2025-10-16)
- [Anthropic: Skill authoring best practices](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/skill-authoring-best-practices)
- [Anthropic: The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
- [OpenAI: skill-creator](https://github.com/openai/skills)
- [Google ADK: 5 Agent Skill Design Patterns](https://cloud.google.com/blog/topics/developers-practitioners/5-agent-skill-design-patterns-every-adk-developer-should-know)
- [OpenAI: Prompt Engineering Best Practices](https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-openai-api)

---

## License

[MIT](./LICENSE)
