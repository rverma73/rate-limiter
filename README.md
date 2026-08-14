# Distributed API Rate Limiter

A distributed per-user API rate limiter built with **FastAPI, Redis, PostgreSQL, JWT, Redis Lua scripting, and Docker Compose**.

The project implements the **Token Bucket algorithm** and uses an atomic Redis Lua script to prevent race conditions when multiple requests arrive concurrently.

## Architecture

```text
                         Client
                           │
                           │ JWT Bearer Token
                           ▼
                    ┌─────────────┐
                    │   FastAPI   │
                    └──────┬──────┘
                           │
                    JWT Authentication
                           │
                           ▼
                    Current User ID
                           │
                           ▼
                    Rate Limiter
                           │
                           ▼
                    ┌─────────────┐
                    │    Redis    │
                    │ Token Bucket│
                    └──────┬──────┘
                           │
                    Redis Lua Script
                           │
                  ┌────────┴────────┐
                  │                 │
              Token available   No token
                  │                 │
                  ▼                 ▼
               HTTP 200          HTTP 429
                  │
                  ▼
              Protected API

        ┌──────────────────────────────┐
        │         PostgreSQL           │
        │     User persistence         │
        └──────────────────────────────┘