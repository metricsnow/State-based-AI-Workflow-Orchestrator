"""LLM nodes for LangGraph workflows with Ollama integration.

This module implements LangGraph nodes that use Ollama LLM for inference.
It provides factory functions for creating LLM nodes with configurable models,
prompt templating, and error handling. Nodes integrate seamlessly with existing
LangGraph workflows and MultiAgentState.

Example:
    ```python
    from langgraph_workflows.llm_nodes import create_llm_node, llm_analysis_node
    from langgraph_workflows.state import MultiAgentState

    # Create a custom LLM node
    custom_node = create_llm_node(
        model="llama2:13b",
        prompt_template="Analyze this: {input}",
        temperature=0.7
    )

    # Use pre-configured analysis node
    state: MultiAgentState = {
        "messages": [],
        "task": "Analyze customer data trends",
        "agent_results": {},
        "current_agent": "llm_analysis",
        "completed": False,
        "metadata": {}
    }
    result = llm_analysis_node(state)
    ```
"""

import logging
from typing import Any, Callable, Dict, Optional

from langchain_core.prompts import PromptTemplate
from typing_extensions import TypedDict

from langchain_ollama_integration import create_ollama_llm
from langgraph_workflows.state import MultiAgentState

logger = logging.getLogger(__name__)


class LLMState(TypedDict):
    """State schema for standalone LLM nodes.

    This state schema is used for LLM nodes that operate independently
    without full MultiAgentState context. It provides a simple interface
    for LLM processing with input/output tracking.

    Attributes:
        input: Input text for LLM processing
        output: Output text from LLM processing
        status: Processing status ("processing", "completed", "error")
        metadata: Additional metadata dictionary
    """

    input: str
    output: str
    status: str
    metadata: Dict[str, Any]


def create_llm_node(
    model: str = "llama2:13b",
    prompt_template: Optional[str] = None,
    temperature: float = 0.7,
    **kwargs
) -> Callable[[LLMState], LLMState]:
    """Create a LangGraph node that uses Ollama LLM.

    This factory function creates a reusable LLM node function that can be
    added to LangGraph workflows. The node processes input text through the
    Ollama LLM and returns structured output with status and metadata.

    Args:
        model: Ollama model name (default: "llama2:13b")
        prompt_template: Optional prompt template string. If provided, uses
            {input} placeholder for input text. If None, passes input directly
            to LLM.
        temperature: Temperature for generation (default: 0.7)
        **kwargs: Additional arguments passed to create_ollama_llm

    Returns:
        A node function that accepts LLMState and returns LLMState

    Example:
        ```python
        # Create node with prompt template
        analysis_node = create_llm_node(
            model="llama2:13b",
            prompt_template="Analyze this data: {input}",
            temperature=0.7
        )

        # Use in workflow
        state: LLMState = {
            "input": "Customer data shows 20% increase",
            "output": "",
            "status": "processing",
            "metadata": {}
        }
        result = analysis_node(state)
        assert result["status"] == "completed"
        assert len(result["output"]) > 0
        ```
    """
    # Create LLM instance
    llm = create_ollama_llm(model=model, temperature=temperature, **kwargs)

    # Create prompt chain if template provided
    if prompt_template:
        prompt = PromptTemplate.from_template(prompt_template)
        chain = prompt | llm
    else:
        chain = llm

    def llm_node(state: LLMState) -> LLMState:
        """LangGraph node that processes input with Ollama LLM.

        This node function is returned by create_llm_node and can be used
        directly in LangGraph workflows. It handles input validation,
        LLM invocation, error handling, and structured output.

        Args:
            state: LLMState containing input text and metadata

        Returns:
            LLMState with output, status, and metadata updated
        """
        try:
            input_text = state.get("input", "")

            if not input_text:
                logger.warning("Empty input in LLM node")
                return {
                    "input": input_text,
                    "output": "",
                    "status": "error",
                    "metadata": {
                        **state.get("metadata", {}),
                        "error": "Empty input",
                        "model": model,
                    },
                }

            logger.info(f"Processing LLM request: {input_text[:50]}...")

            # Invoke LLM with prompt template or direct input
            if prompt_template:
                result = chain.invoke({"input": input_text})
            else:
                result = chain.invoke(input_text)

            # Convert result to string if needed
            output_text = result if isinstance(result, str) else str(result)

            logger.info(
                f"LLM response received: {output_text[:50] if output_text else '...'}..."
            )

            return {
                "input": input_text,
                "output": output_text,
                "status": "completed",
                "metadata": {
                    **state.get("metadata", {}),
                    "model": model,
                    "input_length": len(input_text),
                    "output_length": len(output_text),
                },
            }

        except Exception as e:
            logger.error(f"Error in LLM node: {e}", exc_info=True)
            return {
                "input": state.get("input", ""),
                "output": "",
                "status": "error",
                "metadata": {
                    **state.get("metadata", {}),
                    "error": str(e),
                    "model": model,
                },
            }

    return llm_node


def llm_analysis_node(state: MultiAgentState) -> Dict[str, Any]:
    """Pre-configured LLM node for analysis tasks in multi-agent workflows.

    This node integrates with MultiAgentState and provides AI-powered analysis
    capabilities. It extracts the task from state, processes it through the
    Ollama LLM with a specialized analysis prompt, and updates the state with
    analysis results.

    Args:
        state: MultiAgentState containing task and agent results

    Returns:
        Dictionary with state updates:
        - llm_analysis: Analysis result from LLM
        - llm_status: Status of LLM processing
        - metadata: Updated metadata with LLM processing info

    Example:
        ```python
        state: MultiAgentState = {
            "messages": [],
            "task": "Analyze customer data trends for Q4",
            "agent_results": {
                "data": {"agent": "data", "result": "data_processed"}
            },
            "current_agent": "llm_analysis",
            "completed": False,
            "metadata": {}
        }
        result = llm_analysis_node(state)
        assert "llm_analysis" in result
        assert result["llm_status"] in ["completed", "error"]
        ```
    """
    prompt_template = """You are an AI assistant specializing in data analysis.

Task: {input}

Provide a detailed analysis with clear conclusions and actionable insights."""

    # Create LLM node with analysis prompt
    node = create_llm_node(
        model="llama2:13b",
        prompt_template=prompt_template,
        temperature=0.7,
    )

    # Extract task from state
    task = state.get("task", "")
    agent_results = state.get("agent_results", {})

    # Prepare input text with context from previous agents
    input_text = f"Task: {task}\n\n"

    # Include data agent results if available
    if "data" in agent_results:
        data_result = agent_results["data"]
        input_text += f"Data Context: {data_result}\n\n"

    # Include analysis agent results if available
    if "analysis" in agent_results:
        analysis_result = agent_results["analysis"]
        input_text += f"Previous Analysis: {analysis_result}\n\n"

    input_text += "Provide a comprehensive AI-powered analysis."

    # Create LLM state
    llm_state: LLMState = {
        "input": input_text,
        "output": "",
        "status": "processing",
        "metadata": {},
    }

    # Process with LLM
    llm_result = node(llm_state)

    # Update state with LLM result
    updated_metadata = {
        **state.get("metadata", {}),
        "llm_metadata": llm_result["metadata"],
    }

    return {
        **state,
        "llm_analysis": llm_result["output"],
        "llm_status": llm_result["status"],
        "metadata": updated_metadata,
    }

