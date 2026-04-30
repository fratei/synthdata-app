# SynthData Developer API Reference

## Overview

The SynthData Developer API enables programmatic access to synthetic data generation. This reference covers authentication, SDK usage, and advanced patterns.

## SDKs

Official SDKs (planned):
- **Python**: `pip install synthdata` 
- **JavaScript/TypeScript**: `npm install @creativeware/synthdata`

## Authentication

### API Key

Obtain an API key from the SynthData dashboard. Include it in all requests:

```bash
curl -X POST https://api.synthdata.creativeware.ai/api/v1/generate \
  -H "Authorization: Bearer sd_live_abc123..." \
  -H "Content-Type: application/json" \
  -d '{"data_type": "tabular", "count": 100, ...}'
```

### Python Example

```python
import httpx

client = httpx.Client(
    base_url="https://api.synthdata.creativeware.ai/api/v1",
    headers={"Authorization": "Bearer sd_live_abc123..."},
)

# Generate synthetic user data
response = client.post("/generate", json={
    "data_type": "tabular",
    "schema_definition": {
        "columns": [
            {"name": "name", "type": "string"},
            {"name": "email", "type": "email"},
            {"name": "age", "type": "integer", "min": 18, "max": 90},
        ]
    },
    "count": 1000,
    "output_format": "csv",
})

job = response.json()
print(f"Job queued: {job['job_id']}")
```

## Webhook Notifications (Planned)

Register a webhook URL to receive notifications when jobs complete:

```json
{
  "data_type": "tabular",
  "count": 10000,
  "webhook_url": "https://your-app.com/webhooks/synthdata"
}
```

## Rate Limits & Quotas

See [API.md](API.md#rate-limits) for current rate limits by plan tier.

## Error Handling

All errors include a `detail` field with a human-readable message. Implement exponential backoff for `429` and `5xx` responses.
