# Integration Architecture Guide

Guidance for designing integration architecture — depends on application architecture's interface definitions to determine what needs to connect to what.

## External System Interface Contracts

### Interface Specification Template

For each external system integration:

```markdown
### [External System Name]

**Purpose:** What data or capability this integration provides
**Direction:** Inbound (they call us) / Outbound (we call them) / Bidirectional
**Protocol:** REST / GraphQL / gRPC / Message Queue / File Transfer / WebSocket
**Authentication:** API Key / OAuth2 / mTLS / Basic Auth / None
**Data format:** JSON / XML / Protobuf / CSV / Binary

**Endpoints/Topics:**
| Direction | Path/Topic | Method/Action | Request Schema | Response Schema |
|-----------|-----------|---------------|----------------|-----------------|
| Outbound | /api/v1/resource | GET | - | { ... } |
| Inbound | /webhook/event | POST | { ... } | 200 OK |

**SLA:**
- Availability: 99.9% / best-effort
- Latency: p99 < 200ms / no guarantee
- Rate limit: 1000 req/min / unlimited

**Error handling:** Retry policy, circuit breaker threshold, fallback behavior
```

## Protocol Selection

| Protocol | Best For | Trade-offs |
|----------|----------|------------|
| REST (HTTP/JSON) | CRUD APIs, public APIs, simple integrations | Verbose, no streaming, request-response only |
| GraphQL | Flexible querying, frontend-driven data fetching | Complexity, N+1 risk, caching harder |
| gRPC | Internal service-to-service, low-latency, streaming | Binary protocol (hard to debug), requires proto definitions |
| Message Queue (AMQP) | Async workflows, event-driven, decoupling | Eventual consistency, ordering challenges, operational overhead |
| WebSocket | Real-time bidirectional (chat, live updates) | Connection management, scaling complexity |
| File Transfer (S3/SFTP) | Batch data exchange, large datasets | High latency, no real-time, scheduling complexity |

### Decision Framework

1. Is the interaction synchronous or asynchronous?
   - Sync → REST, GraphQL, gRPC
   - Async → Message Queue, File Transfer
2. Is it internal (our services) or external (third-party)?
   - Internal → gRPC or REST (your choice)
   - External → REST (most widely supported)
3. Is real-time push needed?
   - Yes → WebSocket or Server-Sent Events
   - No → Standard request-response or polling

## Data Synchronization Strategy

### Patterns

| Pattern | How It Works | Use When |
|---------|-------------|----------|
| **API Polling** | Periodically call external API for updates | External system has no push mechanism; data changes infrequently |
| **Webhook** | External system pushes events to our endpoint | External system supports webhooks; need near-real-time |
| **Change Data Capture (CDC)** | Monitor DB changelog (e.g., Debezium) | Need to sync from databases we control; no application-level events |
| **Event Stream** | Publish/subscribe to event topics | High-volume, multiple consumers, need replay capability |
| **Batch ETL** | Scheduled extract-transform-load jobs | Large datasets, acceptable latency (hours), data warehousing |

### Consistency Across Systems

- **Source of truth:** Define which system owns each data entity. Other systems hold projections or cached copies.
- **Conflict resolution:** Last-write-wins, application-level merge, or manual resolution — decide upfront.
- **Idempotency:** All sync operations must be idempotent. Use correlation IDs to deduplicate.

## Fault Isolation & Degradation

### Circuit Breaker Pattern

```
States: CLOSED (normal) → OPEN (failing) → HALF-OPEN (testing recovery)

Configuration:
- Failure threshold: N failures in M seconds → open circuit
- Open duration: wait before testing recovery
- Half-open: allow 1 request through; if success → close, if fail → stay open
```

### Fallback Strategies

| Strategy | Implementation | Use When |
|----------|---------------|----------|
| **Cached response** | Return last known good response | Data doesn't change rapidly, stale data acceptable |
| **Default value** | Return a hardcoded sensible default | Non-critical data, better than error |
| **Graceful degradation** | Disable the feature, show message | Feature is non-essential to core flow |
| **Queue and retry** | Store request, process when recovered | Operation must succeed eventually, can wait |

### Timeout Strategy

- **Connect timeout:** 2-5 seconds (fast fail on unreachable)
- **Read timeout:** Match external system's p99 latency + 50% buffer
- **Total timeout:** Connect + Read + 1 retry budget

### Bulkhead Pattern

Isolate external system calls into separate thread pools or connection pools so that one slow external system cannot exhaust resources needed by others.
