# CLAIF TODO List

## Immediate Tasks (v1.0 Release)

### Testing & Validation
- [ ] Test with actual provider packages (claif_cla, claif_gem, claif_cod)
- [ ] Verify plugin discovery mechanism works correctly
- [ ] Test CLI commands with real API calls
- [ ] Validate MCP server functionality
- [ ] Check configuration loading hierarchy

### Documentation
- [ ] Add docstrings to remaining functions
- [ ] Create simple getting started guide
- [ ] Document environment variables
- [ ] Add troubleshooting section to README

### Code Quality
- [ ] Add basic unit tests for core components
- [ ] Set up pre-commit hooks
- [ ] Run mypy type checking
- [ ] Address any remaining linter warnings

### Release Preparation
- [ ] Verify package metadata in pyproject.toml
- [ ] Test package building with `python -m build`
- [ ] Create GitHub release workflow
- [ ] Prepare PyPI release

## Next Release (v1.1)

### Testing Infrastructure
- [ ] Set up pytest framework
- [ ] Add unit tests for all modules
- [ ] Create integration tests
- [ ] Add GitHub Actions CI

### Bug Fixes
- [ ] Fix any issues discovered in v1.0
- [ ] Improve error messages
- [ ] Handle edge cases better

### Documentation
- [ ] Create proper API documentation
- [ ] Add more usage examples
- [ ] Create provider comparison guide

## Future Enhancements (v1.2+)

### Features
- [ ] Implement response caching
- [ ] Add retry logic
- [ ] Session persistence
- [ ] Cost tracking

### Performance
- [ ] Optimize parallel queries
- [ ] Add connection pooling
- [ ] Implement rate limiting

## Non-Goals for v1.x

These items are intentionally excluded from near-term plans:
- Web UI (use existing MCP tools instead)
- Complex prompt engineering features
- Provider-specific advanced features
- Database backends
- Authentication systems
- Multi-user support

## Contributing

When adding new items:
1. Keep tasks small and specific
2. Focus on core functionality
3. Avoid feature creep
4. Prioritize stability over features