# Script Tests

Tests for project scripts, including Ollama model management scripts.

## Testing Philosophy

**CRITICAL**: All tests use production conditions - **NO MOCKS, NO PLACEHOLDERS**.

- Tests use **real Ollama CLI** (not mocked)
- Tests validate **actual model availability** (not stubbed)
- Tests execute **real commands** (not simulated)
- Tests connect to **real Ollama service** (not in-memory implementations)

**No placeholders. No mocks. Production Ollama environment only.**

## Test Files

### `test_ollama_model_management.py` ✅ Complete

Comprehensive tests for Ollama model management scripts.

**Status**: ✅ Complete - 14 tests passing (TASK-036)

**Coverage**:
- Model download script (`download_ollama_model.py`)
- Model validation script (`validate_ollama_models.py`)
- Docker setup script (`setup-ollama-models.sh`)
- Script existence and executability
- Model listing functionality
- Model validation (existing and non-existent models)
- Multiple model validation
- Integration workflow testing
- Error handling

**Test Classes**:
- `TestModelDownloadScript`: Download script tests
- `TestModelValidationScript`: Validation script tests
- `TestDockerSetupScript`: Docker setup script tests
- `TestScriptIntegration`: Integration workflow tests
- `TestErrorHandling`: Error handling tests

**Execution Time**: ~12 seconds (well under 1 minute requirement)

**Run Tests**:
```bash
# Run all script tests
pytest project/tests/scripts/ -v

# Run specific test file
pytest project/tests/scripts/test_ollama_model_management.py -v -s

# Run with detailed output
pytest project/tests/scripts/test_ollama_model_management.py -v -s --tb=short
```

## Test Requirements

### Prerequisites
- Ollama CLI must be installed and in PATH
- At least one Ollama model should be available (for validation tests)
- Tests will skip if Ollama is not available

### Production Conditions
- ✅ **Real Ollama CLI**: All tests use actual `ollama` command
- ✅ **Real Model Validation**: Tests validate actual model availability
- ✅ **Real Script Execution**: Tests execute actual Python scripts
- ✅ **No Mocks**: No mocked subprocess calls or Ollama responses
- ✅ **No Placeholders**: All tests use real environment values

## Test Results

**Latest Run**: 14 tests passed in 12.13 seconds

```
TestModelDownloadScript::test_script_exists                    PASSED
TestModelDownloadScript::test_script_help_usage                PASSED
TestModelDownloadScript::test_script_without_args              PASSED
TestModelValidationScript::test_script_exists                 PASSED
TestModelValidationScript::test_list_models_functionality     PASSED
TestModelValidationScript::test_validate_existing_model        PASSED
TestModelValidationScript::test_validate_nonexistent_model    PASSED
TestModelValidationScript::test_validate_multiple_models      PASSED
TestDockerSetupScript::test_script_exists                      PASSED
TestDockerSetupScript::test_script_is_executable               PASSED
TestDockerSetupScript::test_script_syntax                      PASSED
TestScriptIntegration::test_scripts_work_together              PASSED
TestErrorHandling::test_download_script_handles_missing_ollama PASSED
TestErrorHandling::test_validation_script_handles_invalid_input PASSED
```

## Related Documentation

- **[Ollama Model Management Guide](../../docs/ollama-model-management-guide.md)** - Script usage and examples
- **[LangChain-Ollama Integration Guide](../../docs/langchain-ollama-integration-guide.md)** - Ollama integration with LangChain
- **[TASK-036](../../dev/tasks/TASK-036.md)** - Model Download and Validation task

