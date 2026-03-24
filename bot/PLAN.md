# Bot Development Plan

## Overview

This document outlines the development plan for the Telegram bot that interfaces with the Learning Management System (LMS) backend. The bot provides students with a conversational interface to access their academic data, including lab scores, course progress, and personalized assistance via LLM integration.

## Phase 1: Scaffold & Architecture (Current Task)

**Goal:** Establish a testable, modular architecture where business logic is separated from the Telegram transport layer.

- Create directory structure: `handlers/`, `services/`, `config.py`, `bot.py`
- Implement `--test` CLI mode for local testing without Telegram credentials
- Design handlers that work independently of the Telegram API
- Set up `pyproject.toml` with proper dependencies using `uv`

**Key Design Decision:** Handlers receive plain command strings and return plain text responses. This allows testing without a Telegram connection and makes the codebase more maintainable.

## Phase 2: Backend Integration

**Goal:** Connect the bot to the LMS backend API for data retrieval.

- Implement `LMSClient` service for API communication
- Add authentication using `LMS_API_KEY`
- Create handlers for `/scores`, `/labs`, `/progress` commands
- Handle API errors gracefully with user-friendly messages

## Phase 3: Intent Routing & LLM Integration

**Goal:** Enable natural language queries through intent classification.

- Implement intent detection (either rule-based or LLM-powered)
- Route user messages to appropriate handlers
- Integrate Qwen API for generating personalized responses
- Add context awareness for multi-turn conversations

## Phase 4: Deployment & Monitoring

**Goal:** Deploy the bot to production (VM) with proper process management.

- Create `.env.bot.secret` with production credentials
- Set up process management (nohup/systemd) for auto-restart
- Add logging for debugging and monitoring
- Document troubleshooting procedures

## Testing Strategy

- Unit tests for handlers (pytest)
- Integration tests for LMS client
- Manual testing via `--test` mode before deployment
- End-to-end testing in Telegram after deployment

## Risk Mitigation

- **API Rate Limiting:** Implement caching for frequently accessed data
- **Credential Security:** Never commit `.env.bot.secret` to git
- **Process Crashes:** Use restart policies and log monitoring
