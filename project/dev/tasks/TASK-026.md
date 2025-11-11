# TASK-026: Update Requirements with LangChain-Ollama Integration

## Task Information
- **Task ID**: TASK-026
- **Created**: 2025-01-27
- **Status**: Waiting
- **Priority**: High
- **Agent**: Mission Executor
- **Estimated Time**: 0.5-1 hour
- **Actual Time**: TBD
- **Type**: Dependencies
- **Dependencies**: None
- **Parent PRD**: `project/docs/prd_phase3.md` - Milestone 1.7

## Task Description
Update requirements.txt to include `langchain-ollama` package for Ollama LLM integration. This corrects the PRD which incorrectly references `langchain_community.llms.Ollama` (deprecated). Use the official `langchain-ollama` package as validated by Mission Analyst.

## Problem Statement
The PRD Phase 3 shows incorrect import: `from langchain_community.llms import Ollama`. Mission Analyst identified this as deprecated. The correct package is `langchain-ollama` which provides `OllamaLLM` class. This must be added to requirements.txt before implementation.

## Requirements

### Functional Requirements
- [ ] `langchain-ollama` package added to requirements.txt
- [ ] Version constraint specified (>=0.1.0)
- [ ] Package compatible with existing LangChain version
- [ ] Dependencies documented

### Technical Requirements
- [ ] Package name: `langchain-ollama`
- [ ] Minimum version: 0.1.0
- [ ] Compatibility with `langchain>=0.2.0` (existing)
- [ ] Compatibility with `langgraph>=0.6.0` (existing)

## Implementation Plan

### Phase 1: Analysis
- [ ] Review current requirements.txt
- [ ] Verify langchain-ollama package availability
- [ ] Check version compatibility with existing packages
- [ ] Review Mission Analyst findings on correct package

### Phase 2: Planning
- [ ] Determine appropriate version constraint
- [ ] Plan package addition
- [ ] Verify compatibility

### Phase 3: Implementation
- [ ] Add `langchain-ollama>=0.1.0` to requirements.txt
- [ ] Verify package name and version
- [ ] Test package installation in venv
- [ ] Verify import works: `from langchain_ollama import OllamaLLM`

### Phase 4: Testing
- [ ] Install package: `pip install -r requirements.txt`
- [ ] Verify import: `python -c "from langchain_ollama import OllamaLLM; print('OK')"`
- [ ] Verify no dependency conflicts
- [ ] Test basic OllamaLLM initialization

### Phase 5: Documentation
- [ ] Document package addition
- [ ] Document correct import pattern
- [ ] Update any existing documentation referencing incorrect import

## Technical Implementation

### Requirements.txt Update
```txt
# Core dependencies for LangGraph development environment
# TASK-014: LangGraph Development Environment Setup

# LangGraph and LangChain
langgraph>=0.6.0
langchain>=0.2.0
langchain-core>=0.2.0

# Ollama Integration (TASK-026: Phase 3)
langchain-ollama>=0.1.0

# Core dependencies
pydantic>=2.0.0
typing-extensions>=4.8.0
```

### Correct Import Pattern
```python
# CORRECT (use this):
from langchain_ollama import OllamaLLM

# INCORRECT (do not use):
# from langchain_community.llms import Ollama
```

## Testing

### Manual Testing
- [ ] Activate venv: `source venv/bin/activate`
- [ ] Install: `pip install -r requirements.txt`
- [ ] Verify import: `python -c "from langchain_ollama import OllamaLLM"`
- [ ] Test initialization: `llm = OllamaLLM(model="llama2", base_url="http://localhost:11434")`
- [ ] Verify no import errors

### Automated Testing
- [ ] Requirements validation test
- [ ] Import test
- [ ] Dependency conflict check

## Acceptance Criteria
- [ ] `langchain-ollama>=0.1.0` added to requirements.txt
- [ ] Package installs successfully
- [ ] Import works: `from langchain_ollama import OllamaLLM`
- [ ] No dependency conflicts
- [ ] Basic initialization works
- [ ] Documentation updated with correct import pattern

## Dependencies
- **External**: langchain-ollama package (PyPI)
- **Internal**: requirements.txt, existing LangChain packages

## Risks and Mitigation

### Risk 1: Package Not Available
- **Probability**: Very Low
- **Impact**: High
- **Mitigation**: Verify package exists on PyPI, check package name spelling, use official LangChain package

### Risk 2: Version Compatibility Issues
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**: Test with existing LangChain version, check package compatibility matrix, use compatible versions

### Risk 3: Import Path Changes
- **Probability**: Low
- **Impact**: Medium
- **Mitigation**: Verify import path in package documentation, test import before implementation

## Task Status
- [ ] Analysis Complete
- [ ] Planning Complete
- [ ] Implementation Complete
- [ ] Testing Complete
- [ ] Documentation Complete

## Notes
- **CRITICAL**: Use `langchain-ollama` (not `langchain_community.llms.Ollama`)
- Mission Analyst identified this as critical issue in PRD
- Package provides `OllamaLLM` class (not `Ollama`)
- Verify package installation before proceeding with TASK-033
- Document correct import pattern for future reference

