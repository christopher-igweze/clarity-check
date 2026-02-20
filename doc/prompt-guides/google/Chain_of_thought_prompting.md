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


# Gemini API: Chain of thought prompting


<a target="_blank" href="https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/prompting/Chain_of_thought_prompting.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" height=30/></a>


Using chain of thought helps the LLM take a logical and arithmetic approach. Instead of outputting the answer immediately, the LLM uses smaller and easier steps to get to the answer.


```python
%pip install -U -q "google-genai>=1.0.0"
```


## Configure your API key

To run the following cell, your API key must be stored it in a Colab Secret named `GOOGLE_API_KEY`. If you don't already have an API key, or you're not sure how to create a Colab Secret, see [Authentication](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Authentication.ipynb) for an example.


```python
from google.colab import userdata
from google import genai

GOOGLE_API_KEY=userdata.get('GOOGLE_API_KEY')
client = genai.Client(api_key=GOOGLE_API_KEY)
```


Additionally, select the model you want to use from the available options below:


```python
MODEL_ID = "gemini-3-flash-preview" # @param ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.5-flash-preview", "gemini-3-pro-preview"] {"allow-input":true, isTemplate: true}
```


## Example

Sometimes LLMs can return non-satisfactory answers. To simulate that behavior, you can implement a phrase like "Return the answer immediately" in your prompt.

Without this, the model sometimes uses chain of thought by itself, but it is inconsistent and does not always result in the correct answer.


```python
from IPython.display import Markdown

prompt = """
  5 people can create 5 donuts every 5 minutes. How much time would it take
  25 people to make 100 donuts? Return the answer immediately.
"""

response = client.models.generate_content(
    model=MODEL_ID,
    contents=prompt,
)
Markdown(response.text)
```


To influence this you can implement chain of thought into your prompt and look at the difference in the response. Note the multiple steps within the prompt.


```python
prompt = """
  Question: 11 factories can make 22 cars per hour. How much time would it take 22 factories to make 88 cars?
  Answer: A factory can make 22/11=2 cars per hour. 22 factories can make 22*2=44 cars per hour. Making 88 cars would take 88/44=2 hours. The answer is 2 hours.
  Question: 5 people can create 5 donuts every 5 minutes. How much time would it take 25 people to make 100 donuts?
  Answer:
"""

response = client.models.generate_content(
    model=MODEL_ID,
    contents=prompt,
)
Markdown(response.text)
```


## Next steps

Be sure to explore other examples of prompting in the repository. Try writing prompts about classifying your own data, or try some of the other prompting techniques such as few-shot prompting.


