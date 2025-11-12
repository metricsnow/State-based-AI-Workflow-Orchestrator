"""Multi-agent workflow for LangGraph StateGraph with orchestrator-worker pattern.

This module implements a multi-agent workflow using LangGraph StateGraph with
conditional routing between specialized agents (data_agent, analysis_agent) and
an orchestrator agent. The workflow supports checkpointing for state persistence
and enables resumable multi-agent collaboration.

Example:
    ```python
    from langgraph_workflows.multi_agent_workflow import (
        execute_multi_agent_workflow,
        multi_agent_graph
    )
    from langgraph_workflows.state import MultiAgentState

    # Execute workflow with auto-generated thread_id
    result, thread_id = execute_multi_agent_workflow("process_and_analyze_data")

    # Execute with custom thread_id
    custom_thread_id = "my-workflow-123"
    result, thread_id = execute_multi_agent_workflow(
        "process_and_analyze_data",
        custom_thread_id
    )
    assert thread_id == custom_thread_id

    # Direct graph invocation
    import uuid
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    initial_state: MultiAgentState = {
        "messages": [],
        "task": "test_task",
        "agent_results": {},
        "current_agent": "orchestrator",
        "completed": False,
        "metadata": {}
    }
    result = multi_agent_graph.invoke(initial_state, config=config)
    ```
"""

import uuid
from typing import Any

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from langgraph_workflows.agent_nodes import analysis_agent, data_agent
from langgraph_workflows.llm_nodes import llm_analysis_node
from langgraph_workflows.orchestrator_agent import orchestrator_agent, route_to_agent
from langgraph_workflows.state import MultiAgentState

# Create checkpointer for state persistence
checkpointer = InMemorySaver()

# Build multi-agent graph with orchestrator-worker pattern
workflow = StateGraph(MultiAgentState)

# Add nodes: orchestrator, worker agents, and LLM analysis node
workflow.add_node("orchestrator", orchestrator_agent)
workflow.add_node("data_agent", data_agent)
workflow.add_node("analysis_agent", analysis_agent)
workflow.add_node("llm_analysis", llm_analysis_node)

# Add fixed edge: START -> orchestrator
workflow.add_edge(START, "orchestrator")

# Add conditional edge from orchestrator
# The route_to_agent function reads current_agent from state and routes accordingly
workflow.add_conditional_edges(
    "orchestrator",
    route_to_agent,
    {
        "data": "data_agent",
        "analysis": "analysis_agent",
        "llm_analysis": "llm_analysis",
        "end": END,
    },
)

# Add fixed edges: worker agents and LLM node -> orchestrator
# After completing their tasks, agents route back to orchestrator for coordination
workflow.add_edge("data_agent", "orchestrator")
workflow.add_edge("analysis_agent", "orchestrator")
workflow.add_edge("llm_analysis", "orchestrator")

# Compile graph with checkpointer for state persistence
multi_agent_graph = workflow.compile(checkpointer=checkpointer)


def execute_multi_agent_workflow(
    task: str, thread_id: str | None = None
) -> tuple[dict[str, Any], str]:
    """Execute multi-agent workflow with checkpointing.

    This function provides a convenient interface for executing the multi-agent
    workflow. It creates the initial state, generates a thread_id if not provided,
    and invokes the compiled graph with checkpointing enabled.

    The workflow follows this execution pattern:
    1. Start at orchestrator node
    2. Orchestrator evaluates state and routes to appropriate agent
    3. Agent processes task and updates state
    4. Agent routes back to orchestrator
    5. Orchestrator evaluates again and routes to next agent or END
    6. Process continues until all agents complete or workflow terminates

    Args:
        task: The task string to be processed by the multi-agent workflow.
        thread_id: Optional thread ID for checkpoint tracking. If None, a new
            UUID is generated automatically.

    Returns:
        A tuple containing:
        - final_state: The final state dictionary after workflow execution
        - thread_id: The thread ID used for checkpointing (generated or provided)

    Example:
        ```python
        # Execute with auto-generated thread_id
        result, thread_id = execute_multi_agent_workflow("process_data")

        # Execute with custom thread_id
        custom_id = "my-workflow-123"
        result, thread_id = execute_multi_agent_workflow("process_data", custom_id)
        assert thread_id == custom_id

        # Check workflow completion
        assert result["completed"] is True
        assert "data" in result["agent_results"]
        assert "analysis" in result["agent_results"]
        ```
    """
    if thread_id is None:
        thread_id = str(uuid.uuid4())

    config = {"configurable": {"thread_id": thread_id}}

    initial_state: MultiAgentState = {
        "messages": [],
        "task": task,
        "agent_results": {},
        "current_agent": "orchestrator",
        "completed": False,
        "metadata": {},
    }

    result = multi_agent_graph.invoke(initial_state, config=config)
    return result, thread_id

