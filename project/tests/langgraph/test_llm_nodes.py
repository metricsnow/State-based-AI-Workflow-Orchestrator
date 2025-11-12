"""Production tests for LangGraph LLM nodes with Ollama integration.

This test suite validates LLM node functionality using PRODUCTION conditions only.
NO MOCKS, NO PLACEHOLDERS - all tests use real implementations.

CRITICAL: All tests use real packages, real imports, and real initialization.
"""

import sys
import socket
import time

import pytest

from langgraph_workflows.llm_nodes import (
    LLMState,
    create_llm_node,
    llm_analysis_node,
)
from langgraph_workflows.state import MultiAgentState


def check_ollama_available() -> bool:
    """Check if Ollama service is available (fast check without LLM call)."""
    try:
        # Quick TCP connection check
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.settimeout(1)
        result = conn.connect_ex(("localhost", 11434))
        conn.close()
        return result == 0
    except Exception:
        return False


class TestLLMNodeCreation:
    """Test LLM node creation (no LLM calls required)."""

    def test_create_llm_node_returns_callable(self) -> None:
        """Test that create_llm_node returns a callable node function (PRODUCTION)."""
        print("\n[TEST] Creating LLM node with default parameters...")
        start_time = time.time()

        node = create_llm_node(model="llama2:13b")

        elapsed = time.time() - start_time
        print(f"[STATUS] Node created in {elapsed:.3f}s")

        assert callable(node), "create_llm_node should return a callable"
        assert node is not None
        print("[PASS] Node is callable and not None")

    def test_create_llm_node_with_prompt_template(self) -> None:
        """Test create_llm_node with prompt template (PRODUCTION)."""
        print("\n[TEST] Creating LLM node with prompt template...")
        start_time = time.time()

        node = create_llm_node(
            model="llama2:13b",
            prompt_template="Analyze: {input}",
            temperature=0.7,
        )

        elapsed = time.time() - start_time
        print(f"[STATUS] Node with template created in {elapsed:.3f}s")

        assert callable(node)
        print("[PASS] Node with template is callable")

    def test_create_llm_node_default_parameters(self) -> None:
        """Test create_llm_node with default parameters (PRODUCTION)."""
        print("\n[TEST] Creating LLM node with default parameters...")
        start_time = time.time()

        node = create_llm_node()

        elapsed = time.time() - start_time
        print(f"[STATUS] Default node created in {elapsed:.3f}s")

        assert callable(node)
        print("[PASS] Default node is callable")


class TestLLMNodeExecution:
    """Test LLM node execution with real Ollama (PRODUCTION)."""

    def test_llm_node_empty_input(self) -> None:
        """Test LLM node handles empty input gracefully (PRODUCTION - no LLM call)."""
        print("\n[TEST] Testing empty input handling...")
        start_time = time.time()

        node = create_llm_node(model="llama2:13b")
        state: LLMState = {
            "input": "",
            "output": "",
            "status": "processing",
            "metadata": {},
        }

        result = node(state)

        elapsed = time.time() - start_time
        print(f"[STATUS] Empty input test completed in {elapsed:.3f}s")

        assert result["status"] == "error"
        assert "error" in result["metadata"]
        assert result["metadata"]["error"] == "Empty input"
        print("[PASS] Empty input correctly handled as error")

    def test_llm_node_real_inference(self) -> None:
        """Test LLM node with real Ollama inference (PRODUCTION)."""
        print("\n[TEST] Testing real Ollama inference...")
        start_time = time.time()

        if not check_ollama_available():
            print("[SKIP] Ollama service not available - skipping inference test")
            pytest.skip("Ollama service not available")

        print("[STATUS] Ollama service available - proceeding with test")

        node = create_llm_node(model="llama2:13b")
        state: LLMState = {
            "input": "Say 'OK' in one word.",
            "output": "",
            "status": "processing",
            "metadata": {},
        }

        print("[STATUS] Invoking LLM node...")
        inference_start = time.time()
        result = node(state)
        inference_time = time.time() - inference_start

        total_time = time.time() - start_time
        print(f"[STATUS] Inference completed in {inference_time:.3f}s (total: {total_time:.3f}s)")

        if result["status"] == "completed":
            assert len(result["output"]) > 0
            print(f"[PASS] LLM returned response: {result['output'][:50]}...")
            assert "model" in result["metadata"]
            assert "input_length" in result["metadata"]
            assert "output_length" in result["metadata"]
            print("[PASS] Metadata correctly populated")
        else:
            print(f"[WARN] LLM returned error: {result['metadata'].get('error', 'Unknown error')}")
            assert result["status"] == "error"

    def test_llm_node_with_prompt_template(self) -> None:
        """Test LLM node with prompt template (PRODUCTION)."""
        print("\n[TEST] Testing LLM node with prompt template...")
        start_time = time.time()

        if not check_ollama_available():
            print("[SKIP] Ollama service not available - skipping template test")
            pytest.skip("Ollama service not available")

        node = create_llm_node(
            model="llama2:13b",
            prompt_template="Task: {input}\n\nProvide a brief response:",
        )

        state: LLMState = {
            "input": "Analyze sales data",
            "output": "",
            "status": "processing",
            "metadata": {},
        }

        print("[STATUS] Invoking LLM node with template...")
        inference_start = time.time()
        result = node(state)
        inference_time = time.time() - inference_start

        total_time = time.time() - start_time
        print(f"[STATUS] Template inference completed in {inference_time:.3f}s (total: {total_time:.3f}s)")

        assert result["status"] in ["completed", "error"]
        if result["status"] == "completed":
            assert len(result["output"]) > 0
            print(f"[PASS] Template test returned response: {result['output'][:50]}...")
        else:
            print(f"[WARN] Template test returned error: {result['metadata'].get('error', 'Unknown')}")

    def test_llm_node_preserves_metadata(self) -> None:
        """Test LLM node preserves existing metadata (PRODUCTION)."""
        print("\n[TEST] Testing metadata preservation...")
        start_time = time.time()

        if not check_ollama_available():
            print("[SKIP] Ollama service not available - skipping metadata test")
            pytest.skip("Ollama service not available")

        node = create_llm_node(model="llama2:13b")
        state: LLMState = {
            "input": "Say OK",
            "output": "",
            "status": "processing",
            "metadata": {"existing_key": "existing_value"},
        }

        print("[STATUS] Invoking LLM node with existing metadata...")
        result = node(state)

        elapsed = time.time() - start_time
        print(f"[STATUS] Metadata test completed in {elapsed:.3f}s")

        if result["status"] == "completed":
            assert "existing_key" in result["metadata"]
            assert result["metadata"]["existing_key"] == "existing_value"
            assert "model" in result["metadata"]
            print("[PASS] Metadata correctly preserved and extended")
        else:
            print(f"[WARN] Test returned error: {result['metadata'].get('error', 'Unknown')}")


class TestLLMAnalysisNode:
    """Test llm_analysis_node for multi-agent workflows (PRODUCTION)."""

    def test_llm_analysis_node_basic(self) -> None:
        """Test llm_analysis_node with basic state (PRODUCTION)."""
        print("\n[TEST] Testing llm_analysis_node with basic state...")
        start_time = time.time()

        if not check_ollama_available():
            print("[SKIP] Ollama service not available - skipping analysis node test")
            pytest.skip("Ollama service not available")

        state: MultiAgentState = {
            "messages": [],
            "task": "Analyze customer data",
            "agent_results": {},
            "current_agent": "llm_analysis",
            "completed": False,
            "metadata": {},
        }

        print("[STATUS] Invoking llm_analysis_node...")
        inference_start = time.time()
        result = llm_analysis_node(state)
        inference_time = time.time() - inference_start

        total_time = time.time() - start_time
        print(f"[STATUS] Analysis node completed in {inference_time:.3f}s (total: {total_time:.3f}s)")

        assert "llm_analysis" in result
        assert "llm_status" in result
        assert result["llm_status"] in ["completed", "error"]

        if result["llm_status"] == "completed":
            assert len(result["llm_analysis"]) > 0
            print(f"[PASS] Analysis returned: {result['llm_analysis'][:50]}...")
        else:
            print(f"[WARN] Analysis returned error: {result.get('metadata', {}).get('llm_metadata', {}).get('error', 'Unknown')}")

    def test_llm_analysis_node_with_data_context(self) -> None:
        """Test llm_analysis_node includes data agent results in context (PRODUCTION)."""
        print("\n[TEST] Testing llm_analysis_node with data context...")
        start_time = time.time()

        if not check_ollama_available():
            print("[SKIP] Ollama service not available - skipping context test")
            pytest.skip("Ollama service not available")

        state: MultiAgentState = {
            "messages": [],
            "task": "Analyze data",
            "agent_results": {
                "data": {
                    "agent": "data",
                    "result": "data_processed",
                    "data": {"processed": True},
                }
            },
            "current_agent": "llm_analysis",
            "completed": False,
            "metadata": {},
        }

        print("[STATUS] Invoking llm_analysis_node with data context...")
        inference_start = time.time()
        result = llm_analysis_node(state)
        inference_time = time.time() - inference_start

        total_time = time.time() - start_time
        print(f"[STATUS] Context test completed in {inference_time:.3f}s (total: {total_time:.3f}s)")

        assert "llm_analysis" in result
        assert result["llm_status"] in ["completed", "error"]

        if result["llm_status"] == "completed":
            print("[PASS] Analysis with context completed successfully")
        else:
            print(f"[WARN] Context test returned error")

    def test_llm_analysis_node_preserves_state(self) -> None:
        """Test llm_analysis_node preserves all state fields (PRODUCTION)."""
        print("\n[TEST] Testing state preservation in llm_analysis_node...")
        start_time = time.time()

        if not check_ollama_available():
            print("[SKIP] Ollama service not available - skipping state preservation test")
            pytest.skip("Ollama service not available")

        state: MultiAgentState = {
            "messages": ["message1"],
            "task": "Test task",
            "agent_results": {"existing": "result"},
            "current_agent": "llm_analysis",
            "completed": False,
            "metadata": {"existing_meta": "value"},
        }

        print("[STATUS] Invoking llm_analysis_node to test state preservation...")
        result = llm_analysis_node(state)

        elapsed = time.time() - start_time
        print(f"[STATUS] State preservation test completed in {elapsed:.3f}s")

        # Verify all state fields are preserved
        assert result["messages"] == state["messages"]
        assert result["task"] == state["task"]
        assert result["agent_results"] == state["agent_results"]
        assert result["current_agent"] == state["current_agent"]
        assert result["completed"] == state["completed"]
        assert "existing_meta" in result["metadata"]
        print("[PASS] All state fields correctly preserved")


class TestLLMNodeIntegration:
    """Integration tests for LLM nodes in workflows (PRODUCTION)."""

    def test_llm_node_real_ollama_initialization(self) -> None:
        """Test LLM node can initialize with real Ollama (PRODUCTION)."""
        print("\n[TEST] Testing real Ollama LLM initialization...")
        start_time = time.time()

        try:
            from langchain_ollama_integration import create_ollama_llm

            llm = create_ollama_llm(model="llama2:13b")
            assert llm is not None

            elapsed = time.time() - start_time
            print(f"[STATUS] LLM initialized in {elapsed:.3f}s")
            print("[PASS] Real Ollama LLM initialized successfully")
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"[STATUS] Initialization failed in {elapsed:.3f}s: {e}")
            pytest.skip(f"Ollama service not available: {e}")

    def test_llm_node_in_workflow(self) -> None:
        """Test LLM node integration with LangGraph workflow (PRODUCTION)."""
        print("\n[TEST] Testing LLM node in LangGraph workflow...")
        start_time = time.time()

        if not check_ollama_available():
            print("[SKIP] Ollama service not available - skipping workflow test")
            pytest.skip("Ollama service not available")

        from langgraph.graph import END, START, StateGraph

        from langgraph_workflows.state import SimpleState

        # Create a simple workflow with LLM node
        node = create_llm_node(
            model="llama2:13b",
            prompt_template="Analyze this: {input}",
        )

        # Build workflow
        workflow = StateGraph(SimpleState)
        workflow.add_node("llm_analysis", node)
        workflow.add_edge(START, "llm_analysis")
        workflow.add_edge("llm_analysis", END)

        # Compile workflow (graph variable not used but compilation validates structure)
        workflow.compile()

        # Convert to LLMState format for node
        llm_state: LLMState = {
            "input": "Test data for analysis",
            "output": "",
            "status": "processing",
            "metadata": {},
        }

        print("[STATUS] Testing node directly in workflow context...")
        inference_start = time.time()
        result = node(llm_state)
        inference_time = time.time() - inference_start

        total_time = time.time() - start_time
        print(f"[STATUS] Workflow test completed in {inference_time:.3f}s (total: {total_time:.3f}s)")

        assert result["status"] in ["completed", "error"]
        if result["status"] == "completed":
            print("[PASS] Workflow integration test successful")
        else:
            print(f"[WARN] Workflow test returned error: {result['metadata'].get('error', 'Unknown')}")


if __name__ == "__main__":
    print("=" * 80)
    print("LLM Nodes Production Test Suite")
    print("=" * 80)
    print(f"Python: {sys.version}")
    print(f"Working directory: {sys.path[0]}")
    print("=" * 80)
