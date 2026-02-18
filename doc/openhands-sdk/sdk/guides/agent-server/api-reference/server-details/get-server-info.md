> ## Documentation Index
> Fetch the complete documentation index at: https://docs.openhands.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Get Server Info



## OpenAPI

````yaml openapi/agent-sdk.json get /server_info
openapi: 3.1.0
info:
  title: OpenHands Agent Server
  description: OpenHands Agent Server - REST/WebSocket interface for OpenHands AI Agent
  version: 0.1.0
servers: []
security: []
paths:
  /server_info:
    get:
      tags:
        - Server Details
      summary: Get Server Info
      operationId: get_server_info_server_info_get
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ServerInfo'
components:
  schemas:
    ServerInfo:
      properties:
        uptime:
          type: number
          title: Uptime
        idle_time:
          type: number
          title: Idle Time
        title:
          type: string
          title: Title
          default: OpenHands Agent Server
        version:
          type: string
          title: Version
          default: 1.11.4
        docs:
          type: string
          title: Docs
          default: /docs
        redoc:
          type: string
          title: Redoc
          default: /redoc
      type: object
      required:
        - uptime
        - idle_time
      title: ServerInfo

````
