# Product Requirements Document: Phase 8 - Advanced Orchestration

**Project**: AI-Powered Workflow Orchestration for Trading Operations  
**Phase**: Phase 8 - Advanced Orchestration  
**Version**: 1.0  
**Date**: 2025-01-27  
**Author**: Mission Planner Agent  
**Status**: Draft  
**Parent PRD**: `project/docs/prd.md`

---

## Document Control

- **Phase Name**: Advanced Orchestration
- **Phase Number**: 8
- **Version**: 1.0
- **Author**: Mission Planner Agent
- **Last Updated**: 2025-01-27
- **Status**: Draft
- **Dependencies**: Phase 7 (Security & Optimization)
- **Duration Estimate**: 4-5 weeks
- **Team Size**: 1-2 developers

---

## Executive Summary

### Phase Vision
Implement advanced orchestration features including dynamic DAGs, LangGraph Studio, multi-LLM routing, workflow versioning, and advanced analytics. This phase adds sophisticated capabilities for production use.

### Key Objectives
1. **Advanced Airflow**: Dynamic DAGs, custom operators
2. **LangGraph Studio**: Visual workflow development
3. **Multi-LLM Routing**: Intelligent LLM selection
4. **Workflow Versioning**: Version control and rollback
5. **Analytics**: Advanced reporting and insights

### Success Metrics
- **Advanced Features**: All advanced features implemented
- **Developer Experience**: LangGraph Studio functional
- **LLM Optimization**: Multi-LLM routing working
- **Versioning**: Workflow versioning operational
- **Analytics**: Analytics dashboard functional

---

## Detailed Milestones

### Milestone 3.1: Advanced Airflow Features

**Objective**: Implement advanced Airflow capabilities

#### Requirements
- Dynamic DAG generation
- Custom operators for AI workflows
- Advanced scheduling (cron, datasets)
- DAG versioning

#### Technology
- **Apache Airflow** (Trust Score: 9.1)
  - Version: 2.8.4+
  - Advanced features: Dynamic DAGs, custom operators, datasets

#### User Story
As a System Operator, I want advanced Airflow features so that I can handle complex orchestration scenarios.

#### Technical Specifications

**Dynamic DAG Generation**:
```python
from airflow import DAG
from airflow.decorators import task
from datetime import datetime, timezone
import yaml

def generate_dags_from_config():
    """Generate DAGs dynamically from configuration"""
    with open('workflows_config.yaml') as f:
        configs = yaml.safe_load(f)
    
    for config in configs:
        dag_id = config['dag_id']
        globals()[dag_id] = create_dag_from_config(config)

def create_dag_from_config(config: dict):
    @dag(
        dag_id=config['dag_id'],
        start_date=datetime(2025, 1, 1),
        schedule=config.get('schedule'),
        catchup=False
    )
    def dynamic_dag():
        # Create tasks from config
        for task_config in config['tasks']:
            @task(task_id=task_config['id'])
            def task_func():
                return task_config['function']()
    return dynamic_dag()
```

**Custom Operators for AI Workflows**:
```python
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LangGraphOperator(BaseOperator):
    """Custom operator for LangGraph workflows"""
    
    @apply_defaults
    def __init__(
        self,
        workflow_id: str,
        parameters: dict,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.workflow_id = workflow_id
        self.parameters = parameters
    
    def execute(self, context):
        # Execute LangGraph workflow
        from langgraph_service import execute_workflow
        result = execute_workflow(self.workflow_id, self.parameters)
        return result
```

**Advanced Scheduling**:
```python
from airflow.timetables.trigger import CronTriggerTimetable
from airflow.datasets import Dataset

# Cron scheduling
@dag(
    dag_id="scheduled_workflow",
    start_date=datetime(2025, 1, 1),
    timetable=CronTriggerTimetable("0 2 * * *"),  # Daily at 2 AM
    catchup=False
)
def scheduled_dag():
    pass

# Dataset-based scheduling
dataset = Dataset("s3://bucket/data")

@dag(
    dag_id="dataset_triggered",
    schedule=[dataset],  # Triggered by dataset updates
    catchup=False
)
def dataset_dag():
    pass
```

**DAG Versioning**:
```python
from airflow.models import Variable

@dag(
    dag_id="versioned_workflow",
    version=Variable.get("workflow_version", default_var="1.0"),
    catchup=False
)
def versioned_dag():
    # Version-aware DAG
    pass
```

#### Acceptance Criteria
- [ ] Dynamic DAG generation working from configuration
- [ ] Custom operators created for AI workflows (LangGraph, LLM)
- [ ] Advanced scheduling implemented (cron, datasets)
- [ ] DAG versioning functional
- [ ] DAGs can be generated programmatically
- [ ] Custom operators tested and documented
- [ ] Scheduling patterns documented

#### Testing Requirements
- **Unit Tests**: Test dynamic DAG generation, custom operators, scheduling
- **Integration Tests**: Test complete workflows with advanced features

#### Dependencies
- Phase 1 completed (Airflow basics)
- Airflow 2.8.4+ with advanced features
- Configuration management

#### Risks and Mitigation
- **Risk**: Dynamic DAG complexity
  - **Mitigation**: Start with simple patterns, validate configurations, test thoroughly
- **Risk**: Custom operator maintenance
  - **Mitigation**: Document operators well, version operators, test independently

---

### Milestone 3.2: LangGraph Studio Integration

**Objective**: Set up LangGraph Studio for workflow development

#### Requirements
- LangGraph Studio running
- Workflow visualization
- Debugging capabilities
- Workflow testing interface

#### Technology
- **LangGraph Studio** (Trust Score: 9.2)
  - Version: Latest
  - Desktop app for LangGraph development

#### User Story
As a developer, I want visual workflow development so that I can iterate faster.

#### Technical Specifications

**LangGraph Studio Setup**:
```bash
# Install LangGraph Studio
npm install -g @langchain/langgraph-studio

# Or use Docker
docker run -p 8123:8123 langchain/langgraph-studio
```

**Workflow Configuration for Studio**:
```python
# langgraph.json
{
  "graphs": {
    "my_workflow": {
      "path": "workflows/my_workflow.py",
      "entrypoint": "graph"
    }
  },
  "checkpointer": {
    "type": "memory"
  }
}
```

**Workflow Export for Studio**:
```python
from langgraph.graph import StateGraph

# Workflow must be exportable for Studio
workflow = StateGraph(State)
# ... build workflow ...

graph = workflow.compile()

# Export for Studio
# Studio can visualize and debug this workflow
```

#### Acceptance Criteria
- [ ] LangGraph Studio running (local or Docker)
- [ ] Workflow visualization working (graph structure visible)
- [ ] Debugging capabilities functional (step-through, state inspection)
- [ ] Testing interface operational (run workflows, test inputs)
- [ ] Workflows can be imported into Studio
- [ ] State inspection working
- [ ] Breakpoints functional

#### Testing Requirements
- **Manual Testing**: Test Studio features, visualization, debugging
- **Integration Tests**: Test workflow import/export, Studio integration

#### Dependencies
- Phase 2 completed (LangGraph workflows)
- LangGraph Studio installed
- Node.js (if using npm installation)

#### Risks and Mitigation
- **Risk**: Studio setup complexity
  - **Mitigation**: Use Docker version, follow official setup guide
- **Risk**: Workflow compatibility
  - **Mitigation**: Follow Studio-compatible patterns, test import/export

---

### Milestone 3.3: Multi-LLM Routing

**Objective**: Implement intelligent LLM routing

#### Requirements
- Route requests to appropriate LLM (Ollama, vLLM, OpenAI)
- Cost optimization logic
- Performance-based routing
- Fallback mechanisms

#### Technology
- **LangChain, Ollama, vLLM, OpenAI** (Trust Scores: 7.5, 7.5, 6.2, N/A)
  - Multi-LLM integration and routing

#### User Story
As a System Operator, I want intelligent LLM routing so that I can optimize cost and performance.

#### Technical Specifications

**LLM Router Implementation**:
```python
from langchain_community.llms import Ollama, VLLM
from langchain_openai import ChatOpenAI
from typing import Literal
import time

class LLMRouter:
    """Intelligent LLM router"""
    
    def __init__(self):
        self.ollama = Ollama(model="llama2", base_url="http://ollama:11434")
        self.vllm = VLLM(model="mistral", base_url="http://vllm:8000")
        self.openai = ChatOpenAI(model="gpt-4", temperature=0.7)
        
        # Cost per token (example)
        self.costs = {
            "ollama": 0.0,  # Local, free
            "vllm": 0.0001,  # Local GPU
            "openai": 0.03  # API cost
        }
        
        # Performance metrics
        self.latencies = {
            "ollama": 2.0,  # seconds
            "vllm": 0.5,
            "openai": 1.0
        }
    
    def route(self, request: dict, strategy: Literal["cost", "performance", "balanced"] = "balanced"):
        """Route to appropriate LLM"""
        task_type = request.get("task_type", "general")
        priority = request.get("priority", "normal")
        
        if strategy == "cost":
            llm = self._route_by_cost(task_type)
        elif strategy == "performance":
            llm = self._route_by_performance(task_type, priority)
        else:  # balanced
            llm = self._route_balanced(task_type, priority)
        
        return self._execute_with_fallback(llm, request)
    
    def _route_by_cost(self, task_type: str):
        """Route to cheapest LLM"""
        if task_type == "simple":
            return self.ollama
        return self.vllm
    
    def _route_by_performance(self, task_type: str, priority: str):
        """Route to fastest LLM"""
        if priority == "high":
            return self.vllm
        return self.ollama
    
    def _route_balanced(self, task_type: str, priority: str):
        """Balance cost and performance"""
        if task_type == "simple" and priority == "normal":
            return self.ollama
        elif priority == "high":
            return self.vllm
        else:
            return self.vllm
    
    def _execute_with_fallback(self, llm, request: dict):
        """Execute with fallback mechanism"""
        try:
            return llm.invoke(request["prompt"])
        except Exception as e:
            # Fallback to Ollama
            if llm != self.ollama:
                return self.ollama.invoke(request["prompt"])
            raise
```

#### Acceptance Criteria
- [ ] Multi-LLM routing implemented (Ollama, vLLM, OpenAI)
- [ ] Cost optimization logic working
- [ ] Performance-based routing functional
- [ ] Fallback mechanisms in place
- [ ] Routing strategy configurable
- [ ] Cost tracking implemented
- [ ] Performance metrics tracked
- [ ] Routing decisions logged

#### Testing Requirements
- **Unit Tests**: Test routing logic, cost calculation, performance metrics
- **Integration Tests**: Test LLM routing, fallback mechanisms

#### Dependencies
- Phase 3 completed (Ollama)
- Phase 5 completed (vLLM)
- OpenAI API access (if using OpenAI)
- LangChain multi-LLM support

#### Risks and Mitigation
- **Risk**: LLM availability
  - **Mitigation**: Implement fallback mechanisms, health checks, monitor LLM status
- **Risk**: Cost tracking accuracy
  - **Mitigation**: Track actual usage, validate cost calculations, monitor spending

---

### Milestone 3.4: Workflow Versioning and Rollback

**Objective**: Implement workflow versioning system

#### Requirements
- Version control for workflows
- Rollback capabilities
- A/B testing support
- Version comparison

#### Technology
- **Git, Airflow, LangGraph** (Trust Scores: N/A, 9.1, 9.2)
  - Version control and workflow management

#### User Story
As a developer, I want workflow versioning so that I can safely iterate on workflows.

#### Technical Specifications

**Workflow Versioning System**:
```python
from git import Repo
import json
from datetime import datetime, timezone

class WorkflowVersionManager:
    """Manage workflow versions"""
    
    def __init__(self, repo_path: str):
        self.repo = Repo(repo_path)
        self.workflows_dir = "workflows"
    
    def create_version(self, workflow_id: str, workflow_def: dict) -> str:
        """Create new workflow version"""
        version = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        
        # Save workflow definition
        workflow_file = f"{self.workflows_dir}/{workflow_id}_v{version}.json"
        with open(workflow_file, 'w') as f:
            json.dump(workflow_def, f, indent=2)
        
        # Commit to git
        self.repo.index.add([workflow_file])
        self.repo.index.commit(f"Version {version} of {workflow_id}")
        
        # Tag version
        self.repo.create_tag(f"{workflow_id}-v{version}")
        
        return version
    
    def rollback(self, workflow_id: str, target_version: str):
        """Rollback to specific version"""
        tag = f"{workflow_id}-v{target_version}"
        self.repo.git.checkout(tag)
        # Deploy rolled back version
        return self.load_workflow(workflow_id, target_version)
    
    def compare_versions(self, workflow_id: str, v1: str, v2: str) -> dict:
        """Compare two workflow versions"""
        w1 = self.load_workflow(workflow_id, v1)
        w2 = self.load_workflow(workflow_id, v2)
        
        return {
            "added": self._diff(w1, w2, "added"),
            "removed": self._diff(w1, w2, "removed"),
            "modified": self._diff(w1, w2, "modified")
        }
```

**A/B Testing Support**:
```python
def create_ab_test_workflow(workflow_id: str, version_a: str, version_b: str, split: float = 0.5):
    """Create A/B test workflow"""
    @dag(dag_id=f"{workflow_id}_ab_test")
    def ab_test_dag():
        @task
        def route_to_version():
            import random
            return "A" if random.random() < split else "B"
        
        route = route_to_version()
        
        # Execute version A or B based on route
        @task.branch
        def execute_version(route_result: str):
            if route_result == "A":
                return [f"{workflow_id}_v{version_a}"]
            return [f"{workflow_id}_v{version_b}"]
        
        execute_version(route)
    
    return ab_test_dag()
```

#### Acceptance Criteria
- [ ] Version control implemented for workflows (Git-based)
- [ ] Rollback capabilities working (can revert to previous version)
- [ ] A/B testing support functional (can test multiple versions)
- [ ] Version comparison available (diff between versions)
- [ ] Version history tracked
- [ ] Rollback tested and validated
- [ ] A/B test results tracked

#### Testing Requirements
- **Version Control Tests**: Test versioning, rollback, comparison
- **A/B Testing Tests**: Test A/B test workflows, result tracking

#### Dependencies
- Git repository
- Workflow storage system
- Phase 1-3 completed (workflows)

#### Risks and Mitigation
- **Risk**: Version management complexity
  - **Mitigation**: Use Git best practices, automate versioning, document process
- **Risk**: Rollback data loss
  - **Mitigation**: Backup before rollback, test rollback procedures, validate data integrity

---

### Milestone 3.5: Advanced Analytics and Reporting

**Objective**: Create analytics dashboard for workflow insights

#### Requirements
- Workflow execution analytics
- Performance metrics dashboard
- Cost analysis (LLM usage)
- Success rate tracking

#### Technology
- **Grafana, TimescaleDB** (Trust Scores: N/A - Infrastructure)
  - Analytics and time-series database

#### User Story
As a user, I want workflow analytics so that I can optimize system performance.

#### Technical Specifications

**Analytics Data Collection**:
```python
from prometheus_client import Counter, Histogram, Gauge
import psycopg2
from datetime import datetime, timezone

# Metrics
workflow_executions = Counter('workflow_executions_total', 'Total executions', ['workflow_id', 'status'])
workflow_duration = Histogram('workflow_duration_seconds', 'Execution duration', ['workflow_id'])
llm_cost = Counter('llm_cost_total', 'Total LLM cost', ['model', 'workflow_id'])
workflow_success_rate = Gauge('workflow_success_rate', 'Success rate', ['workflow_id'])

def track_workflow_execution(workflow_id: str, status: str, duration: float, cost: float):
    """Track workflow execution"""
    workflow_executions.labels(workflow_id=workflow_id, status=status).inc()
    workflow_duration.labels(workflow_id=workflow_id).observe(duration)
    llm_cost.labels(model="ollama", workflow_id=workflow_id).inc(cost)
    
    # Store in TimescaleDB
    conn = psycopg2.connect("postgresql://timescaledb:5432/analytics")
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO workflow_executions (workflow_id, status, duration, cost, timestamp) VALUES (%s, %s, %s, %s, %s)",
        (workflow_id, status, duration, cost, datetime.now(timezone.utc))
    )
    conn.commit()
```

**Analytics Dashboard** (Grafana):
- Workflow execution trends
- Success/failure rates
- Performance metrics (latency, throughput)
- Cost analysis (LLM usage, infrastructure)
- Resource utilization

**Cost Analysis**:
```python
def calculate_llm_cost(workflow_id: str, start_date: datetime, end_date: datetime) -> dict:
    """Calculate LLM costs for workflow"""
    conn = psycopg2.connect("postgresql://timescaledb:5432/analytics")
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            model,
            SUM(tokens) as total_tokens,
            SUM(cost) as total_cost
        FROM llm_usage
        WHERE workflow_id = %s AND timestamp BETWEEN %s AND %s
        GROUP BY model
    """, (workflow_id, start_date, end_date))
    
    results = cur.fetchall()
    return {
        "workflow_id": workflow_id,
        "period": {"start": start_date, "end": end_date},
        "costs_by_model": {row[0]: {"tokens": row[1], "cost": row[2]} for row in results},
        "total_cost": sum(row[2] for row in results)
    }
```

#### Acceptance Criteria
- [ ] Analytics dashboard created in Grafana
- [ ] Performance metrics tracked (execution time, throughput)
- [ ] Cost analysis functional (LLM usage, infrastructure)
- [ ] Success rate tracking working
- [ ] Workflow execution trends visible
- [ ] Cost breakdown by model/workflow available
- [ ] Historical data queryable
- [ ] Reports exportable

#### Testing Requirements
- **Analytics Tests**: Test data collection, dashboard functionality, cost calculations
- **Integration Tests**: Test analytics pipeline, data storage, querying

#### Dependencies
- Phase 4 completed (Grafana)
- TimescaleDB or similar time-series database
- Analytics data collection infrastructure

#### Risks and Mitigation
- **Risk**: Data volume growth
  - **Mitigation**: Use time-series database, implement data retention, aggregate old data
- **Risk**: Cost calculation accuracy
  - **Mitigation**: Validate cost calculations, track actual usage, reconcile with bills

---

## Success Criteria

### Phase 8 Completion Criteria
- [ ] All five milestones completed and validated
- [ ] Advanced Airflow features working (dynamic DAGs, custom operators)
- [ ] LangGraph Studio functional (visualization, debugging)
- [ ] Multi-LLM routing operational (cost/performance optimization)
- [ ] Workflow versioning system working (rollback, A/B testing)
- [ ] Analytics dashboard complete (metrics, cost analysis)
- [ ] All features tested and documented
- [ ] Integration tests passing

### Quality Gates
- **Advanced Features**: All advanced features functional
- **Developer Experience**: LangGraph Studio improves workflow development
- **Analytics**: Analytics provide actionable insights
- **Documentation**: All features documented

---

## Risk Assessment

### Technical Risks

**Risk 1: Advanced Airflow Features Complexity**
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: Start with simple dynamic DAGs, use official examples, test incrementally
- **Contingency**: Simplify features, focus on core functionality

**Risk 2: LangGraph Studio Compatibility**
- **Probability**: Medium
- **Impact**: Low
- **Mitigation**: Follow Studio-compatible patterns, test import/export, use official documentation
- **Contingency**: Use alternative visualization tools

**Risk 3: Multi-LLM Routing Complexity**
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: Start with simple routing, add complexity incrementally, test thoroughly
- **Contingency**: Simplify routing logic, use fixed routing

---

## Security Requirements (CRITICAL)

### Credential Management - MANDATORY

**ALL credentials MUST be stored in `.env` file. This is a MANDATORY security requirement.**

#### Requirements
- **ALL API keys, database credentials, secret keys, tokens, and passwords MUST be in `.env` file only**
- **NEVER hardcode credentials in source code**
- **NEVER commit `.env` file to version control** (already in `.gitignore`)
- **Always use environment variables loaded from `.env` file**
- **Create `.env.example` file with placeholder values as template**
- **Document all required environment variables in documentation**

#### Credential Types That Must Be in `.env`:
- LangGraph Studio credentials
- Multi-LLM routing API keys
- Database passwords
- Any other sensitive configuration

#### Implementation Pattern:
```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access credentials from environment
LANGGRAPH_STUDIO_API_KEY = os.getenv('LANGGRAPH_STUDIO_API_KEY')
LLM_ROUTING_CONFIG = os.getenv('LLM_ROUTING_CONFIG')
```

#### Validation:
- Code review must verify no hardcoded credentials
- All credential access must use `os.getenv()` or similar
- `.env.example` must list all required variables
- Documentation must specify all required environment variables

## Dependencies and Prerequisites

### System Requirements
- All previous phases completed
- LangGraph Studio (desktop app or Docker)
- TimescaleDB or similar (for analytics)
- Git repository (for versioning)

### Software Dependencies
- Python 3.11+ with virtual environment (venv) - always use venv for local development
- Airflow 2.8.4+ with advanced features
- LangGraph Studio
- Multi-LLM integrations (install with venv activated)
- Analytics tools

### External Dependencies
- OpenAI API access (if using OpenAI routing)
- Git repository access

---

## Timeline and Effort Estimation

### Milestone Estimates
- **Milestone 3.1**: 5-7 days
- **Milestone 3.2**: 3-4 days
- **Milestone 3.3**: 4-6 days
- **Milestone 3.4**: 4-5 days
- **Milestone 3.5**: 5-7 days

### Total Phase Estimate
- **Duration**: 4-5 weeks
- **Effort**: 100-120 hours
- **Team**: 1-2 developers

### Critical Path
1. Milestone 3.1 (Advanced Airflow) - Foundation
2. Milestone 3.3 (Multi-LLM Routing) - Can run in parallel
3. Milestone 3.2 (LangGraph Studio) - Can run in parallel
4. Milestone 3.4 (Versioning) - Depends on workflows
5. Milestone 3.5 (Analytics) - Depends on all features

---

## Deliverables

### Code Deliverables
- [ ] Advanced Airflow features (dynamic DAGs, custom operators)
- [ ] LangGraph Studio integration
- [ ] Multi-LLM routing implementation
- [ ] Workflow versioning system
- [ ] Analytics data collection
- [ ] Analytics dashboards

### Documentation Deliverables
- [ ] Phase 8 PRD (this document)
- [ ] Advanced Airflow guide
- [ ] LangGraph Studio guide
- [ ] Multi-LLM routing guide
- [ ] Versioning guide
- [ ] Analytics guide

### Configuration Deliverables
- [ ] LangGraph Studio configuration
- [ ] Multi-LLM routing configuration
- [ ] Versioning system configuration
- [ ] Analytics database schema
- [ ] Grafana dashboard JSON files

---

## Next Phase Preview

**Phase 9: Enterprise Features** will build upon Phase 8 by:
- Setting up CI/CD pipeline
- Adding trading system integrations
- Implementing enterprise security
- Conducting scalability testing
- Creating system showcase

**Prerequisites for Phase 9**:
- Phase 8 completed and validated
- All advanced features operational
- Analytics system functional

---

**PRD Phase 8 Version**: 1.0  
**Last Updated**: 2025-01-27  
**Next Review**: Upon Phase 8 completion

