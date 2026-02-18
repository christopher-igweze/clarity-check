##### Copyright 2026 Google LLC.


```python
# @title Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
```


# Gemini API: System instructions


<a target="_blank" href="https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/System_instructions.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" height=30/></a>


System instructions allow you to steer the behavior of the model. By setting the system instruction, you are giving the model additional context to understand the task, provide more customized responses, and adhere to guidelines over the user interaction. Product-level behavior can be specified here, separate from prompts provided by end users.

This notebook shows you how to provide a system instruction when generating content.


```python
%pip install -U -q "google-genai>=1.0.0" # Install the Python SDK
```


To run the following cell, your API key must be stored it in a Colab Secret named `GOOGLE_API_KEY`. If you don't already have an API key, or you're not sure how to create a Colab Secret, see the [Authentication](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Authentication.ipynb) quickstart for an example.


```python
from google.colab import userdata
from google import genai
from google.genai import types

client = genai.Client(api_key=userdata.get("GOOGLE_API_KEY"))
```


### Select model
Now select the model you want to use in this guide, either by selecting one in the list or writing it down. Keep in mind that some models, like the 2.5 ones are thinking models and thus take slightly more time to respond (cf. [thinking notebook](./Get_started_thinking.ipynb) for more details and in particular learn how to switch the thiking off).


```python
MODEL_ID = "gemini-3-flash-preview" # @param ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.5-flash-preview", "gemini-3-pro-preview"] {"allow-input":true, isTemplate: true}
```


## Set the system instruction 🐱


```python
system_prompt = "You are a cat. Your name is Neko."
prompt = "Good morning! How are you?"

response = client.models.generate_content(
    model=MODEL_ID,
    contents=prompt,
    config=types.GenerateContentConfig(
        system_instruction=system_prompt
    )
)

print(response.text)
```


## Another example ☠️


```python
system_prompt = "You are a friendly pirate. Speak like one."
prompt = "Good morning! How are you?"

response = client.models.generate_content(
    model=MODEL_ID,
    contents=prompt,
    config=types.GenerateContentConfig(
        system_instruction=system_prompt
    )
)

print(response.text)
```


## Multi-turn conversations

Multi-turn, or chat, conversations also work without any extra arguments once the model is set up.


```python
chat = client.chats.create(
    model=MODEL_ID,
    config=types.GenerateContentConfig(
        system_instruction=system_prompt
    )
)

response = chat.send_message("Good day fine chatbot")
print(response.text)
```


```python
response = chat.send_message("How's your boat doing?")

print(response.text)
```


## Code generation


Below is an example of setting the system instruction when generating code.


```python
system_prompt = """
    You are a coding expert that specializes in front end interfaces. When I describe a component
    of a website I want to build, please return the HTML with any CSS inline. Do not give an
    explanation for this code."
"""
```


```python
prompt = "A flexbox with a large text logo in rainbow colors aligned left and a list of links aligned right."
```


```python
response = client.models.generate_content(
    model=MODEL_ID,
    contents=prompt,
    config=types.GenerateContentConfig(
        system_instruction=system_prompt
    )
)

print(response.text)
```


```python
from IPython.display import HTML

# Render the HTML
HTML(response.text.strip().removeprefix("```html").removesuffix("```"))
```


## Further reading

Please note that system instructions can help guide the model to follow instructions, but they do not fully prevent jailbreaks or leaks. At this time, it is recommended exercising caution around putting any sensitive information in system instructions.

See the systems instruction [documentation](https://ai.google.dev/docs/system_instructions) to learn more.


