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

**Status**: ✅ Complete - 45 tests passing (TASK-015, TASK-020)

**Coverage**:
- State creation (WorkflowState, SimpleState, MultiAgentState)
- Message reducer functionality (add_messages)
- Data reducer functionality (merge_dicts)
- Agent results reducer functionality (merge_agent_results)
- Status reducer functionality (last_value)
- State validation (validate_state, validate_simple_state, validate_multi_agent_state)
- State updates with reducers
- Type hints validation

**Test Categories**:
- State creation (6 tests: 3 WorkflowState, 3 MultiAgentState)
- Message reducer (3 tests)
- Data reducer (4 tests)
- Agent results reducer (4 tests)
- Status reducer (3 tests)
- State validation (12 tests: 7 WorkflowState, 5 MultiAgentState)
- State updates (9 tests: 4 WorkflowState, 5 MultiAgentState)
- Type hints (3 tests: 2 WorkflowState, 1 MultiAgentState)

**Run Tests**:
```bash
pytest project/tests/langgraph/test_state.py -v
```

### `test_basic_workflow.py` ✅ Complete
Comprehensive tests for basic LangGraph StateGraph workflow with nodes.

**Status**: ✅ Complete - 18 tests passing (TASK-016)

**Coverage**:
- Node function tests (node_a, node_b)
- Graph construction and compilation
- Workflow execution end-to-end
- State updates through nodes
- State reducer behavior
- Error handling

**Test Categories**:
- Node function tests (5 tests)
- Graph construction tests (3 tests)
- Workflow execution tests (5 tests)
- State update tests (3 tests)
- Error handling tests (2 tests)

**Run Tests**:
```bash
pytest project/tests/langgraph/test_basic_workflow.py -v
```

### `test_conditional_routing.py` ✅ Complete
Comprehensive tests for conditional routing in LangGraph workflows.

**Status**: ✅ Complete - 15 tests passing (TASK-017)

**Coverage**:
- Routing function tests (should_continue)
- Conditional edge execution
- Error handler node
- End-to-end workflow execution with different routing paths

**Run Tests**:
```bash
pytest project/tests/langgraph/test_conditional_routing.py -v
```

### `test_checkpointing.py` ✅ Complete
Comprehensive tests for LangGraph checkpointing functionality.

**Status**: ✅ Complete - 22 tests passing (TASK-018)

**Coverage**:
- Checkpointer configuration
- Thread ID management
- Checkpoint saving and loading
- State persistence
- Workflow resumption
- Checkpoint isolation

**Run Tests**:
```bash
pytest project/tests/langgraph/test_checkpointing.py -v
```

### `test_agent_nodes.py` ✅ Complete
Comprehensive tests for LangGraph specialized agent nodes.

**Status**: ✅ Complete - 16 tests passing (TASK-021)

**Coverage**:
- Data agent functionality (data_agent)
- Analysis agent functionality (analysis_agent)
- Error handling versions (data_agent_with_error_handling, analysis_agent_with_error_handling)
- State update patterns
- Result format consistency

**Test Categories**:
- Data agent tests (4 tests)
- Analysis agent tests (4 tests)
- Error handling tests (4 tests)
- State update tests (3 tests)
- Result format consistency (1 test)

**Test Philosophy**:
- ✅ Real LangGraph components (no mocks)
- ✅ Production-like test data (no placeholders)
- ✅ Actual state updates (not stubbed)
- ✅ Real reducer functions (not mocked)

**Run Tests**:
```bash
pytest project/tests/langgraph/test_agent_nodes.py -v
```

### `test_orchestrator.py` ✅ Complete
Comprehensive tests for LangGraph orchestrator agent node.

**Status**: ✅ Complete - 21 tests passing (TASK-022)

**Coverage**:
- Orchestrator agent functionality (orchestrator_agent)
- Routing function (route_to_agent)
- Error handling version (orchestrator_agent_with_errors)
- Integration with real agent nodes
- Complete production workflow sequence

**Test Categories**:
- Orchestrator agent tests (6 tests)
- Routing function tests (6 tests)
- Error handling tests (6 tests)
- Integration tests (3 tests, including complete production workflow)

**Test Philosophy**:
- ✅ Real LangGraph components (no mocks)
- ✅ Production-like test data (no placeholders)
- ✅ Actual state updates (not stubbed)
- ✅ Real agent nodes (not mocked)
- ✅ Complete workflow integration tests

**Run Tests**:
```bash
pytest project/tests/langgraph/test_orchestrator.py -v
```

### `test_multi_agent_workflow.py` ✅ Complete
Comprehensive tests for LangGraph multi-agent workflow.

**Status**: ✅ Complete - 19 tests passing (TASK-023, TASK-035)

**Coverage**:
- Graph construction and compilation
- Multi-agent workflow execution
- Agent routing and collaboration
- State persistence across agents
- Checkpointing with multi-agent workflows
- Error handling in multi-agent context
- Complete workflow integration scenarios
- LLM analysis node integration

**Test Categories**:
- Graph construction tests (3 tests)
- Workflow execution tests (3 tests)
- Agent routing tests (3 tests)
- State persistence tests (2 tests)
- Checkpointing tests (3 tests)
- Error handling tests (2 tests)
- Integration tests (3 tests, including LLM analysis)

**Test Philosophy**:
- ✅ Real LangGraph StateGraph (no mocks)
- ✅ Production-like test data (no placeholders)
- ✅ Actual checkpointing (InMemorySaver)
- ✅ Real agent nodes (not mocked)
- ✅ Complete workflow integration tests
- ✅ Optimized LLM model selection (gemma3:1b)

**Model Optimization**:
- **Test Model**: gemma3:1b (optimized for testing)
- **Performance**: 27.5% faster test suite
- **Override**: Use `TEST_OLLAMA_MODEL` environment variable

**Run Tests**:
```bash
pytest project/tests/langgraph/test_multi_agent_workflow.py -v
```

### `test_multi_agent_integration.py` ✅ Complete
Comprehensive integration tests for multi-agent workflow validating all Milestone 1.5 acceptance criteria.

**Status**: ✅ Complete - 17 tests passing (TASK-024)

**Coverage**:
- All 8 Milestone 1.5 acceptance criteria validation
- Complete multi-agent workflow execution
- Agent collaboration patterns
- State persistence across agents
- Conditional routing integration
- Checkpointing integration
- Error handling in multi-agent context
- Multiple workflow executions
- Metadata handling

**Test Categories**:
- Acceptance Criteria Tests (8 tests): One test per Milestone 1.5 acceptance criterion
  - AC1: Specialized agents created
  - AC2: StateGraph configured with multiple nodes
  - AC3: Agents collaborate successfully
  - AC4: Conditional routing implemented
  - AC5: State management working
  - AC6: Agent results aggregated
  - AC7: Workflow completes successfully
  - AC8: Checkpointing works
- Integration Scenario Tests (8 tests): Complete workflow scenarios
- Comprehensive Validation Test (1 test): Validates all acceptance criteria in single test

**Test Coverage**:
- `multi_agent_workflow.py`: 100% coverage (24 statements, 0 missing)
- All acceptance criteria explicitly validated
- Integration scenarios cover end-to-end workflows
- Error handling and edge cases tested

**Test Philosophy**:
- ✅ Real LangGraph StateGraph (no mocks)
- ✅ Production-like test data (no placeholders)
- ✅ Actual checkpointing (InMemorySaver)
- ✅ Real agent nodes (not mocked)
- ✅ Complete workflow integration tests
- ✅ All Milestone 1.5 acceptance criteria validated

**Run Tests**:
```bash
pytest project/tests/langgraph/test_multi_agent_integration.py -v
```

### `test_langchain_ollama_integration.py` ✅ Complete
Comprehensive tests for langchain-ollama package integration (TASK-026).

**Status**: ✅ Complete - 13 tests passing (TASK-026)

**Coverage**:
- Package import verification (primary and alternative import paths)
- Version requirement validation (>=0.1.0)
- OllamaLLM class attributes and initialization
- Dependency verification (ollama package)
- LangChain compatibility (BaseLLM inheritance)
- Requirements.txt validation
- Virtual environment verification
- Package metadata verification

**Test Categories**:
- Package import tests (3 tests)
- Version and requirements tests (2 tests)
- Class and initialization tests (3 tests)
- Dependency tests (2 tests)
- Compatibility tests (2 tests)
- Environment tests (1 test)

**Test Philosophy**:
- ✅ Real package imports (no mocks)
- ✅ Real class initialization (no placeholders)
- ✅ Production conditions only
- ✅ Actual version checks
- ✅ Real dependency verification

**Run Tests**:
```bash
pytest project/tests/langgraph/test_langchain_ollama_integration.py -v
```

### `test_llm_nodes.py` ✅ Complete
Production tests for LangGraph LLM nodes with Ollama integration.

**Status**: ✅ Complete - 16 tests passing (TASK-034, TASK-035)

**Coverage**:
- LLM node creation and configuration
- Real Ollama LLM inference (production conditions)
- LLM analysis node integration
- Error handling and model validation
- State preservation in LLM nodes
- Workflow integration with LLM nodes

**Test Categories**:
- LLM node creation tests (3 tests)
- LLM node execution tests (3 tests)
- LLM analysis node tests (3 tests)
- LLM node integration tests (2 tests)
- Error handling tests (5 tests)

**Test Philosophy**:
- ✅ **Production conditions only** - NO MOCKS, NO PLACEHOLDERS
- ✅ Real Ollama LLM instances
- ✅ Real model inference
- ✅ Actual Ollama service connection
- ✅ Optimized model selection (gemma3:1b)

**Model Optimization**:
- **Test Model**: gemma3:1b (~1.3 GB, 0.492s inference)
- **Performance**: 27.5% faster test suite (101.74s vs 140.42s)
- **Size**: 48% smaller than previous model (1.3 GB vs 2.5 GB)
- **Override**: Use `TEST_OLLAMA_MODEL` environment variable

**Run Tests**:
```bash
# Run with optimized model (default: gemma3:1b)
pytest project/tests/langgraph/test_llm_nodes.py -v

# Run with specific model
TEST_OLLAMA_MODEL=phi4-mini:3.8b pytest project/tests/langgraph/test_llm_nodes.py -v
```

**Documentation**: See `project/docs/llm-test-optimization-guide.md` for detailed optimization guide.

### `test_llm_integration.py` ✅ Complete
Comprehensive tests for LLM integration in LangGraph workflows validating all Milestone 1.7 acceptance criteria.

**Status**: ✅ Complete - 26 tests passing (TASK-037)

**Coverage**:
- All 7 Milestone 1.7 acceptance criteria validation
- Ollama LLM initialization and inference
- LLM node creation and execution
- LLM integration in LangGraph workflows
- Error handling and edge cases
- Model validation and availability
- Workflow integration scenarios

**Test Categories**:
- Milestone 1.7 Acceptance Criteria Tests (7 tests): All acceptance criteria validated
  - AC1: Ollama running locally
  - AC2: Model downloaded
  - AC3: LangChain integration working
  - AC4: Basic inference working
  - AC5: LangGraph workflow uses Ollama LLM
  - AC6: Model responses are reasonable
  - AC7: Error handling for LLM calls
- Ollama LLM Integration Tests (5 tests): Real LLM initialization and inference
- LLM Node Tests (5 tests): Node creation, execution, and error handling
- LLM Workflow Integration Tests (3 tests): Multi-agent and simple workflow integration
- Error Handling Tests (4 tests): Real error conditions and edge cases
- Model Validation Tests (2 tests): Model availability and default retrieval

**Test Philosophy**:
- ✅ **PRODUCTION CONDITIONS ONLY** - NO MOCKS, NO PLACEHOLDERS
- ✅ Real Ollama LLM instances
- ✅ Real model inference
- ✅ Actual Ollama service connection
- ✅ Real LangGraph workflows
- ✅ Real error conditions (invalid models, unavailable services)
- ✅ Optimized model selection (gemma3:1b)

**Model Optimization**:
- **Test Model**: gemma3:1b (~1.3 GB, 0.492s inference)
- **Performance**: Fast test execution with optimized model
- **Override**: Use `TEST_OLLAMA_MODEL` environment variable

**Test Coverage**: 89% coverage
- `langchain_ollama_integration/__init__.py`: 100%
- `langchain_ollama_integration/llm_factory.py`: 74%
- `langgraph_workflows/llm_nodes.py`: 94%

**Run Tests**:
```bash
# Run with optimized model (default: gemma3:1b)
pytest project/tests/langgraph/test_llm_integration.py -v

# Run with specific model
TEST_OLLAMA_MODEL=phi4-mini:3.8b pytest project/tests/langgraph/test_llm_integration.py -v

# Run with coverage
pytest project/tests/langgraph/test_llm_integration.py --cov=langchain_ollama_integration --cov=langgraph_workflows.llm_nodes -v
```

### `test_integration.py` ✅ Complete
Comprehensive integration tests for complete stateful workflow.

**Status**: ✅ Complete - 30 tests passing (TASK-019)

**Coverage**:
- Complete workflow execution (end-to-end)
- State persistence across steps
- Conditional routing integration
- Checkpointing integration
- Workflow resumption
- Error handling
- All Milestone 1.4 acceptance criteria validation

**Test Categories**:
- Complete workflow execution (4 tests)
- State persistence (3 tests)
- Conditional routing (4 tests)
- Checkpointing (4 tests)
- Workflow resumption (4 tests)
- Error handling (3 tests)
- Acceptance criteria validation (8 tests)

**Coverage**: >80% for all workflow modules
- checkpoint_workflow.py: 91% coverage
- conditional_workflow.py: 89% coverage
- agent_nodes.py: 100% coverage (16 tests)
- basic_workflow.py: 78% coverage
- state.py: 79% coverage

**Run Tests**:
```bash
pytest project/tests/langgraph/test_integration.py -v
```

## Status

- ✅ **Installation Tests** (TASK-014): Complete - 5 tests passing
- ✅ **State Definition Tests** (TASK-015, TASK-020): Complete - 45 tests passing (includes MultiAgentState)
- ✅ **Basic Workflow Tests** (TASK-016): Complete - 18 tests passing
- ✅ **Conditional Routing Tests** (TASK-017): Complete - 15 tests passing
- ✅ **Checkpointing Tests** (TASK-018): Complete - 22 tests passing
- ✅ **Integration Tests** (TASK-019): Complete - 30 tests passing
- ✅ **Agent Nodes Tests** (TASK-021): Complete - 16 tests passing
- ✅ **Orchestrator Tests** (TASK-022): Complete - 21 tests passing
- ✅ **Multi-Agent Workflow Tests** (TASK-023): Complete - 19 tests passing
- ✅ **Multi-Agent Integration Tests** (TASK-024): Complete - 17 tests passing
- ✅ **LangChain Ollama Integration Tests** (TASK-026): Complete - 13 tests passing
- ✅ **LLM Nodes Tests** (TASK-034, TASK-035): Complete - 16 tests passing
- ✅ **LLM Integration Tests** (TASK-037): Complete - 26 tests passing
- ✅ **Total**: 272 tests passing - All tests use production LangGraph environment

**CRITICAL**: All tests use real LangGraph libraries and production patterns. No mocks or placeholders are used.

**Performance Optimization**: Test suite optimized with gemma3:1b model - 27.5% faster runtime (101.74s vs 140.42s). See `project/docs/llm-test-optimization-guide.md` for details.

## Running Tests

```bash
# Run all LangGraph tests
pytest project/tests/langgraph/ -v

# Run only installation tests
pytest project/tests/langgraph/test_installation.py -v

# Run only state tests
pytest project/tests/langgraph/test_state.py -v

# Run only basic workflow tests
pytest project/tests/langgraph/test_basic_workflow.py -v

# Run only conditional routing tests
pytest project/tests/langgraph/test_conditional_routing.py -v

# Run only checkpointing tests
pytest project/tests/langgraph/test_checkpointing.py -v

# Run only integration tests
pytest project/tests/langgraph/test_integration.py -v

# Run only agent nodes tests
pytest project/tests/langgraph/test_agent_nodes.py -v

# Run only orchestrator tests
pytest project/tests/langgraph/test_orchestrator.py -v

# Run only multi-agent workflow tests
pytest project/tests/langgraph/test_multi_agent_workflow.py -v

# Run only multi-agent integration tests
pytest project/tests/langgraph/test_multi_agent_integration.py -v

# Run only langchain-ollama integration tests
pytest project/tests/langgraph/test_langchain_ollama_integration.py -v

# Run only LLM nodes tests
pytest project/tests/langgraph/test_llm_nodes.py -v

# Run only LLM integration tests
pytest project/tests/langgraph/test_llm_integration.py -v

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
- langchain-ollama 1.0.0+ (TASK-026)
- typing-extensions 4.8.0+
- pydantic 2.0.0+

## Test Requirements

All tests require:
- Virtual environment activated (`venv`)
- LangGraph and dependencies installed
- Python 3.11+

## Next Steps

- ✅ TASK-016: Basic StateGraph with Nodes Implementation (Complete - 18 tests)
- ✅ TASK-017: Conditional Routing Implementation (Complete - 15 tests)
- ✅ TASK-018: Checkpointing Configuration and Testing (Complete - 22 tests)
- ✅ TASK-019: Stateful Workflow Integration Tests (Complete - 30 tests)
- ✅ TASK-020: Multi-Agent State Structure Design (Complete - included in state tests)
- ✅ TASK-021: Specialized Agent Nodes Implementation (Complete - 16 tests)
- ✅ TASK-022: Orchestrator Agent Node Implementation (Complete - 21 tests)
- ✅ TASK-023: Multi-Agent StateGraph Configuration (Complete - 19 tests)
- ✅ TASK-024: Multi-Agent Collaboration Testing (Complete - 17 tests)
- ✅ TASK-026: LangChain-Ollama Integration (Complete - 13 tests)

**All Phase 2 Milestone 1.5 tasks complete!**
**Phase 3 Milestone 1.7 in progress: TASK-026 complete**

