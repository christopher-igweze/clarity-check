> ## Documentation Index
> Fetch the complete documentation index at: https://docs.openhands.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Ready

> Readiness check - returns OK only if the server has completed initialization.

This endpoint should be used by Kubernetes readiness probes to determine
when the pod is ready to receive traffic. Returns 503 during initialization.



## OpenAPI

````yaml openapi/agent-sdk.json get /ready
openapi: 3.1.0
info:
  title: OpenHands Agent Server
  description: OpenHands Agent Server - REST/WebSocket interface for OpenHands AI Agent
  version: 0.1.0
servers: []
security: []
paths:
  /ready:
    get:
      tags:
        - Server Details
      summary: Ready
      description: >-
        Readiness check - returns OK only if the server has completed
        initialization.


        This endpoint should be used by Kubernetes readiness probes to determine

        when the pod is ready to receive traffic. Returns 503 during
        initialization.
      operationId: ready_ready_get
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                additionalProperties:
                  type: string
                type: object
                title: Response Ready Ready Get

````
