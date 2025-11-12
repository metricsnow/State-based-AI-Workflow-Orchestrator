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

from langchain_ollama_integration import create_llm, create_ollama_llm
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
    model: Optional[str] = None,
    prompt_template: Optional[str] = None,
    temperature: float = 0.7,
    provider: Optional[str] = None,
    **kwargs
) -> Callable[[LLMState], LLMState]:
    """Create a LangGraph node that uses unified LLM factory.

    This factory function creates a reusable LLM node function that can be
    added to LangGraph workflows. The node processes input text through the
    LLM (Ollama or OpenAI based on configuration) and returns structured
    output with status and metadata.

    Args:
        model: Model name (provider-specific).
               For Ollama: defaults to OLLAMA_MODEL env var or "llama3.2:latest"
               For OpenAI: defaults to OPENAI_MODEL env var or "gpt-4o-mini" (cheapest)
               If None, uses provider defaults from environment.
        prompt_template: Optional prompt template string. If provided, uses
            {input} placeholder for input text. If None, passes input directly
            to LLM.
        temperature: Temperature for generation (default: 0.7)
        provider: Explicit provider override ('ollama', 'openai', 'auto').
                  If None, uses LLM_PROVIDER env var (default: 'openai').
        **kwargs: Additional arguments passed to create_llm

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
    # Create LLM instance using unified factory
    # Factory automatically selects provider from environment or explicit override
    llm = create_llm(provider=provider, model=model, temperature=temperature, **kwargs)
    
    # Get model name for metadata (from LLM instance or parameters)
    model_name = model
    if model_name is None:
        # Try to get from LLM instance attributes
        if hasattr(llm, 'model_name'):
            model_name = llm.model_name
        elif hasattr(llm, 'model'):
            model_name = llm.model
        else:
            # Fallback: get from environment
            from langchain_ollama_integration import get_llm_provider, get_openai_model, get_ollama_model
            provider_name = provider or get_llm_provider()
            if provider_name == "openai":
                model_name = get_openai_model()
            else:
                model_name = get_ollama_model()

    # Create prompt chain if template provided
    if prompt_template:
        prompt = PromptTemplate.from_template(prompt_template)
        chain = prompt | llm
    else:
        chain = llm

    def llm_node(state: LLMState) -> LLMState:
        """LangGraph node that processes input with unified LLM.

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
                        "model": model_name,
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
                    "model": model_name,
                    "input_length": len(input_text),
                    "output_length": len(output_text),
                },
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error in LLM node: {error_msg}", exc_info=True)
            
            # Provide helpful error message for model not found
            if "not found" in error_msg.lower() or "404" in error_msg:
                suggestion = (
                    f"Model '{model_name}' not found. "
                    f"Available models: Use 'ollama list' to see installed models. "
                    f"To download: 'ollama pull {model_name}' or use a different model."
                )
                logger.warning(suggestion)
            
            return {
                "input": state.get("input", ""),
                "output": "",
                "status": "error",
                "metadata": {
                    **state.get("metadata", {}),
                    "error": error_msg,
                    "model": model_name,
                    "error_type": type(e).__name__,
                },
            }

    return llm_node


def llm_analysis_node(state: MultiAgentState) -> Dict[str, Any]:
    """Pre-configured LLM node for analysis tasks in multi-agent workflows.

    This node integrates with MultiAgentState and provides AI-powered analysis
    capabilities. It extracts the task from state, processes it through the
    Ollama LLM with a specialized analysis prompt, and updates the state with
    analysis results in agent_results for consistency with other agents.

    Args:
        state: MultiAgentState containing task and agent results

    Returns:
        Dictionary with state updates:
        - agent_results: Updated with llm_analysis entry containing result, status, metadata
        - metadata: Updated with LLM processing metadata
        - current_agent: Set to "orchestrator" to route back to orchestrator

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
        assert "llm_analysis" in result["agent_results"]
        assert result["agent_results"]["llm_analysis"]["status"] in ["completed", "error"]
        ```
    """
    prompt_template = """You are an AI assistant specializing in data analysis and decision-making.

{input}

Provide a detailed analysis with clear conclusions and recommendations."""

    # Create LLM node with analysis prompt
    # Uses unified factory - automatically selects provider from environment
    node = create_llm_node(
        prompt_template=prompt_template,
        temperature=0.7,
    )

    # Extract task and agent results from state
    task = state.get("task", "")
    agent_results = state.get("agent_results", {})

    # Prepare input text with context from previous agents
    input_text = f"Task: {task}\n\n"

    # Include data agent results if available
    if "data" in agent_results:
        data_result = agent_results["data"]
        # Extract result string from data agent result
        if isinstance(data_result, dict):
            data_str = data_result.get("result", str(data_result))
        else:
            data_str = str(data_result)
        input_text += f"Data: {data_str}\n\n"

    # Include analysis agent results if available
    if "analysis" in agent_results:
        analysis_result = agent_results["analysis"]
        # Extract result string from analysis agent result
        if isinstance(analysis_result, dict):
            analysis_str = analysis_result.get("result", str(analysis_result))
        else:
            analysis_str = str(analysis_result)
        input_text += f"Previous Analysis: {analysis_str}\n\n"

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

    # Update agent_results with LLM analysis result (consistent with other agents)
    updated_results = {
        **agent_results,
        "llm_analysis": {
            "agent": "llm_analysis",
            "result": llm_result["output"],
            "status": llm_result["status"],
            "metadata": llm_result["metadata"],
        },
    }

    # Update metadata with LLM processing info
    updated_metadata = {
        **state.get("metadata", {}),
        "llm_metadata": llm_result["metadata"],
    }

    return {
        **state,
        "agent_results": updated_results,
        "metadata": updated_metadata,
        "current_agent": "orchestrator",  # Route back to orchestrator after LLM analysis
    }

