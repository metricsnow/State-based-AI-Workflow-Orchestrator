# LangGraph Tests

Tests for LangGraph state definitions, reducers, and workflow implementations.

## Testing Philosophy

**CRITICAL**: All LangGraph tests run against **production conditions** - **NEVER with placeholders or mocks**.

- Tests use **real LangGraph libraries** (not mocked)
- Tests validate **actual state definitions** (not stubbed)
- Tests verify **real reducer functions** (not placeholders)
- Tests execute against **production LangGraph patterns** (not test implementations)

**No placeholders. No mocks. Production LangGraph environment only.**

## Test Files

### `test_installation.py` ✅ Complete
LangGraph development environment verification tests.

**Status**: ✅ Complete - 5 tests passing (TASK-014)

**Coverage**:
- Core package imports (langgraph, langchain, langchain_core, pydantic, typing_extensions)
- LangGraph component imports (StateGraph, START, END, InMemorySaver)
- Package version requirements validation
- Development dependencies verification
- Virtual environment detection

**Run Tests**:
```bash
pytest project/tests/langgraph/test_installation.py -v
```

### `test_state.py` ✅ Complete
Comprehensive tests for LangGraph state definitions and reducers.

**Status**: ✅ Complete - 26 tests passing (TASK-015)

**Coverage**:
- State creation (WorkflowState, SimpleState)
- Message reducer functionality (add_messages)
- Data reducer functionality (merge_dicts)
- Status reducer functionality (last_value)
- State validation (validate_state, validate_simple_state)
- State updates with reducers
- Type hints validation

**Test Categories**:
- State creation (3 tests)
- Message reducer (3 tests)
- Data reducer (4 tests)
- Status reducer (3 tests)
- State validation (7 tests)
- State updates (4 tests)
- Type hints (2 tests)

**Run Tests**:
```bash
pytest project/tests/langgraph/test_state.py -v
```

## Status

- ✅ **Installation Tests** (TASK-014): Complete - 5 tests passing
- ✅ **State Definition Tests** (TASK-015): Complete - 26 tests passing
- ✅ **Total**: 31 tests passing - All tests use production LangGraph environment

**CRITICAL**: All tests use real LangGraph libraries and production patterns. No mocks or placeholders are used.

## Running Tests

```bash
# Run all LangGraph tests
pytest project/tests/langgraph/ -v

# Run only installation tests
pytest project/tests/langgraph/test_installation.py -v

# Run only state tests
pytest project/tests/langgraph/test_state.py -v

# Run with coverage
pytest project/tests/langgraph/ --cov=project/langgraph_workflows --cov-report=term-missing
```

## State Module

The state definitions are implemented in `project/langgraph_workflows/`:

- **state.py**: TypedDict state schemas with reducers
  - `WorkflowState`: Complex state for multi-agent workflows
  - `SimpleState`: Simplified state for basic workflows
  - `merge_dicts`: Dictionary merge reducer
  - `last_value`: Status field reducer
  - `validate_state`: State validation functions

**State Schemas**:
- `WorkflowState`: messages (add_messages), task_data (merge_dicts), agent_results (merge_dicts), workflow_status (last_value), metadata (merge_dicts)
- `SimpleState`: data (merge_dicts), status (last_value)

All state fields use proper reducers for correct state aggregation in LangGraph workflows.

## Dependencies

- LangGraph 1.0.3+
- LangChain 1.0.5+
- typing-extensions 4.8.0+
- pydantic 2.0.0+

## Test Requirements

All tests require:
- Virtual environment activated (`venv`)
- LangGraph and dependencies installed
- Python 3.11+

## Next Steps

- TASK-016: Basic StateGraph with Nodes Implementation
- TASK-017: Conditional Routing Implementation
- TASK-018: Checkpointing Configuration and Testing

