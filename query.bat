@echo off
set QUERY=%*
curl -X POST http://127.0.0.1:45104/chat -H "Content-Type: application/json" -d "{\"query\": \"%QUERY%\"}"
