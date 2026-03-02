## Logfire Setup

The project supports Logfire instrumentation for `pydantic_ai` calls.

### Local development

1. Authenticate:
   - `make logfire-auth`
2. Select project:
   - `make logfire-use-project`
3. Enable in `.env`:
   - `LOGFIRE_ENABLED=true`

### Production

Set environment variables:

- `LOGFIRE_ENABLED=true`
- `LOGFIRE_TOKEN=<your_write_token>`
- `LOGFIRE_SERVICE_NAME=smartjobmonitor`
- `LOGFIRE_ENV=production`

### Data policy

Current setup sends metadata-only traces for `pydantic_ai`:

- `include_content=False`
- `include_binary_content=False`

So prompt text and binary content are not sent to Logfire.
