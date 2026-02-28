# Test Codex Repo

This repository is used for Codex CLI test runs and demonstrations.

## Description

This project contains minimal scaffolding intended to validate workflows like branching, committing changes, and opening pull requests. Below is the Calculator REST API built with FastAPI.

## Calculator REST API

Setup
- Install dependencies: pip install -r requirements.txt
- Run server: uvicorn calculator.main:app --reload
- Or via Docker: docker compose up --build

Endpoints
- POST /add       body { "a": float, "b": float } → { "result": float }
- POST /subtract  body { "a": float, "b": float } → { "result": float }
- POST /multiply  body { "a": float, "b": float } → { "result": float }
- POST /divide    body { "a": float, "b": float } → { "result": float } (400 on division by zero)
- POST /power     body { "a": float, "b": float } → { "result": float }
- POST /sqrt      body { "a": float } → { "result": float } (400 on negative input)
- GET  /history   returns last 10 calculations in newest-first order
