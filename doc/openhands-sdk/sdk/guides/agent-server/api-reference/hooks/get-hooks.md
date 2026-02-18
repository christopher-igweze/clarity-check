> ## Documentation Index
> Fetch the complete documentation index at: https://docs.openhands.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Get Hooks

> Load hooks from the workspace .openhands/hooks.json file.

This endpoint reads the hooks configuration from the project's
.openhands/hooks.json file if it exists.

Args:
    request: HooksRequest containing the project directory path.

Returns:
    HooksResponse containing the hook configuration or None.



## OpenAPI

````yaml openapi/agent-sdk.json post /api/hooks
openapi: 3.1.0
info:
  title: OpenHands Agent Server
  description: OpenHands Agent Server - REST/WebSocket interface for OpenHands AI Agent
  version: 0.1.0
servers: []
security: []
paths:
  /api/hooks:
    post:
      tags:
        - Hooks
      summary: Get Hooks
      description: |-
        Load hooks from the workspace .openhands/hooks.json file.

        This endpoint reads the hooks configuration from the project's
        .openhands/hooks.json file if it exists.

        Args:
            request: HooksRequest containing the project directory path.

        Returns:
            HooksResponse containing the hook configuration or None.
      operationId: get_hooks_api_hooks_post
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/HooksRequest'
        required: true
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HooksResponse'
        '422':
          description: Validation Error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HTTPValidationError'
components:
  schemas:
    HooksRequest:
      properties:
        project_dir:
          anyOf:
            - type: string
            - type: 'null'
          title: Project Dir
          description: Workspace directory path for project hooks
      type: object
      title: HooksRequest
      description: Request body for loading hooks.
    HooksResponse:
      properties:
        hook_config:
          anyOf:
            - $ref: '#/components/schemas/HookConfig-Output'
            - type: 'null'
          description: Hook configuration loaded from the workspace, or None if not found
      type: object
      title: HooksResponse
      description: Response containing hooks configuration.
    HTTPValidationError:
      properties:
        detail:
          items:
            $ref: '#/components/schemas/ValidationError'
          type: array
          title: Detail
      type: object
      title: HTTPValidationError
    HookConfig-Output:
      properties:
        pre_tool_use:
          items:
            $ref: '#/components/schemas/HookMatcher-Output'
          type: array
          title: Pre Tool Use
          description: Hooks that run before tool execution
        post_tool_use:
          items:
            $ref: '#/components/schemas/HookMatcher-Output'
          type: array
          title: Post Tool Use
          description: Hooks that run after tool execution
        user_prompt_submit:
          items:
            $ref: '#/components/schemas/HookMatcher-Output'
          type: array
          title: User Prompt Submit
          description: Hooks that run when user submits a prompt
        session_start:
          items:
            $ref: '#/components/schemas/HookMatcher-Output'
          type: array
          title: Session Start
          description: Hooks that run when a session starts
        session_end:
          items:
            $ref: '#/components/schemas/HookMatcher-Output'
          type: array
          title: Session End
          description: Hooks that run when a session ends
        stop:
          items:
            $ref: '#/components/schemas/HookMatcher-Output'
          type: array
          title: Stop
          description: Hooks that run when the agent attempts to stop
      additionalProperties: false
      type: object
      title: HookConfig
      description: >-
        Configuration for all hooks.


        Hooks can be configured either by loading from `.openhands/hooks.json`
        or

        by directly instantiating with typed fields:

            # Direct instantiation with typed fields (recommended):
            config = HookConfig(
                pre_tool_use=[
                    HookMatcher(
                        matcher="terminal",
                        hooks=[HookDefinition(command="block_dangerous.sh")]
                    )
                ]
            )

            # Load from JSON file:
            config = HookConfig.load(".openhands/hooks.json")
    ValidationError:
      properties:
        loc:
          items:
            anyOf:
              - type: string
              - type: integer
          type: array
          title: Location
        msg:
          type: string
          title: Message
        type:
          type: string
          title: Error Type
      type: object
      required:
        - loc
        - msg
        - type
      title: ValidationError
    HookMatcher-Output:
      properties:
        matcher:
          type: string
          title: Matcher
          default: '*'
        hooks:
          items:
            $ref: '#/components/schemas/HookDefinition'
          type: array
          title: Hooks
      type: object
      title: HookMatcher
      description: >-
        Matches events to hooks based on patterns.


        Supports exact match, wildcard (*), and regex (auto-detected or
        /pattern/).
    HookDefinition:
      properties:
        type:
          $ref: '#/components/schemas/HookType'
          default: command
        command:
          type: string
          title: Command
        timeout:
          type: integer
          title: Timeout
          default: 60
      type: object
      required:
        - command
      title: HookDefinition
      description: A single hook definition.
    HookType:
      type: string
      enum:
        - command
        - prompt
      title: HookType
      description: Types of hooks that can be executed.

````
