---
name: api-and-sdk
description: Design and build APIs and SDKs — REST/GraphQL API design, TypeScript SDK development, or MCP server building. Use when designing APIs, building SDKs, creating MCP servers, or working with typed interfaces.
---

# API & SDK

Routes to specialized sub-skills for API design, SDK development, and MCP server building.

## Decision Matrix

| Your Need | Route To | Focus |
|-----------|----------|-------|
| Design REST or GraphQL API | `api-design` | Protocol-level API design (endpoints, schemas, versioning, pagination) |
| Build TypeScript SDK for npm distribution | `sdk-development` | Client library packaging, build config, publishing |
| Build MCP server for LLM tool integration | `mcp-builder` | MCP protocol, tool schemas, evaluation |

## How to Use

1. Identify which sub-skill matches your need from the decision matrix above
2. Invoke that sub-skill directly — it has its own detailed workflow
3. This orchestrator only routes; it does not duplicate sub-skill content

## Sub-skills

- **api-design** — REST/GraphQL API design principles: resource-oriented endpoints, pagination, error handling, versioning, HATEOAS, GraphQL schema-first design, DataLoader for N+1
- **sdk-development** — TypeScript SDK development: public API surface, build config (ESM/CJS/types), publishing, CI/CD
- **mcp-builder** — MCP server building: 4-phase process (research, implement, review, evaluate), Zod/Pydantic schemas, MCP Inspector