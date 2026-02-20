> ## Documentation Index
> Fetch the complete documentation index at: https://docs.openhands.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Health

> Basic health check - returns OK if the server process is running.



## OpenAPI

````yaml openapi/agent-sdk.json get /health
openapi: 3.1.0
info:
  title: OpenHands Agent Server
  description: OpenHands Agent Server - REST/WebSocket interface for OpenHands AI Agent
  version: 0.1.0
servers: []
security: []
paths:
  /health:
    get:
      tags:
        - Server Details
      summary: Health
      description: Basic health check - returns OK if the server process is running.
      operationId: health_health_get
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                type: string
                title: Response Health Health Get

````
