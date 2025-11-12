"""LangGraph workflows module for stateful agent workflows and multi-agent systems.

This module provides state definitions, reducers, and workflow implementations
for building stateful AI agent workflows using LangGraph.
"""

from langgraph_workflows.basic_workflow import (
    execute_workflow,
    graph,
    node_a,
    node_b,
)
from langgraph_workflows.checkpoint_workflow import (
    checkpoint_graph,
    execute_with_checkpoint,
    get_checkpoint_state,
    list_checkpoints,
    resume_workflow,
)
from langgraph_workflows.conditional_workflow import (
    error_handler,
    execute_conditional_workflow,
    graph as conditional_graph,
    node_a_conditional,
    should_continue,
)
from langgraph_workflows.agent_nodes import (
    analysis_agent,
    analysis_agent_with_error_handling,
    data_agent,
    data_agent_with_error_handling,
)
from langgraph_workflows.llm_nodes import (
    LLMState,
    create_llm_node,
    llm_analysis_node,
)
from langgraph_workflows.multi_agent_workflow import (
    execute_multi_agent_workflow,
    multi_agent_graph,
)
from langgraph_workflows.orchestrator_agent import (
    orchestrator_agent,
    orchestrator_agent_with_errors,
    route_to_agent,
)
from langgraph_workflows.state import (
    MultiAgentState,
    SimpleState,
    WorkflowState,
    last_value,
    merge_agent_results,
    merge_dicts,
    validate_multi_agent_state,
    validate_simple_state,
    validate_state,
)

__version__ = "0.1.0"

__all__ = [
    # State definitions
    "WorkflowState",
    "SimpleState",
    "MultiAgentState",
    # Reducers
    "merge_dicts",
    "merge_agent_results",
    "last_value",
    # Validation
    "validate_state",
    "validate_simple_state",
    "validate_multi_agent_state",
    # Agent nodes
    "data_agent",
    "analysis_agent",
    "data_agent_with_error_handling",
    "analysis_agent_with_error_handling",
    # LLM nodes
    "LLMState",
    "create_llm_node",
    "llm_analysis_node",
    # Orchestrator agent
    "orchestrator_agent",
    "orchestrator_agent_with_errors",
    "route_to_agent",
    # Multi-agent workflow
    "multi_agent_graph",
    "execute_multi_agent_workflow",
    # Basic workflow
    "node_a",
    "node_b",
    "graph",
    "execute_workflow",
    # Conditional workflow
    "node_a_conditional",
    "error_handler",
    "should_continue",
    "conditional_graph",
    "execute_conditional_workflow",
    # Checkpoint workflow
    "checkpoint_graph",
    "execute_with_checkpoint",
    "resume_workflow",
    "get_checkpoint_state",
    "list_checkpoints",
]

