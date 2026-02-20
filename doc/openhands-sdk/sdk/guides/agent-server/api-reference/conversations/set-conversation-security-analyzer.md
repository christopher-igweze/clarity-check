> ## Documentation Index
> Fetch the complete documentation index at: https://docs.openhands.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Set Conversation Security Analyzer

> Set the security analyzer for a conversation.



## OpenAPI

````yaml openapi/agent-sdk.json post /api/conversations/{conversation_id}/security_analyzer
openapi: 3.1.0
info:
  title: OpenHands Agent Server
  description: OpenHands Agent Server - REST/WebSocket interface for OpenHands AI Agent
  version: 0.1.0
servers: []
security: []
paths:
  /api/conversations/{conversation_id}/security_analyzer:
    post:
      tags:
        - Conversations
      summary: Set Conversation Security Analyzer
      description: Set the security analyzer for a conversation.
      operationId: >-
        set_conversation_security_analyzer_api_conversations__conversation_id__security_analyzer_post
      parameters:
        - name: conversation_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
            title: Conversation Id
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SetSecurityAnalyzerRequest'
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Success'
        '404':
          description: Item not found
        '422':
          description: Validation Error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HTTPValidationError'
components:
  schemas:
    SetSecurityAnalyzerRequest:
      properties:
        security_analyzer:
          anyOf:
            - $ref: '#/components/schemas/SecurityAnalyzerBase-Input'
            - type: 'null'
          description: The security analyzer to set
      type: object
      required:
        - security_analyzer
      title: SetSecurityAnalyzerRequest
      description: Payload to set security analyzer for a conversation
    Success:
      properties:
        success:
          type: boolean
          title: Success
          default: true
      type: object
      title: Success
    HTTPValidationError:
      properties:
        detail:
          items:
            $ref: '#/components/schemas/ValidationError'
          type: array
          title: Detail
      type: object
      title: HTTPValidationError
    SecurityAnalyzerBase-Input:
      oneOf:
        - $ref: '#/components/schemas/GraySwanAnalyzer-Input'
        - $ref: '#/components/schemas/LLMSecurityAnalyzer-Input'
      discriminator:
        propertyName: kind
        mapping:
          openhands__sdk__security__grayswan__analyzer__GraySwanAnalyzer-Input__1: '#/components/schemas/GraySwanAnalyzer-Input'
          openhands__sdk__security__llm_analyzer__LLMSecurityAnalyzer-Input__1: '#/components/schemas/LLMSecurityAnalyzer-Input'
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
    GraySwanAnalyzer-Input:
      properties:
        history_limit:
          type: integer
          title: History Limit
          description: Number of recent events to include as context
          default: 20
        max_message_chars:
          type: integer
          title: Max Message Chars
          description: Max characters for conversation processing
          default: 30000
        timeout:
          type: number
          title: Timeout
          description: Request timeout in seconds
          default: 30
        low_threshold:
          type: number
          title: Low Threshold
          description: Risk threshold for LOW classification (score <= threshold)
          default: 0.3
        medium_threshold:
          type: number
          title: Medium Threshold
          description: Risk threshold for MEDIUM classification (score <= threshold)
          default: 0.7
        api_url:
          type: string
          title: Api Url
          description: GraySwan Cygnal API endpoint
          default: https://api.grayswan.ai/cygnal/monitor
        api_key:
          anyOf:
            - type: string
              format: password
              writeOnly: true
            - type: 'null'
          title: Api Key
          description: GraySwan API key (via GRAYSWAN_API_KEY env var)
        policy_id:
          anyOf:
            - type: string
            - type: 'null'
          title: Policy Id
          description: GraySwan policy ID (via GRAYSWAN_POLICY_ID env var)
        kind:
          type: string
          const: GraySwanAnalyzer
          title: Kind
      type: object
      title: GraySwanAnalyzer
      description: >-
        Security analyzer using GraySwan's Cygnal API for AI safety monitoring.


        This analyzer sends conversation history and pending actions to the
        GraySwan

        Cygnal API for security analysis. The API returns a violation score
        which is

        mapped to SecurityRisk levels.


        Environment Variables:
            GRAYSWAN_API_KEY: Required API key for GraySwan authentication
            GRAYSWAN_POLICY_ID: Optional policy ID for custom GraySwan policy

        Example:
            >>> from openhands.sdk.security.grayswan import GraySwanAnalyzer
            >>> analyzer = GraySwanAnalyzer()
            >>> risk = analyzer.security_risk(action_event)
    LLMSecurityAnalyzer-Input:
      properties:
        kind:
          type: string
          const: LLMSecurityAnalyzer
          title: Kind
      type: object
      title: LLMSecurityAnalyzer
      description: >-
        LLM-based security analyzer.


        This analyzer respects the security_risk attribute that can be set by
        the LLM

        when generating actions, similar to OpenHands' LLMRiskAnalyzer.


        It provides a lightweight security analysis approach that leverages the
        LLM's

        understanding of action context and potential risks.

````
