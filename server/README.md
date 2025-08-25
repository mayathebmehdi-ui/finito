# Server deployment (Docker)

## Build
```bash
docker build -t policy-analyzer -f server/Dockerfile .
```

## Run
```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -e FIRECRAWL_API_KEY=$FIRECRAWL_API_KEY \
  -e FIRECRAWL_SEARCH_ONLY=true \
  policy-analyzer
```

## Endpoints
- GET /docs
- POST /analyze { url }
- GET /job/{id}
- GET /results
- GET /export/csv?sep=%3B&bom=true
