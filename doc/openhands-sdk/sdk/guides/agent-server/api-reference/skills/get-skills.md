> ## Documentation Index
> Fetch the complete documentation index at: https://docs.openhands.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Get Skills

> Load and merge skills from all configured sources.

Skills are loaded from multiple sources and merged with the following
precedence (later overrides earlier for duplicate names):
1. Sandbox skills (lowest) - Exposed URLs from sandbox
2. Public skills - From GitHub OpenHands/skills repository
3. User skills - From ~/.openhands/skills/
4. Organization skills - From {org}/.openhands or equivalent
5. Project skills (highest) - From {workspace}/.openhands/skills/

Args:
    request: SkillsRequest containing configuration for which sources to load.

Returns:
    SkillsResponse containing merged skills and source counts.



## OpenAPI

````yaml openapi/agent-sdk.json post /api/skills
openapi: 3.1.0
info:
  title: OpenHands Agent Server
  description: OpenHands Agent Server - REST/WebSocket interface for OpenHands AI Agent
  version: 0.1.0
servers: []
security: []
paths:
  /api/skills:
    post:
      tags:
        - Skills
      summary: Get Skills
      description: |-
        Load and merge skills from all configured sources.

        Skills are loaded from multiple sources and merged with the following
        precedence (later overrides earlier for duplicate names):
        1. Sandbox skills (lowest) - Exposed URLs from sandbox
        2. Public skills - From GitHub OpenHands/skills repository
        3. User skills - From ~/.openhands/skills/
        4. Organization skills - From {org}/.openhands or equivalent
        5. Project skills (highest) - From {workspace}/.openhands/skills/

        Args:
            request: SkillsRequest containing configuration for which sources to load.

        Returns:
            SkillsResponse containing merged skills and source counts.
      operationId: get_skills_api_skills_post
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SkillsRequest'
        required: true
      responses:
        '200':
          description: Successful Response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SkillsResponse'
        '422':
          description: Validation Error
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HTTPValidationError'
components:
  schemas:
    SkillsRequest:
      properties:
        load_public:
          type: boolean
          title: Load Public
          description: Load public skills from OpenHands/skills repo
          default: true
        load_user:
          type: boolean
          title: Load User
          description: Load user skills from ~/.openhands/skills/
          default: true
        load_project:
          type: boolean
          title: Load Project
          description: Load project skills from workspace
          default: true
        load_org:
          type: boolean
          title: Load Org
          description: Load organization-level skills
          default: true
        project_dir:
          anyOf:
            - type: string
            - type: 'null'
          title: Project Dir
          description: Workspace directory path for project skills
        org_config:
          anyOf:
            - $ref: '#/components/schemas/OrgConfig'
            - type: 'null'
          description: Organization skills configuration
        sandbox_config:
          anyOf:
            - $ref: '#/components/schemas/SandboxConfig'
            - type: 'null'
          description: Sandbox skills configuration
      type: object
      title: SkillsRequest
      description: Request body for loading skills.
    SkillsResponse:
      properties:
        skills:
          items:
            $ref: '#/components/schemas/SkillInfo'
          type: array
          title: Skills
        sources:
          additionalProperties:
            type: integer
          type: object
          title: Sources
          description: Count of skills loaded from each source
      type: object
      required:
        - skills
      title: SkillsResponse
      description: Response containing all available skills.
    HTTPValidationError:
      properties:
        detail:
          items:
            $ref: '#/components/schemas/ValidationError'
          type: array
          title: Detail
      type: object
      title: HTTPValidationError
    OrgConfig:
      properties:
        repository:
          type: string
          title: Repository
          description: Selected repository (e.g., 'owner/repo')
        provider:
          type: string
          title: Provider
          description: 'Git provider type: github, gitlab, azure, bitbucket'
        org_repo_url:
          type: string
          title: Org Repo Url
          description: >-
            Pre-authenticated Git URL for the organization repository. Contains
            sensitive credentials - handle with care and avoid logging.
        org_name:
          type: string
          title: Org Name
          description: Organization name
      type: object
      required:
        - repository
        - provider
        - org_repo_url
        - org_name
      title: OrgConfig
      description: Configuration for loading organization-level skills.
    SandboxConfig:
      properties:
        exposed_urls:
          items:
            $ref: '#/components/schemas/ExposedUrl'
          type: array
          title: Exposed Urls
          description: List of exposed URLs from the sandbox
      type: object
      title: SandboxConfig
      description: Configuration for loading sandbox-specific skills.
    SkillInfo:
      properties:
        name:
          type: string
          title: Name
        type:
          type: string
          enum:
            - repo
            - knowledge
            - agentskills
          title: Type
        content:
          type: string
          title: Content
        triggers:
          items:
            type: string
          type: array
          title: Triggers
        source:
          anyOf:
            - type: string
            - type: 'null'
          title: Source
        description:
          anyOf:
            - type: string
            - type: 'null'
          title: Description
        is_agentskills_format:
          type: boolean
          title: Is Agentskills Format
          default: false
      type: object
      required:
        - name
        - type
        - content
      title: SkillInfo
      description: Skill information returned by the API.
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
    ExposedUrl:
      properties:
        name:
          type: string
          title: Name
        url:
          type: string
          title: Url
        port:
          type: integer
          title: Port
      type: object
      required:
        - name
        - url
        - port
      title: ExposedUrl
      description: Represents an exposed URL from the sandbox.

````
