# CLAIF TODO List

## Critical: Provider Package Implementation

### Provider Packages Need Implementation
- [ ] Implement `claif_cla` package with claude_code_sdk integration
- [ ] Implement `claif_gem` package with gemini-cli integration  
- [ ] Implement `claif_cod` package for OpenAI/Codex
- [ ] Test plugin discovery with real provider packages
- [ ] Ensure providers properly register via entry points

## Immediate Tasks (Core Framework Polish)

### Testing & Validation
- [x] Plugin discovery mechanism implemented
- [x] CLI commands structure complete
- [x] MCP server implementation done
- [x] Configuration loading hierarchy working
- [ ] Test with actual provider packages once implemented
- [ ] End-to-end testing with real APIs

### Documentation
- [x] Comprehensive README created
- [x] All core functions have docstrings
- [x] Environment variables documented
- [x] Architecture explained in detail
- [ ] Create provider implementation guide
- [ ] Add troubleshooting for common issues

### Code Quality  
- [x] Loguru logging implemented throughout
- [x] Type hints on all public APIs
- [ ] Add unit tests for core components
- [ ] Set up pre-commit hooks
- [ ] Run mypy type checking
- [ ] Add pytest fixtures

### Release Preparation
- [x] Package metadata configured
- [x] Build system (hatchling) set up
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