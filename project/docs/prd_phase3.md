# Product Requirements Document: Phase 3 - Integration & Local LLM

**Project**: AI-Powered Workflow Orchestration for Trading Operations  
**Phase**: Phase 3 - Integration & Local LLM  
**Version**: 1.0  
**Date**: 2025-01-27  
**Author**: Mission Planner Agent  
**Status**: Draft  
**Parent PRD**: `project/docs/prd.md`

---

## Document Control

- **Phase Name**: Integration & Local LLM
- **Phase Number**: 3
- **Version**: 1.0
- **Author**: Mission Planner Agent
- **Last Updated**: 2025-01-27
- **Status**: Draft
- **Dependencies**: Phase 1 (Foundation), Phase 2 (AI Workflow Foundation)
- **Duration Estimate**: 2-3 weeks
- **Team Size**: 1-2 developers

---

## Executive Summary

### Phase Vision
Integrate Airflow orchestration with LangGraph AI workflows via Kafka event streaming, and establish local LLM deployment with Ollama. This phase creates the end-to-end workflow from traditional orchestration to AI-powered decision making.

### Key Objectives
1. **Airflow-LangGraph Integration**: Connect Airflow tasks to LangGraph workflows via Kafka
2. **Event-Driven Coordination**: Implement event-driven workflow coordination
3. **Local LLM Deployment**: Set up Ollama for local LLM inference
4. **End-to-End Workflows**: Create complete workflows from Airflow → Kafka → LangGraph

### Success Metrics
- **Integration**: Airflow tasks successfully trigger LangGraph workflows
- **Event Flow**: Events flow from Airflow → Kafka → LangGraph
- **LLM Integration**: Ollama running with LangChain integration
- **Error Handling**: Basic error handling implemented

---

## Phase Overview

### Scope
This phase integrates all components:
- Airflow-LangGraph integration via Kafka
- Event-driven workflow coordination
- Local LLM deployment (Ollama)
- LangChain integration with Ollama

### Out of Scope
- Production deployment (Phase 4)
- Advanced error handling (Phase 6)
- vLLM integration (Phase 5)
- Monitoring and observability (Phase 4)

### Phase Dependencies
- **Prerequisites**: Phase 1 (Airflow, Kafka), Phase 2 (LangGraph)
- **External Dependencies**: Ollama, LangChain
- **Internal Dependencies**: Event schema from Phase 1, LangGraph workflows from Phase 2

---

## Technical Architecture

### Phase 3 Architecture

```
┌──────────────┐
│   Airflow   │
│    Task     │
└──────┬───────┘
       │ Publishes Event
       │
┌──────▼───────┐
│    Kafka     │
│   Topic:     │
│ workflow-    │
│   events     │
└──────┬───────┘
       │ Consumes Event
       │
┌──────▼──────────────┐
│  LangGraph          │
│  Workflow           │
│  - Consumes Event   │
│  - Processes        │
│  - Calls LLM        │
└──────┬──────────────┘
       │
┌──────▼───────┐
│    Ollama    │
│  Local LLM   │
│  Port 11434  │
└──────────────┘
```

### Technology Stack

#### Integration Layer
- **Kafka**: Event streaming (from Phase 1)
- **Airflow**: Orchestration (from Phase 1)
- **LangGraph**: AI workflows (from Phase 2)

#### LLM Layer
- **Ollama** (Trust Score: 7.5)
  - Version: Latest stable
  - Local LLM deployment
  - Model Support: llama2, mistral, codellama, etc.

#### LLM Integration
- **LangChain** (Trust Score: 7.5)
  - Ollama integration
  - LLM abstraction layer

---

## Detailed Milestones

### Milestone 1.6: Airflow-LangGraph Integration

**Objective**: Connect Airflow tasks to LangGraph workflows via Kafka

#### Requirements
- Airflow task publishes event to Kafka
- LangGraph workflow consumes event and executes
- Results returned to Airflow task
- Error handling implemented

#### Technical Specifications

**Airflow Task → Kafka Producer**:
```python
from airflow.decorators import task
from kafka import KafkaProducer
import json
import uuid
from datetime import datetime

@task
def trigger_langgraph_workflow(data: dict):
    """Airflow task that triggers LangGraph workflow via Kafka"""
    
    # Create Kafka producer
    producer = KafkaProducer(
        bootstrap_servers=['kafka:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    # Create event
    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": "workflow.triggered",
        "timestamp": datetime.utcnow().isoformat(),
        "source": "airflow",
        "workflow_id": "example_dag",
        "workflow_run_id": "run_123",
        "payload": data,
        "metadata": {"environment": "dev", "version": "1.0"}
    }
    
    # Publish event
    future = producer.send('workflow-events', event)
    producer.flush()
    
    # Wait for result (simplified - in production use async pattern)
    # This would typically use a callback or polling mechanism
    return {"status": "triggered", "event_id": event["event_id"]}
```

**LangGraph Workflow → Kafka Consumer**:
```python
from langgraph.graph import StateGraph, START, END
from kafka import KafkaConsumer
import json
from typing import TypedDict

class WorkflowState(TypedDict):
    event: dict
    result: dict
    status: str

def consume_kafka_event(state: WorkflowState):
    """Consume event from Kafka"""
    consumer = KafkaConsumer(
        'workflow-events',
        bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        consumer_timeout_ms=1000
    )
    
    # Consume event (simplified - in production use async pattern)
    for message in consumer:
        event = message.value
        if event.get("event_type") == "workflow.triggered":
            return {"event": event, "status": "processing"}
    
    return state

def process_workflow(state: WorkflowState):
    """Process workflow with event data"""
    event = state.get("event", {})
    payload = event.get("payload", {})
    
    # Process workflow logic
    result = {"processed": True, "data": payload}
    
    return {"result": result, "status": "completed"}

def publish_result(state: WorkflowState):
    """Publish result back to Kafka"""
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    result_event = {
        "event_type": "workflow.completed",
        "workflow_id": state["event"]["workflow_id"],
        "result": state["result"]
    }
    
    producer.send('workflow-results', result_event)
    producer.flush()
    
    return state

# Build graph
workflow = StateGraph(WorkflowState)
workflow.add_node("consume", consume_kafka_event)
workflow.add_node("process", process_workflow)
workflow.add_node("publish", publish_result)

workflow.add_edge(START, "consume")
workflow.add_edge("consume", "process")
workflow.add_edge("process", "publish")
workflow.add_edge("publish", END)

graph = workflow.compile()
```

**Error Handling**:
- Retry mechanism for Kafka operations
- Dead letter queue for failed events
- Error notifications
- Timeout handling

#### Acceptance Criteria
- [ ] Airflow task publishes event to Kafka successfully
- [ ] LangGraph workflow consumes event from Kafka
- [ ] Workflow executes with event data
- [ ] Results returned to Airflow (via callback or polling)
- [ ] Error handling implemented for Kafka operations
- [ ] Event schema validated
- [ ] End-to-end workflow tested

#### Testing Requirements
- **Integration Tests**:
  - Test Airflow → Kafka → LangGraph flow
  - Test event consumption and processing
  - Test result return mechanism
  - Test error scenarios

- **End-to-End Tests**:
  - Test complete workflow execution
  - Test event-driven coordination
  - Test error recovery

#### Dependencies
- Phase 1 completed (Airflow, Kafka)
- Phase 2 completed (LangGraph workflows)
- Kafka Python client
- Understanding of event-driven patterns

#### Risks and Mitigation
- **Risk**: Event-driven complexity
  - **Mitigation**: Start with simple synchronous pattern, add async later
- **Risk**: Error handling across components
  - **Mitigation**: Implement comprehensive error handling, use dead letter queues
- **Risk**: Result return mechanism
  - **Mitigation**: Use callback pattern or polling, implement timeout

---

### Milestone 1.7: Local LLM Deployment (Ollama)

**Objective**: Set up Ollama for local LLM deployment and integrate with LangChain

#### Requirements
- Ollama running locally
- At least one model downloaded (e.g., llama2)
- LangChain integration with Ollama
- Basic inference working

#### Technical Specifications

**Ollama Setup**:
```bash
# Install Ollama (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Download model
ollama pull llama2

# Verify installation
ollama list
```

**LangChain Integration**:
```python
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Initialize Ollama LLM
llm = Ollama(
    model="llama2",
    base_url="http://localhost:11434",
    temperature=0.7
)

# Create prompt template
prompt = PromptTemplate(
    input_variables=["task"],
    template="You are a helpful assistant. Task: {task}"
)

# Create chain
chain = LLMChain(llm=llm, prompt=prompt)

# Run inference
result = chain.run("Analyze this data: [1, 2, 3, 4, 5]")
print(result)
```

**LangGraph Integration**:
```python
from langgraph.graph import StateGraph, START, END
from langchain_community.llms import Ollama
from typing import TypedDict

class LLMState(TypedDict):
    input: str
    output: str
    status: str

def llm_node(state: LLMState):
    """Node that uses Ollama LLM"""
    llm = Ollama(model="llama2", base_url="http://localhost:11434")
    
    prompt = f"Process this: {state['input']}"
    output = llm.invoke(prompt)
    
    return {"output": output, "status": "completed"}

# Build graph
workflow = StateGraph(LLMState)
workflow.add_node("llm_process", llm_node)
workflow.add_edge(START, "llm_process")
workflow.add_edge("llm_process", END)

graph = workflow.compile()
```

**Docker Integration** (Optional):
```yaml
services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0

volumes:
  ollama_data:
```

#### Acceptance Criteria
- [ ] Ollama running locally (or in Docker)
- [ ] At least one model downloaded (llama2 or similar)
- [ ] LangChain integration with Ollama working
- [ ] Basic inference working (text generation)
- [ ] LangGraph workflow uses Ollama LLM
- [ ] Model responses are reasonable
- [ ] Error handling for LLM calls

#### Testing Requirements
- **Manual Testing**:
  - Verify Ollama is running
  - Test model inference via CLI
  - Test LangChain integration
  - Test LangGraph integration

- **Automated Testing**:
  - Test LLM initialization
  - Test inference calls
  - Test error handling
  - Mock LLM calls for unit tests

#### Dependencies
- Ollama installed
- Sufficient disk space for models (4GB+ per model)
- Sufficient RAM (8GB+ recommended)
- LangChain Ollama integration

#### Risks and Mitigation
- **Risk**: Model download size
  - **Mitigation**: Start with smaller models, use model quantization
- **Risk**: LLM performance
  - **Mitigation**: Use appropriate model size, optimize prompts
- **Risk**: Resource requirements
  - **Mitigation**: Monitor resource usage, use Docker for isolation

---

## Integration Patterns

### Event-Driven Workflow Pattern

1. **Airflow Task** publishes event to Kafka
2. **Kafka** stores event in topic
3. **LangGraph Consumer** consumes event
4. **LangGraph Workflow** processes with LLM
5. **Result** published back to Kafka (or returned directly)

### LLM Integration Pattern

1. **LangGraph Node** calls LangChain
2. **LangChain** routes to Ollama
3. **Ollama** processes with local model
4. **Result** returned to LangGraph workflow
5. **Workflow** continues with LLM output

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
- LLM API keys (OpenAI, Anthropic, etc.)
- Ollama configuration
- Database passwords (MongoDB, etc.)
- Kafka connection strings
- Any other sensitive configuration

#### Implementation Pattern:
```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access credentials from environment
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL')
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')
```

#### Validation:
- Code review must verify no hardcoded credentials
- All credential access must use `os.getenv()` or similar
- `.env.example` must list all required variables
- Documentation must specify all required environment variables

## Development Environment

### Docker Compose Addition

```yaml
services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  ollama_data:
```

### Python Dependencies

**Always use venv for local development:**

```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install langchain>=0.2.0 langchain-community>=0.2.0 kafka-python>=2.0.2
```

**Or use requirements.txt:**

```txt
langchain>=0.2.0
langchain-community>=0.2.0
kafka-python>=2.0.2
```

```bash
# With venv activated
pip install -r requirements.txt
```

**Note**: Always activate venv before running any Python commands, installing packages, or running scripts.

---

## Testing Strategy

### Integration Testing
- **Airflow-Kafka Integration**: Test event publishing
- **Kafka-LangGraph Integration**: Test event consumption
- **LangGraph-Ollama Integration**: Test LLM calls
- **End-to-End Workflow**: Test complete flow

### Performance Testing
- **Event Latency**: Measure Kafka event processing time
- **LLM Response Time**: Measure Ollama inference time
- **Workflow Execution Time**: Measure end-to-end time

---

## Success Criteria

### Phase 3 Completion Criteria
- [ ] Both milestones completed and validated
- [ ] Airflow-LangGraph integration working
- [ ] Event-driven coordination functional
- [ ] Ollama running with model downloaded
- [ ] LangChain integration working
- [ ] End-to-end workflow tested
- [ ] Error handling implemented
- [ ] Documentation complete

### Quality Gates
- **Integration**: All components integrated successfully
- **Error Handling**: Basic error handling in place
- **Performance**: Workflow execution <2 minutes (with LLM)
- **Documentation**: Integration patterns documented

---

## Risk Assessment

### Technical Risks

**Risk 1: Integration Complexity**
- **Probability**: High
- **Impact**: High
- **Mitigation**: Start with simple patterns, test incrementally
- **Contingency**: Simplify integration, use direct calls initially

**Risk 2: LLM Performance**
- **Probability**: Medium
- **Impact**: Medium
- **Mitigation**: Use appropriate models, optimize prompts
- **Contingency**: Use smaller models, implement caching

**Risk 3: Event-Driven Reliability**
- **Probability**: Medium
- **Impact**: High
- **Mitigation**: Implement retries, dead letter queues, monitoring
- **Contingency**: Add synchronous fallback mechanism

---

## Timeline and Effort Estimation

### Milestone Estimates
- **Milestone 1.6**: 5-7 days
- **Milestone 1.7**: 3-5 days

### Total Phase Estimate
- **Duration**: 2-3 weeks
- **Effort**: 50-70 hours
- **Team**: 1-2 developers

---

## Deliverables

### Code Deliverables
- [ ] Airflow-LangGraph integration code
- [ ] Kafka consumer/producer implementations
- [ ] Ollama integration with LangChain
- [ ] LangGraph workflows with LLM
- [ ] Error handling implementations
- [ ] Integration tests

### Documentation Deliverables
- [ ] Phase 3 PRD (this document)
- [ ] Integration patterns guide
- [ ] Ollama setup guide
- [ ] Event-driven workflow documentation
- [ ] LLM integration guide

---

## Next Phase Preview

**Phase 4: Production Infrastructure** will build upon Phase 3 by:
- Setting up monitoring (Prometheus/Grafana)
- Containerizing all services with Docker
- Creating FastAPI orchestration API
- Preparing for production deployment

---

**PRD Phase 3 Version**: 1.0  
**Last Updated**: 2025-01-27  
**Next Review**: Upon Phase 3 completion

