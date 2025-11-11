"""Example DAG demonstrating LangGraph workflow integration with Airflow.

This DAG shows how to use the trigger_langgraph_workflow function to trigger
LangGraph workflows from Airflow tasks and retrieve results. Demonstrates
the complete integration pattern: Airflow → Kafka → LangGraph → Result.

DAG Structure:
- prepare_data: Prepares data for LangGraph workflow
- trigger_workflow: Triggers LangGraph workflow and waits for result
- process_result: Processes the workflow result

Data Flow:
- prepare_data returns task data
- trigger_workflow receives data, publishes event, polls for result
- process_result receives workflow result and processes it

Integration Pattern:
1. Airflow task calls trigger_langgraph_workflow()
2. Function publishes WORKFLOW_TRIGGERED event to Kafka
3. LangGraph consumer receives event and executes workflow
4. LangGraph processor publishes result to workflow-results topic
5. Airflow task polls for result and returns it
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Any

from airflow.decorators import dag, task
from airflow_integration.langgraph_trigger import trigger_langgraph_workflow


@dag(
    dag_id="langgraph_integration_example",
    description="Example DAG demonstrating LangGraph workflow integration",
    schedule=timedelta(days=1),
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["langgraph", "integration", "example"],
    default_args={
        "owner": "airflow",
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
)
def langgraph_integration_dag():
    """Example DAG demonstrating LangGraph workflow integration.
    
    This DAG shows the complete integration pattern for triggering
    LangGraph workflows from Airflow and retrieving results.
    """
    
    @task
    def prepare_data() -> Dict[str, Any]:
        """Prepare data for LangGraph workflow.
        
        This task prepares the data structure that will be passed to
        the LangGraph workflow. The data structure should match what
        the workflow expects.
        
        Returns:
            Dictionary containing task description and data for workflow
        """
        print("Preparing data for LangGraph workflow...")
        
        task_data = {
            "task": "analyze_trading_data",
            "data": {
                "symbol": "AAPL",
                "date_range": "2025-01-01:2025-01-31",
                "analysis_type": "trend_analysis",
            },
        }
        
        print(f"Prepared task data: {task_data}")
        return task_data
    
    @task
    def process_result(result: Dict[str, Any]) -> Dict[str, Any]:
        """Process workflow result.
        
        This task receives the result from the LangGraph workflow
        and processes it. In a real scenario, this might involve
        storing results, sending notifications, or triggering
        downstream processes.
        
        Args:
            result: Workflow result dictionary from LangGraph workflow
        
        Returns:
            Processed result dictionary
        """
        print("Processing workflow result...")
        print(f"Workflow completed: {result.get('completed', False)}")
        print(f"Agent results: {result.get('agent_results', {})}")
        print(f"Task: {result.get('task', 'N/A')}")
        print(f"Metadata: {result.get('metadata', {})}")
        
        # In a real scenario, you might:
        # - Store results to database
        # - Send notifications
        # - Trigger downstream processes
        # - Generate reports
        
        processed_result = {
            "status": "processed",
            "workflow_completed": result.get("completed", False),
            "agent_count": len(result.get("agent_results", {})),
            "original_result": result,
        }
        
        print(f"Processed result: {processed_result}")
        return processed_result
    
    # Prepare data
    data = prepare_data()
    
    # Trigger LangGraph workflow and wait for result
    # The trigger_langgraph_workflow function:
    # 1. Publishes WORKFLOW_TRIGGERED event to Kafka
    # 2. Polls for result from workflow-results topic
    # 3. Returns result data or raises exception on timeout/failure
    workflow_result = trigger_langgraph_workflow(
        task_data=data,
        timeout=600,  # 10 minutes timeout
    )
    
    # Process result
    processed = process_result(workflow_result)
    
    # TaskFlow API automatically manages dependencies:
    # prepare_data → trigger_workflow → process_result


# Invoke the DAG function to register it with Airflow
langgraph_integration_dag()

