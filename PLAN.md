#Claif Development Plan

## Overview

CLAIF (Command-Line Artificial Intelligence Framework) is a unified interface for interacting with multiple AI language model providers. The core framework (v1.0) is already complete and stable.

## Immediate Priorities (v1.0.x)

1. **Provider Packages**
   - Implement and release:
     - `claif_cla` (Claude SDK wrapper)
     - `claif_gem` (Gemini CLI wrapper)
     - `claif_cod` (OpenAI/Codex CLI wrapper)
2. **Integration & Testing**
   - End-to-end tests that cover provider discovery and real API calls
   - Example notebooks & CLI demos that use real providers
3. **Packaging & Release**
   - Verify `python -m build` succeeds
   - Publish core `claif` 1.0.x to PyPI
   - Set up GitHub release workflow
4. **Documentation**
   - Provider implementation guide
   - Troubleshooting section for common issues

## Short-Term Roadmap (v1.1)

| Area                | Goals |
| ------------------- | ----- |
| **Testing**         | 80 %+ unit-test coverage, GitHub Actions CI |
| **Code Quality**    | mypy type-checking, pre-commit hooks |
| **Bug Fixes**       | Address feedback from initial users |
| **Docs**            | Full API references, more examples |

## Mid-Term Roadmap (v1.2+)

* Response caching and retry logic
* Session persistence
* Cost tracking & rate limiting
* Performance optimisations (parallel queries, connection pooling)

## Design Principles

1. **Minimal Viable First** – deliver essential functionality quickly.
2. **Provider Independence** – clean separation between core and providers.
3. **Async-First** – embrace modern `async`/`await` patterns.
4. **Type Safety** – comprehensive type hints.
5. **Simplicity** – avoid over-engineering; prefer clear, concise code.

## Current Status Summary

The core `claif` package is production-ready; the next step is to build and integrate the individual provider packages listed above.