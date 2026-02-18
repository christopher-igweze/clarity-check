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


# Gemini API: Prompting Quickstart

<a target="_blank" href="https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Prompting.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" height=30/></a>


This notebook contains examples of how to write and run your first prompts with the Gemini API.


```python
%pip install -U -q "google-genai>=1.4.0" # 1.4.0 is needed for chat history
```


### Set up your API key

To run the following cell, your API key must be stored it in a Colab Secret named `GOOGLE_API_KEY`. If you don't already have an API key, or you're not sure how to create a Colab Secret, see the [Authentication](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Authentication.ipynb) quickstart for an example.


```python
from google.colab import userdata
from google import genai

GOOGLE_API_KEY = userdata.get('GOOGLE_API_KEY')
client = genai.Client(api_key=GOOGLE_API_KEY)
```


## Select your model

Now select the model you want to use in this guide, either by selecting one in the list or writing it down. Keep in mind that some models, like the 2.5 ones are thinking models and thus take slightly more time to respond (cf. [thinking notebook](./Get_started_thinking.ipynb) for more details and in particular learn how to switch the thiking off).


```python
MODEL_ID = "gemini-3-flash-preview" # @param ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.5-flash-preview", "gemini-3-pro-preview"] {"allow-input":true, isTemplate: true}
```


## Run your first prompt

Use the `generate_content` method to generate responses to your prompts. You can pass text directly to generate_content, and use the `.text` property to get the text content of the response.


```python
from IPython.display import Markdown

response = client.models.generate_content(
    model=MODEL_ID,
    contents="Give me python code to sort a list"
)

display(Markdown(response.text))
```


## Use images in your prompt

Here you will download an image from a URL and pass that image in our prompt.

First, you download the image and load it with PIL:


```python
!curl -o image.jpg "https://storage.googleapis.com/generativeai-downloads/images/jetpack.jpg"
```


```python
import PIL.Image
img = PIL.Image.open('image.jpg')
img
```


```python
prompt = """
    This image contains a sketch of a potential product along with some notes.
    Given the product sketch, describe the product as thoroughly as possible based on what you
   see in the image, making sure to note all of the product features. Return output in json format:
   {description: description, features: [feature1, feature2, feature3, etc]}
"""
```


Then you can include the image in our prompt by just passing a list of items to `generate_content`.


```python
response = client.models.generate_content(
    model=MODEL_ID,
    contents=[prompt, img],
)

print(response.text)
```


## Have a chat

The Gemini API enables you to have freeform conversations across multiple turns.

The [ChatSession](https://ai.google.dev/api/python/google/generativeai/ChatSession) class will store the conversation history for multi-turn interactions.


```python
chat = client.chats.create(model=MODEL_ID)
```


```python
response = chat.send_message(
    message="In one sentence, explain how a computer works to a young child."
)

print(response.text)
```


You can see the chat history:


```python
messages = chat.get_history()
for message in messages:
  print(f"{message.role}: {message.parts[0].text}")
```


You can keep sending messages to continue the conversation:


```python
response = chat.send_message("Okay, how about a more detailed explanation to a high schooler?")

print(response.text)
```


## Set the temperature


Every prompt you send to the model includes parameters that control how the model generates responses. Use a `types.GenerateContentConfig` to set these, or omit it to use the defaults.

Temperature controls the degree of randomness in token selection. Use higher values for more creative responses, and lower values for more deterministic responses.


Note: Although you can set the `candidate_count` in the generation_config, 2.0 and later models will only return a single candidate at the this time.


```python
from google.genai import types

response = client.models.generate_content(
    model=MODEL_ID,
    contents='Give me a numbered list of cat facts.',
    config=types.GenerateContentConfig(
        max_output_tokens=2000,
        temperature=1.9,
        stop_sequences=['\n6'] # Limit to 5 facts.
    )
)

display(Markdown(response.text))
```


## Learn more

There's lots more to learn!

* For more fun prompts, check out [Market a Jetpack](https://github.com/google-gemini/cookbook/blob/main/examples/Market_a_Jet_Backpack.ipynb).
* Check out the [safety quickstart](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Safety.ipynb) next to learn about the Gemini API's configurable safety settings, and what to do if your prompt is blocked.
* For lots more details on using the Python SDK, check out the [get started notebook](./Get_started.ipynb) or the [documentation's quickstart](https://ai.google.dev/tutorials/python_quickstart).


