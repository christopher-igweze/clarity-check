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


# Gemini API: Few-shot prompting


<a target="_blank" href="https://colab.research.google.com/github/google-gemini/cookbook/blob/main/examples/prompting/Few_shot_prompting.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" height=30/></a>


Some prompts may need a bit more information or require a specific output schema for the LLM to understand and accomplish the requested task. In such cases, providing example questions with answers to the model may greatly increase the quality of the response.


```python
%pip install -U -q "google-genai>=1.0.0"
```


```python
from google import genai
from google.genai import types
```


## Configure your API key

To run the following cell, your API key must be stored it in a Colab Secret named `GOOGLE_API_KEY`. If you don't already have an API key, or you're not sure how to create a Colab Secret, see [Authentication](https://github.com/google-gemini/cookbook/blob/main/quickstarts/Authentication.ipynb) for an example.


```python
from google.colab import userdata
GOOGLE_API_KEY=userdata.get('GOOGLE_API_KEY')

client=genai.Client(api_key=GOOGLE_API_KEY)
```


## Examples

Use Gemini Flash as your model to run through the following examples.


```python
MODEL_ID="gemini-2.5-flash" # @param ["gemini-2.5-flash-lite","gemini-2.5-flash","gemini-2.5-pro","gemini-3-pro-preview"] {"allow-input":true, isTemplate: true}
```


```python
prompt = """
    Sort the animals from biggest to smallest.
    Question: Sort Tiger, Bear, Dog
    Answer: Bear > Tiger > Dog}
    Question: Sort Cat, Elephant, Zebra
    Answer: Elephant > Zebra > Cat}
    Question: Sort Whale, Goldfish, Monkey
    Answer:
"""

respose=client.models.generate_content(
    model=MODEL_ID,
    contents=prompt,
)

print(respose.text)
```


```python
prompt = """
    Extract cities from text, include country they are in.
    USER: I visited Mexico City and Poznan last year
    MODEL: {"Mexico City": "Mexico", "Poznan": "Poland"}
    USER: She wanted to visit Lviv, Monaco and Maputo
    MODEL: {"Minsk": "Ukraine", "Monaco": "Monaco", "Maputo": "Mozambique"}
    USER: I am currently in Austin, but I will be moving to Lisbon soon
    MODEL:
"""

respose=client.models.generate_content(
    model=MODEL_ID,
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type= 'application/json',
    ),
)

print(respose.text)
```


## Next steps

Be sure to explore other examples of prompting in the repository. Try writing prompts about classifying your own data, or try some of the other prompting techniques such as zero-shot prompting.


