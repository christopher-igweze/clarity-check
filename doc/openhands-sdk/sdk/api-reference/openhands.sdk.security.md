> ## Documentation Index
> Fetch the complete documentation index at: https://docs.openhands.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# openhands.sdk.security

> API reference for openhands.sdk.security module

### class AlwaysConfirm

Bases: [`ConfirmationPolicyBase`](#class-confirmationpolicybase)

#### Methods

#### model\_config = (configuration object)

Configuration for the model, should be a dictionary conforming to \[ConfigDict]\[pydantic.config.ConfigDict].

#### should\_confirm()

Determine if an action with the given risk level requires confirmation.

This method defines the core logic for determining whether user confirmation
is required before executing an action based on its security risk level.

* Parameters:
  `risk` – The security risk level of the action to be evaluated.
  Defaults to SecurityRisk.UNKNOWN if not specified.
* Returns:
  True if the action requires user confirmation before execution,
  False if the action can proceed without confirmation.

### class ConfirmRisky

Bases: [`ConfirmationPolicyBase`](#class-confirmationpolicybase)

#### Properties

* `confirm_unknown`: bool
* `threshold`: [SecurityRisk](#class-securityrisk)

#### Methods

#### model\_config = (configuration object)

Configuration for the model, should be a dictionary conforming to \[ConfigDict]\[pydantic.config.ConfigDict].

#### should\_confirm()

Determine if an action with the given risk level requires confirmation.

This method defines the core logic for determining whether user confirmation
is required before executing an action based on its security risk level.

* Parameters:
  `risk` – The security risk level of the action to be evaluated.
  Defaults to SecurityRisk.UNKNOWN if not specified.
* Returns:
  True if the action requires user confirmation before execution,
  False if the action can proceed without confirmation.

#### classmethod validate\_threshold()

### class ConfirmationPolicyBase

Bases: `DiscriminatedUnionMixin`, `ABC`

#### Methods

#### model\_config = (configuration object)

Configuration for the model, should be a dictionary conforming to \[ConfigDict]\[pydantic.config.ConfigDict].

#### abstractmethod should\_confirm()

Determine if an action with the given risk level requires confirmation.

This method defines the core logic for determining whether user confirmation
is required before executing an action based on its security risk level.

* Parameters:
  `risk` – The security risk level of the action to be evaluated.
  Defaults to SecurityRisk.UNKNOWN if not specified.
* Returns:
  True if the action requires user confirmation before execution,
  False if the action can proceed without confirmation.

### class GraySwanAnalyzer

Bases: [`SecurityAnalyzerBase`](#class-securityanalyzerbase)

Security analyzer using GraySwan’s Cygnal API for AI safety monitoring.

This analyzer sends conversation history and pending actions to the GraySwan
Cygnal API for security analysis. The API returns a violation score which is
mapped to SecurityRisk levels.

Environment Variables:
: GRAYSWAN\_API\_KEY: Required API key for GraySwan authentication
GRAYSWAN\_POLICY\_ID: Optional policy ID for custom GraySwan policy

#### Example

```pycon  theme={null}
>>> from openhands.sdk.security.grayswan import GraySwanAnalyzer
>>> analyzer = GraySwanAnalyzer()
>>> risk = analyzer.security_risk(action_event)
```

#### Properties

* `api_key`: SecretStr | None
* `api_url`: str
* `history_limit`: int
* `low_threshold`: float
* `max_message_chars`: int
* `medium_threshold`: float
* `policy_id`: str | None
* `timeout`: float

#### Methods

#### close()

Clean up resources.

#### model\_config = (configuration object)

Configuration for the model, should be a dictionary conforming to \[ConfigDict]\[pydantic.config.ConfigDict].

#### model\_post\_init()

Initialize the analyzer after model creation.

#### security\_risk()

Analyze action for security risks using GraySwan API.

This method converts the conversation history and the pending action
to OpenAI message format and sends them to the GraySwan Cygnal API
for security analysis.

* Parameters:
  `action` – The ActionEvent to analyze
* Returns:
  SecurityRisk level based on GraySwan analysis

#### set\_events()

Set the events for context when analyzing actions.

* Parameters:
  `events` – Sequence of events to use as context for security analysis

#### validate\_thresholds()

Validate that thresholds are properly ordered.

### class LLMSecurityAnalyzer

Bases: [`SecurityAnalyzerBase`](#class-securityanalyzerbase)

LLM-based security analyzer.

This analyzer respects the security\_risk attribute that can be set by the LLM
when generating actions, similar to OpenHands’ LLMRiskAnalyzer.

It provides a lightweight security analysis approach that leverages the LLM’s
understanding of action context and potential risks.

#### Methods

#### model\_config = (configuration object)

Configuration for the model, should be a dictionary conforming to \[ConfigDict]\[pydantic.config.ConfigDict].

#### security\_risk()

Evaluate security risk based on LLM-provided assessment.

This method checks if the action has a security\_risk attribute set by the LLM
and returns it. The LLM may not always provide this attribute but it defaults to
UNKNOWN if not explicitly set.

### class NeverConfirm

Bases: [`ConfirmationPolicyBase`](#class-confirmationpolicybase)

#### Methods

#### model\_config = (configuration object)

Configuration for the model, should be a dictionary conforming to \[ConfigDict]\[pydantic.config.ConfigDict].

#### should\_confirm()

Determine if an action with the given risk level requires confirmation.

This method defines the core logic for determining whether user confirmation
is required before executing an action based on its security risk level.

* Parameters:
  `risk` – The security risk level of the action to be evaluated.
  Defaults to SecurityRisk.UNKNOWN if not specified.
* Returns:
  True if the action requires user confirmation before execution,
  False if the action can proceed without confirmation.

### class SecurityAnalyzerBase

Bases: `DiscriminatedUnionMixin`, `ABC`

Abstract base class for security analyzers.

Security analyzers evaluate the risk of actions before they are executed
and can influence the conversation flow based on security policies.

This is adapted from OpenHands SecurityAnalyzer but designed to work
with the agent-sdk’s conversation-based architecture.

#### Methods

#### analyze\_event()

Analyze an event for security risks.

This is a convenience method that checks if the event is an action
and calls security\_risk() if it is. Non-action events return None.

* Parameters:
  `event` – The event to analyze
* Returns:
  ActionSecurityRisk if event is an action, None otherwise

#### analyze\_pending\_actions()

Analyze all pending actions in a conversation.

This method gets all unmatched actions from the conversation state
and analyzes each one for security risks.

* Parameters:
  `conversation` – The conversation to analyze
* Returns:
  List of tuples containing (action, risk\_level) for each pending action

#### model\_config = (configuration object)

Configuration for the model, should be a dictionary conforming to \[ConfigDict]\[pydantic.config.ConfigDict].

#### abstractmethod security\_risk()

Evaluate the security risk of an ActionEvent.

This is the core method that analyzes an ActionEvent and returns its risk level.
Implementations should examine the action’s content, context, and potential
impact to determine the appropriate risk level.

* Parameters:
  `action` – The ActionEvent to analyze for security risks
* Returns:
  ActionSecurityRisk enum indicating the risk level

#### should\_require\_confirmation()

Determine if an action should require user confirmation.

This implements the default confirmation logic based on risk level
and confirmation mode settings.

* Parameters:
  * `risk` – The security risk level of the action
  * `confirmation_mode` – Whether confirmation mode is enabled
* Returns:
  True if confirmation is required, False otherwise

### class SecurityRisk

Bases: `str`, `Enum`

Security risk levels for actions.

Based on OpenHands security risk levels but adapted for agent-sdk.
Integer values allow for easy comparison and ordering.

#### Properties

* `description`: str
  Get a human-readable description of the risk level.
* `visualize`: Text
  Return Rich Text representation of this risk level.

#### Methods

#### HIGH = 'HIGH'

#### LOW = 'LOW'

#### MEDIUM = 'MEDIUM'

#### UNKNOWN = 'UNKNOWN'

#### get\_color()

Get the color for displaying this risk level in Rich text.

#### is\_riskier()

Check if this risk level is riskier than another.

Risk levels follow the natural ordering: LOW is less risky than MEDIUM, which is
less risky than HIGH. UNKNOWN is not comparable to any other level.

To make this act like a standard well-ordered domain, we reflexively consider
risk levels to be riskier than themselves. That is:

for risk\_level in list(SecurityRisk):
: assert risk\_level.is\_riskier(risk\_level)

# More concretely:

assert SecurityRisk.HIGH.is\_riskier(SecurityRisk.HIGH)
assert SecurityRisk.MEDIUM.is\_riskier(SecurityRisk.MEDIUM)
assert SecurityRisk.LOW\.is\_riskier(SecurityRisk.LOW)

This can be disabled by setting the reflexive parameter to False.

* Parameters:
  other ([SecurityRisk\*](#class-securityrisk)) – The other risk level to compare against.
  reflexive (bool\*) – Whether the relationship is reflexive.
* Raises:
  `ValueError` – If either risk level is UNKNOWN.
