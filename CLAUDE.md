# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Overview

This is a personal Claude Code skills repository. Each skill is a self-contained directory under `skills/` that can be installed to `~/.claude/skills/`.

## Repository Structure

```
sixshrimp-skills/
├── skills/
│   ├── skill-quality-rater/    # 8-dimension skill quality rater
│   └── browser-learn-skill/    # Browser operation recording & AI self-learning
├── README.md                   # Chinese (default)
├── README_en.md                # English
├── CLAUDE.md
├── LICENSE
└── .gitignore
```

## Skill Format

Each `SKILL.md` follows this structure:

```yaml
---
name: skill-name
description: "What this skill does. Use when..."
version: "x.x.x"
---

# Skill content in markdown...
```

## Architecture Notes

- Skills are atomic units — each directory is self-contained
- `references/` holds detail docs, loaded on demand (zero token cost when unused)
- `scripts/` holds executable tools, called explicitly (not read into context)
- `templates/` holds output format templates

## Development

```bash
# Copy to Claude Code for testing
cp -r skills/skill-quality-rater ~/.claude/skills/
```
