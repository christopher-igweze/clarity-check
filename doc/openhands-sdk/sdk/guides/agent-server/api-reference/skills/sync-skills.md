> ## Documentation Index
> Fetch the complete documentation index at: https://docs.openhands.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Sync Skills

> Force refresh of public skills from GitHub repository.

This triggers a git pull on the cached skills repository to get
the latest skills from the OpenHands/skills repository.

Returns:
    SyncResponse indicating success or failure.



## OpenAPI

````yaml openapi/agent-sdk.json post /api/skills/sync
openapi: 3.1.0
info:
  title: OpenHands Agent Server
  description: OpenHands Agent Server - REST/WebSocket interface for OpenHands AI Agent
  version: 0.1.0
servers: []
security: []
paths:
  /api/skills/sync:
    post:
      tags:
        - Skills
      summary: Sync Skills
      description: |-
        Force refresh of public skills from GitHub repository.

        This triggers a git pull on the cached skills repository to get
        the latest skills from the OpenHands/skills repository.

        Returns:
            SyncResponse indicating success or failure.
      operationId: sync_skills_api_skills_sync_post
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SyncResponse'
components:
  schemas:
    SyncResponse:
      properties:
        status:
          type: string
          enum:
            - success
            - error
          title: Status
        message:
          type: string
          title: Message
      type: object
      required:
        - status
        - message
      title: SyncResponse
      description: Response from skill sync operation.

````
