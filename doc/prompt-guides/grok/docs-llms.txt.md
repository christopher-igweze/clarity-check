===/overview===
<WideSection>
  # Welcome to xAI Documentation

  <span className="mt-4 block text-sm font-medium text-subtle">
    Build with Grok, the AI model designed to deliver truthful, insightful answers.
  </span>

  <div className="h-10" />

  ***

  ## Get started

  <DocGroupCards />

  <div className="h-5" />

  <ModelsPromotionBanner />

  <div className="h-5" />

  ## Quick start with the API

  <QuickActions />
</WideSection>


===/console/billing===
#### Key Information

# Manage Billing

**Ensure you are in the desired team before changing billing information. When you save the billing information or make a purchase for the first time, the billing information is saved to the team you are in and shared with its members.**

There are two ways of billing:

* **Prepaid credits:** You can pre-purchase credits for your team. Your API consumption will be deducted from remaining prepaid credits available.
* **Monthly invoiced billing:** xAI will generate a monthly invoice based on your API consumption, when you don't have available prepaid credits. xAI will charge your default payment method with the invoiced amount at the end of each month.

**Monthly invoiced billing is disabled by default, with default Invoiced Spending Limit of $0.** This will introduce service disruption when you have consumed all of your prepaid credits. To enable monthly invoiced billing, set a higher than $0 Invoiced Spending Limit at [Billing -> API Credits](https://console.x.ai/team/default/billing) on xAI Console.

Your API consumption will be accounted for in the following order:

* Free/Promotional credits
* Prepaid credits
* Monthly invoiced billing (if Invoiced Spending Limit > $0)

**Any prepaid credits and added payment method will be made available to the team you made the purchase in.**

## Prepaid credits



You can only purchase prepaid credits with Guest Checkout at the moment, due to regulatory
requirements.

This is the most common way to build with xAI API. Before using the API, you purchase a given amount of credits. When you use the API, xAI will track your consumption and deduct the amount from the credits available in your account.

You can add prepaid credits on the xAI Console [Billing -> API Credits](https://console.x.ai/team/default/billing) page.

On the same page, you can view the remaining prepaid credits, enter promo code, as well as any free credits granted by xAI team.

Note: When you make the purchase via bank transfer instead of credit card, the payment will take 2-3 business days to process. You will be granted credits after the process has completed.

## Monthly invoiced billing and invoiced billing limit

Enterprise customers might find it beneficial to enroll in monthly invoiced billing to avoid disruption to their services.

When you have set a **$0 invoiced billing limit** (default), xAI will only use your available prepaid credits. **Your API requests will be automatically rejected once your prepaid credits are depleted.**

If you want to use monthly billing, you can **increase your invoiced billing limit** on [Billing -> API Credits](https://console.x.ai/team/default/billing) page. xAI will attempt to use your prepaid credits first, and the remaining amount will be charged to your default payment method at the end of the month. This ensures you won't experience interruption while consuming the API.

Once your monthly invoiced billing amount has reached the invoiced billing limit, you won't be able to get response until you have raised the invoiced billing limit.

## Saving payment method

When you make a purchase, we automatically keep it on file to make your next purchase easier. You can also manually add payment method on xAI Console [Billing -> Billing details -> Add Payment Information](https://console.x.ai/team/default/billing).

Currently we don't allow user to remove the last payment method on file. There might be changes in the future.

## Invoices

You can view your invoices for prepaid credits and monthly invoices on [Billing -> Invoices](https://console.x.ai/team/default/billing/invoices).

## Billing address and tax information

Enter your billing information carefully, as it will appear on your invoices. We are not able to
regenerate the invoices at the moment.

Your billing address and tax information will be displayed on the invoice. On [Billing -> Payment](https://console.x.ai/team/default/billing), you can also add/change your billing address. When you add/change billing address, you can optionally add your organization's tax information.


===/console/collections===
#### Guides

# Using Collections in Console

This guide walks you through managing collections using the [xAI Console](https://console.x.ai) interface.

## Creating a new collection

Navigate to the **Collections** tab in the [xAI Console](https://console.x.ai). Make sure you are in the correct team.

Click on "Create new collection" to create a new `collection`.

You can choose to enable generate embeddings on document upload or not. We recommend leaving the generate embeddings setting to on.

## Viewing and editing collection configuration

You can view and edit the Collection's configuration by clicking on Edit Collection.

This opens up the following modal where you can view the configuration and make changes.

## Adding a document to the collection

Once you have created the new `collection`, you can click on it in the collections table to view the `documents` included in the `collection`.

Click on "Upload document" to upload a new `document`.

Once the upload has completed, each document is given a File ID. You can view the File ID, Collection ID and hash of the `document` by clicking on the `document` in the documents table.

## Deleting documents and collections

You can delete `documents` and `collections` by clicking on the more button on the right side of the collections or documents table.


===/console/faq/accounts===
#### FAQ

# Accounts

## How do I create an account for the API?

You can create an account at https://accounts.x.ai, or https://console.x.ai. To link your X account automatically to
your xAI account, choose to sign up with X account.

You can create multiple accounts of different sign-in methods with the same email.

When you sign-up with a sign-in method and with the same email, we will prompt you whether you
want to create a new account, or link to the existing account. We will not be able to merge the
content, subscriptions, etc. of different accounts.

## How do I update my xAI account email?

You can visit [xAI Accounts](https://accounts.x.ai). On the Account page, you can update your email.

## How do I add other sign-in methods?

Once you have signed-up for an account, you can add additional sign-in methods by going to [xAI Accounts](https://accounts.x.ai).

## I've forgotten my Multi-Factor Authentication (MFA) method, can you remove it?

You can generate your recovery codes at [xAI Accounts](https://accounts.x.ai) Security page.

We can't remove or reset your MFA method unless you have recovery codes due to security considerations. Please reach out to support@x.ai if you would like to delete the account instead.

## If I already have an account for Grok, can I use the same account for API access?

Yes, the account is shared between Grok and xAI API. You can manage the sign-in details at https://accounts.x.ai.

However, the billing is separate for Grok and xAI API. You can manage your billing for xAI API on [xAI Console](https://console.x.ai).
To manage billing for Grok, visit https://grok.com -> Settings -> Billing, or directly with Apple/Google if you made the
purchase via Apple App Store or Google Play.

## How do I manage my account?

You can visit [xAI Accounts](https://accounts.x.ai) to manage your account.

Please note the xAI account is different from the X account, and xAI cannot assist you with X account issues. Please
contact X via [X Help Center](https://help.x.com/) or Premium Support if you encounters any issues with your X account.

## I received an email of someone logging into my xAI account

xAI will send an email to you when someone logs into your xAI account. The login location is an approximation based on your IP address, which is dependent on your network setup and ISP and might not reflect exactly where the login happened.

If you think the login is not you, please [reset your password](https://accounts.x.ai/request-reset-password) and [clear your login sessions](https://accounts.x.ai/sessions). We also recommend all users to [add a multi-factor authentication method](https://accounts.x.ai/security).

## How do I delete my xAI account?

We are sorry to see you go!

You can visit [xAI Accounts](https://accounts.x.ai/account) to delete your account. You can restore your account after log in again and confirming restoration within 30 days.

You can cancel the deletion within 30 days by logging in again to any xAI websites and follow the prompt to confirm restoring the account.

For privacy requests, please go to: https://privacy.x.ai.


===/console/faq/billing===
#### FAQ

# Billing

## I'm having payment issues with an Indian payment card

Unfortunately we cannot process Indian payment cards for our API service. We are working toward supporting it but you might want to consider using a third-party API in the meantime. As Grok Website and Apps' payments are handled differently, those are not affected.

## When will I be charged?

* Prepaid Credits: If you choose to use prepaid credits, you’ll be charged when you buy them. These credits will be assigned to the team you select during purchase.

* Monthly Invoiced Billing: If you set your [invoiced spending limit](/console/billing#monthly-invoiced-billing-and-invoiced-billing-limit) above $0, any usage beyond your prepaid credits will be charged at the end of the month.

* API Usage: When you make API requests, the cost is calculated immediately. The amount is either deducted from your available prepaid credits or added to your monthly invoice if credits are exhausted.

If you change your [invoiced spending limit](/console/billing#monthly-invoiced-billing-and-invoiced-billing-limit) to be greater than $0, you will be charged at the end of the month for any extra consumption after your prepaid credit on the team has run out.

Your API consumption will be calculated when making the requests, and the corresponding amount will be deducted from your remaining credits or added to your monthly invoice.

Check out [Billing](/console/billing) for more information.

## Can you retroactively generate an invoice with new billing information?

We are unable to retroactively generate an invoice. Please ensure your billing information is correct on [xAI Console](https://console.x.ai) Billing -> Payment.

## Can prepaid API credits be refunded?

Unfortunately, we are not able to offer refunds on any prepaid credit purchase unless in regions required by law. For details, please visit https://x.ai/legal/terms-of-service-enterprise.

### My prompt token consumption from the API is different from the token count I get from xAI Console Tokenizer or tokenize text endpoint

The inference endpoints add pre-defined tokens to help us process the request. Therefore, these tokens would be added to the total prompt token consumption. For more information, see:
[Estimating consumption with tokenizer on xAI Console or Estimating consumption with tokenizer on xAI Console or through API](/developers/rate-limits#estimating-consumption-with-tokenizer-on-xai-console-or-through-api).


===/console/faq/security===
#### FAQ

# Security

## Does xAI train on customers' API requests?

xAI never trains on your API inputs or outputs without your explicit permission.

API requests and responses are temporarily stored on our servers for 30 days in case they need to be audited for potential abuse or misuse. This data is automatically deleted after 30 days.

## Is the xAI API HIPAA compliant?

To inquire about a Business Associate Agreement (BAA), please complete our [BAA Questionnaire](https://forms.gle/YAEdX3XUp6MvdEXW9). A member of our team will review your responses and reach out with next steps.

## Is xAI GDPR and SOC II compliant?

We are SOC 2 Type 2 compliant. Customers with a signed NDA can refer to our [Trust Center](https://trust.x.ai/) for up-to-date information on our certifications and data governance.

## Do you have Audit Logs?

Team admins are able to view an audit log of user interactions. This lists all of the user interactions with our API server. You can view it at [xAI Console -> Audit Log](https://console.x.ai/team/default/audit).

The admin can also search by Event ID, Description or User to filter the results shown. For example, this is to filter by description matching `ListApiKeys`:

You can also view the audit log across a range of dates with the time filter:

## How can I securely manage my API keys?

Treat your xAI API keys as sensitive information, like passwords or credit card details. Do not share keys between teammates to avoid unauthorized access. Store keys securely using environment variables or secret management tools. Avoid committing keys to public repositories or source code.

Rotate keys regularly for added security. If you suspect a compromise, log into the xAI console first. Ensure you are viewing the correct team, as API keys are tied to specific teams. Navigate to the "API Keys" section via the sidebar. In the API Keys table, click the vertical ellipsis (three dots) next to the key. Select "Disable key" to deactivate it temporarily or "Delete key" to remove it permanently. Then, click the "Create API Key" button to generate a new one and update your applications.

xAI partners with GitHub's Secret Scanning program to detect leaked keys. If a leak is found, we disable the key and notify you via email. Monitor your account for unusual activity to stay protected.


===/console/usage===
#### Key Information

# Usage Explorer

Sometimes as a team admin, you might want to monitor the API consumption, either to track spending, or to detect anomalies. xAI Console provides an easy-to-use [Usage Explorer](https://console.x.ai/team/default/usage) for team admins to track API usage across API keys, models, etc.

## Basic usage

[Usage Explorer](https://console.x.ai/team/default/usage) page provides intuitive dropdown menus for you to customize how you want to view the consumptions.

For example, you can view your daily credit consumption with `Granularity: Daily`:

By default, the usage is calculated by cost in USD. You can select Dimension -> Tokens or Dimension -> Billing items to change the dimension to token count or billing item count.

You can also see the usage with grouping. This way, you can easily compare the consumption across groups. In this case, we are trying to compare consumptions across test and production API keys, so we select `Group by: API Key`:

## Filters

The basic usage should suffice if you are only viewing general information. However, you can also use filters to conditionally display information.

The filters dropdown gives you the options to filter by a particular API key, a model, a request IP, a cluster, or the token type.


===/developers/advanced-api-usage/async===
#### Advanced API Usage

# Asynchronous Requests

When working with the xAI API, you may need to process hundreds or even thousands of requests. Sending these requests sequentially can be extremely time-consuming.

To improve efficiency, you can use `AsyncClient` from `xai_sdk` or `AsyncOpenAI` from `openai`, which allows you to send multiple requests concurrently. The example below is a Python script demonstrating how to use `AsyncClient` to batch and process requests asynchronously, significantly reducing the overall execution time:

You can also use our Batch API to queue the requests and fetch them later. Please visit [Batch API](/developers/advanced-api-usage/batch-api) for more information.

## Rate Limits

Adjust the `max_concurrent` param to control the maximum number of parallel requests.

You are unable to concurrently run your requests beyond the rate limits shown in the API console.

```pythonXAI
import asyncio
import os

from xai_sdk import AsyncClient
from xai_sdk.chat import Response, user

async def main():
    client = AsyncClient(
        api_key=os.getenv("XAI_API_KEY"),
        timeout=3600, # Override default timeout with longer timeout for reasoning models
    )

    model = "grok-4-1-fast-reasoning"
    requests = [
        "Tell me a joke",
        "Write a funny haiku",
        "Generate a funny X post",
        "Say something unhinged",
    ]


    # Define a semaphore to limit concurrent requests (e.g., max 2 concurrent requests at a time)
    max_in_flight_requests = 2
    semaphore = asyncio.Semaphore(max_in_flight_requests)

    async def process_request(request) -> Response:
        async with semaphore:
            print(f"Processing request: {request}")
            chat = client.chat.create(model=model, max_tokens=100)
            chat.append(user(request))
            return await chat.sample()

    tasks = []
    for request in requests:
        tasks.append(process_request(request))

    responses = await asyncio.gather(*tasks)
    for i, response in enumerate(responses):
        print(f"Total tokens used for response {i}: {response.usage.total_tokens}")

if __name__ == "__main__":
    asyncio.run(main())
```

```pythonOpenAISDK
import asyncio
import os
import httpx
from asyncio import Semaphore

from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(3600.0) # Override default timeout with longer timeout for reasoning models
)

async def send_request(sem: Semaphore, request: str) -> dict:
    """Send a single request to xAI with semaphore control."""
    # The 'async with sem' ensures only a limited number of requests run at once
    async with sem:
        return await client.chat.completions.create(
            model="grok-4-1-fast-reasoning",
            messages=[{"role": "user", "content": request}]
        )

async def process_requests(requests: list[str], max_concurrent: int = 2) -> list[dict]:
    """Process multiple requests with controlled concurrency."""
    # Create a semaphore that limits how many requests can run at the same time # Think of it like having only 2 "passes" to make requests simultaneously
    sem = Semaphore(max_concurrent)

    # Create a list of tasks (requests) that will run using the semaphore
    tasks = [send_request(sem, request) for request in requests]

    # asyncio.gather runs all tasks in parallel but respects the semaphore limit
    # It waits for all tasks to complete and returns their results
    return await asyncio.gather(*tasks)

async def main() -> None:
    """Main function to handle requests and display responses."""
    requests = [
        "Tell me a joke",
        "Write a funny haiku",
        "Generate a funny X post",
        "Say something unhinged"
    ]

    # This starts processing all asynchronously, but only 2 at a time
    # Instead of waiting for each request to finish before starting the next,
    # we can have 2 requests running at once, making it faster overall
    responses = await process_requests(requests)

    # Print each response in order
    for i, response in enumerate(responses):
        print(f"# Response {i}:")
        print(response.choices[0].message.content)

if __name__ == "__main__":
    asyncio.run(main())
```


===/developers/advanced-api-usage/batch-api===
#### Advanced API Usage

# Batch API

The Batch API lets you process large volumes of requests asynchronously with reduced pricing and higher rate limits. For pricing details, see [Batch API Pricing](/developers/models#batch-api-pricing).

## What is the Batch API?

When you make a standard API call to Grok, you send a request and wait for an immediate response. This approach is perfect for interactive applications like chatbots, real-time assistants, or any use case where users are waiting for a response.

The Batch API takes a different approach. Instead of processing requests immediately, you submit them to a queue where they're processed in the background. You don't get an instant response—instead, you check back later to retrieve your results.

**Key differences from real-time API requests:**

| | Real-time API | Batch API |
|---|---|---|
| **Response time** | Immediate (seconds) | Typically within 24 hours |
| **Cost** | Standard pricing | Reduced pricing ([see details](/developers/models#batch-api-pricing)) |
| **Rate limits** | Per-minute limits apply | Requests don't count towards rate limits |
| **Use case** | Interactive, real-time | Background processing, bulk jobs |

**Processing time:** Most batch requests complete within **24 hours**, though processing time may vary depending on system load and batch size.

You can also create, monitor, and manage batches through the [xAI Console](https://console.x.ai/team/default/batches). The Console provides a visual interface for tracking batch progress and viewing results.

## When to use the Batch API

The Batch API is ideal when you don't need immediate results and want to **reduce your API costs**:

* **Running evaluations and benchmarks** - Test model performance across thousands of prompts
* **Processing large datasets** - Analyze customer feedback, classify support tickets, extract entities
* **Content moderation at scale** - Review backlogs of user-generated content
* **Document summarization** - Process reports, research papers, or legal documents in bulk
* **Data enrichment pipelines** - Add AI-generated insights to database records
* **Scheduled overnight jobs** - Generate daily reports or prepare data for dashboards

## How it works

The Batch API workflow consists of four main steps:

1. **Create a batch** - A batch is a container that groups related requests together
2. **Add requests** - Submit your inference requests to the batch queue
3. **Monitor progress** - Poll the batch status to track completion
4. **Retrieve results** - Fetch responses for all processed requests

Let's walk through each step.

## Step 1: Create a batch

A batch acts as a container for your requests. Think of it as a folder that groups related work together—you might create separate batches for different datasets, experiments, or job types.

When you create a batch, you receive a `batch_id` that you'll use to add requests and retrieve results.

```bash
curl -X POST https://api.x.ai/v1/batches \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer $XAI_API_KEY" \\
  -d '{
    "name": "customer_feedback_analysis"
  }'
```

```pythonXAI
from xai_sdk import Client

client = Client()

# Create a batch with a descriptive name
batch = client.batch.create(batch_name="customer_feedback_analysis")
print(f"Created batch: {batch.batch_id}")

# Store the batch_id for later use
batch_id = batch.batch_id
```

## Step 2: Add requests to the batch

With your batch created, you can now add requests to it. Each request is a standard chat completion that will be processed asynchronously.

**With the xAI SDK, adding batch requests is simple:** create `Chat` objects the same way you would for regular chat completions, then pass them as a list. You don't need to construct JSONL files or deal with complex request formats. Just use the familiar `chat.create()` and `chat.append()` pattern you already know.

**Important:** Assign a unique `batch_request_id` to each request. This ID lets you match results back to their original requests, which becomes important when you're processing hundreds or thousands of items. If you don't provide an ID, we generate a UUID for you. Using your own IDs is useful for idempotency (ensuring a request is only processed once) and for linking batch requests to records in your own system.

```pythonXAI
from xai_sdk import Client
from xai_sdk.chat import system, user

client = Client()

# Sample data to process
feedback_items = [
    {"id": "feedback_001", "text": "The product exceeded my expectations!"},
    {"id": "feedback_002", "text": "Shipping took way too long."},
    {"id": "feedback_003", "text": "It works as described, nothing special."},
]

# Build batch requests using familiar Chat objects
batch_requests = []
for item in feedback_items:
    # Create a Chat exactly like you would for a regular request
    chat = client.chat.create(
        model="grok-4-1-fast-reasoning",
        batch_request_id=item["id"],  # Add an ID to track this request
    )
    # Append messages the same way as always
    chat.append(system("Classify the sentiment as positive, negative, or neutral."))
    chat.append(user(item["text"]))
    
    batch_requests.append(chat)

# Pass the list of Chat objects to the batch
client.batch.add(batch_id=batch.batch_id, batch_requests=batch_requests)
print(f"Added {len(batch_requests)} requests to batch")
```

```bash
curl -X POST https://api.x.ai/v1/batches/{batch_id}/requests \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer $XAI_API_KEY" \\
  -d '{
    "batch_requests": [
      {
        "batch_request_id": "feedback_001",
        "batch_request": {
          "chat_get_completion": {
            "messages": [
              {"role": "system", "content": "Classify the sentiment as positive, negative, or neutral."},
              {"role": "user", "content": "The product exceeded my expectations!"}
            ],
            "model": "grok-4-1-fast-reasoning"
          }
        }
      },
      {
        "batch_request_id": "feedback_002",
        "batch_request": {
          "chat_get_completion": {
            "messages": [
              {"role": "system", "content": "Classify the sentiment as positive, negative, or neutral."},
              {"role": "user", "content": "Shipping took way too long."}
            ],
            "model": "grok-4-1-fast-reasoning"
          }
        }
      }
    ]
  }'
```

## Step 3: Monitor batch progress

After adding requests, they begin processing in the background. Since batch processing is asynchronous, you need to poll the batch status to know when results are ready.

The batch state includes counters for pending, successful, and failed requests. Poll periodically until `num_pending` reaches zero, which indicates all requests have been processed (either successfully or with errors).

```bash
# Check batch status
curl https://api.x.ai/v1/batches/{batch_id} \\
  -H "Authorization: Bearer $XAI_API_KEY"

# Response includes state with request counts:
# {
#   "state": {
#     "num_requests": 100,
#     "num_pending": 25,
#     "num_success": 70,
#     "num_error": 5
#   }
# }
```

```pythonXAI
import time
from xai_sdk import Client

client = Client()

# Poll until all requests are processed
print("Waiting for batch to complete...")
while True:
    batch = client.batch.get(batch_id=batch.batch_id)
    
    pending = batch.state.num_pending
    completed = batch.state.num_success + batch.state.num_error
    total = batch.state.num_requests
    
    print(f"Progress: {completed}/{total} complete, {pending} pending")
    
    if pending == 0:
        print("Batch processing complete!")
        break
    
    # Wait before polling again (avoid hammering the API)
    time.sleep(5)
```

### Understanding batch states

The Batch API tracks state at two levels: the **batch level** and the **individual request level**.

**Batch-level state** shows aggregate progress across all requests in a given batch,
accessible through the `batch.state` object returned by the `client.batch.get()` method:

| Counter | Description |
|---|---|
| `num_requests` | Total number of requests added to the batch |
| `num_pending` | Requests waiting to be processed |
| `num_success` | Requests that completed successfully |
| `num_error` | Requests that failed with an error |
| `num_cancelled` | Requests that were cancelled |

When `num_pending` reaches zero, all requests have been processed (either successfully, with errors, or cancelled).

**Individual request states** describe where each request is in its lifecycle, accessible through the `batch_request_metadata` object returned by the `client.batch.list_batch_requests()` [method](#check-individual-request-status):

| State | Description |
|---|---|
| `pending` | Request is queued and waiting to be processed |
| `succeeded` | Request completed successfully, result is available |
| `failed` | Request encountered an error during processing |
| `cancelled` | Request was cancelled (e.g., when the batch was cancelled before this request was processed) |

**Batch lifecycle:** A batch can also be cancelled or expire. [If you cancel a batch](#cancel-a-batch), pending requests won't be processed, but already-completed results remain available. Batches have an expiration time after which results are no longer accessible—check the `expires_at` field when retrieving batch details.

## Step 4: Retrieve results

You can retrieve results at any time, even before the entire batch completes. Results are available as soon as individual requests finish processing, so you can start consuming completed results while other requests are still in progress.

Each result is linked to its original request via the `batch_request_id` you assigned earlier. The `result.response` object is the same SDK `Response` you'd get from a regular chat completion, with all the familiar fields: `.content`, `.usage`, `.finish_reason`, and more.

The SDK provides convenient `.succeeded` and `.failed` properties to separate successful responses from errors.

**Pagination:** Results are returned in pages. Use the `limit` parameter to control page size and `pagination_token` to fetch subsequent pages. When `pagination_token` is `None`, you've reached the end.

```pythonXAI
from xai_sdk import Client

client = Client()

# Paginate through all results
all_succeeded = []
all_failed = []
pagination_token = None

while True:
    # Fetch a page of results (limit controls page size)
    page = client.batch.list_batch_results(
        batch_id=batch.batch_id,
        limit=100,
        pagination_token=pagination_token,
    )
    
    # Collect results from this page
    all_succeeded.extend(page.succeeded)
    all_failed.extend(page.failed)
    
    # Check if there are more pages
    if page.pagination_token is None:
        break
    pagination_token = page.pagination_token

# Process all results
print(f"Successfully processed: {len(all_succeeded)} requests")
for result in all_succeeded:
    # Access the full Response object
    print(f"[{result.batch_request_id}] {result.response.content}")
    print(f"  Tokens used: {result.response.usage.total_tokens}")

if all_failed:
    print(f"\\nFailed: {len(all_failed)} requests")
    for result in all_failed:
        print(f"[{result.batch_request_id}] Error: {result.error_message}")
```

```bash
# Fetch first page
curl "https://api.x.ai/v1/batches/{batch_id}/results?page_size=100" \\
  -H "Authorization: Bearer $XAI_API_KEY"

# Use pagination_token from response to fetch next page
curl "https://api.x.ai/v1/batches/{batch_id}/results?page_size=100&pagination_token={token}" \\
  -H "Authorization: Bearer $XAI_API_KEY"
```

## Additional operations

Beyond the core workflow, the Batch API provides additional operations for managing your batches.

### Cancel a batch

You can cancel a batch before all requests complete. Already-processed requests remain available in the results, but pending requests will not be processed. You cannot add more requests to a cancelled batch.

```bash
curl -X POST https://api.x.ai/v1/batches/{batch_id}:cancel \\
  -H "Authorization: Bearer $XAI_API_KEY"
```

```pythonXAI
from xai_sdk import Client

client = Client()

# Cancel processing
cancelled_batch = client.batch.cancel(batch_id=batch.batch_id)
print(f"Cancelled batch: {cancelled_batch.batch_id}")
print(f"Completed before cancellation: {cancelled_batch.state.num_success} requests")
```

### List all batches

View all batches belonging to your team. Batches are retained until they expire (check the `expires_at` field). This endpoint supports the same `limit` and `pagination_token` parameters for paginating through large lists.

```bash
curl "https://api.x.ai/v1/batches?page_size=20" \\
  -H "Authorization: Bearer $XAI_API_KEY"
```

```pythonXAI
from xai_sdk import Client

client = Client()

# List recent batches
response = client.batch.list(limit=20)

for batch in response.batches:
    status = "complete" if batch.state.num_pending == 0 else "processing"
    print(f"{batch.name} ({batch.batch_id}): {status}")
```

### Check individual request status

For detailed tracking, you can inspect the metadata for each request in a batch. This shows the status, timing, and other details for individual requests. This endpoint supports the same `limit` and `pagination_token` parameters for paginating through large batches.

```bash
curl "https://api.x.ai/v1/batches/{batch_id}/requests?page_size=50" \\
  -H "Authorization: Bearer $XAI_API_KEY"
```

```pythonXAI
from xai_sdk import Client

client = Client()

# Get metadata for individual requests
metadata = client.batch.list_batch_requests(batch_id=batch.batch_id)

for request in metadata.batch_request_metadata:
    print(f"Request {request.batch_request_id}: {request.state}")
```

### Track costs

Each batch tracks the total processing cost. Access the cost breakdown after processing to understand your spending. For pricing details, see [Batch API Pricing on the Models and Pricing page](/developers/models#batch-api-pricing).

```pythonXAI
from xai_sdk import Client

client = Client()

# Get batch with cost information
batch = client.batch.get(batch_id=batch.batch_id)

# Cost is returned in ticks (1e-10 USD) for precision
total_cost_usd = batch.cost_breakdown.total_cost_usd_ticks / 1e10
print("Total cost: $%.4f" % total_cost_usd)
```

## Complete example

This end-to-end example demonstrates a realistic batch workflow: analyzing customer feedback at scale. It creates a batch, submits feedback items for sentiment analysis, waits for processing, and outputs the results. For simplicity, this example doesn't paginate results—see [Step 4](#step-4-retrieve-results) for pagination when processing larger batches.

```pythonXAI
import time
from xai_sdk import Client
from xai_sdk.chat import system, user

client = Client()

# Sample dataset: customer feedback to analyze
feedback_data = [
    {"id": "fb_001", "text": "Absolutely love this product! Best purchase ever."},
    {"id": "fb_002", "text": "Delivery was late and the packaging was damaged."},
    {"id": "fb_003", "text": "Works fine, nothing special to report."},
    {"id": "fb_004", "text": "Customer support was incredibly helpful!"},
    {"id": "fb_005", "text": "The app keeps crashing on my phone."},
]

# Step 1: Create a batch
print("Creating batch...")
batch = client.batch.create(batch_name="feedback_sentiment_analysis")
print(f"Batch created: {batch.batch_id}")

# Step 2: Build and add requests
print("\\nAdding requests...")
batch_requests = []
for item in feedback_data:
    chat = client.chat.create(
        model="grok-4-1-fast-reasoning",
        batch_request_id=item["id"],
    )
    chat.append(system(
        "Analyze the sentiment of the customer feedback. "
        "Respond with exactly one word: positive, negative, or neutral."
    ))
    chat.append(user(item["text"]))
    batch_requests.append(chat)

client.batch.add(batch_id=batch.batch_id, batch_requests=batch_requests)
print(f"Added {len(batch_requests)} requests")

# Step 3: Wait for completion
print("\\nProcessing...")
while True:
    batch = client.batch.get(batch_id=batch.batch_id)
    pending = batch.state.num_pending
    completed = batch.state.num_success + batch.state.num_error
    
    print(f"  {completed}/{batch.state.num_requests} complete")
    
    if pending == 0:
        break
    time.sleep(2)

# Step 4: Retrieve and display results
print("\\n--- Results ---")
results = client.batch.list_batch_results(batch_id=batch.batch_id)

# Create a lookup for original feedback text
feedback_lookup = {item["id"]: item["text"] for item in feedback_data}

for result in results.succeeded:
    original_text = feedback_lookup.get(result.batch_request_id, "")
    sentiment = result.response.content.strip().lower()
    print(f"[{sentiment.upper()}] {original_text[:50]}...")

# Report any failures
if results.failed:
    print("\\n--- Errors ---")
    for result in results.failed:
        print(f"[{result.batch_request_id}] {result.error_message}")

# Display cost
cost_usd = batch.cost_breakdown.total_cost_usd_ticks / 1e10
print("\\nTotal cost: $%.4f" % cost_usd)
```

## Limitations

**Batches**

* A team can have an **unlimited** number of batches.
* Maximum batch creation rate: **1** batch creation per second per team.

**Batch Requests**

* A batch can contain an **unlimited** number of requests in theory, but extremely large batches (>1,000,000 requests) may be throttled for processing stability.
* Each individual request that can be added to a batch has a maximum payload size of **25MB**.
* A team can send up to **100** add-batch-requests API calls every **30 seconds** (this is a rolling limit shared across all batches in the team).

**Unsupported Features**

* **Agentic requests** using [server-side tools](/developers/guides/tools/overview) (such as web search, code execution, or MCP tools) are not supported in batch requests.
* **Client-side tools** (function calling) are not supported in batch requests.

## Related

* [API Reference: Batch endpoints](/developers/rest-api-reference/inference/batches#create-a-new-batch)
* [gRPC Reference: Batch management](/developers/grpc-api-reference#batch-management)
* [Models and pricing — Batch API Pricing](/developers/models#batch-api-pricing)
* [xAI Python SDK](https://github.com/xai-org/xai-sdk-python)


===/developers/advanced-api-usage/deferred-chat-completions===
#### Advanced API Usage

# Deferred Chat Completions

Deferred Chat Completions are currently available only via REST requests or xAI SDK.

Deferred Chat Completions allow you to create a chat completion, get a `response_id`, and retrieve the response at a later time. The result would be available to be requested exactly once within 24 hours, after which it would be discarded.

Your deferred completion rate limit is the same as your chat completions rate limit. To view your rate limit, please visit [xAI Console](https://console.x.ai).

After sending the request to the xAI API, the chat completion result will be available at `https://api.x.ai/v1/chat/deferred-completion/{request_id}`. The response body will contain `{'request_id': 'f15c114e-f47d-40ca-8d5c-8c23d656eeb6'}`, and the `request_id` value can be inserted into the `deferred-completion` endpoint path. Then, we send this GET request to retrieve the deferred completion result.

When the completion result is not ready, the request will return `202 Accepted` with an empty response body.

You can access the model's raw thinking trace via the `message.reasoning_content` of the chat completion response.



## Example

A code example is provided below, where we retry retrieving the result until it has been processed:

```pythonXAI
import os
from datetime import timedelta

from xai_sdk import Client
from xai_sdk.chat import user, system

client = Client(api_key=os.getenv('XAI_API_KEY'))

chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    messages=[system("You are Zaphod Beeblebrox.")]
)
chat.append(user("126/3=?"))

# Poll the result every 10 seconds for a maximum of 10 minutes

response = chat.defer(
    timeout=timedelta(minutes=10), interval=timedelta(seconds=10)
)

# Print the result when it is ready

print(response.content)
```

```pythonRequests
import json
import os
import requests

from tenacity import retry, wait_exponential

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}"
}

payload = {
    "messages": [
        {"role": "system", "content": "You are Zaphod Beeblebrox."},
        {"role": "user", "content": "126/3=?"}
    ],
    "model": "grok-4-1-fast-reasoning",
    "deferred": True
}

response = requests.post(
    "https://api.x.ai/v1/chat/completions",
    headers=headers,
    json=payload
)
request_id = response.json()["request_id"]
print(f"Request ID: {request_id}")

@retry(wait=wait_exponential(multiplier=1, min=1, max=60),)
def get_deferred_completion():
    response = requests.get(f"https://api.x.ai/v1/chat/deferred-completion/{request_id}", headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 202:
        raise Exception("Response not ready yet")
    else:
        raise Exception(f"{response.status_code} Error: {response.text}")

completion_data = get_deferred_completion()
print(json.dumps(completion_data, indent=4))
```

```javascriptWithoutSDK
const axios = require('axios');
const retry = require('retry');

const headers = {
    'Content-Type': 'application/json',
    'Authorization': \`Bearer \${process.env.XAI_API_KEY}\`
};

const payload = {
    messages: [
        { role: 'system', content: 'You are Zaphod Beeblebrox.' },
        { role: 'user', content: '126/3=?' }
    ],
    model: 'grok-4-1-fast-reasoning',
    deferred: true
};

async function main() {
    const requestId = (await axios.post('https://api.x.ai/v1/chat/completions', payload, { headers })).data.request_id;
    console.log(\`Request ID: \${requestId}\`);

    const operation = retry.operation({
        minTimeout: 1000,
        maxTimeout: 60000,
        factor: 2
    });

    const completion = await new Promise((resolve, reject) => {
        operation.attempt(async () => {
            const res = await axios.get(\`https://api.x.ai/v1/chat/deferred-completion/\${requestId}\`, { headers });
            if (res.status === 200) resolve(res.data);
            else if (res.status === 202) operation.retry(new Error('Not ready'));
            else reject(new Error(\`\${res.status}: \${res.statusText}\`));
        });
    });

    console.log(JSON.stringify(completion, null, 4));
}

main().catch(console.error);
```

```bash
RESPONSE=$(curl -s https://api.x.ai/v1/chat/completions \\
-H "Content-Type: application/json" \\
-H "Authorization: Bearer $XAI_API_KEY" \\
-d '{
    "messages": [
        {"role": "system", "content": "You are Zaphod Beeblebrox."},
        {"role": "user", "content": "126/3=?"}
    ],
    "model": "grok-4-1-fast-reasoning",
    "deferred": true
}')

REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id')
echo "Request ID: $REQUEST_ID"

sleep 10

curl -s https://api.x.ai/v1/chat/deferred-completion/$REQUEST_ID \\
-H "Authorization: Bearer $XAI_API_KEY"
```

The response body will be the same as what you would expect with non-deferred chat completions:

```json
{
  "id": "3f4ddfca-b997-3bd4-80d4-8112278a1508",
  "object": "chat.completion",
  "created": 1752077400,
  "model": "grok-4-1-fast-reasoning",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Whoa, hold onto your improbability drives, kid! This is Zaphod Beeblebrox here, the two-headed, three-armed ex-President of the Galaxy, and you're asking me about 126 divided by 3? Pfft, that's kid stuff for a guy who's stolen starships and outwitted the universe itself.\n\nBut get this\u2014126 slashed by 3 equals... **42**! Yeah, that's right, the Ultimate Answer to Life, the Universe, and Everything! Deep Thought didn't compute that for seven and a half million years just for fun, you know. My left head's grinning like a Vogon poet on happy pills, and my right one's already planning a party. If you need more cosmic math or a lift on the Heart of Gold, just holler. Zaphod out! \ud83d\ude80",
        "refusal": null
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 26,
    "completion_tokens": 168,
    "total_tokens": 498,
    "prompt_tokens_details": {
      "text_tokens": 26,
      "audio_tokens": 0,
      "image_tokens": 0,
      "cached_tokens": 4
    },
    "completion_tokens_details": {
      "reasoning_tokens": 304,
      "audio_tokens": 0,
      "accepted_prediction_tokens": 0,
      "rejected_prediction_tokens": 0
    },
    "num_sources_used": 0
  },
  "system_fingerprint": "fp_44e53da025"
}
```

For more details, refer to [Chat completions](/developers/rest-api-reference/inference/chat#chat-completions) and [Get deferred chat completions](/developers/rest-api-reference/inference/chat#get-deferred-chat-completions) in our REST API Reference.


===/developers/advanced-api-usage/fingerprint===
#### Advanced API Usage

# Fingerprint

For each request to the xAI API, the response body will include a unique `system_fingerprint` value. This fingerprint serves as an identifier for the current state of the backend system's configuration.

Example:

```bash
curl https://api.x.ai/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
        "messages": [
          {
            "role": "system",
            "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."
          },
          {
            "role": "user",
            "content": "What is the meaning of life, the universe, and everything?"
          }
        ],
        "model": "grok-4-1-fast-reasoning",
        "stream": false,
        "temperature": 0
      }'
```

Response:

```json
{..., "system_fingerprint":"fp_6ca29cf396"}
```

You can automate your system to keep track of the `system_fingerprint` along with token consumption and other metrics.

## Usage of fingerprint

* **Monitoring System Changes:** The system fingerprint acts as a version control for the backend configuration. If any part of the backend system—such as model parameters, server settings, or even the underlying infrastructure—changes, the fingerprint will also change. This allows developers to track when and how the system has evolved over time. This is crucial for debugging, performance optimization, and ensuring consistency in API responses.
* **Security and Integrity:** The fingerprint can be used to ensure the integrity of the response. If a response's fingerprint matches the expected one based on a recent system configuration, it helps in verifying that the data hasn't been tampered with during transmission or that the service hasn't been compromised. **The fingerprint will change over time and it is expected.**
* **Compliance and Auditing:** For regulated environments, this fingerprint can serve as part of an audit trail, showing when specific configurations were in use for compliance purposes.


===/developers/advanced-api-usage/grok-code-prompt-engineering===
#### Advanced API Usage

# Prompt Engineering for Grok Code Fast 1

## For developers using agentic coding tools

`grok-code-fast-1` is a lightweight agentic model which is designed to excel as your pair-programmer inside most common coding tools. To optimize your experience, we present a few guidelines so that you can fly through your day-to-day coding tasks.

### Provide the necessary context

Most coding tools will gather the necessary context for you on their own. However, it is oftentimes better to be specific by selecting the specific code you want to use as context. This allows `grok-code-fast-1` to focus on your task and prevent unnecessary deviations. Try to specify relevant file paths, project structures, or dependencies and avoid providing irrelevant context.

* No-context prompt to avoid
  > Make error handling better
* Good prompt with specified context
  > My error codes are defined in @errors.ts, can you use that as reference to add proper error handling and error codes to @sql.ts where I am making queries

### Set explicit goals and requirements

Clearly define your goals and the specific problem you want `grok-code-fast-1` to solve. Detailed and concrete queries can lead to better performance. Try to avoid vague or underspecified prompts, as they can result in suboptimal results.

* Vague prompt to avoid
  > Create a food tracker
* Good, detailed prompt
  > Create a food tracker which shows the breakdown of calorie consumption per day divided by different nutrients when I enter a food item. Make it such that I can see an overview as well as get high level trends.

### Continually refine your prompts

`grok-code-fast-1` is a highly efficient model, delivering up to 4x the speed and 1/10th the cost of other leading agentic models. This enables you to test your complex ideas at an unprecedented speed and affordability. Even if the initial output isn’t perfect, we strongly suggest taking advantage of the uniquely rapid and cost-effective iteration to refine your query—using the suggestions above (e.g., adding more context) or by referencing the specific failures from the first attempt.

* Good prompt example with refinement
  > The previous approach didn’t consider the IO heavy process which can block the main thread, we might want to run it in its own threadloop such that it does not block the event loop instead of just using the async lib version

### Assign agentic tasks

We encourage users to try `grok-code-fast-1` for agentic-style tasks rather than one-shot queries. Our Grok 4 models are more suited for one-shot Q\&A while `grok-code-fast-1` is your ideal companion for navigating large mountains of code with tools to deliver you precise answers.

A good way to think about this is:

* `grok-code-fast-1` is great at working quickly and tirelessly to find you the answer or implement the required change.
* Grok 4 is best for diving deep into complex concepts and tough debugging when you provide all the necessary context upfront.

## For developers building coding agents via the xAI API

With `grok-code-fast-1`, we wanted to bring an agentic coding model into the hands of developers. Outside of our launch partners, we welcome all developers to try out `grok-code-fast-1` in tool-call-heavy domains as the fast speed and low cost makes it both efficient and affordable for using many tools to figure out the correct answer.

As mentioned in the blog post, `grok-code-fast-1` is a reasoning model with interleaved tool-calling during its thinking. We also send summarized thinking via the OpenAI-compatible API for better UX support. More API details can be found at /developers/tools/function-calling.

### Reasoning content

`grok-code-fast-1` is a reasoning model, and we expose its thinking trace via `chunk.choices[0].delta.reasoning_content`. Please note that the thinking traces are only accessible when using streaming mode.

### Use native tool calling

`grok-code-fast-1` offers first-party support for native tool-calling and was specifically designed with native tool-calling in mind. We encourage you to use it instead of XML-based tool-call outputs, which may hurt performance.

### Give a detailed system prompt

Be thorough and give many details in your system prompt. A well-written system prompt which describes the task, expectations, and edge-cases the model should be aware of can make a night-and-day difference. For more inspiration, refer to the User Best Practices above.

### Introduce context to the model

`grok-code-fast-1` is accustomed to seeing a lot of context in the initial user prompt. We recommend developers to use XML tags or Markdown-formatted content to mark various sections of the context and to add clarity to certain sections. Descriptive Markdown headings/XML tags and their corresponding definitions will allow `grok-code-fast-1` to use the context more effectively.

### Optimize for cache hits

Our cache hits are a big contributor to `grok-code-fast-1`’s fast inference speed. In agentic tasks where the model uses multiple tools in sequence, most of the prefix remains the same and thus is automatically retrieved from the cache to speed up inference. We recommend against changing or augmenting the prompt history, as that could lead to cache misses and therefore significantly slower inference speeds.


===/developers/advanced-api-usage===
#### Advanced API Usage

# Advanced API Usage

Advanced guides for scaling, optimizing, and integrating xAI APIs.

## In this section

* [Batch API](/developers/advanced-api-usage/batch-api)
* [Deferred Completions](/developers/advanced-api-usage/deferred-chat-completions)
* [Fingerprint](/developers/advanced-api-usage/fingerprint)
* [Async Requests](/developers/advanced-api-usage/async)
* [Use with Code Editors](/developers/advanced-api-usage/use-with-code-editors)
* [Prompt Engineering for Grok Code](/developers/advanced-api-usage/grok-code-prompt-engineering)


===/developers/advanced-api-usage/use-with-code-editors===
# Use with Code Editors

You can use Grok with coding assistant plugins to help you code. Our Code models are specifically optimized for this task, which would provide you a smoother experience.

For pricing and limits of Code models, check out [Models and Pricing](/developers/models).

## Using Grok Code models with Cline

To use Grok with Cline, first download Cline from VSCode marketplace. Once you have installed Cline in VSCode, open Cline.

Click on "Use your own API key".

Then, you can save your xAI API key to Cline.

After setting up your xAI API key with Cline, you can set to use a coding model. Go to Cline settings -> API Configuration and you can choose `grok-code-fast-1` as the model.

## Using Grok Code models with Cursor

You can also use Grok with Cursor to help you code.

After installing Cursor, head to Cursor Settings -> Models.

Open API Keys settings, enter your xAI API key and set Override OpenAI Base URL to `https://api.x.ai/v1`

In the "Add or search model" input box, enter a coding model such as `grok-code-fast-1`. Then click on "Add Custom Model".

## Other code assistants supporting Grok Code models

Besides Cline and Cursor, you can also use our code model with [GitHub Copilot](https://github.com/features/copilot), [opencode](https://opencode.ai/), [Kilo Code](https://kilocode.ai/), [Roo Code](https://roocode.com/) and [Windsurf](https://windsurf.com/).


===/developers/community===
#### Resources

# Community Integrations

Grok is also accessible via your favorite community integrations, enabling you to connect Grok to other parts of your system easily.

## Third-party SDK/frameworks

### LiteLLM

LiteLLM provides a simple SDK or proxy server for calling different LLM providers. If you're using LiteLLM, integrating xAI as your provider is straightforward—just swap out the model name and API key to xAI's Grok model in your configuration.

For latest information and more examples, visit [LiteLLM xAI Provider Documentation](https://docs.litellm.ai/docs/providers/xai).

As a quick start, you can use LiteLLM in the following fashion:

```pythonWithoutSDK
from litellm import completion
import os

os.environ['XAI_API_KEY'] = ""
response = completion(
model="xai/grok-4-1-fast-reasoning",
messages=[
{
"role": "user",
"content": "What's the weather like in Boston today in Fahrenheit?",
}
],
max_tokens=10,
response_format={ "type": "json_object" },
seed=123,
stop=["\n\n"],
temperature=0.2,
top_p=0.9,
tool_choice="auto",
tools=[],
user="user",
)
print(response)
```

### Vercel AI SDK

[Vercel's AI SDK](https://sdk.vercel.ai/) supports a [xAI Grok Provider](https://sdk.vercel.ai/providers/ai-sdk-providers/xai) for integrating with xAI API.

By default it uses your xAI API key in `XAI_API_KEY` variable.

To generate text use the `generateText` function:

```javascriptAISDK
import { xai } from '@ai-sdk/xai';
import { generateText } from 'ai';

const { text } = await generateText({
model: xai.responses('grok-4-1-fast-reasoning'),
prompt: 'Write a vegetarian lasagna recipe for 4 people.',
});
```

You can also customize the setup like the following:

```javascriptAISDK
import { createXai } from '@ai-sdk/xai';

const xai = createXai({
apiKey: 'your-api-key',
});
```

You can also generate images with the `generateImage` function:

```javascriptAISDK
import { xai } from '@ai-sdk/xai';
import { experimental_generateImage as generateImage } from 'ai';

const { image } = await generateImage({
model: xai.image('grok-imagine-image'),
prompt: 'A cat in a tree',
});
```

## Coding assistants

### Continue

You can use Continue extension in VSCode or JetBrains with xAI's models.

To start using xAI models with Continue, you can add the following in Continue's config file `~/.continue/config.json`(MacOS and Linux)/`%USERPROFILE%\.continue\config.json`(Windows).

```json
 "models": [
   {
     "title": "grok-4-1-fast-reasoning",
     "provider": "xAI",
     "model": "grok-4-1-fast-reasoning",
     "apiKey": "[XAI_API_KEY]"
   }
 ]
```

Visit [Continue's Documentation](https://docs.continue.dev/chat/model-setup#grok-2-from-xai) for more details.


===/developers/debugging===
#### Getting Started

# Debugging Errors

When you send a request, you would normally get a `200 OK` response from the server with the expected response body.
If there has been an error with your request, or error with our service, the API endpoint will typically return an error code with error message.

If there is an ongoing service disruption, you can visit
[https://status.x.ai](https://status.x.ai) for the latest updates. The status is also available
via RSS at [https://status.x.ai/feed.xml](https://status.x.ai/feed.xml).

The service status is also indicated in the navigation bar of this site.

Most of the errors will be accompanied by an error message that is self-explanatory. For typical status codes of each endpoint, visit [API Reference](/developers/rest-api-reference) or view our [OpenAPI Document](/openapi.json).

## Status Codes

Here is a list of potential errors and statuses arranged by status codes.

### 4XX Status Codes

| Status Code                    | Endpoints                              | Cause                                                                                                                                                                       | Solution                                                                                                                                         |
| ------------------------------ | -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| 400Bad Request            | All Endpoints                          | - A `POST` method request body specified an invalid argument, or a `GET` method with dynamic route has an invalid param in the URL.- An incorrect API key is supplied. | - Please check your request body or request URL.                                                                                                 |
| 401Unauthorized           | All Endpoints                          | - No authorization header or an invalid authorization token is provided.                                                                                                    | - Supply an `Authorization: Bearer Token <XAI_API_KEY>` in the request header. You can get a new API key on [xAI Console](https://console.x.ai). |
| 403Forbidden              | All Endpoints                          | - Your API key/team doesn't have permission to perform the action.- Your API key/team is blocked.                                                                     | - Ask your team admin for permission.                                                                                                            |
| 404Not Found              | All Endpoints                          | - A model specified in a `POST` method request body is not found.- Trying to reach an invalid endpoint URL. (Misspelled URL)                                           | - Check your request body and endpoint URL with our [API Reference](/developers/rest-api-reference).                                                              |
| 405Method Not Allowed     | All Endpoints                          | - The request method is not allowed. For example, sending a `POST` request to an endpoint supporting only `GET`.                                                            | - Check your request method with our [API Reference](/developers/rest-api-reference).                                                                             |
| 415Unsupported Media Type | All Endpoints Supporting `POST` Method | - An empty request body in `POST` requests.- Not specifying `Content-Type: application/json` header.                                                                  | - Add a valid request body. - Ensure `Content-Type: application/json` header is present in the request header.                             |
| 422Unprocessable Entity   | All Endpoints Supporting `POST` Method | - An invalid format for a field in the `POST` request body.                                                                                                                 | - Check your request body is valid. You can find more information from [API Reference](/developers/rest-api-reference).                                           |
| 429Too Many Requests      | All Inference Endpoints                | - You are sending requests too frequently and reaching rate limit                                                                                                           | - Reduce your request rate or increase your rate limit. You can find your current rate limit on [xAI Console](https://console.x.ai).             |

### 2XX Error Codes

| Status Code      | Endpoints                                   | Cause                                                                                                    | Solution                       |
| ---------------- | ------------------------------------------- | -------------------------------------------------------------------------------------------------------- | ------------------------------ |
| 202Accepted | `/v1/chat/deferred-completion/{request_id}` | - Your deferred chat completion request is queued for processing, but the response is not available yet. | - Wait for request processing. |

## Bug Report

If you believe you have encountered a bug and would like to contribute to our development process, [email API Bug Report](mailto:support@x.ai?subject=API%20Bug%20Report) to support@x.ai with your API request and response and relevant logs.

You can also chat in the `#help` channel of our [xAI API Developer Discord](https://discord.gg/x-ai).


===/developers/faq/accounts===
#### FAQ

# Accounts

## How do I create an account for the API?

You can create an account at https://accounts.x.ai, or https://console.x.ai. To link your X account automatically to
your xAI account, choose to sign up with X account.

You can create multiple accounts of different sign-in methods with the same email.

When you sign-up with a sign-in method and with the same email, we will prompt you whether you
want to create a new account, or link to the existing account. We will not be able to merge the
content, subscriptions, etc. of different accounts.

## How do I update my xAI account email?

You can visit [xAI Accounts](https://accounts.x.ai). On the Account page, you can update your email.

## How do I add other sign-in methods?

Once you have signed-up for an account, you can add additional sign-in methods by going to [xAI Accounts](https://accounts.x.ai).

## I've forgotten my Multi-Factor Authentication (MFA) method, can you remove it?

You can generate your recovery codes at [xAI Accounts](https://accounts.x.ai) Security page.

We can't remove or reset your MFA method unless you have recovery codes due to security considerations. Please reach out to support@x.ai if you would like to delete the account instead.

## If I already have an account for Grok, can I use the same account for API access?

Yes, the account is shared between Grok and xAI API. You can manage the sign-in details at https://accounts.x.ai.

However, the billing is separate for Grok and xAI API. You can manage your billing for xAI API on [xAI Console](https://console.x.ai).
To manage billing for Grok, visit https://grok.com -> Settings -> Billing, or directly with Apple/Google if you made the
purchase via Apple App Store or Google Play.

## How do I manage my account?

You can visit [xAI Accounts](https://accounts.x.ai) to manage your account.

Please note the xAI account is different from the X account, and xAI cannot assist you with X account issues. Please
contact X via [X Help Center](https://help.x.com/) or Premium Support if you encounters any issues with your X account.

## I received an email of someone logging into my xAI account

xAI will send an email to you when someone logs into your xAI account. The login location is an approximation based on your IP address, which is dependent on your network setup and ISP and might not reflect exactly where the login happened.

If you think the login is not you, please [reset your password](https://accounts.x.ai/request-reset-password) and [clear your login sessions](https://accounts.x.ai/sessions). We also recommend all users to [add a multi-factor authentication method](https://accounts.x.ai/security).

## How do I delete my xAI account?

We are sorry to see you go!

You can visit [xAI Accounts](https://accounts.x.ai/account) to delete your account. You can restore your account after log in again and confirming restoration within 30 days.

You can cancel the deletion within 30 days by logging in again to any xAI websites and follow the prompt to confirm restoring the account.

For privacy requests, please go to: https://privacy.x.ai.


===/developers/faq/billing===
#### FAQ

# Billing

## I'm having payment issues with an Indian payment card

Unfortunately we cannot process Indian payment cards for our API service. We are working toward supporting it but you might want to consider using a third-party API in the meantime. As Grok Website and Apps' payments are handled differently, those are not affected.

## When will I be charged?

* Prepaid Credits: If you choose to use prepaid credits, you’ll be charged when you buy them. These credits will be assigned to the team you select during purchase.

* Monthly Invoiced Billing: If you set your [invoiced spending limit](/console/billing#monthly-invoiced-billing-and-invoiced-billing-limit) above $0, any usage beyond your prepaid credits will be charged at the end of the month.

* API Usage: When you make API requests, the cost is calculated immediately. The amount is either deducted from your available prepaid credits or added to your monthly invoice if credits are exhausted.

If you change your [invoiced spending limit](/console/billing#monthly-invoiced-billing-and-invoiced-billing-limit) to be greater than $0, you will be charged at the end of the month for any extra consumption after your prepaid credit on the team has run out.

Your API consumption will be calculated when making the requests, and the corresponding amount will be deducted from your remaining credits or added to your monthly invoice.

Check out [Billing](/console/billing) for more information.

## Can you retroactively generate an invoice with new billing information?

We are unable to retroactively generate an invoice. Please ensure your billing information is correct on [xAI Console](https://console.x.ai) Billing -> Payment.

## Can prepaid API credits be refunded?

Unfortunately, we are not able to offer refunds on any prepaid credit purchase unless in regions required by law. For details, please visit https://x.ai/legal/terms-of-service-enterprise.

### My prompt token consumption from the API is different from the token count I get from xAI Console Tokenizer or tokenize text endpoint

The inference endpoints add pre-defined tokens to help us process the request. Therefore, these tokens would be added to the total prompt token consumption. For more information, see:
[Estimating consumption with tokenizer on xAI Console or Estimating consumption with tokenizer on xAI Console or through API](/developers/rate-limits#estimating-consumption-with-tokenizer-on-xai-console-or-through-api).


===/developers/faq/general===
#### FAQ

# Frequently Asked Questions - General

Frequently asked questions by our customers.

For product-specific questions, visit  or .

### Does the xAI API provide access to live data?

Yes! With the agentic server-side [Web Search](/developers/tools/web-search) and [X Search](/developers/tools/x-search) tools.

### How do I contact Sales?

For customers with bespoke needs or to request custom pricing, please fill out our [Grok for Business form](https://x.ai/grok/business). A member of our team will reach out with next steps. You can also email us at [sales@x.ai](mailto:sales@x.ai).

### Where are your Terms of Service and Privacy Policy?

Please refer to our [Legal Resources](https://x.ai/legal) for our Enterprise Terms of Service and Data Processing Addendum.

### Does xAI sell crypto tokens?

xAI is not affiliated with any cryptocurrency. We are aware of several scam websites that unlawfully use our name and logo.


===/developers/faq===
#### Resources

# FAQ - xAI Console

Frequently asked questions on using the [xAI Console](https://console.x.ai), including creating teams, managing roles, and configuring settings.

You can find details on the following topics:


===/developers/faq/security===
#### FAQ

# Security

## Does xAI train on customers' API requests?

xAI never trains on your API inputs or outputs without your explicit permission.

API requests and responses are temporarily stored on our servers for 30 days in case they need to be audited for potential abuse or misuse. This data is automatically deleted after 30 days.

## Is the xAI API HIPAA compliant?

To inquire about a Business Associate Agreement (BAA), please complete our [BAA Questionnaire](https://forms.gle/YAEdX3XUp6MvdEXW9). A member of our team will review your responses and reach out with next steps.

## Is xAI GDPR and SOC II compliant?

We are SOC 2 Type 2 compliant. Customers with a signed NDA can refer to our [Trust Center](https://trust.x.ai/) for up-to-date information on our certifications and data governance.

## Do you have Audit Logs?

Team admins are able to view an audit log of user interactions. This lists all of the user interactions with our API server. You can view it at [xAI Console -> Audit Log](https://console.x.ai/team/default/audit).

The admin can also search by Event ID, Description or User to filter the results shown. For example, this is to filter by description matching `ListApiKeys`:

You can also view the audit log across a range of dates with the time filter:

## How can I securely manage my API keys?

Treat your xAI API keys as sensitive information, like passwords or credit card details. Do not share keys between teammates to avoid unauthorized access. Store keys securely using environment variables or secret management tools. Avoid committing keys to public repositories or source code.

Rotate keys regularly for added security. If you suspect a compromise, log into the xAI console first. Ensure you are viewing the correct team, as API keys are tied to specific teams. Navigate to the "API Keys" section via the sidebar. In the API Keys table, click the vertical ellipsis (three dots) next to the key. Select "Disable key" to deactivate it temporarily or "Delete key" to remove it permanently. Then, click the "Create API Key" button to generate a new one and update your applications.

xAI partners with GitHub's Secret Scanning program to detect leaked keys. If a leak is found, we disable the key and notify you via email. Monitor your account for unusual activity to stay protected.


===/developers/faq/team-management===
#### FAQ

# Team Management

## What are teams?

Teams are the level at which xAI tracks API usage, processes billing, and issues invoices.

* If you’re the team creator and don’t need a new team, you can rename your Personal Team and add members instead of creating a new one.
* Each team has **roles**:
  * **Admin**: Can modify team name, billing details, and manage members.
  * **Member**: Cannot make these changes.
  * The team creator is automatically an Admin.

## Which team am I on?

When you sign up for xAI, you’re automatically assigned to a **Personal Team**, which you can view the top bar of [xAI Console](https://console.x.ai).

## How can I manage teams and team members?

### Create a Team

1. Click the dropdown menu in the xAI Console.
2. Select **+ Create Team**.
3. Follow the on-screen instructions. You can edit these details later.

### Rename or Describe a Team

Admins can update the team name and description on the [Settings page](https://console.x.ai/team/default/settings).

### Manage Team Members

Admins can add or remove members by email on the [Users page](https://console.x.ai/team/default/users).

* Assign members as **Admin** or **Member**.
* If a user is removed, their API keys remain with the team.

### Delete a Team

Deleting a team removes its prepaid credits.

To permanently delete a team:

1. Go to the [Settings page](https://console.x.ai/team/default/settings).
2. Follow the instructions under **Delete Team**.

## How to automatically add users to team with my organization's email domain?

Admins can enable automatic team joining for users with a shared email domain:

1. Go to the [Settings page](https://console.x.ai/team/default/settings).
2. Add the domain under **Verified Domains**.
3. Add a `domain-verification` key to your domain’s DNS TXT record to verify ownership.

Users signing up with a verified domain email will automatically join the team.


===/developers/files/collections/api===
#### Files & Collections

# Using Collections via API

This guide walks you through managing collections programmatically using the xAI SDK and REST API.

## Creating a Management Key

To use the Collections API, you need to create a Management API Key with the `AddFileToCollection` permission. This permission is required for uploading documents to collections.

1. Navigate to the **Management Keys** section in the [xAI Console](https://console.x.ai)
2. Click on **Create Management Key**
3. Select the `AddFileToCollection` permission along with any other permissions you need
4. If you need to perform operations other than uploading documents (such as creating, updating, or deleting collections), enable the corresponding permissions in the **Collections Endpoint** group
5. Copy and securely store your Management API Key

Make sure to copy your Management API Key immediately after creation. You won't be able to see it again.

## Creating a collection

```python customLanguage="pythonXAI"
import os
from xai_sdk import Client
client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    management_api_key=os.getenv("XAI_MANAGEMENT_API_KEY"),
    timeout=3600,
)

collection = client.collections.create(
    name="SEC Filings",
)

print(collection)
```

```javascript customLanguage="javascriptWithoutSDK"
const response = await fetch('https://management-api.x.ai/v1/collections', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${process.env.XAI_MANAGEMENT_API_KEY}`,
  },
  body: JSON.stringify({ collection_name: 'SEC Filings' }),
});
const collection = await response.json();
console.log(collection);
```

```bash
curl https://management-api.x.ai/v1/collections \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_MANAGEMENT_API_KEY" \
  -d '{"collection_name": "SEC Filings"}'
```

## Listing collections

```python customLanguage="pythonXAI"
# ... Create client
collections = client.collections.list()
print(collections)
```

```javascript customLanguage="javascriptWithoutSDK"
const response = await fetch('https://management-api.x.ai/v1/collections', {
  headers: {
    'Authorization': `Bearer ${process.env.XAI_MANAGEMENT_API_KEY}`,
  },
});
const collections = await response.json();
console.log(collections);
```

```bash
curl https://management-api.x.ai/v1/collections \
  -H "Authorization: Bearer $XAI_MANAGEMENT_API_KEY"
```

## Viewing collection configuration

```python customLanguage="pythonXAI"
# ... Create client
collection = client.collections.get("collection_dbc087b1-6c99-493d-86c6-b401fee34a9d")

print(collection)
```

```javascript customLanguage="javascriptWithoutSDK"
const collectionId = 'collection_dbc087b1-6c99-493d-86c6-b401fee34a9d';
const response = await fetch(`https://management-api.x.ai/v1/collections/${collectionId}`, {
  headers: {
    'Authorization': `Bearer ${process.env.XAI_MANAGEMENT_API_KEY}`,
  },
});
const collection = await response.json();
console.log(collection);
```

```bash
curl https://management-api.x.ai/v1/collections/collection_dbc087b1-6c99-493d-86c6-b401fee34a9d \
  -H "Authorization: Bearer $XAI_MANAGEMENT_API_KEY"
```

## Updating collection configuration

```python customLanguage="pythonXAI"
# ... Create client
collection = client.collections.update(
    "collection_dbc087b1-6c99-493d-86c6-b401fee34a9d",
    name="SEC Filings (New)"
)

print(collection)
```

```javascript customLanguage="javascriptWithoutSDK"
const collectionId = 'collection_dbc087b1-6c99-493d-86c6-b401fee34a9d';
const response = await fetch(`https://management-api.x.ai/v1/collections/${collectionId}`, {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${process.env.XAI_MANAGEMENT_API_KEY}`,
  },
  body: JSON.stringify({ collection_name: 'SEC Filings (New)' }),
});
const collection = await response.json();
console.log(collection);
```

```bash
curl https://management-api.x.ai/v1/collections/collection_dbc087b1-6c99-493d-86c6-b401fee34a9d \
  -X PUT \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_MANAGEMENT_API_KEY" \
  -d '{"collection_name": "SEC Filings (New)"}'
```

## Uploading documents

Uploading a document to a collection is a two-step process:

1. Upload the file to the xAI API
2. Add the uploaded file to your collection

```python customLanguage="pythonXAI"
# ... Create client
with open("tesla-20241231.html", "rb") as file:
    file_data = file.read()

document = client.collections.upload_document(
    collection_id="collection_dbc087b1-6c99-493d-86c6-b401fee34a9d",
    name="tesla-20241231.html",
    data=file_data,
)
print(document)
```

```javascript customLanguage="javascriptWithoutSDK"
const collectionId = 'collection_dbc087b1-6c99-493d-86c6-b401fee34a9d';

// Step 1: Upload file
const formData = new FormData();
formData.append('file', file);
formData.append('purpose', 'assistants');
const uploadResponse = await fetch('https://api.x.ai/v1/files', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${process.env.XAI_API_KEY}` },
  body: formData,
});
const { id: fileId } = await uploadResponse.json();

// Step 2: Add to collection
await fetch(`https://management-api.x.ai/v1/collections/${collectionId}/documents/${fileId}`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${process.env.XAI_MANAGEMENT_API_KEY}` },
});
```

```bash
# Step 1: Upload file
curl https://api.x.ai/v1/files \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -F file=@tesla-20241231.html

# Step 2: Add file to collection (use file_id from step 1)
curl -X POST https://management-api.x.ai/v1/collections/$COLLECTION_ID/documents/$FILE_ID \
  -H "Authorization: Bearer $XAI_MANAGEMENT_API_KEY"
```

### Uploading with metadata fields

If your collection has [metadata fields](/developers/files/collections/metadata) defined (the collection must have these fields set in `field_definitions` when created or updated - see the linked metadata page for details), include them using the `fields` parameter:

```python customLanguage="pythonXAI"
# ... Create client
with open("paper.pdf", "rb") as file:
    file_data = file.read()

document = client.collections.upload_document(
    collection_id="collection_dbc087b1-6c99-493d-86c6-b401fee34a9d",
    name="paper.pdf",
    data=file_data,
    fields={
        "author": "Sandra Kim",
        "year": "2024",
        "title": "Q3 Revenue Analysis"
    },
)
print(document)
```

```bash
curl https://management-api.x.ai/v1/collections/collection_dbc087b1-6c99-493d-86c6-b401fee34a9d/documents \
  -H "Authorization: Bearer $XAI_MANAGEMENT_API_KEY" \
  -F "name=paper.pdf" \
  -F "data=@paper.pdf" \
  -F "content_type=application/pdf" \
  -F 'fields={"author": "Sandra Kim", "year": "2024", "title": "Q3 Revenue Analysis"}'
```

## Searching documents

You can also search documents using the Responses API with the `file_search` tool. See the [Collections Search Tool](/developers/tools/collections-search) guide for more details.

```python customLanguage="pythonXAI"
# ... Create client
response = client.collections.search(
    query="What were the key revenue drivers based on the SEC filings?",
    collection_ids=["collection_dbc087b1-6c99-493d-86c6-b401fee34a9d"],
)
print(response)
```

```javascript customLanguage="javascriptWithoutSDK"
const response = await fetch('https://api.x.ai/v1/documents/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${process.env.XAI_API_KEY}`,
  },
  body: JSON.stringify({
    query: 'What were the key revenue drivers based on the SEC filings?',
    source: {
      collection_ids: ['collection_dbc087b1-6c99-493d-86c6-b401fee34a9d'],
    },
  }),
});
const results = await response.json();
console.log(results);
```

```bash
curl https://api.x.ai/v1/documents/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "query": "What were the key revenue drivers based on the SEC filings?",
    "source": {
      "collection_ids": ["collection_dbc087b1-6c99-493d-86c6-b401fee34a9d"]
    }
  }'
```

### Search modes

There are three search methods available:

* **Keyword search**
* **Semantic search**
* **Hybrid search** (combines both keyword and semantic methods)

By default, the system uses hybrid search, which generally delivers the best and most comprehensive results.

| Mode | Description | Best for | Drawbacks |
|------|-------------|----------|-----------|
| Keyword | Searches for exact matches of specified words, phrases, or numbers | Precise terms (e.g., account numbers, dates, specific financial figures) | May miss contextually relevant content |
| Semantic | Understands meaning and context to find conceptually related content | Discovering general ideas, topics, or intent even when exact words differ | Less precise for specific terms |
| Hybrid | Combines keyword and semantic search for broader and more accurate results | Most real-world use cases | Slightly higher latency |

The hybrid approach balances precision and recall, making it the recommended default for the majority of queries.

An example to set hybrid mode:

```bash
curl https://api.x.ai/v1/documents/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
      "query": "What were the key revenue drivers based on the SEC filings?",
      "source": {
          "collection_ids": [
              "collection_dbc087b1-6c99-493d-86c6-b401fee34a9d"
          ]
      },
      "retrieval_mode": {"type": "hybrid"}
}'
```

You can set `"retrieval_mode": {"type": "keyword"}` for keyword search and `"retrieval_mode": {"type": "semantic"}` for semantic search.

## Deleting a document

```python customLanguage="pythonXAI"
# ... Create client

client.collections.remove_document(
    collection_id="collection_dbc087b1-6c99-493d-86c6-b401fee34a9d",
    file_id="file_55a709d4-8edc-4f83-84d9-9f04fe49f832",
)
```

```javascript customLanguage="javascriptWithoutSDK"
const collectionId = 'collection_dbc087b1-6c99-493d-86c6-b401fee34a9d';
const fileId = 'file_55a709d4-8edc-4f83-84d9-9f04fe49f832';

await fetch(`https://management-api.x.ai/v1/collections/${collectionId}/documents/${fileId}`, {
  method: 'DELETE',
  headers: { 'Authorization': `Bearer ${process.env.XAI_MANAGEMENT_API_KEY}` },
});
```

```bash
curl https://management-api.x.ai/v1/collections/collection_dbc087b1-6c99-493d-86c6-b401fee34a9d/documents/file_55a709d4-8edc-4f83-84d9-9f04fe49f832 \
  -X DELETE \
  -H "Authorization: Bearer $XAI_MANAGEMENT_API_KEY"
```

## Deleting a collection

```python customLanguage="pythonXAI"
# ... Create client

client.collections.delete(collection_id="collection_dbc087b1-6c99-493d-86c6-b401fee34a9d")
```

```javascript customLanguage="javascriptWithoutSDK"
const collectionId = 'collection_dbc087b1-6c99-493d-86c6-b401fee34a9d';

await fetch(`https://management-api.x.ai/v1/collections/${collectionId}`, {
  method: 'DELETE',
  headers: { 'Authorization': `Bearer ${process.env.XAI_MANAGEMENT_API_KEY}` },
});
```

```bash
curl https://management-api.x.ai/v1/collections/collection_dbc087b1-6c99-493d-86c6-b401fee34a9d \
  -X DELETE \
  -H "Authorization: Bearer $XAI_MANAGEMENT_API_KEY"
```

## Next Steps

[Metadata Fields →](/developers/files/collections/metadata) - Learn how to attach structured attributes to documents for filtering and contextual embeddings


===/developers/files/collections/metadata===
#### Files & Collections

# Metadata Fields

Metadata fields allow you to attach structured attributes to documents in a collection. These fields enable:

* **Filtered retrieval** — Narrow search results to documents matching specific criteria (e.g., `author="Sandra Kim"`)
* **Contextual embeddings** — Inject metadata into chunks to improve retrieval accuracy (e.g., prepending document title to each chunk)
* **Data integrity constraints** — Enforce required fields or uniqueness across documents

## Creating a Collection with Metadata Fields

Define metadata fields using `field_definitions` when creating a collection:

```bash
curl -X POST "https://management-api.x.ai/v1/collections" \
  -H "Authorization: Bearer $XAI_MANAGEMENT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "research_papers",
    "field_definitions": [
      { "key": "author", "required": true },
      { "key": "year", "required": true, "unique": true },
      { "key": "title", "inject_into_chunk": true }
    ]
  }'
```

### Field Definition Options

| Option | Description |
|--------|-------------|
| `required` | Document uploads must include this field. Defaults to `false`. |
| `unique` | Only one document in the collection can have a given value for this field. Defaults to `false`. |
| `inject_into_chunk` | Prepends this field's value to every embedding chunk, improving retrieval by providing context. Defaults to `false`. |

## Uploading Documents with Metadata

Include metadata as a JSON object in the `fields` parameter:

```bash
curl -X POST "https://management-api.x.ai/v1/collections/{collection_id}/documents" \
  -H "Authorization: Bearer $XAI_MANAGEMENT_API_KEY" \
  -F "name=paper.pdf" \
  -F "data=@paper.pdf" \
  -F "content_type=application/pdf" \
  -F 'fields={"author": "Sandra Kim", "year": "2024", "title": "Q3 Revenue Analysis"}'
```

## Filtering Documents in Search

Use the `filter` parameter to restrict search results based on metadata values. The filter uses AIP-160 syntax:

```bash
curl -X POST "https://api.x.ai/v1/documents/search" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "revenue growth",
    "source": { "collection_ids": ["collection_xxx"] },
    "filter": "author=\"Sandra Kim\" AND year>=2020"
  }'
```

### Supported Filter Operators

| Operator | Example | Description |
|----------|---------|-------------|
| `=` | `author="Jane"` | Equals |
| `!=` | `status!="draft"` | Not equals |
| `<`, `>`, `<=`, `>=` | `year>=2020` | Numeric/lexical comparison |
| `AND` | `a="x" AND b="y"` | Both conditions must match |
| `OR` | `a="x" OR a="y"` | Either condition matches |

`OR` has higher precedence than `AND`. Use parentheses for clarity: `a="x" AND (b="y" OR b="z")`.

Wildcard matching (e.g., `author="E*"`) is not supported. All string comparisons are exact matches.

Filtering on fields that don't exist in your documents returns no results. Double-check that field names match your collection's `field_definitions`.

## AIP-160 Filter String Examples

### Basic Examples

```bash
# Equality (double or single quotes for strings with spaces)
author="Sandra Kim"
author='Sandra Kim'

# Equality (no quotes needed for simple values)
year=2024
status=active

# Not equal
status!="archived"
status!='archived'
```

### Comparison Operators

```bash
# Numeric comparisons
year>=2020
year>2019
score<=0.95
price<100

# Combined comparisons (range)
year>=2020 AND year<=2024
```

### Logical Operators

```bash
# AND - both conditions must match
author="Sandra Kim" AND year=2024

# OR - either condition matches
status="pending" OR status="in_progress"

# Combined (OR has higher precedence than AND)
department="Engineering" AND status="active" OR status="pending"

# Use parentheses for clarity
department="Engineering" AND (status="active" OR status="pending")
```

### Complex Examples

```bash
# Multiple conditions
author="Sandra Kim" AND year>=2020 AND status!="draft"

# Nested logic with parentheses
(author="Sandra Kim" OR author="John Doe") AND year>=2020

# Multiple fields with mixed operators
category="finance" AND (year=2023 OR year=2024) AND status!="archived"
```

## Quick Reference

| Use Case | Filter String |
|----------|---------------|
| Exact match | `author="Sandra Kim"` |
| Numeric comparison | `year>=2020` |
| Not equal | `status!="archived"` |
| Multiple conditions | `author="Sandra Kim" AND year=2024` |
| Either condition | `status="pending" OR status="draft"` |
| Grouped logic | `(status="active" OR status="pending") AND year>=2020` |
| Complex filter | `category="finance" AND year>=2020 AND status!="archived"` |


===/developers/files/collections===
#### Files & Collections

# Collections

Collections offers xAI API users a robust set of tools and methods to seamlessly integrate their enterprise requirements and internal knowledge bases with the xAI API. Whether you're building a RAG application or need to search across large document sets, Collections provides the infrastructure to manage and query your content.

**Looking for Files?** If you want to attach files directly to chat messages for conversation context, see [Files](/developers/files). Collections are different—they provide persistent document storage with semantic search across many documents.

## Core Concepts

There are two entities that users can create within the Collections service:

* **File** — A single entity of a user-uploaded file.
* **Collection** — A group of files linked together, with an embedding index for efficient retrieval.
  * When you create a collection you have the option to automatically generate embeddings for any files uploaded to that collection. You can then perform semantic search across files in multiple collections.
  * A single file can belong to multiple collections.

## What You Can Do

With Collections, you can:

* **Create collections** to organize your documents
* **Upload documents** in various formats (HTML, PDF, text, etc.)
* **Search semantically** across your documents using natural language queries
* **Configure chunking and embeddings** to optimize retrieval
* **Manage documents** by listing, updating, and deleting them

## Getting Started

Choose how you want to work with Collections:

* [Using the Console →](/console/collections) - Create collections and upload documents through the xAI Console interface
* [Using the API →](/developers/files/collections/api) - Programmatically manage collections with the SDK and REST API

## Metadata Fields

Collections support **metadata fields** — structured attributes you can attach to documents for enhanced retrieval and data integrity:

* **Filtered retrieval** — Narrow search results to documents matching specific criteria (e.g., `author="Sandra Kim"`)
* **Contextual embeddings** — Inject metadata into chunks to improve retrieval accuracy (e.g., prepending document title to each chunk)
* **Data integrity constraints** — Enforce required fields or uniqueness across documents

When creating a collection, define metadata fields with options like `required`, `unique`, and `inject_into_chunk` to control how metadata is validated and used during search.

[Learn more about metadata fields →](/developers/files/collections/metadata)

## Usage Limits

To be able to upload files and add to a collections you must have credits in your account.

**Maximum file size**: 100MB**Maximum number of files**: 100,000 files uploaded globally.**Maximum total size**: 100GB

Please [contact us](https://x.ai/contact) to increase any of these limits.

## Data Privacy

We do not use user data stored on Collections for model training purposes.

## Supported MIME Types

While we support any `UTF-8` encoded text file, we also have special file conversion and chunking techniques for certain MIME types.

The following would be a non-exhaustive list for the MIME types that we support:

* application/csv
* application/dart
* application/ecmascript
* application/epub
* application/epub+zip
* application/json
* application/ms-java
* application/msword
* application/pdf
* application/typescript
* application/vnd.adobe.pdf
* application/vnd.curl
* application/vnd.dart
* application/vnd.jupyter
* application/vnd.ms-excel
* application/vnd.ms-outlook
* application/vnd.oasis.opendocument.text
* application/vnd.openxmlformats-officedocument.presentationml.presentation
* application/vnd.openxmlformats-officedocument.presentationml.slide
* application/vnd.openxmlformats-officedocument.presentationml.slideshow
* application/vnd.openxmlformats-officedocument.presentationml.template
* application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
* application/vnd.openxmlformats-officedocument.spreadsheetml.template
* application/vnd.openxmlformats-officedocument.wordprocessingml.document
* application/x-csh
* application/x-epub+zip
* application/x-hwp
* application/x-hwp-v5
* application/x-latex
* application/x-pdf
* application/x-php
* application/x-powershell
* application/x-sh
* application/x-shellscript
* application/x-tex
* application/x-zsh
* application/xhtml
* application/xml
* application/zip
* text/cache-manifest
* text/calendar
* text/css
* text/csv
* text/html
* text/javascript
* text/jsx
* text/markdown
* text/n3
* text/php
* text/plain
* text/rtf
* text/tab-separated-values
* text/troff
* text/tsv
* text/tsx
* text/turtle
* text/uri-list
* text/vcard
* text/vtt
* text/x-asm
* text/x-bibtex
* text/x-c
* text/x-c++hdr
* text/x-c++src
* text/x-chdr
* text/x-coffeescript
* text/x-csh
* text/x-csharp
* text/x-csrc
* text/x-d
* text/x-diff
* text/x-emacs-lisp
* text/x-erlang
* text/x-go
* text/x-haskell
* text/x-java
* text/x-java-properties
* text/x-java-source
* text/x-kotlin
* text/x-lisp
* text/x-lua
* text/x-objcsrc
* text/x-pascal
* text/x-perl
* text/x-perl-script
* text/x-python
* text/x-python-script
* text/x-r-markdown
* text/x-rst
* text/x-ruby-script
* text/x-rust
* text/x-sass
* text/x-scala
* text/x-scheme
* text/x-script.python
* text/x-scss
* text/x-sh
* text/x-sql
* text/x-swift
* text/x-tcl
* text/x-tex
* text/x-vbasic
* text/x-vcalendar
* text/xml
* text/xml-dtd
* text/yaml


===/developers/files/managing-files===
#### Files & Collections

# Managing Files

The Files API provides a complete set of operations for managing your files. Before using files in chat conversations, you need to upload them using one of the methods described below.

## Uploading Files

You can upload files in several ways: from a file path, raw bytes, BytesIO object, or an open file handle.

### Upload from File Path

```pythonXAI
import os
from xai_sdk import Client

client = Client(api_key=os.getenv("XAI_API_KEY"))

# Upload a file from disk
file = client.files.upload("/path/to/your/document.pdf")

print(f"File ID: {file.id}")
print(f"Filename: {file.filename}")
print(f"Size: {file.size} bytes")
print(f"Created at: {file.created_at}")
```

```pythonOpenAISDK
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

# Upload a file
with open("/path/to/your/document.pdf", "rb") as f:
    file = client.files.create(
        file=f,
        purpose="assistants"
    )

print(f"File ID: {file.id}")
print(f"Filename: {file.filename}")
```

```pythonRequests
import os
import requests

url = "https://api.x.ai/v1/files"
headers = {
    "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}"
}

with open("/path/to/your/document.pdf", "rb") as f:
    files = {"file": f}
    data = {"purpose": "assistants"}
    response = requests.post(url, headers=headers, files=files, data=data)

file_data = response.json()
print(f"File ID: {file_data['id']}")
print(f"Filename: {file_data['filename']}")
```

```bash
curl https://api.x.ai/v1/files \\
  -H "Authorization: Bearer $XAI_API_KEY" \\
  -F file=@/path/to/your/document.pdf \\
  -F purpose=assistants
```

### Upload from Bytes

```pythonXAI
import os
from xai_sdk import Client

client = Client(api_key=os.getenv("XAI_API_KEY"))

# Upload file content directly from bytes
content = b"This is my document content.\\nIt can span multiple lines."
file = client.files.upload(content, filename="document.txt")

print(f"File ID: {file.id}")
print(f"Filename: {file.filename}")
```

### Upload from file object

```pythonXAI
import os
from xai_sdk import Client

client = Client(api_key=os.getenv("XAI_API_KEY"))

# Upload a file directly from disk
file = client.files.upload(open("document.pdf", "rb"), filename="document.pdf")

print(f"File ID: {file.id}")
print(f"Filename: {file.filename}")
```

## Upload with Progress Tracking

Track upload progress for large files using callbacks or progress bars.

### Custom Progress Callback

```pythonXAI
import os
from xai_sdk import Client

client = Client(api_key=os.getenv("XAI_API_KEY"))

# Define a custom progress callback
def progress_callback(bytes_uploaded: int, total_bytes: int):
    percentage = (bytes_uploaded / total_bytes) * 100 if total_bytes else 0
    mb_uploaded = bytes_uploaded / (1024 * 1024)
    mb_total = total_bytes / (1024 * 1024)
    print(f"Progress: {mb_uploaded:.2f}/{mb_total:.2f} MB ({percentage:.1f}%)")

# Upload with progress tracking
file = client.files.upload(
    "/path/to/large-file.pdf",
    on_progress=progress_callback
)

print(f"Successfully uploaded: {file.filename}")
```

### Progress Bar with tqdm

```pythonXAI
import os
from xai_sdk import Client
from tqdm import tqdm

client = Client(api_key=os.getenv("XAI_API_KEY"))

file_path = "/path/to/large-file.pdf"
total_bytes = os.path.getsize(file_path)

# Upload with tqdm progress bar
with tqdm(total=total_bytes, unit="B", unit_scale=True, desc="Uploading") as pbar:
    file = client.files.upload(
        file_path,
        on_progress=pbar.update
    )

print(f"Successfully uploaded: {file.filename}")
```

## Listing Files

Retrieve a list of your uploaded files with pagination and sorting options.

### Available Options

* **`limit`**: Maximum number of files to return. If not specified, uses server default of 100.
* **`order`**: Sort order for the files. Either `"asc"` (ascending) or `"desc"` (descending).
* **`sort_by`**: Field to sort by. Options: `"created_at"`, `"filename"`, or `"size"`.
* **`pagination_token`**: Token for fetching the next page of results.

```pythonXAI
import os
from xai_sdk import Client

client = Client(api_key=os.getenv("XAI_API_KEY"))

# List files with pagination and sorting
response = client.files.list(
    limit=10,
    order="desc",
    sort_by="created_at"
)

for file in response.data:
    print(f"File: {file.filename} (ID: {file.id}, Size: {file.size} bytes)")
```

```pythonOpenAISDK
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

# List files
files = client.files.list()

for file in files.data:
    print(f"File: {file.filename} (ID: {file.id})")
```

```pythonRequests
import os
import requests

url = "https://api.x.ai/v1/files"
headers = {
    "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}"
}

response = requests.get(url, headers=headers)
files = response.json()

for file in files.get("data", []):
    print(f"File: {file['filename']} (ID: {file['id']})")
```

```bash
curl https://api.x.ai/v1/files \\
  -H "Authorization: Bearer $XAI_API_KEY"
```

## Getting File Metadata

Retrieve detailed information about a specific file.

```pythonXAI
import os
from xai_sdk import Client

client = Client(api_key=os.getenv("XAI_API_KEY"))

# Get file metadata by ID
file = client.files.get("file-abc123")

print(f"Filename: {file.filename}")
print(f"Size: {file.size} bytes")
print(f"Created: {file.created_at}")
print(f"Team ID: {file.team_id}")
```

```pythonOpenAISDK
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

# Get file metadata
file = client.files.retrieve("file-abc123")

print(f"Filename: {file.filename}")
print(f"Size: {file.bytes} bytes")
```

```pythonRequests
import os
import requests

file_id = "file-abc123"
url = f"https://api.x.ai/v1/files/{file_id}"
headers = {
    "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}"
}

response = requests.get(url, headers=headers)
file = response.json()

print(f"Filename: {file['filename']}")
print(f"Size: {file['bytes']} bytes")
```

```bash
curl https://api.x.ai/v1/files/file-abc123 \\
  -H "Authorization: Bearer $XAI_API_KEY"
```

## Getting File Content

Download the actual content of a file.

```pythonXAI
import os
from xai_sdk import Client

client = Client(api_key=os.getenv("XAI_API_KEY"))

# Get file content
content = client.files.content("file-abc123")

# Content is returned as bytes
print(f"Content length: {len(content)} bytes")
print(f"Content preview: {content[:100]}")
```

```pythonOpenAISDK
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

# Get file content
content = client.files.content("file-abc123")

print(f"Content: {content.text}")
```

```pythonRequests
import os
import requests

file_id = "file-abc123"
url = f"https://api.x.ai/v1/files/{file_id}/content"
headers = {
    "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}"
}

response = requests.get(url, headers=headers)
content = response.content

print(f"Content length: {len(content)} bytes")
```

```bash
curl https://api.x.ai/v1/files/file-abc123/content \\
  -H "Authorization: Bearer $XAI_API_KEY"
```

## Deleting Files

Remove files when they're no longer needed.

```pythonXAI
import os
from xai_sdk import Client

client = Client(api_key=os.getenv("XAI_API_KEY"))

# Delete a file
delete_response = client.files.delete("file-abc123")

print(f"Deleted: {delete_response.deleted}")
print(f"File ID: {delete_response.id}")
```

```pythonOpenAISDK
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

# Delete a file
delete_response = client.files.delete("file-abc123")

print(f"Deleted: {delete_response.deleted}")
print(f"File ID: {delete_response.id}")
```

```pythonRequests
import os
import requests

file_id = "file-abc123"
url = f"https://api.x.ai/v1/files/{file_id}"
headers = {
    "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}"
}

response = requests.delete(url, headers=headers)
result = response.json()

print(f"Deleted: {result['deleted']}")
print(f"File ID: {result['id']}")
```

```bash
curl -X DELETE https://api.x.ai/v1/files/file-abc123 \\
  -H "Authorization: Bearer $XAI_API_KEY"
```

## Limitations and Considerations

### File Size Limits

* **Maximum file size**: 48 MB per file
* **Processing time**: Larger files may take longer to process

### File Retention

* **Cleanup**: Delete files when no longer needed to manage storage
* **Access**: Files are scoped to your team/organization

### Supported Formats

While many text-based formats are supported, the system works best with:

* Structured documents (with clear sections, headings)
* Plain text and markdown
* Documents with clear information hierarchy

Supported file types include:

* Plain text files (.txt)
* Markdown files (.md)
* Code files (.py, .js, .java, etc.)
* CSV files (.csv)
* JSON files (.json)
* PDF documents (.pdf)
* And many other text-based formats

## Next Steps

Now that you know how to manage files, learn how to use them in chat conversations:


===/developers/files===
#### Files & Collections

# Files

The Files API enables you to upload documents and use them in chat conversations with Grok. When you attach files to a chat message, the system automatically activates the `attachment_search` tool, transforming your request into an agentic workflow where Grok can intelligently search through and reason over your documents to answer questions.

You can view more information at [Files API Reference](/developers/rest-api-reference/files).

**Looking for Collections?** If you need persistent document storage with semantic search across many documents, see [Collections](/developers/files/collections). Files are different—they're for attaching documents to chat conversations for immediate context.

## How Files Work with Chat

Behind the scenes, when you attach files to a chat message, the xAI API implicitly adds the `attachment_search` server-side tool to your request. This means:

1. **Automatic Agentic Behavior**: Your chat request becomes an agentic request, where Grok autonomously searches through your documents
2. **Intelligent Document Analysis**: The model can reason over document content, extract relevant information, and synthesize answers
3. **Multi-Document Support**: You can attach multiple files, and Grok will search across all of them

This seamless integration allows you to simply attach files and ask questions—the complexity of document search and retrieval is handled automatically by the agentic workflow.

## Understanding Document Search

When you attach files to a chat message, the xAI API automatically activates the `attachment_search` [server-side tool](/developers/tools/overview). This transforms your request into an [agentic workflow](/developers/tools/overview#how-it-works) where Grok:

1. **Analyzes your query** to understand what information you're seeking
2. **Searches the documents** intelligently, finding relevant sections across all attached files
3. **Extracts and synthesizes information** from multiple sources if needed
4. **Provides a comprehensive answer** with the context from your documents

### Agentic Workflow

Just like other agentic tools (web search, X search, code execution), document search operates autonomously:

* **Multiple searches**: The model may search documents multiple times with different queries to find comprehensive information
* **Reasoning**: The model uses its reasoning capabilities to decide what to search for and how to interpret the results
* **Streaming visibility**: In streaming mode, you can see when the model is searching your documents via tool call notifications

### Token Usage with Files

File-based chats follow similar token patterns to other agentic requests:

* **Prompt tokens**: Include the conversation history and internal processing. Document content is processed efficiently
* **Reasoning tokens**: Used for planning searches and analyzing document content
* **Completion tokens**: The final answer text
* **Cached tokens**: Repeated document content benefits from prompt caching for efficiency

The actual document content is processed by the server-side tool and doesn't directly appear in the message history, keeping token usage optimized.

### Pricing

Document search is billed per tool invocation, in addition to standard token costs. Each time the model searches your documents, it counts as one tool invocation. For complete pricing details, see the [Tools Pricing](/developers/models#tools-pricing) table.

## Getting Started

To use files with Grok, you'll need to:

1. **[Upload and manage files](/developers/files/managing-files)** - Learn how to upload, list, retrieve, and delete files using the Files API
2. **[Chat with files](/developers/model-capabilities/files/chat-with-files)** - Discover how to attach files to chat messages and ask questions about your documents

## Quick Example

Here's a quick example of the complete workflow:

```pythonXAI
import os
from xai_sdk import Client
from xai_sdk.chat import user, file

client = Client(api_key=os.getenv("XAI_API_KEY"))

# 1. Upload a document
document_content = b"""Quarterly Sales Report - Q4 2024
Total Revenue: $5.2M
Growth: +18% YoY
"""

uploaded_file = client.files.upload(document_content, filename="sales.txt")

# 2. Chat with the file
chat = client.chat.create(model="grok-4-fast")
chat.append(user("What was the total revenue?", file(uploaded_file.id)))

# 3. Get the answer
response = chat.sample()
print(response.content)  # "The total revenue was $5.2M"

# 4. Clean up
client.files.delete(uploaded_file.id)
```

## Key Features

### Multiple File Support

Attach [multiple documents](/developers/model-capabilities/files/chat-with-files#multiple-file-attachments) to a single query and Grok will search across all of them to find relevant information.

### Multi-Turn Conversations

File context persists across [conversation turns](/developers/model-capabilities/files/chat-with-files#multi-turn-conversations-with-files), allowing you to ask follow-up questions without re-attaching files.

### Code Execution Integration

Combine files with the [code execution tool](/developers/model-capabilities/files/chat-with-files#combining-files-with-code-execution) to perform advanced data analysis, statistical computations, and transformations on your uploaded data. The model can write and execute Python code that processes your files directly.

## Limitations

* **File size**: Maximum 48 MB per file
* **No batch requests**: File attachments with document search are agentic requests and do not support batch mode (`n > 1`)
* **Agentic models only**: Requires models that support agentic tool calling (e.g., `grok-4-fast`, `grok-4`)
* **Supported file formats**:
  * Plain text files (.txt)
  * Markdown files (.md)
  * Code files (.py, .js, .java, etc.)
  * CSV files (.csv)
  * JSON files (.json)
  * PDF documents (.pdf)
  * And many other text-based formats

## Next Steps


===/developers/grpc-api-reference===
# gRPC API Reference

The xAI gRPC API is a robust, high-performance gRPC interface designed for seamless integration into existing systems.

The base url for all services is at `api.x.ai`. For all services, you have to authenticate with the header `Authorization: Bearer <your xAI API key>`.

Visit [xAI API Protobuf Definitions](https://github.com/xai-org/xai-proto) to view and download our protobuf definitions.

***

<GrpcDocsSection title="Image" protoFileName={'xai/api/v1/image.proto'} serviceFullName={'xai_api.Image'} />

<GrpcDocsSection title="Models" protoFileName={'xai/api/v1/models.proto'} serviceFullName={'xai_api.Models'} />

<GrpcDocsSection title="Raw Sampling of a Language Model" protoFileName={'xai/api/v1/sample.proto'} serviceFullName={'xai_api.Sample'} />


===/developers/introduction===
#### Introduction

# What is Grok?

Grok is a family of Large Language Models (LLMs) developed by [xAI](https://x.ai).

Inspired by the Hitchhiker's Guide to the Galaxy, Grok is a maximally truth-seeking AI that provides insightful, unfiltered truths about the universe.

xAI offers an API for developers to programmatically interact with our Grok [models](/developers/models). The same models power our consumer facing services such as [Grok.com](https://grok.com), the [iOS](https://apps.apple.com/us/app/grok/id6670324846) and [Android](https://play.google.com/store/apps/details?id=ai.x.grok) apps, as well as [Grok in X experience](https://grok.x.com).

## What is the xAI API? How is it different from Grok in other services?

The xAI API is a toolkit for developers to integrate xAI's Grok models into their own applications, the xAI API provides the building blocks to create new AI experiences.

To get started building with the xAI API, please head to [The Hitchhiker's Guide to Grok](/developers/quickstart).

## xAI API vs Grok in other services

| Category                      | xAI API                          | Grok.com                          | Mobile Apps                  | Grok in 𝕏                          |
|-------------------------------|----------------------------------|-----------------------------------|----------------------------|------------------------------------|
| **Accessible**                | API (api.x.ai)                   | grok.com + PWA (Android)          | App Store / Play Store     | X.com + 𝕏 apps                     |
| **Billing**                   | xAI                              | xAI / 𝕏                           | xAI / 𝕏                    | 𝕏                                  |
| **Programming Required**      | Yes                              | No                                | No                         | No                                 |
| **Description**               | Programmatic access for developers | Full-featured web AI assistant   | Mobile AI assistant        | X-integrated AI (fewer features)   |

Because these are separate offerings, your purchase on X (e.g. X Premium) won't affect your service status on xAI API, and vice versa.

This documentation is intended for users using xAI API.


===/developers/management-api-guide===
#### Key Information

# Using Management API

Some enterprise users may prefer to manage their account details programmatically rather than manually through the xAI Console. For this reason, we have developed a Management API to enable enterprise users to efficiently manage their team details.

You can read the endpoint specifications and descriptions at [Management API Reference](/developers/rest-api-reference/management).

You need to get a management key, which is separate from your API key, to use the management API. The management key can be obtained at [xAI Console](https://console.x.ai) -> Settings -> Management Keys.

The base URL is at `https://management-api.x.ai`, which is also different from the inference API.

## Operations related to API Keys

You can create, list, update, and delete API keys via the management API.

You can also manage the access control lists (ACLs) associated with the API keys.

The available ACL types are:

* `api-key:model`
* `api-key:endpoint`

To enable all models and endpoints available to your team, use:

* `api-key:model:*`
* `api-key:endpoint:*`

Or if you need to specify the particular endpoint available to the API:

* `api-key:endpoint:chat` for chat and vision models
* `api-key:endpoint:image` for image generation models

And to specify models the API key has access to:

* `api-key:model:<model name such as grok-4-1-fast-reasoning>`

### Create an API key

An example to create an API key with all models and endpoints enabled, limiting requests to 5 queries per second and 100 queries per minute, without token number restrictions.

```bash
curl https://management-api.x.ai/auth/teams/{teamId}/api-keys \\
    -X POST \\
    -H "Authorization: Bearer <Your Management API Key>" \\
    -d '{
            "name": "My API key",
            "acls": ["api-key:model:*", "api-key:endpoint:*"],
            "qps": 5,
            "qpm": 100,
            "tpm": null
        }'
```

Specify `tpm` to any integer string to limit the number of tokens produced/consumed per minute. When the token rate limit is triggered, new requests will be rejected and in-flight requests will continue processing.

The newly-created API key will be returned in the `"apiKey"` field of the response object. The API Key ID is returned as `"apiKeyId"` in the response body as well, which is useful for updating and deleting operations.

### List API keys

To retrieve a list of API keys from a team, you can run the following:

```bash
curl https://management-api.x.ai/auth/teams/{teamId}/api-keys?pageSize=10&paginationToken= \\
    -H "Authorization: Bearer <Your Management API Key>"
```

You can customize the query parameters such as `pageSize` and `paginationToken`.

### Update an API key

You can update an API key after it has been created. For example, to update the `qpm` of an API key:

```bash
curl https://management-api.x.ai/auth/api-keys/{apiKeyId} \\
    -X PUT \\
    -H "Authorization: Bearer <Your Management API Key>" \\
    -d '{
            "apiKey": {
                "qpm": 200
            },
            "fieldMask": "qpm",
        }'
```

Or to update the `name` of an API key:

```bash
curl https://management-api.x.ai/auth/api-keys/{apiKeyId} \\
    -X PUT \\
    -H "Authorization: Bearer <Your Management API Key>" \\
    -d '{
            "apiKey": {
                "name": "Updated API key"
            },
            "fieldMask": "name",
        }'
```

### Delete an API key

You can also delete an API key with the following:

```bash
curl https://management-api.x.ai/auth/api-keys/{apiKeyId} \\
    -X DELETE \\
    -H "Authorization: Bearer <Your Management API Key>"
```

### Check propagation status of API key across clusters

There could be a slight delay between creating an API key, and the API key being available for use across all clusters.

You can check the propagation status of the API key via API.

```bash
curl https://management-api.x.ai/auth/api-keys/{apiKeyId}/propagation \\
    -H "Authorization: Bearer <Your Management API Key>"
```

### List all models available for the team

You can list all the available models for a team with our management API as well.

The model names in the output can be used with setting ACL string on an API key as `api-key:model:<model-name>`

```bash
curl https://management-api.x.ai/auth/teams/{teamId}/models \\
    -H "Authorization: Bearer <Your Management API Key>"
```

## Access Control List (ACL) management

We also offer endpoint to list possible ACLs for a team. You can then apply the endpoint ACL strings to your API keys.

To view possible endpoint ACLs for a team's API keys:

```bash
curl https://management-api.x.ai/auth/teams/{teamId}/endpoints \\
    -H "Authorization: Bearer <Your Management API Key>"
```

## Validate a management key

You can check if your key is a valid management key. If validation succeeds, the endpoint returns meta information about the management key.
This endpoint does not require any Access Control List (ACL) permissions.

```bash
curl https://management-api.x.ai/auth/management-keys/validation \\
    -H "Authorization: Bearer <Your Management API Key>"
```

## Audit Logs

You can retrieve audit logs for your team. Audit events track changes to team settings, API keys, team membership, and other administrative actions.

### List audit events

To retrieve audit events for a team:

```bash
curl "https://management-api.x.ai/audit/teams/{teamId}/events?pageSize=10" \\
    -H "Authorization: Bearer <Your Management API Key>"
```

You can customize the query parameters:

* `pageSize` - Number of events per page
* `pageToken` - Token for fetching the next page of results
* `eventFilter.userId` - Filter events to a specific user
* `eventFilter.query` - Full-text search in event descriptions
* `eventTimeFrom` - Filter events from a specific time (ISO 8601 format)
* `eventTimeTo` - Filter events up to a specific time (ISO 8601 format)

To fetch the next page of results, use the `nextPageToken` from the response:

```bash
curl "https://management-api.x.ai/audit/teams/{teamId}/events?pageSize=10&pageToken={nextPageToken}" \\
    -H "Authorization: Bearer <Your Management API Key>"
```

Example with time filter:

```bash
curl "https://management-api.x.ai/audit/teams/{teamId}/events?pageSize=50&eventTimeFrom=2025-01-01T00:00:00Z" \\
    -H "Authorization: Bearer <Your Management API Key>"
```


===/developers/migration/models===
#### Key Information

# Migrating to New Models

As we release newer, more advanced models, we are focusing resources on supporting customers with these models and will
be phasing out older versions.

You will see `deprecated` tag by the deprecated model names on [xAI Console](https://console.x.ai) models page. You
should consider moving to a newer model when the model of your choice is being deprecated.

We may transition a `deprecated` model to `obsolete` and discontinue serving the model across our services.
An `obsolete` model will be removed from our [Models and Pricing](../models) page as well as from [xAI Console](https://console.x.ai).

## Moving from an older generation model

When you move from an older model generation to a newer one, you usually won't need to make significant changes to
how you use the API. In your request body, you can switch the `"model"` field from the deprecating model to a current
model on [xAI Console](https://console.x.ai) models page.

The newer models are more performant, but you might want to check if your prompts and other parameters can work with the
new model and modify if necessary.

## Moving to the latest endpoints

When you are setting up to use new models, it might also be a good idea to ensure you're using the latest endpoints. The
latest endpoints have more stable supports for the model functionalities. Endpoints that are marked with `legacy`
might not receive any updates that support newer functionalities.

In general, the following endpoints are recommended: - Text and image input and text output: [Chat Completions](/developers/rest-api-reference/inference/chat#chat-completions) - `/v1/chat/completions` - Text input and image output: [Image Generation](/developers/rest-api-reference/inference/images#image-generation) - `/v1/image/generations` - Tokenization: [Tokenize Text](/developers/rest-api-reference/inference/other#tokenize-text) - `/v1/tokenize-text`


===/developers/model-capabilities/audio/voice-agent===
#### Model Capabilities

# Voice Agent API

Build interactive voice conversations with Grok models using WebSocket. The Grok Voice Agent API accepts audio and text inputs and creates text and audio responses in real-time.

**WebSocket Endpoint:** `wss://api.x.ai/v1/realtime`

The Voice Agent API is billed at a flat per-minute rate. See [Voice Agent API Pricing](/developers/models#voice-agent-api-pricing) for details.

## Authentication

You can authenticate [WebSocket](#connect-via-websocket) connections using the xAI API key or an ephemeral token.

**IMPORTANT:** It is **recommended to use an ephemeral token** when authenticating from the client side (e.g. browser).
If you use the xAI API key to authenticate from the client side, **the client may see the API key and make unauthorized API requests with it.**

### Using API Key Directly - Server Only

For server-side applications where the API key is not exposed to clients, you can authenticate directly with your xAI API key.

**Server-side only:** Only use API key authentication from secure server environments. Never expose your API key in client-side code.

```pythonWithoutSDK
import os
import websockets

XAI_API_KEY = os.getenv("XAI_API_KEY")
base_url = "wss://api.x.ai/v1/realtime"

# Connect with API key in Authorization header
async with websockets.connect(
    uri=base_url,
    ssl=True,
    additional_headers={"Authorization": f"Bearer {XAI_API_KEY}"}
) as websocket:
    # WebSocket connection is now authenticated
    pass
```

```javascriptWithoutSDK
import WebSocket from "ws";

const baseUrl = "wss://api.x.ai/v1/realtime";

// Connect with API key in Authorization header
const ws = new WebSocket(baseUrl, {
  headers: {
    Authorization: "Bearer " + process.env.XAI_API_KEY,
    "Content-Type": "application/json",
  },
});

ws.on("open", () => {
  console.log("Connected with API key authentication");
});
```

### Using Ephemeral Tokens

You need to set up another server or endpoint to fetch the ephemeral token from xAI. The ephemeral token will give the holder a scoped access to resources.

**Endpoint:** `POST https://api.x.ai/v1/realtime/client_secrets`

```bash
curl --url https://api.x.ai/v1/realtime/client_secrets \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer $XAI_API_KEY" \\
  --data '{
    "expires_after": { 
      "seconds": 300 
    }
  }'

# Note: Does not support "session" or "expires_after.anchor" fields
```

```pythonWithoutSDK
# Example ephemeral token endpoint with FastAPI

import os
import httpx
from fastapi import FastAPI

app = FastAPI()
SESSION_REQUEST_URL = "https://api.x.ai/v1/realtime/client_secrets"
XAI_API_KEY = os.getenv("XAI_API_KEY")

@app.post("/session")
async def get_ephemeral_token():
    # Send request to xAI endpoint to retrieve the ephemeral token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=SESSION_REQUEST_URL,
            headers={
                "Authorization": f"Bearer {XAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"expires_after": {"seconds": 300}},
        )
    
    # Return the response body from xAI with ephemeral token
    return response.json()
```

```javascriptWithoutSDK
// Example ephemeral token endpoint with Express

import express from 'express';

const app = express();
const SESSION_REQUEST_URL = "https://api.x.ai/v1/realtime/client_secrets";

app.use(express.json());

app.post("/session", async (req, res) => {
  const r = await fetch(SESSION_REQUEST_URL, {
    method: "POST",
    headers: {
      Authorization: \`Bearer \${process.env.XAI_API_KEY}\`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      expires_after: { seconds: 300 }
    }),
  });
  
  const data = await r.json();
  res.json(data);
});

app.listen(8081);
```

The ephemeral token can be used in the same fashion as an API key:

```pythonWithoutSDK
import os
import websockets

base_url = "wss://api.x.ai/v1/realtime"

# Connect with API key in Authorization header
async with websockets.connect(
    uri=base_url,
    ssl=True,
    additional_headers={"Authorization": f"Bearer {OBTAINED_EPHEMERAL_TOKEN}"}
) as websocket:
    # WebSocket connection is now authenticated
    pass
```

```javascriptWithoutSDK
import WebSocket from "ws";

const baseUrl = "wss://api.x.ai/v1/realtime";

// Connect with API key in Authorization header
const ws = new WebSocket(baseUrl, {
  headers: {
    Authorization: "Bearer " + OBTAINED_EPHEMERAL_TOKEN,
    "Content-Type": "application/json",
  },
});

ws.on("open", () => {
  console.log("Connected with ephemeral token authentication");
});
```

If you need to send the ephemeral token from the browser, you can add the ephemeral token with a prefix `xai-client-secret.` to the `sec-websocket-protocol` header:

```javascriptWithoutSDK
new WebSocket("api.x.ai", [\`xai-client-secret.\${OBTAINED_EPHEMERAL_TOKEN}\`]);
```

## Voice Options

The Grok Voice Agent API supports 5 different voice options, each with distinct characteristics. Select the voice that best fits your application's personality and use case.

### Available Voices

| Voice | Type | Tone | Description | Sample |
|-------|------|------|-------------|:------:|
| **`Ara`** | Female | Warm, friendly | Default voice, balanced and conversational |  |
| **`Rex`** | Male | Confident, clear | Professional and articulate, ideal for business applications |  |
| **`Sal`** | Neutral | Smooth, balanced | Versatile voice suitable for various contexts |  |
| **`Eve`** | Female | Energetic, upbeat | Engaging and enthusiastic, great for interactive experiences |  |
| **`Leo`** | Male | Authoritative, strong | Decisive and commanding, suitable for instructional content |  |

### Selecting a Voice

Specify the voice in your session configuration using the `voice` parameter:

```pythonWithoutSDK
# Configure session with a specific voice
session_config = {
    "type": "session.update",
    "session": {
        "voice": "Ara",  # Choose from: Ara, Rex, Sal, Eve, Leo
        "instructions": "You are a helpful assistant.",
        # Audio format settings (these are the defaults if not specified)
        "audio": {
            "input": {"format": {"type": "audio/pcm", "rate": 24000}},
            "output": {"format": {"type": "audio/pcm", "rate": 24000}}
        }
    }
}

await ws.send(json.dumps(session_config))
```

```javascriptWithoutSDK
// Configure session with a specific voice
const sessionConfig = {
  type: "session.update",
  session: {
    voice: "Ara", // Choose from: Ara, Rex, Sal, Eve, Leo
    instructions: "You are a helpful assistant.",
    // Audio format settings (these are the defaults if not specified)
    audio: {
      input: { format: { type: "audio/pcm", rate: 24000 } },
      output: { format: { type: "audio/pcm", rate: 24000 } }
    }
  }
};

ws.send(JSON.stringify(sessionConfig));
```

## Audio Format

The Grok Voice Agent API supports multiple audio formats for real-time audio streaming. Audio data must be encoded as base64 strings when sent over WebSocket.

### Supported Audio Formats

The API supports three audio format types:

| Format | Encoding | Container Types | Sample Rate |
|--------|----------|-----------------|-------------|
| **`audio/pcm`** | Linear16, Little-endian | Raw, WAV, AIFF | Configurable (see below) |
| **`audio/pcmu`** | G.711 μ-law (Mulaw) | Raw | 8000 Hz |
| **`audio/pcma`** | G.711 A-law | Raw | 8000 Hz |

### Supported Sample Rates

When using `audio/pcm` format, you can configure the sample rate to one of the following supported values:

| Sample Rate | Quality | Description |
|-------------|---------|-------------|
| **8000 Hz** | Telephone | Narrowband, suitable for voice calls |
| **16000 Hz** | Wideband | Good for speech recognition |
| **21050 Hz** | Standard | Balanced quality and bandwidth |
| **24000 Hz** | High (Default) | Recommended for most use cases |
| **32000 Hz** | Very High | Enhanced audio clarity |
| **44100 Hz** | CD Quality | Standard for music / media |
| **48000 Hz** | Professional | Studio-grade audio / Web Browser |

**Note:** Sample rate configuration is only applicable for `audio/pcm` format. The `audio/pcmu` and `audio/pcma` formats use their standard encoding specifications.

### Audio Specifications

| Property | Value | Description |
|----------|-------|-------------|
| **Sample Rate** | Configurable (PCM only) | Sample rate in Hz (see supported rates above) |
| **Default Sample Rate** | 24kHz | 24,000 samples per second (for PCM) |
| **Channels** | Mono | Single channel audio |
| **Encoding** | Base64 | Audio bytes encoded as base64 string |
| **Byte Order** | Little-endian | 16-bit samples in little-endian format (for PCM) |

### Configuring Audio Format

You can configure the audio format and sample rate for both input and output in the session configuration:

```pythonWithoutSDK
# Configure audio format with custom sample rate for input and output
session_config = {
    "type": "session.update",
    "session": {
        "audio": {
            "input": {
                "format": {
                    "type": "audio/pcm",  # or "audio/pcmu" or "audio/pcma"
                    "rate": 16000  # Only applicable for audio/pcm
                }
            },
            "output": {
                "format": {
                    "type": "audio/pcm",  # or "audio/pcmu" or "audio/pcma"
                    "rate": 16000  # Only applicable for audio/pcm
                }
            }
        },
        "instructions": "You are a helpful assistant.",
    }
}

await ws.send(json.dumps(session_config))
```

```javascriptWithoutSDK
// Configure audio format with custom sample rate for input and output
const sessionConfig = {
  type: "session.update",
  session: {
    audio: {
      input: {
        format: {
          type: "audio/pcm", // or "audio/pcmu" or "audio/pcma"
          rate: 16000 // Only applicable for audio/pcm
        }
      },
      output: {
        format: {
          type: "audio/pcm", // or "audio/pcmu" or "audio/pcma"
          rate: 16000 // Only applicable for audio/pcm
        }
      }
    },
    instructions: "You are a helpful assistant.",
  }
};

ws.send(JSON.stringify(sessionConfig));
```

## Connect via WebSocket

You can connect to the realtime model via WebSocket. The audio data needs to be serialized into base64-encoded strings.

The examples below show connecting to the WebSocket endpoint from the server environment.

```pythonWithoutSDK
import asyncio
import json
import os
from typing import Any

import websockets
from websockets.asyncio.client import ClientConnection

XAI_API_KEY = os.getenv("XAI_API_KEY")
base_url = "wss://api.x.ai/v1/realtime"

# Process received message

async def on_message(ws: ClientConnection, message: websockets.Data):
    data = json.loads(message)
    print("Received event:", json.dumps(data, indent=2))

    # Optionally, you can send an event after processing message
    # You can create an event dictionary and send:
    # await send_message(ws, event)

# Send message with an event to server

async def send_message(ws: ClientConnection, event: dict[str, Any]):
    await ws.send(json.dumps(event))

# Example event to be sent on connection open

async def on_open(ws: ClientConnection):
    print("Connected to server.")

    # Configure the session with voice, audio format, and instructions
    session_config = {
        "type": "session.update",
        "session": {
            "voice": "Ara",
            "instructions": "You are a helpful assistant.",
            "turn_detection": {"type": "server_vad"},
            "audio": {
                "input": {"format": {"type": "audio/pcm", "rate": 24000}},
                "output": {"format": {"type": "audio/pcm", "rate": 24000}}
            }
        }
    }
    await send_message(ws, session_config)

    # Send a user text message content
    event = {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": "hello"}],
        },
    }
    await send_message(ws, event)

    # Send an event to request a response, so Grok will start processing on our previous message
    event = {
        "type": "response.create",
        "response": {
            "modalities": ["text", "audio"],
        },
    }
    await send_message(ws, event)

async def main():
    # Connect to the secure websocket
    async with websockets.connect(
        uri=base_url,
        ssl=True,
        additional_headers={"Authorization": f"Bearer {XAI_API_KEY}"}
    ) as websocket:

        # Send request on connection open
        await on_open(ws=websocket)

        while True:
            try:
                # Receive message and print it
                message = await websocket.recv()
                await on_message(websocket, message)
            except websockets.exceptions.ConnectionClosed:
                print("Connection Closed")
                break

asyncio.run(main())
```

```javascriptWithoutSDK
import WebSocket from "ws";

const baseUrl = "wss://api.x.ai/v1/realtime";
const ws = new WebSocket(baseUrl, {
  headers: {
    Authorization: "Bearer " + process.env.XAI_API_KEY,
    "Content-Type": "application/json",
  },
});

ws.on("open", function open() {
  console.log("Connected to server.");

  // Configure the session with voice, audio format, and instructions
  const sessionConfig = {
    type: "session.update",
    session: {
      voice: "Ara",
      instructions: "You are a helpful assistant.",
      turn_detection: { type: "server_vad" },
      audio: {
        input: { format: { type: "audio/pcm", rate: 24000 } },
        output: { format: { type: "audio/pcm", rate: 24000 } }
      }
    }
  };
  ws.send(JSON.stringify(sessionConfig));

  // Create a new conversation message and send to server
  let event = {
    type: "conversation.item.create",
    item: {
      type: "message",
      role: "user",
      content: [{ type: "input_text", text: "hello" }],
    },
  };
  ws.send(JSON.stringify(event));

  // Send an event to request a response, so Grok will start processing on our previous message
  event = {
    type: "response.create",
  };
  ws.send(JSON.stringify(event));
});

ws.on("message", function incoming(message) {
  const serverEvent = JSON.parse(message);
  console.log(serverEvent);
});
```

## Message types

There are a few message types used in interacting with the models. [Client events](#client-events) are sent by user to the server, and [Server events](#server-events) are sent by server to client.

### Client Events

### Server Events

## Session Messages

### Client Events

* **`"session.update"`** - Update session configuration such as system prompt, voice, audio format and search settings

  ```json
  {
      "type": "session.update",
      "session": {
          "instructions": "pass a system prompt here",
          "voice": "Ara",
          "turn_detection": {
              "type": "server_vad" or null,
          },
          "audio": {
              "input": {
                  "format": {
                      "type": "audio/pcm",
                      "rate": 24000
                  }
              },
              "output": {
                  "format": {
                      "type": "audio/pcm",
                      "rate": 24000
                  }
              }
          }
      }
  }
  ```

  **Session Parameters:**

  | Parameter | Type | Description |
  |-----------|------|-------------|
  | `instructions` | string | System prompt |
  | `voice` | string | Voice selection: `Ara`, `Rex`, `Sal`, `Eve`, `Leo` (see [Voice Options](#voice-options)) |
  | `turn_detection.type` | string | null | `"server_vad"` for automatic detection, `null` for manual text turns |
  | `audio.input.format.type` | string | Input format: `"audio/pcm"`, `"audio/pcmu"`, or `"audio/pcma"` |
  | `audio.input.format.rate` | number | Input sample rate (PCM only): 8000, 16000, 21050, 24000, 32000, 44100, 48000 |
  | `audio.output.format.type` | string | Output format: `"audio/pcm"`, `"audio/pcmu"`, or `"audio/pcma"` |
  | `audio.output.format.rate` | number | Output sample rate (PCM only): 8000, 16000, 21050, 24000, 32000, 44100, 48000 |

### Receiving and Playing Audio

Decode and play base64 PCM16 audio received from the API. Use the same sample rate as configured:

```pythonWithoutSDK
import base64
import numpy as np

# Configure session with 16kHz sample rate for lower bandwidth (input and output)
session_config = {
    "type": "session.update",
    "session": {
        "instructions": "You are a helpful assistant.",
        "voice": "Ara",
        "turn_detection": {
            "type": "server_vad",
        },
        "audio": {
            "input": {
                "format": {
                    "type": "audio/pcm",
                    "rate": 16000  # 16kHz for lower bandwidth usage
                }
            },
            "output": {
                "format": {
                    "type": "audio/pcm",
                    "rate": 16000  # 16kHz for lower bandwidth usage
                }
            }
        }
    }
}
await ws.send(json.dumps(session_config))

# When processing audio, use the same sample rate
SAMPLE_RATE = 16000

# Convert audio data to PCM16 and base64
def audio_to_base64(audio_data: np.ndarray) -> str:
    """Convert float32 audio array to base64 PCM16 string."""
    # Normalize to [-1, 1] and convert to int16
    audio_int16 = (audio_data * 32767).astype(np.int16)
    # Encode to base64
    audio_bytes = audio_int16.tobytes()
    return base64.b64encode(audio_bytes).decode('utf-8')

# Convert base64 PCM16 to audio data
def base64_to_audio(base64_audio: str) -> np.ndarray:
    """Convert base64 PCM16 string to float32 audio array."""
    # Decode base64
    audio_bytes = base64.b64decode(base64_audio)
    # Convert to int16 array
    audio_int16 = np.frombuffer(audio_bytes, dtype=np.int16)
    # Normalize to [-1, 1]
    return audio_int16.astype(np.float32) / 32768.0
```

```javascriptWithoutSDK
// Configure session with 16kHz sample rate for lower bandwidth (input and output)
const sessionConfig = {
  type: "session.update",
  session: {
    instructions: "You are a helpful assistant.",
    voice: "Ara",
    turn_detection: { type: "server_vad" },
    audio: {
      input: {
        format: {
          type: "audio/pcm",
          rate: 16000 // 16kHz for lower bandwidth usage
        }
      },
      output: {
        format: {
          type: "audio/pcm",
          rate: 16000 // 16kHz for lower bandwidth usage
        }
      }
    }
  }
};
ws.send(JSON.stringify(sessionConfig));

// When processing audio, use the same sample rate
const SAMPLE_RATE = 16000;

// Create AudioContext with matching sample rate
const audioContext = new AudioContext({ sampleRate: SAMPLE_RATE });

// Helper function to convert Float32Array to base64 PCM16
function float32ToBase64PCM16(float32Array) {
  const pcm16 = new Int16Array(float32Array.length);
  for (let i = 0; i < float32Array.length; i++) {
    const s = Math.max(-1, Math.min(1, float32Array[i]));
    pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
  }
  const bytes = new Uint8Array(pcm16.buffer);
  return btoa(String.fromCharCode(...bytes));
}

// Helper function to convert base64 PCM16 to Float32Array
function base64PCM16ToFloat32(base64String) {
  const binaryString = atob(base64String);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  const pcm16 = new Int16Array(bytes.buffer);
  const float32 = new Float32Array(pcm16.length);
  for (let i = 0; i < pcm16.length; i++) {
    float32[i] = pcm16[i] / 32768.0;
  }
  return float32;
}
```

### Server Events

* **`"session.updated"`** - Acknowledge the client's `"session.update"` message that the session has been updated
  ```json
  {
      "event_id": "event_123",
      "type": "session.updated",
      "session": {
          "instructions": "You are a helpful assistant.",
          "voice": "Ara",
          "turn_detection": {
              "type": "server_vad"
          }
      }
  }
  ```

## Using Tools with Grok Voice Agent API

The Grok Voice Agent API supports various tools that can be configured in your session to enhance the capabilities of your voice agent. Tools can be configured in the `session.update` message.

### Available Tool Types

* **Collections Search (`file_search`)** - Search through your uploaded document collections
* **Web Search (`web_search`)** - Search the web for current information
* **X Search (`x_search`)** - Search X (Twitter) for posts and information
* **Custom Functions** - Define your own function tools with JSON schemas

### Configuring Tools in Session

Tools are configured in the `tools` array of the session configuration. Here are examples showing how to configure different tool types:

### Collections Search with `file_search`

Use the `file_search` tool to enable your voice agent to search through document collections. You'll need to create a collection first using the [Collections API](/developers/rest-api-reference/collections).

```pythonWithoutSDK
COLLECTION_ID = "your-collection-id"  # Replace with your collection ID

session_config = {
    "type": "session.update",
    "session": {
        ...
        "tools": [
            {
                "type": "file_search",
                "vector_store_ids": [COLLECTION_ID],
                "max_num_results": 10,
            },
        ],
    },
}
```

```javascriptWithoutSDK
const COLLECTION_ID = "your-collection-id"; // Replace with your collection ID

const sessionConfig = {
    type: "session.update",
    session: {
        ...
        tools: [
            {
                type: "file_search",
                vector_store_ids: [COLLECTION_ID],
                max_num_results: 10,
            },
        ],
    },
};
```

### Web Search and X Search

Configure web search and X search tools to give your voice agent access to current information from the web and X (Twitter).

```pythonWithoutSDK
session_config = {
    "type": "session.update",
    "session": {
        ...
        "tools": [
            {
                "type": "web_search",
            },
            {
                "type": "x_search",
                "allowed_x_handles": ["elonmusk", "xai"],
            },
        ],
    },
}
```

```javascriptWithoutSDK
const sessionConfig = {
    type: "session.update",
    session: {
        ...
        tools: [
            {
                type: "web_search",
            },
            {
                type: "x_search",
                allowed_x_handles: ["elonmusk", "xai"],
            },
        ],
    },
};
```

### Custom Function Tools

You can define custom function tools with JSON schemas to extend your voice agent's capabilities.

```pythonWithoutSDK
session_config = {
    "type": "session.update",
    "session": {
        ...
        "tools": [
            {
                "type": "function",
                "name": "generate_random_number",
                "description": "Generate a random number between min and max values",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "min": {
                            "type": "number",
                            "description": "Minimum value (inclusive)",
                        },
                        "max": {
                            "type": "number",
                            "description": "Maximum value (inclusive)",
                        },
                    },
                    "required": ["min", "max"],
                },
            },
        ],
    },
}
```

```javascriptWithoutSDK
const sessionConfig = {
    type: "session.update",
    session: {
        ...
        tools: [
            {
                type: "function",
                name: "generate_random_number",
                description: "Generate a random number between min and max values",
                parameters: {
                    type: "object",
                    properties: {
                        min: {
                            type: "number",
                            description: "Minimum value (inclusive)",
                        },
                        max: {
                            type: "number",
                            description: "Maximum value (inclusive)",
                        },
                    },
                    required: ["min", "max"],
                },
            },
        ],
    },
};
```

### Combining Multiple Tools

You can combine multiple tool types in a single session configuration:

```pythonWithoutSDK
session_config = {
    "type": "session.update",
    "session": {
        ...
        "tools": [
            {
                "type": "file_search",
                "vector_store_ids": ["your-collection-id"],
                "max_num_results": 10,
            },
            {
                "type": "web_search",
            },
            {
                "type": "x_search",
            },
            {
                "type": "function",
                "name": "generate_random_number",
                "description": "Generate a random number",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "min": {"type": "number"},
                        "max": {"type": "number"},
                    },
                    "required": ["min", "max"],
                },
            },
        ],
    },
}
```

```javascriptWithoutSDK
const sessionConfig = {
    type: "session.update",
    session: {
        ...
        tools: [
            {
                type: "file_search",
                vector_store_ids: ["your-collection-id"],
                max_num_results: 10,
            },
            {
                type: "web_search",
            },
            {
                type: "x_search",
            },
            {
                type: "function",
                name: "generate_random_number",
                description: "Generate a random number",
                parameters: {
                    type: "object",
                    properties: {
                        min: { type: "number" },
                        max: { type: "number" },
                    },
                    required: ["min", "max"],
                },
            },
        ],
    },
};
```

For more details on Collections, see the [Collections API documentation](/developers/rest-api-reference/collections). For search tool parameters and options, see the [Web Search](/developers/tools/web-search) and [X Search](/developers/tools/x-search) guides.

### Handling Function Call Responses

When you define custom function tools, the voice agent will call these functions during conversation. You need to handle these function calls, execute them, and return the results to continue the conversation.

### Function Call Flow

1. **Agent decides to call a function** → sends `response.function_call_arguments.done` event
2. **Your code executes the function** → processes the arguments and generates a result
3. **Send result back to agent** → sends `conversation.item.create` with the function output
4. **Request continuation** → sends `response.create` to let the agent continue

### Complete Example

```pythonWithoutSDK
import json
import websockets

# Define your function implementations
def get_weather(location: str, units: str = "celsius"):
    """Get current weather for a location"""
    # In production, call a real weather API
    return {
        "location": location,
        "temperature": 22,
        "units": units,
        "condition": "Sunny",
        "humidity": 45
    }

def book_appointment(date: str, time: str, service: str):
    """Book an appointment"""
    # In production, interact with your booking system
    import random
    confirmation = f"CONF{random.randint(1000, 9999)}"
    return {
        "status": "confirmed",
        "confirmation_code": confirmation,
        "date": date,
        "time": time,
        "service": service
    }

# Map function names to implementations
FUNCTION_HANDLERS = {
    "get_weather": get_weather,
    "book_appointment": book_appointment
}

async def handle_function_call(ws, event):
    """Handle function call from the voice agent"""
    function_name = event["name"]
    call_id = event["call_id"]
    arguments = json.loads(event["arguments"])
    
    print(f"Function called: {function_name} with args: {arguments}")
    
    # Execute the function
    if function_name in FUNCTION_HANDLERS:
        result = FUNCTION_HANDLERS[function_name](**arguments)
        
        # Send result back to agent
        await ws.send(json.dumps({
            "type": "conversation.item.create",
            "item": {
                "type": "function_call_output",
                "call_id": call_id,
                "output": json.dumps(result)
            }
        }))
        
        # Request agent to continue with the result
        await ws.send(json.dumps({
            "type": "response.create"
        }))
    else:
        print(f"Unknown function: {function_name}")

# In your WebSocket message handler
async def on_message(ws, message):
    event = json.loads(message)
    
    # Listen for function calls
    if event["type"] == "response.function_call_arguments.done":
        await handle_function_call(ws, event)
    elif event["type"] == "response.output_audio.delta":
        # Handle audio response
        pass
```

```javascriptWithoutSDK
// Define your function implementations
const functionHandlers = {
  get_weather: async (args) => {
    // In production, call a real weather API
    return {
      location: args.location,
      temperature: 22,
      units: args.units || "celsius",
      condition: "Sunny",
      humidity: 45
    };
  },
  
  book_appointment: async (args) => {
    // In production, interact with your booking system
    const confirmation = \`CONF\${Math.floor(Math.random() * 9000) + 1000}\`;
    return {
      status: "confirmed",
      confirmation_code: confirmation,
      date: args.date,
      time: args.time,
      service: args.service
    };
  }
};

// Handle function calls from the voice agent
async function handleFunctionCall(ws, event) {
  const functionName = event.name;
  const callId = event.call_id;
  const args = JSON.parse(event.arguments);
  
  console.log(\`Function called: \${functionName\} with args:\`, args);
  
  // Execute the function
  const handler = functionHandlers[functionName];
  if (handler) {
    const result = await handler(args);
    
    // Send result back to agent
    ws.send(JSON.stringify({
      type: "conversation.item.create",
      item: {
        type: "function_call_output",
        call_id: callId,
        output: JSON.stringify(result)
      }
    }));
    
    // Request agent to continue with the result
    ws.send(JSON.stringify({
      type: "response.create"
    }));
  } else {
    console.error(\`Unknown function: \${functionName\}\`);
  }
}

// In your WebSocket message handler
ws.on("message", (message) => {
  const event = JSON.parse(message);
  
  // Listen for function calls
  if (event.type === "response.function_call_arguments.done") {
    handleFunctionCall(ws, event);
  } else if (event.type === "response.output_audio.delta") {
    // Handle audio response
  }
});
```

### Function Call Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `response.function_call_arguments.done` | Server → Client | Function call triggered with complete arguments |
| `conversation.item.create` (function\_call\_output) | Client → Server | Send function execution result back |
| `response.create` | Client → Server | Request agent to continue processing |

### Real-World Example: Weather Query

When a user asks "What's the weather in San Francisco?", here's the complete flow:

| Step | Direction | Event | Description |
|:----:|:---------:|-------|-------------|
| 1 | Client → Server | `input_audio_buffer.append` | User speaks: "What's the weather in San Francisco?" |
| 2 | Server → Client | `response.function_call_arguments.done` | Agent decides to call `get_weather` with `location: "San Francisco"` |
| 3 | Client → Server | `conversation.item.create` | Your code executes `get_weather()` and sends result: `{temperature: 68, condition: "Sunny"}` |
| 4 | Client → Server | `response.create` | Request agent to continue with function result |
| 5 | Server → Client | `response.output_audio.delta` | Agent responds: "The weather in San Francisco is currently 68°F and sunny." |

Function calls happen automatically during conversation flow. The agent decides when to call functions based on the function descriptions and conversation context.

## Conversation messages

### Server Events

* **`"conversation.created"`** - The first message at connection. Notifies the client that a conversation session has been created

  ```json
  {
      "event_id": "event_9101",
      "type": "conversation.created",
      "conversation": {
          "id": "conv_001",
          "object": "realtime.conversation"
      }
  }
  ```

## Conversation item messages

### Client

* `"conversation.item.create"`: Create a new user message with text.

  ```json
  {
      "type": "conversation.item.create",
      "previous_item_id": "", // Optional, used to insert turn into history
      "item": {
          "type": "message",
          "role": "user",
          "content": [
              {
                  "type": "input_text",
                  "text": "Hello, how are you?"
              }
          ]
      }
  }
  ```

### Server

* `"conversation.item.added"`: Responding to the client that a new user message has been added to conversation history, or if an assistance response has been added to conversation history.

  ```json
  {
    "event_id": "event_1920",
    "type": "conversation.item.added",
    "previous_item_id": "msg_002",
    "item": {
      "id": "msg_003",
      "object": "realtime.item",
      "type": "message",
      "status": "completed",
      "role": "user",
      "content": [
        {
          "type": "input_audio",
          "transcript": "hello how are you"
        }
      ]
    }
  }
  ```

* `"conversation.item.input_audio_transcription.completed"`: Notify the client the audio transcription for input has been completed.

  ```json
  {
      "event_id": "event_2122",
      "type": "conversation.item.input_audio_transcription.completed",
      "item_id": "msg_003",
      "transcript": "Hello, how are you?"
  }
  ```

## Input audio buffer messages

### Client

* `"input_audio_buffer.append"`: Append chunks of audio data to the buffer. The audio needs to be base64-encoded. The server does not send back corresponding message.

  ```json
  {
      "type": "input_audio_buffer.append",
      "audio": "<Base64EncodedAudioData>"
  }
  ```

* `"input_audio_buffer.clear"`: Clear input audio buffer. Server sends back `"input_audio_buffer.cleared"` message.

  ```json
  {
    "type": "input_audio_buffer.clear"
  }
  ```

* `"input_audio_buffer.commit"`: Create a new user message by committing the audio buffer created by previous `"input_audio_buffer.append"` messages. Confirmed by `"input_audio_buffer.committed"` from server.

  Only available when `"turn_detection"` setting in session is `"type": null`. Otherwise the
  conversation turn will be automatically committed by VAD on the server.

  ```json
  {
      "type": "input_audio_buffer.commit"
  }
  ```

### Server

* `"input_audio_buffer.speech_started"`: Notify the client the server's VAD has detected the start of a speech.

  Only available when `"turn_detection"` setting in session is `"type": "server_vad"`.

  ```json
  {
    "event_id": "event_1516",
    "type": "input_audio_buffer.speech_started",
    "item_id": "msg_003"
  }
  ```

* `"input_audio_buffer.speech_stopped"`: Notify the client the server's VAD has detected the end of a speech.

  Only available when `"turn_detection"` setting in session is `"type": "server_vad"`.

  ```json
  {
    "event_id": "event_1516",
    "type": "input_audio_buffer.speech_stopped",
    "item_id": "msg_003"
  }
  ```

* `"input_audio_buffer.cleared"`: Input audio buffer has been cleared.

  ```json
  {
    "event_id": "event_1516",
    "type": "input_audio_buffer.cleared"
  }
  ```

* `"input_audio_buffer.committed"`: Input audio buffer has been committed.

  ```json
  {
    "event_id": "event_1121",
    "type": "input_audio_buffer.committed",
    "previous_item_id": "msg_001",
    "item_id": "msg_002"
  }
  ```

## Response messages

### Client

* `"response.create"`: Request the server to create a new assistant response when using client side vad. (This is handled automatically when using server side vad.)

  ```json
  {
      "type": "response.create"
  }
  ```

### Server

* `"response.created"`: A new assistant response turn is in progress. Audio delta created from this assistant turn will have the same response id. Followed by `"response.output_item.added"`.

  ```json
  {
    "event_id": "event_2930",
    "type": "response.created",
    "response": {
      "id": "resp_001",
      "object": "realtime.response",
      "status": "in_progress",
      "output": []
    }
  }
  ```

* `"response.output_item.added"`: A new assistant response is added to message history.

  ```json
  {
    "event_id": "event_3334",
    "type": "response.output_item.added",
    "response_id": "resp_001",
    "output_index": 0,
    "item": {
      "id": "msg_007",
      "object": "realtime.item",
      "type": "message",
      "status": "in_progress",
      "role": "assistant",
      "content": []
    }
  }
  ```

* `"response.done"`: The assistant's response is completed. Sent after all the `"response.output_audio_transcript.done"` and `"response.output_audio.done"` messages. Ready for the client to add a new conversation item.

  ```json
  {
      "event_id": "event_3132",
      "type": "response.done",
      "response": {
          "id": "resp_001",
          "object": "realtime.response",
          "status": "completed",
      }
  }
  ```

## Response audio and transcription messages

### Client

The client does not need to send messages to get these audio and transcription responses. They would be automatically created following `"response.create"` message.

### Server

* `"response.output_audio_transcript.delta"`: Audio transcript delta of the assistant response.
  ```json
  {
    "event_id": "event_4950",
    "type": "response.output_audio_transcript.delta",
    "response_id": "resp_001",
    "item_id": "msg_008",
    "delta": "Text response..."
  }
  ```

* `"response.output_audio_transcript.done"`: The audio transcript delta of the assistant response has finished generating.

  ```json
  {
    "event_id": "event_5152",
    "type": "response.output_audio_transcript.done",
    "response_id": "resp_001",
    "item_id": "msg_008"
  }
  ```

* `"response.output_audio.delta"`: The audio stream delta of the assistant response.
  ```json
  {
    "event_id": "event_4950",
    "type": "response.output_audio.delta",
    "response_id": "resp_001",
    "item_id": "msg_008",
    "output_index": 0,
    "content_index": 0,
    "delta": "<Base64EncodedAudioDelta>"
  }
  ```

* `"response.output_audio.done"`: Notifies client that the audio for this turn has finished generating.
  ```json
  {
      "event_id": "event_5152",
      "type": "response.output_audio.done",
      "response_id": "resp_001",
      "item_id": "msg_008",
  }
  ```


===/developers/model-capabilities/audio/voice===
#### Model Capabilities

# Voice Overview

We're introducing a new API for voice interactions with Grok. We're initially launching with the Grok Voice Agent API and will soon be launching dedicated speech-to-text and text-to-speech APIs.

## Grok Voice Agent API

Build powerful real-time voice applications with the Grok Voice Agent API. Create interactive voice conversations with Grok models via WebSocket for voice assistants, phone agents, and interactive voice applications.

**WebSocket Endpoint:** `wss://api.x.ai/v1/realtime`

## <NotificationBanner variant={"info"}>The Voice Agent API is only available in `us-east-1` region.</NotificationBanner>

### Enterprise Ready

Optimized for enterprise use cases across Customer Support, Medical, Legal, Finance, Insurance, and more. The Grok Voice Agent API delivers the reliability and precision that regulated industries demand.

* **Telephony** - Connect to platforms like Twilio, Vonage, and other SIP providers
* **Tool Calling** - CRMs, calendars, ticketing systems, databases, and custom APIs
* **Multilingual** - Serve global customers in their native language with natural accents
* **Low Latency** - Real-time responses for natural, human-like conversations
* **Accuracy** - Precise transcription and understanding of critical information:
  * Industry-specific terminology including medical, legal, and financial vocabulary
  * Email addresses, dates, and alphanumeric codes
  * Names, addresses, and phone numbers

### Getting Started

The Grok Voice Agent API enables interactive voice conversations with Grok models via WebSocket. Perfect for building voice assistants, phone agents, and interactive voice applications.

**Use Cases:**

* Voice Assistants for web and mobile
* AI-powered phone systems with Twilio
* Real-time customer support
* Interactive Voice Response (IVR) systems

[Documentation →](/developers/model-capabilities/audio/voice-agent)

### Low Latency

Built for real-time conversations. The Grok Voice Agent API is optimized for minimal response times, enabling natural back-and-forth dialogue without awkward pauses. Stream audio bidirectionally over WebSocket for instant voice-to-voice interactions that feel like talking to a human.

### Multilingual with Natural Accents

The Grok Voice Agent API speaks over 100 languages with native-quality accents. The model automatically detects the input language and responds naturally in the same language-no configuration required.

### Supported Languages

English, Spanish, French, German, Italian, Portuguese, Dutch, Russian, Chinese (Mandarin), Japanese, Korean, Arabic, Hindi, Turkish, Polish, Swedish, Danish, Norwegian, Finnish, Czech, and many more.

Each language features natural pronunciation, appropriate intonation patterns, and culturally-aware speech rhythms. You can also specify a preferred language or accent in your system instructions for consistent multilingual experiences.

### Tool Calling

Extend your voice agent's capabilities with powerful built-in tools that execute during conversations:

* **Web Search** - Real-time internet search for current information, news, and facts
* **X Search** - Search posts, trends, and discussions from X
* **Collections** - RAG-powered search over your uploaded documents and knowledge bases
* **Custom Functions** - Define your own tools with JSON schemas for booking, lookups, calculations, and more

Tools are called automatically based on conversation context. Your voice agent can search the web, query your documents, and execute custom business logic-all while maintaining a natural conversation flow.

### Voice Personalities

Choose from 5 distinct voices, each with unique characteristics suited to different applications:

| Voice | Type | Tone | Description | Sample |
|-------|------|------|-------------|:------:|
| **`Ara`** | Female | Warm, friendly | Default voice, balanced and conversational |  |
| **`Rex`** | Male | Confident, clear | Professional and articulate, ideal for business applications |  |
| **`Sal`** | Neutral | Smooth, balanced | Versatile voice suitable for various contexts |  |
| **`Eve`** | Female | Energetic, upbeat | Engaging and enthusiastic, great for interactive experiences |  |
| **`Leo`** | Male | Authoritative, strong | Decisive and commanding, suitable for instructional content |  |

### Flexible Audio Formats

Support for multiple audio formats and sample rates to match your application's requirements:

* **PCM (Linear16)** - High-quality audio with configurable sample rates (8kHz–48kHz)
* **G.711 μ-law** - Optimized for telephony applications
* **G.711 A-law** - Standard for international telephony

### Example Applications

Complete working examples are available demonstrating various voice integration patterns:

#### Web Voice Agent

Real-time voice chat in the browser with React frontend and Python/Node.js backends.

**Architecture:**

```
Browser (React) ←WebSocket→ Backend (FastAPI/Express) ←WebSocket→ xAI API
```

**Features:**

* Real-time audio streaming
* Visual transcript display
* Debug console for development
* Interchangeable backends

[GitHub →](https://github.com/xai-org/xai-cookbook/tree/main/voice-examples/agent/web)

#### Phone Voice Agent (Twilio)

AI-powered phone system using Twilio integration.

**Architecture:**

```
Phone Call ←SIP→ Twilio ←WebSocket→ Node.js Server ←WebSocket→ xAI API
```

**Features:**

* Phone call integration
* Real-time voice processing
* Function/tool calling support
* Production-ready architecture

[GitHub →](https://github.com/xai-org/xai-cookbook/tree/main/voice-examples/agent/telephony)

#### WebRTC Voice Agent

The Grok Voice Agent API uses WebSocket connections. Direct WebRTC connections are not available currently.

You can use a WebRTC server to connect the client to a server that then connects to the Grok Voice Agent API.

**Architecture:**

```
Browser (React) ←WebRTC→ Backend (Express) ←WebSocket→ xAI API
```

**Features:**

* Real-time audio streaming
* Visual transcript display
* Debug console for development
* WebRTC backend handles all WebSocket connections to xAI API

[GitHub →](https://github.com/xai-org/xai-cookbook/tree/main/voice-examples/agent/webrtc)

### Third Party Integrations

Build voice agents using popular third-party frameworks and platforms that integrate with the Grok Voice Agent API.

**LiveKit**

Build real-time voice agents using LiveKit's open-source framework with native Grok Voice Agent API integration and WebRTC Support.

[Docs →](https://docs.livekit.io/agents/integrations/xai/) | [GitHub →](https://github.com/livekit/agents/tree/main/livekit-plugins/livekit-plugins-xai)

**Voximplant**

Build real-time voice agents using Voximplant's open-source framework with native Grok Voice Agent API integration and SIP Support.

[Docs →](https://voximplant.com/products/grok-client) | [GitHub →](https://github.com/voximplant/grok-voice-agent-example)

**Pipecat**

Build real-time voice agents using Pipecat's open-source framework with native Grok Voice Agent API integration and advanced conversation management.

[Docs →](https://docs.pipecat.ai/server/services/s2s/grok) | [GitHub →](https://github.com/pipecat-ai/pipecat/blob/main/examples/foundational/51-grok-realtime.py)


===/developers/model-capabilities/files/chat-with-files===
#### Model Capabilities

# Chat with Files

Once you've uploaded files, you can reference them in conversations using the `file()` helper function in the xAI Python SDK. When files are attached, the system automatically enables document search capabilities, transforming your request into an agentic workflow.

## Basic Chat with a Single File

Reference an uploaded file in a conversation to let the model search through it for relevant information.

```pythonXAI
import os
from xai_sdk import Client
from xai_sdk.chat import user, file

client = Client(api_key=os.getenv("XAI_API_KEY"))

# Upload a document
document_content = b"""Quarterly Sales Report - Q4 2024

Revenue Summary:
- Total Revenue: $5.2M
- Year-over-Year Growth: +18%
- Quarter-over-Quarter Growth: +7%

Top Performing Products:
- Product A: $2.1M revenue (+25% YoY)
- Product B: $1.8M revenue (+12% YoY)
- Product C: $1.3M revenue (+15% YoY)
"""

uploaded_file = client.files.upload(document_content, filename="sales_report.txt")

# Create a chat with the file attached
chat = client.chat.create(model="grok-4-fast")
chat.append(user("What was the total revenue in this report?", file(uploaded_file.id)))

# Get the response
response = chat.sample()

print(f"Answer: {response.content}")
print(f"\\nUsage: {response.usage}")

# Clean up
client.files.delete(uploaded_file.id)
```

```pythonOpenAISDK
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

# Upload a file
document_content = b"""Quarterly Sales Report - Q4 2024

Revenue Summary:
- Total Revenue: $5.2M
- Year-over-Year Growth: +18%
"""

with open("temp_sales.txt", "wb") as f:
    f.write(document_content)

with open("temp_sales.txt", "rb") as f:
    uploaded_file = client.files.create(file=f, purpose="assistants")

# Create a chat with the file
response = client.responses.create(
    model="grok-4-fast",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "What was the total revenue in this report?"},
                {"type": "input_file", "file_id": uploaded_file.id}
            ]
        }
    ]
)

final_answer = response.output[-1].content[0].text

print(f"Answer: {final_answer}")

# Clean up
client.files.delete(uploaded_file.id)
```

```pythonRequests
import os
import requests

api_key = os.getenv("XAI_API_KEY")
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Upload file first
upload_url = "https://api.x.ai/v1/files"
files = {"file": ("sales_report.txt", b"Total Revenue: $5.2M")}
data = {"purpose": "assistants"}
upload_response = requests.post(upload_url, headers={"Authorization": f"Bearer {api_key}"}, files=files, data=data)
file_id = upload_response.json()["id"]

# Create chat with file
chat_url = "https://api.x.ai/v1/responses"
payload = {
    "model": "grok-4-fast",
    "input": [
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": "What was the total revenue in this report?"},
                {"type": "input_file", "file_id": file_id}
            ]
        }
    ]
}
response = requests.post(chat_url, headers=headers, json=payload)
print(response.json())
```

```bash
# First upload the file
FILE_ID=$(curl https://api.x.ai/v1/files \\
  -H "Authorization: Bearer $XAI_API_KEY" \\
  -F file=@sales_report.txt \\
  -F purpose=assistants | jq -r '.id')

# Then use it in chat
curl -X POST "https://api.x.ai/v1/responses" \\
  -H "Authorization: Bearer $XAI_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d "{
    \\"model\\": \\"grok-4-fast\\",
    \\"input\\": [
      {
        \\"role\\": \\"user\\",
        \\"content\\": [
          {\\"type\\": \\"input_text\\", \\"text\\": \\"What was the total revenue in this report?\\"},
          {\\"type\\": \\"input_file\\", \\"file_id\\": \\"$FILE_ID\\"}
        ]
      }
    ]
  }"
```

## Streaming Chat with Files

Get real-time responses while the model searches through your documents.

```pythonXAI
import os
from xai_sdk import Client
from xai_sdk.chat import user, file

client = Client(api_key=os.getenv("XAI_API_KEY"))

# Upload a document
document_content = b"""Product Specifications:
- Model: XR-2000
- Weight: 2.5 kg
- Dimensions: 30cm x 20cm x 10cm
- Power: 100W
- Features: Wireless connectivity, LCD display, Energy efficient
"""

uploaded_file = client.files.upload(document_content, filename="specs.txt")

# Create chat with streaming
chat = client.chat.create(model="grok-4-fast")
chat.append(user("What is the weight of the XR-2000?", file(uploaded_file.id)))

# Stream the response
is_thinking = True
for response, chunk in chat.stream():
    # Show tool calls as they happen
    for tool_call in chunk.tool_calls:
        print(f"\\nSearching: {tool_call.function.name}")
    
    if response.usage.reasoning_tokens and is_thinking:
        print(f"\\rThinking... ({response.usage.reasoning_tokens} tokens)", end="", flush=True)
    
    if chunk.content and is_thinking:
        print("\\n\\nAnswer:")
        is_thinking = False
    
    if chunk.content:
        print(chunk.content, end="", flush=True)

print(f"\\n\\nUsage: {response.usage}")

# Clean up
client.files.delete(uploaded_file.id)
```

## Multiple File Attachments

Query across multiple documents simultaneously.

```pythonXAI
import os
from xai_sdk import Client
from xai_sdk.chat import user, file

client = Client(api_key=os.getenv("XAI_API_KEY"))

# Upload multiple documents
file1_content = b"Document 1: The project started in January 2024."
file2_content = b"Document 2: The project budget is $500,000."
file3_content = b"Document 3: The team consists of 5 engineers and 2 designers."

file1 = client.files.upload(file1_content, filename="timeline.txt")
file2 = client.files.upload(file2_content, filename="budget.txt")
file3 = client.files.upload(file3_content, filename="team.txt")

# Create chat with multiple files
chat = client.chat.create(model="grok-4-fast")
chat.append(
    user(
        "Based on these documents, when did the project start, what is the budget, and how many people are on the team?",
        file(file1.id),
        file(file2.id),
        file(file3.id),
    )
)

response = chat.sample()

print(f"Answer: {response.content}")
print("\\nDocuments searched: 3")
print(f"Usage: {response.usage}")

# Clean up
client.files.delete(file1.id)
client.files.delete(file2.id)
client.files.delete(file3.id)
```

## Multi-Turn Conversations with Files

Maintain context across multiple questions about the same documents. Use encrypted content to preserve file context efficiently across multiple turns.

```pythonXAI
import os
from xai_sdk import Client
from xai_sdk.chat import user, file

client = Client(api_key=os.getenv("XAI_API_KEY"))

# Upload an employee record
document_content = b"""Employee Information:
Name: Alice Johnson
Department: Engineering
Years of Service: 5
Performance Rating: Excellent
Skills: Python, Machine Learning, Cloud Architecture
Current Project: AI Platform Redesign
"""

uploaded_file = client.files.upload(document_content, filename="employee.txt")

# Create a multi-turn conversation with encrypted content
chat = client.chat.create(
    model="grok-4-fast",
    use_encrypted_content=True,  # Enable encrypted content for efficient multi-turn
)

# First turn: Ask about the employee name
chat.append(user("What is the employee's name?", file(uploaded_file.id)))
response1 = chat.sample()
print("Q1: What is the employee's name?")
print(f"A1: {response1.content}\\n")

# Add the response to conversation history
chat.append(response1)

# Second turn: Ask about department (agentic context is retained via encrypted content)
chat.append(user("What department does this employee work in?"))
response2 = chat.sample()
print("Q2: What department does this employee work in?")
print(f"A2: {response2.content}\\n")

# Add the response to conversation history
chat.append(response2)

# Third turn: Ask about skills
chat.append(user("What skills does this employee have?"))
response3 = chat.sample()
print("Q3: What skills does this employee have?")
print(f"A3: {response3.content}\\n")

# Clean up
client.files.delete(uploaded_file.id)
```

## Combining Files with Other Modalities

You can combine file attachments with images and other content types in a single message.

```pythonXAI
import os
from xai_sdk import Client
from xai_sdk.chat import user, file, image

client = Client(api_key=os.getenv("XAI_API_KEY"))

# Upload a text document with cat care information
text_content = b"Cat Care Guide: Cats require daily grooming, especially long-haired breeds. Regular brushing helps prevent matting and reduces shedding."
text_file = client.files.upload(text_content, filename="cat-care.txt")

# Use both file and image in the same message
chat = client.chat.create(model="grok-4-fast")
chat.append(
    user(
        "Based on the attached care guide, do you have any advice about the pictured cat?",
        file(text_file.id),
        image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/Cat03.jpg/1200px-Cat03.jpg"),
    )
)

response = chat.sample()

print(f"Analysis: {response.content}")
print(f"\\nUsage: {response.usage}")

# Clean up
client.files.delete(text_file.id)
```

## Combining Files with Code Execution

For data analysis tasks, you can attach data files and enable the code execution tool. This allows Grok to write and run Python code to analyze and process your data.

```pythonXAI
import os
from xai_sdk import Client
from xai_sdk.chat import user, file
from xai_sdk.tools import code_execution

client = Client(api_key=os.getenv("XAI_API_KEY"))

# Upload a CSV data file
csv_content = b"""product,region,revenue,units_sold
Product A,North,245000,1200
Product A,South,189000,950
Product A,East,312000,1500
Product A,West,278000,1350
Product B,North,198000,800
Product B,South,156000,650
Product B,East,234000,950
Product B,West,201000,850
Product C,North,167000,700
Product C,South,134000,550
Product C,East,198000,800
Product C,West,176000,725
"""

data_file = client.files.upload(csv_content, filename="sales_data.csv")

# Create chat with both file attachment and code execution
chat = client.chat.create(
    model="grok-4-fast",
    tools=[code_execution()],  # Enable code execution
)

chat.append(
    user(
        "Analyze this sales data and calculate: 1) Total revenue by product, 2) Average units sold by region, 3) Which product-region combination has the highest revenue",
        file(data_file.id)
    )
)

# Stream the response to see code execution in real-time
is_thinking = True
for response, chunk in chat.stream():
    for tool_call in chunk.tool_calls:
        if tool_call.function.name == "code_execution":
            print("\\n[Executing Code]")
    
    if response.usage.reasoning_tokens and is_thinking:
        print(f"\\rThinking... ({response.usage.reasoning_tokens} tokens)", end="", flush=True)
    
    if chunk.content and is_thinking:
        print("\\n\\nAnalysis Results:")
        is_thinking = False
    
    if chunk.content:
        print(chunk.content, end="", flush=True)

print(f"\\n\\nUsage: {response.usage}")

# Clean up
client.files.delete(data_file.id)
```

The model will:

1. Access the attached data file
2. Write Python code to load and analyze the data
3. Execute the code in a sandboxed environment
4. Perform calculations and statistical analysis
5. Return the results and insights in the response

## Limitations and Considerations

### Request Constraints

* **No batch requests**: File attachments with document search are agentic requests and do not support batch mode (`n > 1`)
* **Streaming recommended**: Use streaming mode for better observability of document search process

### Document Complexity

* Highly unstructured or very long documents may require more processing
* Well-organized documents with clear structure are easier to search
* Large documents with many searches can result in higher token usage

### Model Compatibility

* **Recommended models**: `grok-4-fast`, `grok-4` for best document understanding
* **Agentic requirement**: File attachments require [agentic-capable](/developers/tools/overview) models that support server-side tools.

## Next Steps

Learn more about managing your files:


===/developers/model-capabilities/images/generation===
#### Model Capabilities

# Image Generation

Generate images from text prompts, edit existing images with natural language, or iteratively refine images through multi-turn conversations. The API supports batch generation of multiple images, and control over aspect ratio and resolution.

## Quick Start

Generate an image with a single API call:

```python customLanguage="pythonXAI"
import xai_sdk

client = xai_sdk.Client()

response = client.image.sample(
    prompt="A collage of London landmarks in a stenciled street‑art style",
    model="grok-imagine-image",
)

print(response.url)
```

```bash
curl -X POST https://api.x.ai/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-image",
    "prompt": "A collage of London landmarks in a stenciled street‑art style"
  }'
```

```python customLanguage="pythonOpenAISDK"
from openai import OpenAI

client = OpenAI(
    base_url="https://api.x.ai/v1",
    api_key="YOUR_API_KEY",
)

response = client.images.generate(
    model="grok-imagine-image",
    prompt="A collage of London landmarks in a stenciled street‑art style",
)

print(response.data[0].url)
```

```javascript customLanguage="javascriptOpenAISDK"
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: process.env.XAI_API_KEY,
    baseURL: 'https://api.x.ai/v1',
});

const response = await client.images.generate({
    model: "grok-imagine-image",
    prompt: "A collage of London landmarks in a stenciled street‑art style",
});

console.log(response.data[0].url);
```

```javascript customLanguage="javascriptAISDK"
import { xai } from "@ai-sdk/xai";
import { generateImage } from "ai";

const { image } = await generateImage({
    model: xai.image("grok-imagine-image"),
    prompt: "A collage of London landmarks in a stenciled street‑art style",
});

console.log(image.base64);
```

Images are returned as URLs by default. URLs are temporary, so download or process promptly. You can also request [base64 output](#base64-output) for embedding images directly.

## Image Editing

Edit an existing image by providing a source image along with your prompt. The model understands the image content and applies your requested changes.

The OpenAI SDK's `images.edit()` method is not supported for image editing because it uses `multipart/form-data`, while the xAI API requires `application/json`. Use the xAI SDK, Vercel AI SDK, or direct HTTP requests instead.

With the xAI SDK, use the same `sample()` method — just add the `image_url` parameter:

```python customLanguage="pythonXAI"
import base64
import xai_sdk

client = xai_sdk.Client()

# Load image from file and encode as base64
with open("landmarks.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

response = client.image.sample(
    prompt="Change the landmarks to be New York City landmarks",
    model="grok-imagine-image",
    image_url=f"data:image/jpeg;base64,{image_data}",
)

print(response.url)
```

```bash
# Using a public URL as the source image
curl -X POST https://api.x.ai/v1/images/edits \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-image",
    "prompt": "Change the landmarks to be New York City landmarks",
    "image": {
      "url": "https://example.com/landmarks.jpg",
      "type": "image_url"
    }
  }'
```

```javascript customLanguage="javascriptAISDK"
import { xai } from "@ai-sdk/xai";
import { generateImage } from "ai";
import fs from "fs";

// Load image and encode as base64
const imageBuffer = fs.readFileSync("landmarks.jpg");
const base64Image = imageBuffer.toString("base64");

const { image } = await generateImage({
    model: xai.image("grok-imagine-image"),
    prompt: "Change the landmarks to be New York City landmarks",
    providerOptions: {
        xai: {
            image: `data:image/jpeg;base64,${base64Image}`,
        },
    },
});

console.log(image.base64);
```

You can provide the source image as:

* A **public URL** pointing to an image
* A **base64-encoded data URI** (e.g., `data:image/jpeg;base64,...`)

## Multi-Turn Editing

Chain multiple edits together by using each output as the input for the next. This enables iterative refinement — start with a base image and progressively add details, adjust styles, or make corrections.

## Style Transfer

The `grok-imagine-image` model excels across a wide range of visual styles — from ultra-realistic photography to anime, oil paintings, pencil sketches, and beyond. Transform existing images by simply describing the desired aesthetic in your prompt.

## Concurrent Requests

When you need to generate multiple images with **different prompts** — such as applying various style transfers to the same source image, or generating unrelated images in parallel — use `AsyncClient` with `asyncio.gather` to fire requests concurrently. This is significantly faster than issuing them one at a time.

If you want multiple variations from the **same prompt**, use [`sample_batch()` with the `n` parameter](#multiple-images) instead. That generates all images in a single request and is the most efficient approach for same-prompt generation.

```python customLanguage="pythonXAI"
import asyncio
import xai_sdk

async def generate_concurrently():
    client = xai_sdk.AsyncClient()

    source_image = "https://example.com/portrait.jpg"

    # Each request uses a different prompt
    prompts = [
        "Render this image as an oil painting in the style of impressionism",
        "Render this image as a pencil sketch with detailed shading",
        "Render this image as pop art with bold colors and halftone dots",
        "Render this image as a watercolor painting with soft edges",
    ]

    # Fire all requests concurrently
    tasks = [
        client.image.sample(
            prompt=prompt,
            model="grok-imagine-image",
            image_url=source_image,
        )
        for prompt in prompts
    ]

    results = await asyncio.gather(*tasks)

    for prompt, result in zip(prompts, results):
        print(f"{prompt}: {result.url}")

asyncio.run(generate_concurrently())
```

## Configuration

### Multiple Images

Generate multiple images in a single request using the `sample_batch()` method and the `n` parameter. This returns a list of `ImageResponse` objects.

```python customLanguage="pythonXAI"
import xai_sdk

client = xai_sdk.Client()

responses = client.image.sample_batch(
    prompt="A futuristic city skyline at night",
    model="grok-imagine-image",
    n=4,
)

for i, image in enumerate(responses):
    print(f"Variation {i + 1}: {image.url}")
```

```bash
curl -X POST https://api.x.ai/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-image",
    "prompt": "A futuristic city skyline at night",
    "n": 4
  }'
```

### Aspect Ratio

Control image dimensions with the `aspect_ratio` parameter:

| Ratio | Use case |
|-------|----------|
| `1:1` | Social media, thumbnails |
| `16:9` / `9:16` | Widescreen, mobile, stories |
| `4:3` / `3:4` | Presentations, portraits |
| `3:2` / `2:3` | Photography |
| `2:1` / `1:2` | Banners, headers |
| `19.5:9` / `9:19.5` | Modern smartphone displays |
| `20:9` / `9:20` | Ultra-wide displays |
| `auto` | Model auto-selects the best ratio for the prompt |

```python customLanguage="pythonXAI"
import xai_sdk

client = xai_sdk.Client()

response = client.image.sample(
    prompt="Mountain landscape at sunrise",
    model="grok-imagine-image",
    aspect_ratio="16:9",
)

print(response.url)
```

```bash
curl -X POST https://api.x.ai/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-image",
    "prompt": "Mountain landscape at sunrise",
    "aspect_ratio": "16:9"
  }'
```

### Resolution

You can specify different resolutions of the output image. Currently supported image resolutions are:

* 1k
* 2k

```python customLanguage="pythonXAI"
import xai_sdk

client = xai_sdk.Client()

response = client.image.sample(
    prompt="An astronaut performing EVA in LEO.",
    model="grok-imagine-image",
    resolution="2k"
)

```

```bash
curl -X POST https://api.x.ai/v1/images/generations \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $XAI_API_KEY" \
-d '{
    "model": "grok-imagine-image",
    "prompt": "An astronaut performing EVA in LEO.",
    "resolution": "2k"
}'
```

### Base64 Output

For embedding images directly without downloading, request base64:

```python customLanguage="pythonXAI"
import xai_sdk

client = xai_sdk.Client()

response = client.image.sample(
    prompt="A serene Japanese garden",
    model="grok-imagine-image",
    image_format="base64",
)

# Save to file
with open("garden.jpg", "wb") as f:
    f.write(response.image)
```

```bash
curl -X POST https://api.x.ai/v1/images/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-image",
    "prompt": "A serene Japanese garden",
    "response_format": "b64_json"
  }'
```

### Response Details

The xAI SDK exposes additional metadata on the response object beyond the image URL or base64 data.

**Moderation** — Check whether the generated image passed content moderation:

```python customLanguage="pythonXAI"
if response.respect_moderation:
    print(response.url)
else:
    print("Image filtered by moderation")
```

**Model** — Get the actual model used (resolving any aliases):

```python customLanguage="pythonXAI"
print(f"Model: {response.model}")
```

## Pricing

Image generation uses flat per-image pricing rather than token-based pricing like text models. Each generated image incurs a fixed fee regardless of prompt length.

For image editing, you are charged for both the input image and the generated output image.

For full pricing details on the `grok-imagine-image` model, see the [model page](/developers/models/grok-imagine-image).

## Limitations

* **Maximum images per request:** 10
* **URL expiration:** Generated URLs are temporary
* **Content moderation:** Images are subject to content policy review

## Related

* [Models](/developers/models) — Available image models
* [Video Generation](/developers/model-capabilities/video/generation) — Animate generated images
* [API Reference](/developers/rest-api-reference) — Full endpoint documentation


===/developers/model-capabilities/images/understanding===
#### Model Capabilities

# Image Understanding

When sending images, it is advised to not store request/response history on the server. Otherwise the request may fail.
See .

Some models allow images in the input. The model will consider the image context when generating the response.

## Constructing the message body - difference from text-only prompt

The request message to image understanding is similar to text-only prompt. The main difference is that instead of text input:

```json
[
  {
    "role": "user",
    "content": "What is in this image?"
  }
]
```

We send in `content` as a list of objects:

```json
[
  {
    "role": "user",
    "content": [
      {
        "type": "input_image",
        "image_url": "data:image/jpeg;base64,<base64_image_string>",
        "detail": "high"
      },
      {
        "type": "input_text",
        "text": "What is in this image?"
      }
    ]
  }
]
```

The `image_url.url` can also be the image's url on the Internet.

### Image understanding example

```python customLanguage="pythonXAI"
import os
from xai_sdk import Client
from xai_sdk.chat import user, image

client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    management_api_key=os.getenv("XAI_MANAGEMENT_API_KEY"),
    timeout=3600,
)

image_url = "https://science.nasa.gov/wp-content/uploads/2023/09/web-first-images-release.png"


chat = client.chat.create(model="grok-4-1-fast-reasoning")
chat.append(
    user(
        "What's in this image?",
        image(image_url=image_url, detail="high"),
    )
)

response = chat.sample()
print(response)

# The response ID that can be used to continue the conversation later

print(response.id)
```

```python customLanguage="pythonOpenAISDK"
import os
import httpx
from openai import OpenAI

client = OpenAI(
    api_key="<YOUR_XAI_API_KEY_HERE>",
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(3600.0), # Override default timeout with longer timeout for reasoning models
)
image_url = (
    "https://science.nasa.gov/wp-content/uploads/2023/09/web-first-images-release.png"
)

response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_image",
                    "image_url": image_url,
                    "detail": "high",
                },
                {
                    "type": "input_text",
                    "text": "What's in this image?",
                },
            ],
        },
    ],
)

print(response)

# The response ID that can be used to continue the conversation later

print(response.id)
```

```javascript customLanguage="javascriptOpenAISDK"
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: "<api key>",
    baseURL: "https://api.x.ai/v1",
    timeout: 360000, // Override default timeout with longer timeout for reasoning models
});

const image_url =
    "https://science.nasa.gov/wp-content/uploads/2023/09/web-first-images-release.png";

const response = await client.responses.create({
    model: "grok-4-1-fast-reasoning",
    input: [
        {
            role: "user",
            content: [
                {
                    type: "input_image",
                    image_url: image_url,
                    detail: "high",
                },
                {
                    type: "input_text",
                    text: "What's in this image?",
                },
            ],
        },
    ],
});

console.log(response);

// The response ID that can be used to recall the conversation later
console.log(response.id);
```

```javascript customLanguage="javascriptAISDK"
import { xai } from '@ai-sdk/xai';
import { generateText } from 'ai';

const { text, response } = await generateText({
    model: xai.responses('grok-4-1-fast-reasoning'),
    messages: [
        {
            role: 'user',
            content: [
                {
                    type: 'image',
                    image: new URL('https://science.nasa.gov/wp-content/uploads/2023/09/web-first-images-release.png'),
                },
                {
                    type: 'text',
                    text: "What's in this image?",
                },
            ],
        },
    ]
});

console.log(text);

// The response ID can be used to continue the conversation
console.log(response.id);
```

```bash
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -m 3600 \
  -d '{
    "model": "grok-4-1-fast-reasoning",
    "input": [
      {
        "role": "user",
        "content": [
          {
            "type": "input_image",
            "image_url": "https://science.nasa.gov/wp-content/uploads/2023/09/web-first-images-release.png",
            "detail": "high"
          },
          {
            "type": "input_text",
            "text": "What'\''s in this image?"
          }
        ]
      }
    ]
  }'
```

### Image input general limits

* Maximum image size: `20MiB`
* Maximum number of images: No limit
* Supported image file types: `jpg/jpeg` or `png`.
* Any image/text input order is accepted (e.g. text prompt can precede image prompt)


===/developers/model-capabilities/legacy/chat-completions===
#### Model Capabilities

# Chat Completions

Chat Completions is offered as a legacy endpoint. Most of our new features will come to  first.

Looking to migrate? Check out our [Migrating to Responses API](/developers/model-capabilities/text/comparison) guide for a detailed comparison and migration steps.

Text in, text out. Chat is the most popular feature on the xAI API, and can be used for anything from summarizing articles, generating creative writing, answering questions, providing customer support, to assisting with coding tasks.

## Prerequisites

* xAI Account: You need an xAI account to access the API.
* API Key: Ensure that your API key has access to the Chat Completions endpoint and the model you want to use is enabled.

If you don't have these and are unsure of how to create one, follow [the Hitchhiker's Guide to Grok](/developers/quickstart).

You can create an API key on the [xAI Console API Keys Page](https://console.x.ai/team/default/api-keys).

Set your API key in your environment:

```bash
export XAI_API_KEY="your_api_key"
```

## A basic chat completions example

You can also stream the response, which is covered in [Streaming Response](/developers/model-capabilities/text/streaming).

The user sends a request to the xAI API endpoint. The API processes this and returns a complete response.

```python customLanguage="pythonXAI"
import os

from xai_sdk import Client
from xai_sdk.chat import user, system

client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    timeout=3600, # Override default timeout with longer timeout for reasoning models
)

chat = client.chat.create(model="grok-4-1-fast-reasoning")
chat.append(system("You are a PhD-level mathematician."))
chat.append(user("What is 2 + 2?"))

response = chat.sample()
print(response.content)
```

```python customLanguage="pythonOpenAISDK"
import os
import httpx
from openai import OpenAI

client = OpenAI(
    api_key="<YOUR_XAI_API_KEY_HERE>",
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(3600.0), # Override default timeout with longer timeout for reasoning models
)

completion = client.chat.completions.create(
    model="grok-4-1-fast-reasoning",
    messages=[
        {"role": "system", "content": "You are a PhD-level mathematician."},
        {"role": "user", "content": "What is 2 + 2?"},
    ],
)

print(completion.choices[0].message)
```

```javascript customLanguage="javascriptOpenAISDK"
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: "<api key>",
    baseURL: "https://api.x.ai/v1",
    timeout: 360000, // Override default timeout with longer timeout for reasoning models
});

const completion = await client.chat.completions.create({
    model: "grok-4-1-fast-reasoning",
    messages: [
        {
            role: "system",
            content: "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."
        },
        {
            role: "user",
            content: "What is the meaning of life, the universe, and everything?"
        },
    ],
});
console.log(completion.choices[0].message);
```

```javascript customLanguage="javascriptAISDK"
import { xai } from '@ai-sdk/xai';
import { generateText } from 'ai';

const result = await generateText({
  model: xai('grok-4-1-fast-reasoning'),
  system:
    "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy.",
  prompt: 'What is the meaning of life, the universe, and everything?',
});

console.log(result.text);
```

```bash
curl https://api.x.ai/v1/chat/completions \
-H "Content-Type: application/json" \
-H "Authorization: Bearer $XAI_API_KEY" \
-m 3600 \
-d '{
    "messages": [
        {
            "role": "system",
            "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."
        },
        {
            "role": "user",
            "content": "What is the meaning of life, the universe, and everything?"
        }
    ],
    "model": "grok-4-1-fast-reasoning",
    "stream": false
}'
```

Response:

```python customLanguage="pythonXAI"
'2 + 2 equals 4.'
```

```python customLanguage="pythonOpenAISDK"
ChatCompletionMessage(
  content='2 + 2 equals 4.',
  refusal=None,
  role='assistant',
  audio=None,
  function_call=None,
  tool_calls=None
)
```

```javascript customLanguage="javascriptOpenAISDK"
{
  role: 'assistant',
  content: `Ah, the ultimate question! According to Douglas Adams' "The Hitchhiker's Guide to the Galaxy," the answer to the ultimate question of life, the universe, and everything is **42**. However, the guide also notes that the actual question to which this is the answer is still unknown. Isn't that delightfully perplexing? Now, if you'll excuse me, I'll just go ponder the intricacies of existence.`
  refusal: null
}
```

```javascript customLanguage="javascriptAISDK"
// result object structure
{
  text: "Ah, the ultimate question! As someone...",
  finishReason: "stop",
  usage: {
    inputTokens: 716,
    outputTokens: 126,
    totalTokens: 1009,
    reasoningTokens: 167
  },
  totalUsage: { /* same as usage */ }
}
```

```bash
{
  "id": "0daf962f-a275-4a3c-839a-047854645532",
  "object": "chat.completion",
  "created": 1739301120,
  "model": "grok-4-1-fast-reasoning",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "The meaning of life, the universe, and everything is a question that has puzzled philosophers, scientists, and hitchhikers alike. According to the Hitchhiker's Guide to the Galaxy, the answer to this ultimate question is simply \"42\". However, the exact nature of the question itself remains unknown. So, while we may have the answer, the true meaning behind it is still up for debate. In the meantime, perhaps we should all just enjoy the journey and have a good laugh along the way!",
        "refusal": null
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 41,
    "completion_tokens": 104,
    "total_tokens": 145,
    "prompt_tokens_details": {
      "text_tokens": 41,
      "audio_tokens": 0,
      "image_tokens": 0,
      "cached_tokens": 0
    }
  },
  "system_fingerprint": "fp_84ff176447"
}
```

## Conversations

The xAI API is stateless and does not process new request with the context of your previous request history.

However, you can provide previous chat generation prompts and results to a new chat generation request to let the model process your new request with the context in mind.

An example message:

```json
{
  "role": "system",
  "content": [{ "type": "text", "text": "You are a helpful and funny assistant."}]
}
{
  "role": "user",
  "content": [{ "type": "text", "text": "Why don't eggs tell jokes?" }]
},
{
  "role": "assistant",
  "content": [{ "type": "text", "text": "They'd crack up!" }]
},
{
  "role": "user",
  "content": [{"type": "text", "text": "Can you explain the joke?"}],
}
```

By specifying roles, you can change how the model ingests the content.
The `system` role content should define, in an instructive tone, the way the model should respond to user request.
The `user` role content is usually used for user requests or data sent to the model.
The `assistant` role content is usually either in the model's response, or when sent within the prompt, indicates the model's response as part of conversation history.

The `developer` role is supported as an alias for `system`. Only a **single** system/developer message should be used, and it should always be the **first message** in your conversation.

## Image understanding

Some models allow image in the input. The model will consider the image context, when generating the response.

### Constructing the message body - difference from text-only prompt

The request message to image understanding is similar to text-only prompt. The main difference is that instead of text input:

```json
[
{
    "role": "user",
    "content": "What is in this image?"
}
]
```

We send in `content` as a list of objects:

```json
[
{
    "role": "user",
    "content": [
{
    "type": "image_url",
    "image_url": {
    "url": "data:image/jpeg;base64,<base64_image_string>",
    "detail": "high"
}
},
{
    "type": "text",
    "text": "What is in this image?"
}
    ]
}
]
```

The `image_url.url` can also be the image's url on the Internet.

### Image understanding example

```pythonXAI
import os

from xai_sdk import Client
from xai_sdk.chat import user, image

client = Client(api_key=os.getenv('XAI_API_KEY'))

image_url = "https://science.nasa.gov/wp-content/uploads/2023/09/web-first-images-release.png"

chat = client.chat.create(model="grok-4")
chat.append(
    user(
        "What's in this image?",
        image(image_url=image_url, detail="high"),
    )
)

response = chat.sample()
print(response.content)
```

```pythonOpenAISDK
import os
from openai import OpenAI

XAI_API_KEY = os.getenv("XAI_API_KEY")
image_url = (
"https://science.nasa.gov/wp-content/uploads/2023/09/web-first-images-release.png"
)

client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                    "detail": "high",
                },
            },
            {
                "type": "text",
                "text": "What's in this image?",
            },
        ],
    },
]

completion = client.chat.completions.create(
    model="grok-4",
    messages=messages,
)

print(completion.choices[0].message.content)
```

```javascriptOpenAISDK
import OpenAI from "openai";
const openai = new OpenAI({
apiKey: process.env.XAI_API_KEY,
baseURL: "https://api.x.ai/v1",
});
const image_url =
"https://science.nasa.gov/wp-content/uploads/2023/09/web-first-images-release.png";

const completion = await openai.chat.completions.create({
    model: "grok-4",
    messages: [
        {
            role: "user",
            content: [
                {
                    type: "image_url",
                    image_url: {
                        url: image_url,
                        detail: "high",
                    },
                },
                {
                    type: "text",
                    text: "What's in this image?",
                },
            ],
        },
    ],
});

console.log(completion.choices[0].message.content);
```

```javascriptAISDK
import { xai } from '@ai-sdk/xai';
import { generateText } from 'ai';

const result = await generateText({
model: "grok-4",
messages: [
        {
            role: 'user',
            content: [
                {
                    type: 'image',
                    image: new URL(
                        'https://science.nasa.gov/wp-content/uploads/2023/09/web-first-images-release.png',
                    ),
                },
                {
                    type: 'text',
                    text: "What's in this image?",
                },
            ],
        },
    ],
});

console.log(result.text);
```

### Image input general limits

* Maximum image size: `20MiB`
* Maximum number of images: No limit
* Supported image file types: `jpg/jpeg` or `png`.
* Any image/text input order is accepted (e.g. text prompt can precede image prompt)

### Image detail levels

The `"detail"` field controls the level of pre-processing applied to the image that will be provided to the model. It is optional and determines the resolution at which the image is processed. The possible values for `"detail"` are:

* **`"auto"`**: The system will automatically determine the image resolution to use. This is the default setting, balancing speed and detail based on the model's assessment.
* **`"low"`**: The system will process a low-resolution version of the image. This option is faster and consumes fewer tokens, making it more cost-effective, though it may miss finer details.
* **`"high"`**: The system will process a high-resolution version of the image. This option is slower and more expensive in terms of token usage, but it allows the model to attend to more nuanced details in the image.


===/developers/model-capabilities/text/comparison===
#### Model Capabilities

# Comparison with Chat Completions API

The Responses API is the recommended way to interact with xAI models. Here's how it compares to the legacy Chat Completions API:

| Feature | Responses API | Chat Completions API (Deprecated) |
|---------|---------------|-----------------------------------|
| **Stateful Conversations** |  Built-in support via `previous_response_id` |  Stateless - must resend full history |
| **Server-side Storage** |  Responses stored for 30 days |  No storage - manage history yourself |
| **Reasoning Models** |  Full support with encrypted reasoning content |  Limited - only `grok-3-mini` returns `reasoning_content` |
| **Agentic Tools** |  Native support for tools (search, code execution, MCP) |  Function calling only |
| **Billing Optimization** |  Automatic caching of conversation history |  Full history billed on each request |
| **Future Features** |  All new capabilities delivered here first |  Legacy endpoint, limited updates |

## Key API Changes

### Parameter Mapping

| Chat Completions | Responses API | Notes |
|-----------------|---------------|-------|
| `messages` | `input` | Array of message objects |
| `max_tokens` | `max_output_tokens` | Maximum tokens to generate |
| — | `previous_response_id` | Continue a stored conversation |
| — | `store` | Control server-side storage (default: `true`) |
| — | `include` | Request additional data like `reasoning.encrypted_content` |

### Response Structure

The response format differs between the two APIs:

**Chat Completions** returns content in `choices[0].message.content`:

```json
{
  "id": "chatcmpl-123",
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "Hello! How can I help you?"
    }
  }]
}
```

**Responses API** returns content in an `output` array with typed items:

```json
{
  "id": "resp_123",
  "output": [{
    "type": "message",
    "role": "assistant",
    "content": [{
      "type": "output_text",
      "text": "Hello! How can I help you?"
    }]
  }]
}
```

### Multi-turn Conversations

With Chat Completions, you must resend the entire conversation history with each request. With Responses API, you can use `previous_response_id` to continue a conversation:

```pythonWithoutSDK
# First request
response = client.responses.create(
    model="grok-4",
    input=[{"role": "user", "content": "What is 2+2?"}],
)

# Continue the conversation - no need to resend history
second_response = client.responses.create(
    model="grok-4",
    previous_response_id=response.id,
    input=[{"role": "user", "content": "Now multiply that by 10"}],
)
```

## Migration Path

Migrating from Chat Completions to Responses API is straightforward. Here's how to update your code for each SDK:

### Vercel AI SDK

Switch from `xai()` to `xai.responses()`:

```javascriptAISDK deletedLines="1" addedLines="2"
  model: xai('grok-4'),
  model: xai.responses('grok-4'),
```

### OpenAI SDK (JavaScript)

Switch from `client.chat.completions.create` to `client.responses.create`, and rename `messages` to `input`:

```javascriptWithoutSDK deletedLines="1,3" addedLines="2,4"
const response = await client.chat.completions.create({
const response = await client.responses.create({
    messages: [
    input: [
        { role: "user", content: "Hello!" }
    ],
});
```

### OpenAI SDK (Python)

Switch from `client.chat.completions.create` to `client.responses.create`, and rename `messages` to `input`:

```pythonWithoutSDK deletedLines="1,3" addedLines="2,4"
response = client.chat.completions.create(
response = client.responses.create(
    messages=[
    input=[
        {"role": "user", "content": "Hello!"}
    ],
)
```

### cURL

Change the endpoint from `/v1/chat/completions` to `/v1/responses`, and rename `messages` to `input`:

```bash deletedLines="1,5" addedLines="2,6"
curl https://api.x.ai/v1/chat/completions \
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{ "model": "grok-4", "messages": [{"role": "user", "content": "Hello!"}] }'
  -d '{ "model": "grok-4", "input": [{"role": "user", "content": "Hello!"}] }'
```

This will work for most use cases. If you have a unique integration, refer to the [Responses API documentation](/developers/model-capabilities/text/generate-text) for detailed guidance.


===/developers/model-capabilities/text/generate-text===
#### Model Capabilities

# Generate Text

The Responses API is the preferred way of interacting with our models via API. It allows optional **stateful interactions** with our models,
where **previous input prompts, reasoning content and model responses are saved and stored on xAI's servers**. You can continue the interaction by appending new
prompt messages instead of resending the full conversation. This behavior is on by default. If you would like to store your request/response locally, please see [Disable storing previous request/response on server](#disable-storing-previous-requestresponse-on-server).

Although you don't need to enter the conversation history in the request body, you will still be
billed for the entire conversation history when using Responses API. The cost might be reduced as
part of the conversation history is .

**The responses will be stored for 30 days, after which they will be removed. This means you can use the response ID to retrieve or continue a conversation within 30 days of sending the request.**
If you want to continue a conversation after 30 days, please store your responses history and the encrypted thinking content locally, and pass them in a new request body.

For Python, we also offer our [xAI SDK](https://github.com/xai-org/xai-sdk-python) which covers all of our features and uses gRPC for optimal performance. It's fine to mix both. The xAI SDK allows you to interact with all our products such as Collections, Voice API, API key management, and more, while the Responses API is more suited for chatbots and usage in RESTful APIs.

## Prerequisites

* xAI Account: You need an xAI account to access the API.
* API Key: Ensure that your API key has access to the Responses API endpoint and the model you want to use is enabled.

If you don't have these and are unsure of how to create one, follow [the Hitchhiker's Guide to Grok](/developers/quickstart).

You can create an API key on the [xAI Console API Keys Page](https://console.x.ai/team/default/api-keys).

Set your API key in your environment:

```bash
export XAI_API_KEY="your_api_key"
```

## Creating a new model response

The first step in using Responses API is analogous to using the legacy Chat Completions API. You will create a new response with prompts. By default, your request/response history is stored on our server.

`instructions` parameter is currently not supported. The API will return an error if it is specified.

```python customLanguage="pythonXAI"
import os
from xai_sdk import Client
from xai_sdk.chat import user, system

client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    management_api_key=os.getenv("XAI_MANAGEMENT_API_KEY"),
    timeout=3600,
)

chat = client.chat.create(model="grok-4-1-fast-reasoning")
chat.append(system("You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."))
chat.append(user("What is the meaning of life, the universe, and everything?"))
response = chat.sample()

print(response)

# The response ID that can be used to continue the conversation later

print(response.id)
```

```python customLanguage="pythonOpenAISDK"
import os
import httpx
from openai import OpenAI

client = OpenAI(
    api_key="<YOUR_XAI_API_KEY_HERE>",
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(3600.0), # Override default timeout with longer timeout for reasoning models
)

response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[
        {"role": "system", "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."},
        {"role": "user", "content": "What is the meaning of life, the universe, and everything?"},
    ],
)

print(response)

# The response ID that can be used to continue the conversation later

print(response.id)
```

```javascript customLanguage="javascriptOpenAISDK"
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: "<api key>",
    baseURL: "https://api.x.ai/v1",
    timeout: 360000, // Override default timeout with longer timeout for reasoning models
});

const response = await client.responses.create({
    model: "grok-4-1-fast-reasoning",
    input: [
        {
            role: "system",
            content: "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."
        },
        {
            role: "user",
            content: "What is the meaning of life, the universe, and everything?"
        },
    ],
});

console.log(response);

// The response ID that can be used to recall the conversation later
console.log(response.id);
```

```javascript customLanguage="javascriptAISDK"
import { xai } from '@ai-sdk/xai';
import { generateText } from 'ai';

const { text, response } = await generateText({
  model: xai.responses('grok-4-1-fast-reasoning'),
  system: "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy.",
  prompt: "What is the meaning of life, the universe, and everything?",
});

console.log(text);

// The response ID can be used to continue the conversation
console.log(response.id);
```

```bash
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -m 3600 \
  -d '{
    "model": "grok-4-1-fast-reasoning",
    "input": [
        {
            "role": "system",
            "content": "You are Grok, a chatbot inspired by the Hitchhiker'\''s Guide to the Galaxy."
        },
        {
            "role": "user",
            "content": "What is the meaning of life, the universe, and everything?"
        }
    ]
}'
```

The `developer` role is supported as an alias for `system`. Only a **single** system/developer message should be used, and it should always be the **first message** in your conversation.

### Disable storing previous request/response on server

If you do not want to store your previous request/response on the server, you can set `store: false` on the request.

```python customLanguage="pythonXAI"
import os
from xai_sdk import Client
from xai_sdk.chat import user, system

client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    management_api_key=os.getenv("XAI_MANAGEMENT_API_KEY"),
    timeout=3600,
)

chat = client.chat.create(model="grok-4-1-fast-reasoning", store_messages=False)
chat.append(system("You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."))
chat.append(user("What is the meaning of life, the universe, and everything?"))
response = chat.sample()

print(response)
```

```python customLanguage="pythonOpenAISDK"
import os
import httpx
from openai import OpenAI

client = OpenAI(
    api_key="<YOUR_XAI_API_KEY_HERE>",
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(3600.0), # Override default timeout with longer timeout for reasoning models
)

response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[
        {"role": "system", "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."},
        {"role": "user", "content": "What is the meaning of life, the universe, and everything?"},
    ],
    store=False
)

print(response)
```

```javascript customLanguage="javascriptOpenAISDK"
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: "<api key>",
    baseURL: "https://api.x.ai/v1",
    timeout: 360000, // Override default timeout with longer timeout for reasoning models
});

const response = await client.responses.create({
    model: "grok-4-1-fast-reasoning",
    input: [
        {
            role: "system",
            content: "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."
        },
        {
            role: "user",
            content: "What is the meaning of life, the universe, and everything?"
        },
    ],
    store: false
});

console.log(response);
```

```bash
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -m 3600 \
  -d '{
    "model": "grok-4-1-fast-reasoning",
    "input": [
        {
            "role": "system",
            "content": "You are Grok, a chatbot inspired by the Hitchhiker'\''s Guide to the Galaxy."
        },
        {
            "role": "user",
            "content": "What is the meaning of life, the universe, and everything?"
        }
    ],
    "store": false
}'
```

### Returning encrypted thinking content

If you want to return the encrypted thinking traces, you need to specify `use_encrypted_content=True` in xAI SDK or gRPC request message, or `include: ["reasoning.encrypted_content"]` in the request body.

Modify the steps to create a chat client (xAI SDK) or change the request body as following:

```python customLanguage="pythonXAI"
chat = client.chat.create(model="grok-4-1-fast-reasoning",
        use_encrypted_content=True)
```

```python customLanguage="pythonOpenAISDK"
response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[
        {"role": "system", "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."},
        {"role": "user", "content": "What is the meaning of life, the universe, and everything?"},
    ],
    include=["reasoning.encrypted_content"]
)
```

```javascript customLanguage="javascriptWithoutSDK"
const response = await client.responses.create({
    model: "grok-4-1-fast-reasoning",
    input: [
        {"role": "system", "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."},
        {"role": "user", "content": "What is the meaning of life, the universe, and everything?"},
    ],
    include: ["reasoning.encrypted_content"],
});
```

```javascript customLanguage="javascriptAISDK"
import { xai } from '@ai-sdk/xai';
import { generateText } from 'ai';

const { text, reasoning } = await generateText({
  model: xai.responses('grok-4-1-fast-reasoning'),
  system: "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy.",
  prompt: "What is the meaning of life, the universe, and everything?",
  providerOptions: {
    xai: {
      include: ['reasoning.encrypted_content'],
    },
  },
});

console.log(text);
console.log(reasoning); // Contains encrypted reasoning content
```

```bash
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -m 3600 \
  -d '{
    "model": "grok-4-1-fast-reasoning",
    "input": [
        {
            "role": "system",
            "content": "You are Grok, a chatbot inspired by the Hitchhiker'\''s Guide to the Galaxy."
        },
        {
            "role": "user",
            "content": "What is the meaning of life, the universe, and everything?"
        }
    ],
    "include": ["reasoning.encrypted_content"]
}'
```

See [Adding encrypted thinking content](#adding-encrypted-thinking-content) on how to use the returned encrypted thinking content when making a new request.

## Chaining the conversation

We now have the `id` of the first response. With Chat Completions API, we typically send a stateless new request with all the previous messages.

With Responses API, we can send the `id` of the previous response, and the new messages to append to it.

```python customLanguage="pythonXAI"
import os
from xai_sdk import Client
from xai_sdk.chat import user, system

client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    management_api_key=os.getenv("XAI_MANAGEMENT_API_KEY"),
    timeout=3600,
)

chat = client.chat.create(model="grok-4-1-fast-reasoning", store_messages=True)
chat.append(system("You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."))
chat.append(user("What is the meaning of life, the universe, and everything?"))
response = chat.sample()

print(response)

# The response ID that can be used to continue the conversation later

print(response.id)

# New steps

chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    previous_response_id=response.id,
    store_messages=True,
)
chat.append(user("What is the meaning of 42?"))
second_response = chat.sample()

print(second_response)

# The response ID that can be used to continue the conversation later

print(second_response.id)
```

```python customLanguage="pythonOpenAISDK"
# Previous steps
import os
import httpx
from openai import OpenAI

client = OpenAI(
    api_key="<YOUR_XAI_API_KEY_HERE>",
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(3600.0), # Override default timeout with longer timeout for reasoning models
)

response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[
        {"role": "system", "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."},
        {"role": "user", "content": "What is the meaning of life, the universe, and everything?"},
    ],
)

print(response)

# The response ID that can be used to continue the conversation later

print(response.id)

# New steps

second_response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    previous_response_id=response.id,
    input=[
        {"role": "user", "content": "What is the meaning of 42?"},
    ],
)

print(second_response)

# The response ID that can be used to continue the conversation later

print(second_response.id)
```

```javascript customLanguage="javascriptWithoutSDK"
// Previous steps
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: "<api key>",
    baseURL: "https://api.x.ai/v1",
    timeout: 360000, // Override default timeout with longer timeout for reasoning models
});

const response = await client.responses.create({
    model: "grok-4-1-fast-reasoning",
    input: [
        {
            role: "system",
            content: "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."
        },
        {
            role: "user",
            content: "What is the meaning of life, the universe, and everything?"
        },
    ],
});

console.log(response);

// The response ID that can be used to recall the conversation later
console.log(response.id);

const secondResponse = await client.responses.create({
    model: "grok-4-1-fast-reasoning",
    previous_response_id: response.id,
    input: [
        {"role": "user", "content": "What is the meaning of 42?"},
    ],
});

console.log(secondResponse);

// The response ID that can be used to recall the conversation later
console.log(secondResponse.id);
```

```javascript customLanguage="javascriptAISDK"
import { xai } from '@ai-sdk/xai';
import { generateText } from 'ai';

// First request
const result = await generateText({
  model: xai.responses('grok-4-1-fast-reasoning'),
  system: "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy.",
  prompt: "What is the meaning of life, the universe, and everything?",
});

console.log(result.text);

// Get the response ID from the response object
const responseId = result.response.id;

// Continue the conversation using previousResponseId
const { text: secondResponse } = await generateText({
  model: xai.responses('grok-4-1-fast-reasoning'),
  prompt: "What is the meaning of 42?",
  providerOptions: {
    xai: {
      previousResponseId: responseId,
    },
  },
});

console.log(secondResponse);
```

```bash
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -m 3600 \
  -d '{
    "model": "grok-4-1-fast-reasoning",
    "previous_response_id": "The previous response ID",
    "input": [
        {
            "role": "user",
            "content": "What is the meaning of 42?"
        }
    ]
}'
```

### Adding encrypted thinking content

After returning the encrypted thinking content, you can also add it to a new response's input:

```python customLanguage="pythonXAI"
import os
from xai_sdk import Client
from xai_sdk.chat import user, system

client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    management_api_key=os.getenv("XAI_MANAGEMENT_API_KEY"),
    timeout=3600,
)

chat = client.chat.create(model="grok-4-1-fast-reasoning", store_messages=True, use_encrypted_content=True)
chat.append(system("You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."))
chat.append(user("What is the meaning of life, the universe, and everything?"))
response = chat.sample()

print(response)

# The response ID that can be used to continue the conversation later

print(response.id)

# New steps

chat.append(response)  ## Append the response and the SDK will automatically add the outputs from response to message history

chat.append(user("What is the meaning of 42?"))
second_response = chat.sample()

print(second_response)

# The response ID that can be used to continue the conversation later

print(second_response.id)
```

```python customLanguage="pythonOpenAISDK"
# Previous steps
import os
import httpx
from openai import OpenAI

client = OpenAI(
    api_key="<YOUR_XAI_API_KEY_HERE>",
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(3600.0), # Override default timeout with longer timeout for reasoning models
)

response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[
        {"role": "system", "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."},
        {"role": "user", "content": "What is the meaning of life, the universe, and everything?"},
    ],
    include=["reasoning.encrypted_content"]
)

print(response)

# The response ID that can be used to continue the conversation later

print(response.id)

# New steps

second_response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[
        *response.output,  # Use response.output instead of the stored response
        {"role": "user", "content": "What is the meaning of 42?"},
    ],
)

print(second_response)

# The response ID that can be used to continue the conversation later

print(second_response.id)
```

```javascript customLanguage="javascriptWithoutSDK"
// Previous steps
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: "<api key>",
    baseURL: "https://api.x.ai/v1",
    timeout: 360000, // Override default timeout with longer timeout for reasoning models
});

const response = await client.responses.create({
    model: "grok-4-1-fast-reasoning",
    input: [
        {
            role: "system",
            content: "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."
        },
        {
            role: "user",
            content: "What is the meaning of life, the universe, and everything?"
        },
    ],
    include: ["reasoning.encrypted_content"],
});

console.log(response);

// The response ID that can be used to recall the conversation later
console.log(response.id);

const secondResponse = await client.responses.create({
    model: "grok-4-1-fast-reasoning",
    input: [
        ...response.output,  // Use response.output instead of the stored response
        {"role": "user", "content": "What is the meaning of 42?"},
    ],
});

console.log(secondResponse);

// The response ID that can be used to recall the conversation later
console.log(secondResponse.id);
```

```javascript customLanguage="javascriptAISDK"
import { xai } from '@ai-sdk/xai';
import { generateText } from 'ai';

// First request with encrypted reasoning content
const result = await generateText({
  model: xai.responses('grok-4-1-fast-reasoning'),
  system: "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy.",
  prompt: "What is the meaning of life, the universe, and everything?",
  providerOptions: {
    xai: {
      include: ['reasoning.encrypted_content'],
    },
  },
});

console.log(result.text);

// Continue the conversation using previousResponseId
// The encrypted content is automatically included when using previousResponseId
const { text: secondResponse } = await generateText({
  model: xai.responses('grok-4-1-fast-reasoning'),
  prompt: "What is the meaning of 42?",
  providerOptions: {
    xai: {
      previousResponseId: result.response.id,
      include: ['reasoning.encrypted_content'],
    },
  },
});

console.log(secondResponse);
```

```bash
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -m 3600 \
  -d '{
    "model": "grok-4-1-fast-reasoning",
    "input": [
        {
            "role": "system",
            "content": "You are Grok, a chatbot inspired by the Hitchhiker'\''s Guide to the Galaxy."
        },
        {
            "role": "user",
            "content": "What is the meaning of life, the universe, and everything?"
        },
        {
            "id": "rs_51abe1aa-599b-80b6-57c8-dddc6263362f_us-east-1",
            "summary": [],
            "type": "reasoning",
            "status": "completed",
            "encrypted_content": "bvV88j99ILvgfHRTHCUSJtw+ISji6txJzPdZNbcSVuDk4OMG2Z9r5wOBBwjd3u3Hhm9XtpCWJO1YgTOlpgbn+g7DZX+pOagYYrCFUpQ19XkWz6Je8bHG9JcSDoGDqNgRbDbAUO8at6RCyqgPupJj5ArBDCt73fGQLTC4G3S0JMK9LsPiWz6GPj6qyzYoRzkj4R6bntRm74E4h8Y+z6u6B7+ixPSv8s1EFs8c+NUAB8TNKZZpXZquj2LXfx1xAie85Syl7qLqxLNtDG1dNBhBnHpYoE4gQzwyXqywf5pF2Q2imzPNzGQhurK+6gaNWgZbxRmjhdsW6TnzO5Kk6pzb5qpfgfcEScQeYHSj5GpD+yDUCNlhdbzhhWnEErH+wuBPpTG6UQhiC7m7yrJ7IY2E8K/BeUPlUvkhMaMwb4dA279pWMJdchNJ+TAxca+JVc80pXMG/PmrQUNJU9qdXRLbNmQbRadBNwV2qkPfgggL3q0yNd7Un9P+atmP3B9keBILif3ufsBDtVUobEniiyGV7YVDvQ/fQRVs7XDxJiOKkogjjQySyHgpjseO8iG5xtb9mrz6B3mDvv2aAuyDL6MHZRM7QDVPjUbgNMzDm5Sm3J7IhtzfR+3eMDws3qeTsxOt1KOslu983Btv1Wx37b5HJqX1pQU1dae/kOSJ7MifFd6wMkQtQBDgVoG3ka9wq5Vxq9Ki8bDOOMcwA2kUXhCcY3TZCXJfDWSKPTcCoNCYIv5LT2NFVdamiSfLIyeOjBNz459BfMvAoOZShFViQyc5YwjnReUQPQ8a18jcz8GoAK1O99e0h91oYxIgDV52EfS+IYrzqvJOEQbKQinB+LJwkPbBEp7ZtgAtiNBzm985hNgLfiBaVFWcRYwI3tNBCT1vkw2YI0NEEG0yOF29x+u64XzqyP1CX1pU6sGXEFn3RPdfYibf6bt/Y1BRqBL5l0CrXWsgDw02SqIFta8OvJ7Iwmq40/4acE/Ew6eWO/z2MHkWgqSpwGNjn7MfeKkTi44foZjfNqN9QOFQt6VG2tY+biKZDo0h9DAftae8Q2Xs2UDvsBYOm7YEahVkput6/uKzxljpXlz269qHk6ckvdN9hKLbaTO3/IZPCCPQ5a/a/sWn/1VOJj72sDk+23RNjBf0FL6bJMXZI5aQdtxbF1zij9mWcP9nJ9FHhj53ytuf1NiKl5xU8ZsaoKmCAJcXUz1n2FZvyWlqvgPYiszc7R8Y5dF6QbW2mlKnXzVy6qRMHNeQqGhCEncyT5nPNSdK5QlUwLokAIg"
        },
        {
            "content": [
                {
                    "type": "output_text",
                    "text": "42\n\nThis is, of course, the iconic answer from Douglas Adams'\'' *The Hitchhiker'\''s Guide to the Galaxy*, where a supercomputer named Deep Thought spends 7.5 million years computing the \"Answer to the Ultimate Question of Life, the Universe, and Everything\"—only to reveal it'\''s 42. (The real challenge, it turns out, is figuring out what the actual *question* was.)\n\nIf you'\''re asking in a more literal or philosophical sense, the universe doesn'\''t have a single tidy answer—it'\''s full of mysteries like quantum mechanics, dark matter, and why cats knock things off tables. But 42? That'\''s as good a starting point as any. What'\''s your take on it?",
                    "logprobs": null,
                    "annotations": []
                }
            ],
            "id": "msg_c2f68a9b-87cd-4f85-a9e9-b6047213a3ce_us-east-1",
            "role": "assistant",
            "type": "message",
            "status": "completed"
        },
        {
            "role": "user",
            "content": "What is the meaning of 42?"
        }
    ],
    "include": [
        "reasoning.encrypted_content"
    ]
}'
```

## Retrieving a previous model response

If you have a previous response's ID, you can retrieve the content of the response.

```python customLanguage="pythonXAI"
import os
from xai_sdk import Client
from xai_sdk.chat import user, system

client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    management_api_key=os.getenv("XAI_MANAGEMENT_API_KEY"),
    timeout=3600,
)

response = client.chat.get_stored_completion("<The previous response's id>")

print(response)
```

```python customLanguage="pythonOpenAISDK"
import os
import httpx
from openai import OpenAI

client = OpenAI(
    api_key="<YOUR_XAI_API_KEY_HERE>",
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(3600.0), # Override default timeout with longer timeout for reasoning models
)

response = client.responses.retrieve("<The previous response's id>")

print(response)
```

```javascript customLanguage="javascriptOpenAISDK"
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: "<api key>",
    baseURL: "https://api.x.ai/v1",
    timeout: 360000, // Override default timeout with longer timeout for reasoning models
});

const response = await client.responses.retrieve("<The previous response's id>");

console.log(response);
```

```javascript customLanguage="javascriptAISDK"
// Note: The Vercel AI SDK does not provide a method to retrieve previous responses.
// Use the OpenAI SDK as shown above for this functionality.

import OpenAI from "openai";

const client = new OpenAI({
    apiKey: "<api key>",
    baseURL: "https://api.x.ai/v1",
    timeout: 360000,
});

const response = await client.responses.retrieve("<The previous response's id>");

console.log(response);
```

```bash
curl https://api.x.ai/v1/responses/{response_id} \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -m 3600
```

## Delete a model response

If you no longer want to store the previous model response, you can delete it.

```python customLanguage="pythonXAI"
import os
from xai_sdk import Client
from xai_sdk.chat import user, system

client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    management_api_key=os.getenv("XAI_MANAGEMENT_API_KEY"),
    timeout=3600,
)

response = client.chat.delete_stored_completion("<The previous response's id>")
print(response)
```

```python customLanguage="pythonOpenAISDK"
import os
import httpx
from openai import OpenAI

client = OpenAI(
    api_key="<YOUR_XAI_API_KEY_HERE>",
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(3600.0), # Override default timeout with longer timeout for reasoning models
)

response = client.responses.delete("<The previous response's id>")

print(response)
```

```javascript customLanguage="javascriptOpenAISDK"
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: "<api key>",
    baseURL: "https://api.x.ai/v1",
    timeout: 360000, // Override default timeout with longer timeout for reasoning models
});

const response = await client.responses.delete("<The previous response's id>");

console.log(response);
```

```javascript customLanguage="javascriptAISDK"
// Note: The Vercel AI SDK does not provide a method to delete previous responses.
// Use the OpenAI SDK as shown above for this functionality.

import OpenAI from "openai";

const client = new OpenAI({
    apiKey: "<api key>",
    baseURL: "https://api.x.ai/v1",
    timeout: 360000,
});

const response = await client.responses.delete("<The previous response's id>");

console.log(response);
```

```bash
curl -X DELETE https://api.x.ai/v1/responses/{response_id} \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -m 3600
```


===/developers/model-capabilities/text/reasoning===
#### Model Capabilities

# Reasoning

`presencePenalty`, `frequencyPenalty` and `stop` parameters are not supported by reasoning models.
Adding them in the request would result in an error.

## Key Features

* **Think Before Responding**: Thinks through problems step-by-step before delivering an answer.
* **Math & Quantitative Strength**: Excels at numerical challenges and logic puzzles.
* **Reasoning Trace**: Usage metrics expose `reasoning_tokens`. Some models can also return encrypted reasoning via `include: ["reasoning.encrypted_content"]` (see below).

In Chat Completions, only `grok-3-mini` returns `message.reasoning_content`.

`grok-3`, `grok-4` and `grok-4-fast-reasoning` do not return `reasoning_content`. If supported, you can request [encrypted reasoning content](#encrypted-reasoning-content) via `include: ["reasoning.encrypted_content"]` in the Responses API instead.

### Encrypted Reasoning Content

For `grok-4`, the reasoning content is encrypted by us and can be returned if you pass `include: ["reasoning.encrypted_content"]` to the Responses API. You can send the encrypted content back to provide more context to a previous conversation. See [Adding encrypted thinking content](/developers/model-capabilities/text/generate-text#adding-encrypted-thinking-content) for more details on how to use the content.

## Control how hard the model thinks

`reasoning_effort` is not supported by `grok-3`, `grok-4` and `grok-4-fast-reasoning`. Specifying `reasoning_effort` parameter will get
an error response. Only `grok-3-mini` supports `reasoning_effort`.

The `reasoning_effort` parameter controls how much time the model spends thinking before responding. It must be set to one of these values:

* **`low`**: Minimal thinking time, using fewer tokens for quick responses.
* **`high`**: Maximum thinking time, leveraging more tokens for complex problems.

Choosing the right level depends on your task: use `low` for simple queries that should complete quickly, and `high` for harder problems where response latency is less important.

## Usage Example

Here’s a simple example using `grok-3-mini` to multiply 101 by 3.

```pythonXAI
import os

from xai_sdk import Client
from xai_sdk.chat import system, user

client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    timeout=3600, # Override default timeout with longer timeout for reasoning models
)

chat = client.chat.create(
    model="grok-3-mini",
    reasoning_effort="high",
    messages=[system("You are a highly intelligent AI assistant.")],
)
chat.append(user("What is 101\*3?"))

response = chat.sample()

print("Final Response:")
print(response.content)

print("Number of completion tokens:")
print(response.usage.completion_tokens)

print("Number of reasoning tokens:")
print(response.usage.reasoning_tokens)
```

```pythonOpenAISDK
import os
import httpx
from openai import OpenAI

client = OpenAI(
    base_url="https://api.x.ai/v1",
    api_key=os.getenv("XAI_API_KEY"),
    timeout=httpx.Timeout(3600.0), # Override default timeout with longer timeout for reasoning models
)

response = client.responses.create(
    model="grok-3-mini",
    reasoning={"effort": "high"},
    input=[
        {"role": "system", "content": "You are a highly intelligent AI assistant."},
        {"role": "user", "content": "What is 101*3?"},
    ],
)

message = next(item for item in response.output if item.type == "message")
text = next(c.text for c in message.content if c.type == "output_text")

print("Final Response:")
print(text)

print("Number of output tokens:")
print(response.usage.output_tokens)

print("Number of reasoning tokens:")
print(response.usage.output_tokens_details.reasoning_tokens)
```

```javascriptOpenAISDK
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: "<api key>",
    baseURL: "https://api.x.ai/v1",
    timeout: 360000, // Override default timeout with longer timeout for reasoning models
});

const response = await client.responses.create({
    model: "grok-3-mini",
    reasoning: { effort: "high" },
    input: [
        {
            "role": "system",
            "content": "You are a highly intelligent AI assistant.",
        },
        {
            "role": "user",
            "content": "What is 101*3?",
        },
    ],
});

// Find the message in the output array
const message = response.output.find((item) => item.type === "message");
const textContent = message?.content?.find((c) => c.type === "output_text");

console.log("\\nFinal Response:", textContent?.text);

console.log("\\nNumber of output tokens:", response.usage.output_tokens);

console.log("\\nNumber of reasoning tokens:", response.usage.output_tokens_details.reasoning_tokens);
```

```javascriptAISDK
import { xai } from '@ai-sdk/xai';
import { generateText } from 'ai';

const result = await generateText({
  model: xai.responses('grok-3-mini'),
  system: 'You are a highly intelligent AI assistant.',
  prompt: 'What is 101*3?',
});

console.log('Final Response:', result.text);
console.log('Number of completion tokens:', result.totalUsage.completionTokens);
console.log('Number of reasoning tokens:', result.totalUsage.reasoningTokens);
```

```bash
curl https://api.x.ai/v1/responses \\
-H "Content-Type: application/json" \\
-H "Authorization: Bearer $XAI_API_KEY" \\
-m 3600 \\
-d '{
    "input": [
        {
            "role": "system",
            "content": "You are a highly intelligent AI assistant."
        },
        {
            "role": "user",
            "content": "What is 101*3?"
        }
    ],
    "model": "grok-3-mini",
    "reasoning": { "effort": "high" },
    "stream": false
}'
```

### Sample Output

```output

Final Response:
The result of 101 multiplied by 3 is 303.

Number of completion tokens:
14

Number of reasoning tokens:
310
```

## Notes on Consumption

When you use a reasoning model, the reasoning tokens are also added to your final consumption amount. The reasoning token consumption will likely increase when you use a higher `reasoning_effort` setting.


===/developers/model-capabilities/text/streaming===
#### Model Capabilities

# Streaming

Streaming outputs is **supported by all models with text output capability** (Chat, Image Understanding, etc.). It is **not supported by models with image output capability** (Image Generation).

Streaming outputs uses [Server-Sent Events (SSE)](https://en.wikipedia.org/wiki/Server-sent_events) that let the server send back the delta of content in event streams.

Streaming responses are beneficial for providing real-time feedback, enhancing user interaction by allowing text to be displayed as it's generated.

To enable streaming, you must set `"stream": true` in your request.

When using streaming output with reasoning models, you might want to **manually override request
timeout** to avoid prematurely closing connection.

```pythonXAI
import os

from xai_sdk import Client
from xai_sdk.chat import user, system

client = Client(
    api_key=os.getenv('XAI_API_KEY'),
    timeout=3600, # Override default timeout with longer timeout for reasoning models
)

chat = client.chat.create(model="grok-4-1-fast-reasoning")
chat.append(
    system("You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."),
)
chat.append(
    user("What is the meaning of life, the universe, and everything?")
)

for response, chunk in chat.stream():
    print(chunk.content, end="", flush=True) # Each chunk's content
    print(response.content, end="", flush=True) # The response object auto-accumulates the chunks

print(response.content) # The full response
```

```pythonOpenAISDK
import os
import httpx
from openai import OpenAI

XAI_API_KEY = os.getenv("XAI_API_KEY")
client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(3600.0) # Timeout after 3600s for reasoning models
)

stream = client.chat.completions.create(
    model="grok-4-1-fast-reasoning",
    messages=[
        {"role": "system", "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."},
        {"role": "user", "content": "What is the meaning of life, the universe, and everything?"},
    ],
    stream=True # Set streaming here
)

for chunk in stream:
    print(chunk.choices[0].delta.content, end="", flush=True)
```

```javascriptOpenAISDK
import OpenAI from "openai";
const openai = new OpenAI({
    apiKey: "<api key>",
    baseURL: "https://api.x.ai/v1",
    timeout: 360000, // Timeout after 3600s for reasoning models
});

const stream = await openai.chat.completions.create({
    model: "grok-4-1-fast-reasoning",
    messages: [
        { role: "system", content: "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy." },
        {
            role: "user",
            content: "What is the meaning of life, the universe, and everything?",
        }
    ],
    stream: true
});

for await (const chunk of stream) {
    console.log(chunk.choices[0].delta.content);
}
```

```javascriptAISDK
import { xai } from '@ai-sdk/xai';
import { streamText } from 'ai';

const result = streamText({
  model: xai.responses('grok-4'),
  system:
    "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy.",
  prompt: 'What is the meaning of life, the universe, and everything?',
});

for await (const chunk of result.textStream) {
  process.stdout.write(chunk);
}
```

```bash
curl https://api.x.ai/v1/chat/completions \\
-H "Content-Type: application/json" \\
-H "Authorization: Bearer $XAI_API_KEY" \\
-m 3600 \\
-d '{
    "messages": [
        {
            "role": "system",
            "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."
        },
        {
            "role": "user",
            "content": "What is the meaning of life, the universe, and everything?"
        }
    ],
    "model": "grok-4-1-fast-reasoning",
    "stream": true
}'
```

You'll get the event streams like these:

```json
data: {
    "id":"<completion_id>","object":"chat.completion.chunk","created":<creation_time>,
    "model":"grok-4-1-fast-reasoning",
    "choices":[{"index":0,"delta":{"content":"Ah","role":"assistant"}}],
    "usage":{"prompt_tokens":41,"completion_tokens":1,"total_tokens":42,
    "prompt_tokens_details":{"text_tokens":41,"audio_tokens":0,"image_tokens":0,"cached_tokens":0}},
    "system_fingerprint":"fp_xxxxxxxxxx"
}

data: {
    "id":"<completion_id>","object":"chat.completion.chunk","created":<creation_time>,
    "model":"grok-4-1-fast-reasoning",
    "choices":[{"index":0,"delta":{"content":",","role":"assistant"}}],
    "usage":{"prompt_tokens":41,"completion_tokens":2,"total_tokens":43,
    "prompt_tokens_details":{"text_tokens":41,"audio_tokens":0,"image_tokens":0,"cached_tokens":0}},
    "system_fingerprint":"fp_xxxxxxxxxx"
}

data: [DONE]
```

It is recommended that you use a client SDK to parse the event stream.

Example streaming responses in Python/Javascript:

```
Ah, the ultimate question! According to Douglas Adams, the answer is **42**. However, the trick lies in figuring out what the actual question is. If you're looking for a bit more context or a different perspective:

- **Philosophically**: The meaning of life might be to seek purpose, happiness, or to fulfill one's potential.
- **Biologically**: It could be about survival, reproduction, and passing on genes.
- **Existentially**: You create your own meaning through your experiences and choices.

But let's not forget, the journey to find this meaning might just be as important as the answer itself! Keep exploring, questioning, and enjoying the ride through the universe. And remember, don't panic!
```


===/developers/model-capabilities/text/structured-outputs===
#### Model Capabilities

# Structured Outputs

Structured Outputs is a feature that lets the API return responses in a specific, organized format, like JSON or other schemas you define. Instead of getting free-form text, you receive data that's consistent and easy to parse.

Ideal for tasks like document parsing, entity extraction, or report generation, it lets you define schemas using tools like
[Pydantic](https://pydantic.dev/) or [Zod](https://zod.dev/) to enforce data types, constraints, and structure.

When using structured outputs, the LLM's response is **guaranteed** to match your input schema.

## Supported models

Structured outputs is supported by all language models.

## Supported schemas

For structured output, the following types are supported for structured output:

* string
  * `minLength` and `maxLength` properties are not supported
* number
  * integer
  * float
* object
* array
  * `minItems` and `maxItem` properties are not supported
  * `maxContains` and `minContains` properties are not supported
* boolean
* enum
* anyOf

`allOf` is not supported at the moment.

## Example: Invoice Parsing

A common use case for Structured Outputs is parsing raw documents. For example, invoices contain structured data like vendor details, amounts, and dates, but extracting this data from raw text can be error-prone. Structured Outputs ensure the extracted data matches a predefined schema.

Let's say you want to extract the following data from an invoice:

* Vendor name and address
* Invoice number and date
* Line items (description, quantity, price)
* Total amount and currency

We'll use structured outputs to have Grok generate a strongly-typed JSON for this.

### Step 1: Defining the Schema

You can use [Pydantic](https://pydantic.dev/) or [Zod](https://zod.dev/) to define your schema.

```pythonWithoutSDK
from datetime import date
from enum import Enum

from pydantic import BaseModel, Field

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"

class LineItem(BaseModel):
    description: str = Field(description="Description of the item or service")
    quantity: int = Field(description="Number of units", ge=1)
    unit_price: float = Field(description="Price per unit", ge=0)

class Address(BaseModel):
    street: str = Field(description="Street address")
    city: str = Field(description="City")
    postal_code: str = Field(description="Postal/ZIP code")
    country: str = Field(description="Country")

class Invoice(BaseModel):
    vendor_name: str = Field(description="Name of the vendor")
    vendor_address: Address = Field(description="Vendor's address")
    invoice_number: str = Field(description="Unique invoice identifier")
    invoice_date: date = Field(description="Date the invoice was issued")
    line_items: list[LineItem] = Field(description="List of purchased items/services")
    total_amount: float = Field(description="Total amount due", ge=0)
    currency: Currency = Field(description="Currency of the invoice")
```

```javascriptWithoutSDK
import { z } from "zod";

const CurrencyEnum = z.enum(["USD", "EUR", "GBP"]);

const LineItemSchema = z.object({
    description: z.string().describe("Description of the item or service"),
    quantity: z.number().int().min(1).describe("Number of units"),
    unit_price: z.number().min(0).describe("Price per unit"),
});

const AddressSchema = z.object({
    street: z.string().describe("Street address"),
    city: z.string().describe("City"),
    postal_code: z.string().describe("Postal/ZIP code"),
    country: z.string().describe("Country"),
});

const InvoiceSchema = z.object({
    vendor_name: z.string().describe("Name of the vendor"),
    vendor_address: AddressSchema.describe("Vendor's address"),
    invoice_number: z.string().describe("Unique invoice identifier"),
    invoice_date: z.string().date().describe("Date the invoice was issued"),
    line_items: z.array(LineItemSchema).describe("List of purchased items/services"),
    total_amount: z.number().min(0).describe("Total amount due"),
    currency: CurrencyEnum.describe("Currency of the invoice"),
});
```

### Step 2: Prepare The Prompts

### System Prompt

The system prompt instructs the model to extract invoice data from text. Since the schema is defined separately, the prompt can focus on the task without explicitly specifying the required fields in the output JSON.

```text
Given a raw invoice, carefully analyze the text and extract the relevant invoice data into JSON format.
```

### Example Invoice Text

```text
Vendor: Acme Corp, 123 Main St, Springfield, IL 62704
Invoice Number: INV-2025-001
Date: 2025-02-10
Items:
- Widget A, 5 units, $10.00 each
- Widget B, 2 units, $15.00 each
Total: $80.00 USD
```

### Step 3: The Final Code

Use the structured outputs feature of the the SDK to parse the invoice.

```pythonXAI
import os
from datetime import date
from enum import Enum

from pydantic import BaseModel, Field

from xai_sdk import Client
from xai_sdk.chat import system, user

# Pydantic Schemas

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"

class LineItem(BaseModel):
    description: str = Field(description="Description of the item or service")
    quantity: int = Field(description="Number of units", ge=1)
    unit_price: float = Field(description="Price per unit", ge=0)

class Address(BaseModel):
    street: str = Field(description="Street address")
    city: str = Field(description="City")
    postal_code: str = Field(description="Postal/ZIP code")
    country: str = Field(description="Country")

class Invoice(BaseModel):
    vendor_name: str = Field(description="Name of the vendor")
    vendor_address: Address = Field(description="Vendor's address")
    invoice_number: str = Field(description="Unique invoice identifier")
    invoice_date: date = Field(description="Date the invoice was issued")
    line_items: list[LineItem] = Field(description="List of purchased items/services")
    total_amount: float = Field(description="Total amount due", ge=0)
    currency: Currency = Field(description="Currency of the invoice")

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(model="grok-4-1-fast-reasoning")

chat.append(system("Given a raw invoice, carefully analyze the text and extract the invoice data into JSON format."))
chat.append(
user("""
Vendor: Acme Corp, 123 Main St, Springfield, IL 62704
Invoice Number: INV-2025-001
Date: 2025-02-10
Items: - Widget A, 5 units, $10.00 each - Widget B, 2 units, $15.00 each
Total: $80.00 USD
""")
)

# The parse method returns a tuple of the full response object as well as the parsed pydantic object.

response, invoice = chat.parse(Invoice)
assert isinstance(invoice, Invoice)

# Can access fields of the parsed invoice object directly

print(invoice.vendor_name)
print(invoice.invoice_number)
print(invoice.invoice_date)
print(invoice.line_items)
print(invoice.total_amount)
print(invoice.currency)

# Can also access fields from the raw response object such as the content.

# In this case, the content is the JSON schema representation of the parsed invoice object

print(response.content)
```

```pythonOpenAISDK
from openai import OpenAI

from pydantic import BaseModel, Field
from datetime import date
from enum import Enum

# Pydantic Schemas

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"

class LineItem(BaseModel):
    description: str = Field(description="Description of the item or service")
    quantity: int = Field(description="Number of units", ge=1)
    unit_price: float = Field(description="Price per unit", ge=0)

class Address(BaseModel):
    street: str = Field(description="Street address")
    city: str = Field(description="City")
    postal_code: str = Field(description="Postal/ZIP code")
    country: str = Field(description="Country")

class Invoice(BaseModel):
    vendor_name: str = Field(description="Name of the vendor")
    vendor_address: Address = Field(description="Vendor's address")
    invoice_number: str = Field(description="Unique invoice identifier")
    invoice_date: date = Field(description="Date the invoice was issued")
    line_items: list[LineItem] = Field(description="List of purchased items/services")
    total_amount: float = Field(description="Total amount due", ge=0)
    currency: Currency = Field(description="Currency of the invoice")

client = OpenAI(
    api_key="<YOUR_XAI_API_KEY_HERE>",
    base_url="https://api.x.ai/v1",
)

completion = client.beta.chat.completions.parse(
    model="grok-4-1-fast-reasoning",
    messages=[
    {"role": "system", "content": "Given a raw invoice, carefully analyze the text and extract the invoice data into JSON format."},
    {"role": "user", "content": """
    Vendor: Acme Corp, 123 Main St, Springfield, IL 62704
    Invoice Number: INV-2025-001
    Date: 2025-02-10
    Items:

    - Widget A, 5 units, $10.00 each
    - Widget B, 2 units, $15.00 each
      Total: $80.00 USD
      """}
      ],
      response_format=Invoice,
  )

invoice = completion.choices[0].message.parsed
print(invoice)
```

```javascriptOpenAISDK
import OpenAI from "openai";
import { zodResponseFormat } from "openai/helpers/zod";
import { z } from "zod";

const CurrencyEnum = z.enum(["USD", "EUR", "GBP"]);

const LineItemSchema = z.object({
    description: z.string().describe("Description of the item or service"),
    quantity: z.number().int().min(1).describe("Number of units"),
    unit_price: z.number().min(0).describe("Price per unit"),
});

const AddressSchema = z.object({
    street: z.string().describe("Street address"),
    city: z.string().describe("City"),
    postal_code: z.string().describe("Postal/ZIP code"),
    country: z.string().describe("Country"),
});

const InvoiceSchema = z.object({
    vendor_name: z.string().describe("Name of the vendor"),
    vendor_address: AddressSchema.describe("Vendor's address"),
    invoice_number: z.string().describe("Unique invoice identifier"),
    invoice_date: z.string().date().describe("Date the invoice was issued"),
    line_items: z.array(LineItemSchema).describe("List of purchased items/services"),
    total_amount: z.number().min(0).describe("Total amount due"),
    currency: CurrencyEnum.describe("Currency of the invoice"),
});

const client = new OpenAI({
    apiKey: "<api key>",
    baseURL: "https://api.x.ai/v1",
});

const completion = await client.beta.chat.completions.parse({
    model: "grok-4-1-fast-reasoning",
    messages: [
    { role: "system", content: "Given a raw invoice, carefully analyze the text and extract the invoice data into JSON format." },
    { role: "user", content: \`
    Vendor: Acme Corp, 123 Main St, Springfield, IL 62704
    Invoice Number: INV-2025-001
    Date: 2025-02-10
    Items:

    - Widget A, 5 units, $10.00 each
    - Widget B, 2 units, $15.00 each
      Total: $80.00 USD
      \` },
    ],
    response_format: zodResponseFormat(InvoiceSchema, "invoice"),
});

const invoice = completion.choices[0].message.parsed;
console.log(invoice);
```

```javascriptAISDK
import { xai } from '@ai-sdk/xai';
import { generateText, Output } from 'ai';
import { z } from 'zod';

const CurrencyEnum = z.enum(['USD', 'EUR', 'GBP']);

const LineItemSchema = z.object({
  description: z.string().describe('Description of the item or service'),
  quantity: z.number().int().min(1).describe('Number of units'),
  unit_price: z.number().min(0).describe('Price per unit'),
});

const AddressSchema = z.object({
  street: z.string().describe('Street address'),
  city: z.string().describe('City'),
  postal_code: z.string().describe('Postal/ZIP code'),
  country: z.string().describe('Country'),
});

const InvoiceSchema = z.object({
  vendor_name: z.string().describe('Name of the vendor'),
  vendor_address: AddressSchema.describe("Vendor's address"),
  invoice_number: z.string().describe('Unique invoice identifier'),
  invoice_date: z.string().date().describe('Date the invoice was issued'),
  line_items: z
    .array(LineItemSchema)
    .describe('List of purchased items/services'),
  total_amount: z.number().min(0).describe('Total amount due'),
  currency: CurrencyEnum.describe('Currency of the invoice'),
});

const result = await generateText({
  model: xai.responses('grok-4'),
  output: Output.object({ schema: InvoiceSchema }),
  system:
    'Given a raw invoice, carefully analyze the text and extract the invoice data into JSON format.',
  prompt: \`
  Vendor: Acme Corp, 123 Main St, Springfield, IL 62704
  Invoice Number: INV-2025-001
  Date: 2025-02-10
  Items:

  - Widget A, 5 units, $10.00 each
  - Widget B, 2 units, $15.00 each
    Total: $80.00 USD
    \`,
});

console.log(result._output);
```

### Step 4: Type-safe Output

The output will **always** be type-safe and respect the input schema.

```json
{
  "vendor_name": "Acme Corp",
  "vendor_address": {
    "street": "123 Main St",
    "city": "Springfield",
    "postal_code": "62704",
    "country": "IL"
  },
  "invoice_number": "INV-2025-001",
  "invoice_date": "2025-02-10",
  "line_items": [
    { "description": "Widget A", "quantity": 5, "unit_price": 10.0 },
    { "description": "Widget B", "quantity": 2, "unit_price": 15.0 }
  ],
  "total_amount": 80.0,
  "currency": "USD"
}
```

## Structured Outputs with Tools

Structured outputs with tools is only available for the Grok 4 family of models (e.g., `grok-4-1-fast`, `grok-4-fast`, `grok-4-1-fast-non-reasoning`, `grok-4-fast-non-reasoning`).

You can combine structured outputs with tool calling to get type-safe responses from tool-augmented queries. This works with both:

* **[Agentic tool calling](/developers/tools/overview)**: Server-side tools like web search, X search, and code execution that the model orchestrates autonomously.
* **[Function calling](/developers/tools/function-calling)**: User-supplied tools where you define custom functions and handle tool execution yourself.

This combination enables workflows where the model can use tools to gather information and return results in a predictable, strongly-typed format.

### Example: Agentic Tools with Structured Output

This example uses web search to find the latest research on a topic and extracts structured data into a schema:

```python customLanguage="pythonWithoutSDK"
from pydantic import BaseModel, Field

class ProofInfo(BaseModel):
    name: str = Field(description="Name of the proof or paper")
    authors: str = Field(description="Authors of the proof")
    year: str = Field(description="Year published")
    summary: str = Field(description="Brief summary of the approach")
```

```javascript customLanguage="javascriptWithoutSDK"
import { z } from "zod";

const ProofInfoSchema = z.object({
    name: z.string().describe("Name of the proof or paper"),
    authors: z.string().describe("Authors of the proof"),
    year: z.string().describe("Year published"),
    summary: z.string().describe("Brief summary of the approach"),
});
```

```python customLanguage="pythonXAI"
import os
from pydantic import BaseModel, Field

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import web_search

# ProofInfo schema defined above

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4-1-fast",
    tools=[web_search()],
)

chat.append(user("Find the latest machine-checked proof of the four color theorem."))

response, proof = chat.parse(ProofInfo)

print(f"Name: {proof.name}")
print(f"Authors: {proof.authors}")
print(f"Year: {proof.year}")
print(f"Summary: {proof.summary}")
```

```python customLanguage="pythonOpenAISDK"
import os
from openai import OpenAI
from pydantic import BaseModel, Field

# ProofInfo schema defined above

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

response = client.responses.parse(
    model="grok-4-1-fast",
    input="Find the latest machine-checked proof of the four color theorem.",
    tools=[
        {"type": "web_search"}
    ],
    text_format=ProofInfo,
)

proof = response.output_parsed
print(f"Name: {proof.name}")
print(f"Authors: {proof.authors}")
print(f"Year: {proof.year}")
print(f"Summary: {proof.summary}")
```

```javascript customLanguage="javascriptOpenAISDK"
import OpenAI from "openai";
import { zodResponseFormat } from "openai/helpers/zod";
import { z } from "zod";

// ProofInfoSchema defined above

const client = new OpenAI({
    apiKey: process.env.XAI_API_KEY,
    baseURL: "https://api.x.ai/v1",
});

// Convert Zod schema to JSON schema format
const format = zodResponseFormat(ProofInfoSchema, "proof_info");

const response = await client.responses.create({
    model: "grok-4-1-fast",
    input: "Find the latest machine-checked proof of the four color theorem.",
    tools: [
        { type: "web_search" }
    ],
    text: {
        format: {
            type: "json_schema",
            name: format.json_schema.name,
            schema: format.json_schema.schema,
            strict: true,
        }
    }
});

// Find the message in the output array
const message = response.output.find((item) => item.type === "message");
const textContent = message?.content?.find((c) => c.type === "output_text");

if (textContent) {
    const proof = JSON.parse(textContent.text);
    console.log(`Name: ${proof.name}`);
    console.log(`Authors: ${proof.authors}`);
    console.log(`Year: ${proof.year}`);
    console.log(`Summary: ${proof.summary}`);
}
```

### Example: Client-side Tools with Structured Output

This example uses a client-side function tool to compute Collatz sequence steps and returns the result in a structured format:

```python customLanguage="pythonWithoutSDK"
from pydantic import BaseModel, Field

class CollatzResult(BaseModel):
    starting_number: int = Field(description="The input number")
    steps: int = Field(description="Number of steps to reach 1")
```

```javascript customLanguage="javascriptWithoutSDK"
const CollatzResultSchema = {
    type: "object",
    properties: {
        starting_number: { type: "integer", description: "The input number" },
        steps: { type: "integer", description: "Number of steps to reach 1" },
    },
    required: ["starting_number", "steps"],
    additionalProperties: false,
};
```

```python customLanguage="pythonXAI"
import os
import json
from pydantic import BaseModel, Field

from xai_sdk import Client
from xai_sdk.chat import tool, tool_result, user

# CollatzResult schema defined above

def collatz_steps(n: int) -> int:
    """Returns the number of steps for n to reach 1 in the Collatz sequence."""
    steps = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps

collatz_tool = tool(
    name="collatz_steps",
    description="Compute the number of steps for a number to reach 1 in the Collatz sequence",
    parameters={
        "type": "object",
        "properties": {
            "n": {"type": "integer", "description": "The starting number"},
        },
        "required": ["n"],
    },
)

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4-1-fast-non-reasoning",
    tools=[collatz_tool],
)

chat.append(user("Use the collatz_steps tool to find how many steps it takes for 20250709 to reach 1."))

# Handle tool calls until we get a final response
while True:
    response = chat.sample()
    
    if not response.tool_calls:
        break
    
    chat.append(response)
    for tc in response.tool_calls:
        args = json.loads(tc.function.arguments)
        result = collatz_steps(args["n"])
        chat.append(tool_result(str(result)))

# Parse the final response into structured output
response, result = chat.parse(CollatzResult)

print(f"Starting number: {result.starting_number}")
print(f"Steps to reach 1: {result.steps}")
```

```python customLanguage="pythonOpenAISDK"
import os
import json
from openai import OpenAI
from pydantic import BaseModel, Field

# CollatzResult schema defined above

def collatz_steps(n: int) -> int:
    """Returns the number of steps for n to reach 1 in the Collatz sequence."""
    steps = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "collatz_steps",
            "description": "Compute the number of steps for a number to reach 1 in the Collatz sequence",
            "parameters": {
                "type": "object",
                "properties": {
                    "n": {"type": "integer", "description": "The starting number"},
                },
                "required": ["n"],
            },
        },
    }
]

messages = [
    {"role": "user", "content": "Use the collatz_steps tool to find how many steps it takes for 20250709 to reach 1."}
]

# Handle tool calls until we get a final response
while True:
    completion = client.chat.completions.create(
        model="grok-4-1-fast-non-reasoning",
        messages=messages,
        tools=tools,
    )
    
    message = completion.choices[0].message
    
    if not message.tool_calls:
        break
    
    messages.append(message)
    for tc in message.tool_calls:
        args = json.loads(tc.function.arguments)
        result = collatz_steps(args["n"])
        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": str(result),
        })

# Final call with structured output
completion = client.beta.chat.completions.parse(
    model="grok-4-1-fast-non-reasoning",
    messages=messages,
    response_format=CollatzResult,
)

result = completion.choices[0].message.parsed
print(f"Starting number: {result.starting_number}")
print(f"Steps to reach 1: {result.steps}")
```

```javascript customLanguage="javascriptOpenAISDK"
import OpenAI from "openai";

// CollatzResultSchema defined above

function collatzSteps(n) {
    let steps = 0;
    while (n !== 1) {
        n = n % 2 === 0 ? n / 2 : 3 * n + 1;
        steps++;
    }
    return steps;
}

const client = new OpenAI({
    apiKey: process.env.XAI_API_KEY,
    baseURL: "https://api.x.ai/v1",
});

const tools = [
    {
        type: "function",
        function: {
            name: "collatz_steps",
            description: "Compute the number of steps for a number to reach 1 in the Collatz sequence",
            parameters: {
                type: "object",
                properties: {
                    n: { type: "integer", description: "The starting number" },
                },
                required: ["n"],
            },
        },
    },
];

let messages = [
    { role: "user", content: "Use the collatz_steps tool to find how many steps it takes for 20250709 to reach 1." }
];

// Handle tool calls until we get a final response
while (true) {
    const completion = await client.chat.completions.create({
        model: "grok-4-1-fast-non-reasoning",
        messages,
        tools,
    });

    const message = completion.choices[0].message;

    if (!message.tool_calls) {
        break;
    }

    messages.push(message);
    for (const tc of message.tool_calls) {
        const args = JSON.parse(tc.function.arguments);
        const result = collatzSteps(args.n);
        messages.push({
            role: "tool",
            tool_call_id: tc.id,
            content: String(result),
        });
    }
}

// Final call with structured output
const completion = await client.chat.completions.create({
    model: "grok-4-1-fast-non-reasoning",
    messages,
    response_format: {
        type: "json_schema",
        json_schema: {
            name: "collatz_result",
            schema: CollatzResultSchema,
            strict: true,
        },
    },
});

const result = JSON.parse(completion.choices[0].message.content);
console.log("Starting number:", result.starting_number);
console.log("Steps to reach 1:", result.steps);
```

## Alternative: Using `response_format` with `sample()` or `stream()`

When using the xAI Python SDK, there's an alternative way to retrieve structured outputs. Instead of using the `parse()` method, you can pass your Pydantic model directly to the `response_format` parameter when creating a chat, and then use `sample()` or `stream()` to get the response.

### How It Works

When you pass a Pydantic model to `response_format`, the SDK automatically:

1. Converts your Pydantic model to a JSON schema
2. Constrains the model's output to conform to that schema
3. Returns the response as a JSON string, that is conforming to the Pydantic model, in `response.content`

You then manually parse the JSON string into your Pydantic model instance.

### Key Differences

| Approach | Method | Returns | Parsing |
|----------|--------|---------|---------|
| **Using `parse()`** | `chat.parse(Model)` | Tuple of `(Response, Model)` | Automatic - SDK parses for you |
| **Using `response_format`** | `chat.sample()` or `chat.stream()` | `Response` with JSON string | Manual - You parse `response.content` |

### When to Use Each Approach

* **Use `parse()`** when you want the simplest, most convenient experience with automatic parsing
* **Use `response_format` + `sample()` or `stream()`** when you:
  * Want more control over the parsing process
  * Need to handle the raw JSON string before parsing
  * Want to use streaming with structured outputs
  * Are integrating with existing code that expects to work with `sample()` or `stream()`

### Example Using `response_format`

```pythonXAI
import os
from datetime import date
from enum import Enum

from pydantic import BaseModel, Field
from xai_sdk import Client
from xai_sdk.chat import system, user

# Pydantic Schemas
class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


class LineItem(BaseModel):
    description: str = Field(description="Description of the item or service")
    quantity: int = Field(description="Number of units", ge=1)
    unit_price: float = Field(description="Price per unit", ge=0)


class Address(BaseModel):
    street: str = Field(description="Street address")
    city: str = Field(description="City")
    postal_code: str = Field(description="Postal/ZIP code")
    country: str = Field(description="Country")


class Invoice(BaseModel):
    vendor_name: str = Field(description="Name of the vendor")
    vendor_address: Address = Field(description="Vendor's address")
    invoice_number: str = Field(description="Unique invoice identifier")
    invoice_date: date = Field(description="Date the invoice was issued")
    line_items: list[LineItem] = Field(description="List of purchased items/services")
    total_amount: float = Field(description="Total amount due", ge=0)
    currency: Currency = Field(description="Currency of the invoice")


client = Client(api_key=os.getenv("XAI_API_KEY"))

# Pass the Pydantic model to response_format instead of using parse()
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    response_format=Invoice,  # Pass the Pydantic model here
)

chat.append(system("Given a raw invoice, carefully analyze the text and extract the invoice data into JSON format."))
chat.append(
    user("""
Vendor: Acme Corp, 123 Main St, Springfield, IL 62704
Invoice Number: INV-2025-001
Date: 2025-02-10
Items: - Widget A, 5 units, $10.00 each - Widget B, 2 units, $15.00 each
Total: $80.00 USD
""")
)

# Use sample() instead of parse() - returns Response object
response = chat.sample()

# The response.content is a valid JSON string conforming to your schema
print(response.content)
# Output: {"vendor_name": "Acme Corp", "vendor_address": {...}, ...}

# Manually parse the JSON string into your Pydantic model
invoice = Invoice.model_validate_json(response.content)
assert isinstance(invoice, Invoice)

# Access fields of the parsed invoice object
print(invoice.vendor_name)
print(invoice.invoice_number)
print(invoice.total_amount)
```

### Streaming with Structured Outputs

You can also use `stream()` with `response_format` to get streaming structured output. The chunks will progressively build up the JSON string:

```pythonXAI
import os

from pydantic import BaseModel, Field
from xai_sdk import Client
from xai_sdk.chat import system, user


class Summary(BaseModel):
    title: str = Field(description="A brief title")
    key_points: list[str] = Field(description="Main points from the text")
    sentiment: str = Field(description="Overall sentiment: positive, negative, or neutral")


client = Client(api_key=os.getenv("XAI_API_KEY"))

chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    response_format=Summary,  # Pass the Pydantic model here
)

chat.append(system("Analyze the following text and provide a structured summary."))
chat.append(user("The new product launch exceeded expectations with record sales..."))


# Stream the response - chunks contain partial JSON
for response, chunk in chat.stream():
    print(chunk.content, end="", flush=True)


# Parse the complete JSON string into your model
summary = Summary.model_validate_json(response.content)
print(f"Title: {summary.title}")
print(f"Sentiment: {summary.sentiment}")
```


===/developers/model-capabilities/video/generation===
#### Model Capabilities

# Video Generation

Generate videos from text prompts, animate still images, or edit existing videos with natural language. The API supports configurable duration, aspect ratio, and resolution for generated videos — with the SDK handling the asynchronous polling automatically.

## Quick Start

Generate a video with a single API call:

```python customLanguage="pythonXAI"
import xai_sdk

client = xai_sdk.Client()

response = client.video.generate(
    prompt="A glowing crystal-powered rocket launching from the red dunes of Mars, ancient alien ruins lighting up in the background as it soars into a sky full of unfamiliar constellations",
    model="grok-imagine-video",
    duration=10,
    aspect_ratio="16:9",
    resolution="720p",
)

print(response.url)
```

```bash
curl -X POST https://api.x.ai/v1/videos/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-video",
    "prompt": "A glowing crystal-powered rocket launching from the red dunes of Mars, ancient alien ruins lighting up in the background as it soars into a sky full of unfamiliar constellations",
    "duration": 10,
    "aspect_ratio": "16:9",
    "resolution": "720p"
  }'
```

Video generation is an **asynchronous process** that typically takes up to several minutes to complete. The exact time varies based on:

* **Prompt complexity** — More detailed scenes require additional processing
* **Duration** — Longer videos take more time to generate
* **Resolution** — Higher resolutions (720p vs 480p) increase processing time
* **Video editing** — Editing existing videos adds overhead compared to image-to-video or text-to-video

### How it works

Under the hood, video generation is a two-step process:

1. **Start** — Submit a generation request and receive a `request_id`
2. **Poll** — Repeatedly check the status using the `request_id` until the video is ready

The xAI SDK's `generate()` method abstracts this entirely — it submits your request, polls for the result, and returns the completed video response. You don't need to manage request IDs or implement polling logic. For long-running generations, you can [customize the polling behavior](#customize-polling-behavior) with timeout and interval parameters, or [handle polling manually](#handle-polling-manually) for full control over the generation lifecycle.

**REST API users** must implement this two-step flow manually:

**Step 1: Start the generation request**

```bash
curl -X POST https://api.x.ai/v1/videos/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-video",
    "prompt": "A glowing crystal-powered rocket launching from Mars"
  }'
```

Response:

```json
{"request_id": "d97415a1-5796-b7ec-379f-4e6819e08fdf"}
```

**Step 2: Poll for the result**

Use the `request_id` to check the status. Keep polling every few seconds until the video is ready:

```bash
curl -X GET "https://api.x.ai/v1/videos/{request_id}" \
  -H "Authorization: Bearer $XAI_API_KEY"
```

The response includes a `status` field with one of these values:

| Status | Description |
|--------|-------------|
| `pending` | Video is still being generated |
| `done` | Video is ready |
| `expired` | Request has expired |

Response (when complete):

```json
{
  "status": "done",
  "video": {
    "url": "https://vidgen.x.ai/.../video.mp4",
    "duration": 8,
    "respect_moderation": true
  },
  "model": "grok-imagine-video"
}
```

Videos are returned as temporary URLs — download or process them promptly.

## Generate Videos from Images

Transform a still image into a video by providing a source image along with your prompt. The model animates the image content based on your instructions.

```python customLanguage="pythonXAI"
import base64
import xai_sdk

client = xai_sdk.Client()

# Load image from file and encode as base64
with open("landscape.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

response = client.video.generate(
    prompt="Animate the clouds drifting across the sky and add gentle swaying to the trees",
    model="grok-imagine-video",
    image_url=f"data:image/jpeg;base64,{image_data}",
)

print(response.url)
```

```bash
# Using a public URL as the source image
curl -X POST https://api.x.ai/v1/videos/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-video",
    "prompt": "Animate the clouds drifting across the sky and add gentle swaying to the trees",
    "image": {"url": "https://example.com/landscape.jpg"}
  }'
```

You can provide the source image as:

* A **public URL** pointing to an image
* A **base64-encoded data URI** (e.g., `data:image/jpeg;base64,...`)

The demo below shows this in action — hold to animate a still image:

## Edit Existing Videos

Edit an existing video by providing a source video along with your prompt. The model understands the video content and applies your requested changes.

The demo below shows video editing in action — `grok-imagine-video` delivers high-fidelity edits with strong scene preservation, modifying only what you ask for while keeping the rest of the video intact:

## Concurrent Requests

When you need to generate multiple videos or apply several edits to the same source video, use `AsyncClient` with `asyncio.gather` to fire requests concurrently. Since video generation and editing are long-running processes, running requests in parallel is significantly faster than issuing them sequentially.

The example below applies all three edits from the interactive demo above — adding a necklace, changing the outfit color, and adding a hat — concurrently:

```python customLanguage="pythonXAI"
import asyncio
import xai_sdk

async def edit_concurrently():
    client = xai_sdk.AsyncClient()

    source_video = "https://example.com/balcony-scene.mp4"

    # Each request applies a different edit to the same video
    prompts = [
        "Give the woman a silver necklace",
        "Change the color of the woman's outfit to red",
        "Give the woman a wide-brimmed black hat",
    ]

    # Fire all edit requests concurrently
    tasks = [
        client.video.generate(
            prompt=prompt,
            model="grok-imagine-video",
            video_url=source_video,
        )
        for prompt in prompts
    ]

    results = await asyncio.gather(*tasks)

    for prompt, result in zip(prompts, results):
        print(f"{prompt}: {result.url}")

asyncio.run(edit_concurrently())
```

## Configuration

The video generation API lets you control the output format of your generated videos. You can specify the duration, aspect ratio, and resolution to match your specific use case.

### Duration

Control video length with the `duration` parameter. The allowed range is 1–15 seconds.

Video editing does not support custom `duration`. The edited video retains the duration of the original, which is capped at 8.7 seconds.

### Aspect Ratio

| Ratio | Use case |
|-------|----------|
| `1:1` | Social media, thumbnails |
| `16:9` / `9:16` | Widescreen, mobile, stories (default: `16:9`) |
| `4:3` / `3:4` | Presentations, portraits |
| `3:2` / `2:3` | Photography |

For image-to-video generation, the output defaults to the input image's aspect ratio. If you specify the `aspect_ratio` parameter, it will override this and stretch the image to the desired aspect ratio.

Video editing does not support custom `aspect_ratio` — the output matches the input video's aspect ratio.

### Resolution

| Resolution | Description |
|------------|-------------|
| `720p` | HD quality |
| `480p` | Standard definition, faster processing (default) |

Video editing does not support custom `resolution`. The output resolution matches the input video's resolution, capped at 720p (e.g., a 1080p input will be downsized to 720p).

### Example

```python customLanguage="pythonXAI"
import xai_sdk

client = xai_sdk.Client()

response = client.video.generate(
    prompt="Timelapse of a flower blooming in a sunlit garden",
    model="grok-imagine-video",
    duration=10,
    aspect_ratio="16:9",
    resolution="720p",
)

print(f"Video URL: {response.url}")
print(f"Duration: {response.duration}s")
```

```bash
curl -X POST https://api.x.ai/v1/videos/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-video",
    "prompt": "Timelapse of a flower blooming in a sunlit garden",
    "duration": 10,
    "aspect_ratio": "16:9",
    "resolution": "720p"
  }'
```

## Customize Polling Behavior

When using the SDK's `generate()` method, you can control how long to wait and how frequently to check for results using the `timeout` and `interval` parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `timeout` | Maximum time to wait for the video to complete | 10 minutes |
| `interval` | Time between status checks | 100 milliseconds |

```python customLanguage="pythonXAI"
from datetime import timedelta
import xai_sdk

client = xai_sdk.Client()

response = client.video.generate(
    prompt="Epic cinematic drone shot flying through mountain peaks",
    model="grok-imagine-video",
    duration=15,
    timeout=timedelta(minutes=15),  # Wait up to 15 minutes
    interval=timedelta(seconds=5),  # Check every 5 seconds
)

print(response.url)
```

If the video isn't ready within the timeout period, a `TimeoutError` is raised. For even finer control, use the [manual polling approach](#handle-polling-manually) with `start()` and `get()`.

## Handle Polling Manually

For fine-grained control over the generation lifecycle, use `start()` to initiate generation and `get()` to check status.

The `get()` method returns a response with a `status` field. Import the status enum from the SDK:

```python customLanguage="pythonXAI"
import time
import xai_sdk
from xai_sdk.proto import deferred_pb2

client = xai_sdk.Client()

# Start the generation request
start_response = client.video.start(
    prompt="A cat lounging in a sunbeam, tail gently swishing",
    model="grok-imagine-video",
    duration=5,
)

print(f"Request ID: {start_response.request_id}")

# Poll for results
while True:
    result = client.video.get(start_response.request_id)
    
    if result.status == deferred_pb2.DeferredStatus.DONE:
        print(f"Video URL: {result.response.video.url}")
        break
    elif result.status == deferred_pb2.DeferredStatus.EXPIRED:
        print("Request expired")
        break
    elif result.status == deferred_pb2.DeferredStatus.PENDING:
        print("Still processing...")
        time.sleep(5)
```

```bash
# Step 1: Start generation
curl -X POST https://api.x.ai/v1/videos/generations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
    "model": "grok-imagine-video",
    "prompt": "A cat lounging in a sunbeam, tail gently swishing",
    "duration": 5
  }'

# Response: {"request_id": "{request_id}"}

# Step 2: Poll for results
curl -X GET https://api.x.ai/v1/videos/{request_id} \
  -H "Authorization: Bearer $XAI_API_KEY"
```

The available status values are:

| Proto Value | Description |
|-------------|-------------|
| `deferred_pb2.DeferredStatus.PENDING` | Video is still being generated |
| `deferred_pb2.DeferredStatus.DONE` | Video is ready |
| `deferred_pb2.DeferredStatus.EXPIRED` | Request has expired |

## Response Details

The xAI SDK exposes additional metadata on the response object beyond the video URL.

**Moderation** — Check whether the generated video passed content moderation:

```python customLanguage="pythonXAI"
if response.respect_moderation:
    print(response.url)
else:
    print("Video filtered by moderation")
```

**Duration** — Get the actual duration of the generated video:

```python customLanguage="pythonXAI"
print(f"Duration: {response.duration} seconds")
```

**Model** — Get the actual model used (resolving any aliases):

```python customLanguage="pythonXAI"
print(f"Model: {response.model}")
```

## Pricing

Video generation uses per-second pricing. Longer videos cost more, and both duration and resolution affect the total cost.

For full pricing details on the `grok-imagine-video` model, see the [model page](/developers/models).

## Limitations

* **Maximum duration:** 15 seconds for generation, 8.7 seconds for editing input videos
* **URL expiration:** Generated URLs are ephemeral and should not be relied upon for long-term storage
* **Resolutions:** 480p or 720p
* **Content moderation:** Videos are subject to content policy review

## Related

* [Models](/developers/models) — Available video models and pricing
* [Image Generation](/developers/model-capabilities/images/generation) — Generate still images from text
* [API Reference](/developers/rest-api-reference) — Full endpoint documentation


===/developers/models===
#### Key Information

# Models and Pricing

An overview of our models' capabilities and their associated pricing.

## Model Pricing

| Model | Modalities | Capabilities | Context | Rate Limits | Pricing [in (cached in) / out] |
| --- | --- | --- | --- | --- | --- |
| grok-4-1-fast-reasoning | text, image → text | functions, structured, reasoning | 2,000,000 | 4M TPM, 480 RPM | $0.20 ($0.05) / $0.50 |
| grok-4-1-fast-reasoning | text, image → text | functions, structured, reasoning | 2,000,000 | 4M TPM, 480 RPM | $0.20 ($0.05) / $0.50 |
| grok-4-1-fast-non-reasoning | text, image → text | functions, structured | 2,000,000 | 4M TPM, 480 RPM | $0.20 ($0.05) / $0.50 |
| grok-4-1-fast-non-reasoning | text, image → text | functions, structured | 2,000,000 | 4M TPM, 480 RPM | $0.20 ($0.05) / $0.50 |
| grok-4-1-fast-non-reasoning | text, image → text | functions, structured | 2,000,000 | 4M TPM, 480 RPM | $0.20 ($0.05) / $0.50 |
| grok-code-fast-1 | text → text | functions, structured, reasoning | 256,000 | 2M TPM, 480 RPM | $0.20 ($0.02) / $1.50 |
| grok-code-fast-1 | text → text | functions, structured, reasoning | 256,000 | 2M TPM, 480 RPM | $0.20 ($0.02) / $1.50 |
| grok-4-0709 | text, image → text | functions, structured, reasoning | 256,000 | 2M TPM, 480 RPM | $3.00 ($0.75) / $15.00 |
| grok-4-0709 | text, image → text | functions, structured, reasoning | 256,000 | 2M TPM, 480 RPM | $3.00 ($0.75) / $15.00 |
| grok-3 | text → text | functions, structured | 131,072 | 600 RPM | $3.00 ($0.75) / $15.00 |
| grok-3 | text → text | functions, structured | 131,072 | 600 RPM | $3.00 ($0.75) / $15.00 |
| grok-3-mini | text → text | functions, structured, reasoning | 131,072 | 480 RPM | $0.30 ($0.07) / $0.50 |
| grok-3-mini | text → text | functions, structured, reasoning | 131,072 | 480 RPM | $0.30 ($0.07) / $0.50 |
| grok-2-image-1212 | text → image | - | - | 300 RPM | $0.07/image |
| grok-2-image-1212 | text → image | - | - | 300 RPM | $0.07/image |
| grok-2-vision-1212 | text, image → text | functions, structured | 32,768 | 600 RPM | $2.00 ($0.00) / $10.00 |
| grok-4-fast-reasoning | text, image → text | functions, structured, reasoning | 2,000,000 | 4M TPM, 480 RPM | $0.20 ($0.05) / $0.50 |
| grok-4-fast-non-reasoning | text, image → text | functions, structured | 2,000,000 | 4M TPM, 480 RPM | $0.20 ($0.05) / $0.50 |
| grok-2-vision-1212 | text, image → text | functions, structured | 32,768 | 600 RPM | $2.00 ($0.00) / $10.00 |
| grok-4-fast-non-reasoning | text, image → text | functions, structured | 2,000,000 | 4M TPM, 480 RPM | $0.20 ($0.05) / $0.50 |
| grok-4-fast-reasoning | text, image → text | functions, structured, reasoning | 2,000,000 | 4M TPM, 480 RPM | $0.20 ($0.05) / $0.50 |
| grok-imagine-image-pro | text, image → image | - | - | 30 RPM | $0.07/image |
| grok-imagine-image | text, image → image | - | - | 300 RPM | $0.02/image |
| grok-imagine-image | text, image → image | - | - | 300 RPM | $0.02/image |
| grok-imagine-image-pro | text, image → image | - | - | 30 RPM | $0.07/image |
| grok-imagine-video | text, image, video → video | - | - | 60 RPM | $0.050/sec |
| grok-imagine-video | text, image, video → video | - | - | 60 RPM | $0.050/sec |


When moving from `grok-3`/`grok-3-mini` to `grok-4`, please note the following differences:

## Tools Pricing

Requests which make use of xAI provided [server-side tools](/developers/tools/overview) are priced based on two components: **token usage** and **server-side tool invocations**. Since the agent autonomously decides how many tools to call, costs scale with query complexity.

### Token Costs

All standard token types are billed at the [rate](#model-pricing) for the model used in the request:

* **Input tokens**: Your query and conversation history
* **Reasoning tokens**: Agent's internal thinking and planning
* **Completion tokens**: The final response
* **Image tokens**: Visual content analysis (when applicable)
* **Cached prompt tokens**: Prompt tokens that were served from cache rather than recomputed

### Tool Invocation Costs

| Tool | Description | Cost / 1k Calls | Tool Name |
| --- | --- | --- | --- |
| Web Search | Search the internet and browse web pages | $5 | `web_search` |
| X Search | Search X posts, user profiles, and threads | $5 | `x_search` |
| Code Execution | Run Python code in a sandboxed environment | $5 | `code_execution`, `code_interpreter*` |
| File Attachments | Search through files attached to messages | $10 | `attachment_search` |
| Collections Search | Query your uploaded document collections (RAG) | $2.50 | `collections_search`, `file_search*` |
| Image Understanding | Analyze images found during Web Search and X Search\*\* | Token-based | `view_image` |
| X Video Understanding | Analyze videos found during X Search\*\* | Token-based | `view_x_video` |
| Remote MCP Tools | Connect and use custom MCP tool servers | Token-based | *(set by MCP server)* |
\* All tool names work in the Responses API. In the gRPC API (Python xAI SDK), `code_interpreter` and `file_search` are not supported.
\*\* Only applies to images and videos found by search tools — not to images passed directly in messages.

For the view image and view x video tools, you will not be charged for the tool invocation itself but will be charged for the image tokens used to process the image or video.

For Remote MCP tools, you will not be charged for the tool invocation but will be charged for any tokens used.

For more information on using Tools, please visit [our guide on Tools](/developers/tools/overview).

## Batch API Pricing

The [Batch API](/developers/advanced-api-usage/batch-api) lets you process large volumes of requests asynchronously at **50% of standard pricing** — effectively cutting your token costs in half. Batch requests are queued and processed in the background, with most completing within 24 hours.

| | Real-time API | Batch API |
|---|---|---|
| **Token pricing** | Standard rates | **50% off** standard rates |
| **Response time** | Immediate (seconds) | Typically within 24 hours |
| **Rate limits** | Per-minute limits apply | Requests don't count towards rate limits |

The 50% discount applies to all token types — input tokens, output tokens, cached tokens, and reasoning tokens. To see batch pricing for a specific model, visit the model's detail page and toggle **"Show batch API pricing"**.

Batch API pricing applies to text and language models only. Image and video generation models are not supported in the Batch API. See [Batch API documentation](/developers/advanced-api-usage/batch-api) for full details, limitations, and usage examples.

## Voice Agent API Pricing

The [Voice Agent API](/developers/model-capabilities/audio/voice-agent) is a real-time voice conversation offering, billed at a straightforward flat rate of $0.05 per minute of connection time.

| | Details |
|---|---|
| **Pricing** | $0.05 / minute ($3.00 / hour) |
| **Rate Limit** | 10 concurrent sessions per team |
| **Capabilities** | Function calling (web search, X search, collections, custom functions) |

When using the Voice Agent API with tools such as function calling, web search, X search, or collections, you will be charged for the tool invocations in addition to the per-minute voice session cost. See [Tool Invocation Costs](#tool-invocation-costs) above for tool pricing details.

For more details on how to get started with the Voice Agent API, see the [Voice Agent API documentation](/developers/model-capabilities/audio/voice-agent).

## Usage Guidelines Violation Fee

When your request is deemed to be in violation of our usage guideline by our system, we will still charge for the generation of the request.

For violations that are caught before generation in the Responses API, we will charge a $0.05 usage guideline violation fee per request.

## Additional Information Regarding Models

* **No access to realtime events without search tools enabled**
  * Grok has no knowledge of current events or data beyond what was present in its training data.
  * To incorporate realtime data with your request, enable server-side search tools (Web Search / X Search). See [Web Search](/developers/tools/web-search) and [X Search](/developers/tools/x-search).
* **Chat models**
  * No role order limitation: You can mix `system`, `user`, or `assistant` roles in any sequence for your conversation context.
* **Image input models**
  * Maximum image size: `20MiB`
  * Maximum number of images: No limit
  * Supported image file types: `jpg/jpeg` or `png`.
  * Any image/text input order is accepted (e.g. text prompt can precede image prompt)

The knowledge cut-off date of Grok 3 and Grok 4 is November, 2024.

## Model Aliases

Some models have aliases to help users automatically migrate to the next version of the same model. In general:

* `<modelname>` is aliased to the latest stable version.
* `<modelname>-latest` is aliased to the latest version. This is suitable for users who want to access the latest features.
* `<modelname>-<date>` refers directly to a specific model release. This will not be updated and is for workflows that demand consistency.

For most users, the aliased `<modelname>` or `<modelname>-latest` are recommended, as you would receive the latest features automatically.

## Billing and Availability

Your model access might vary depending on various factors such as geographical location, account limitations, etc.

For how the **bills are charged**, visit [Manage Billing](/console/billing) for more information.

For the most up-to-date information on **your team's model availability**, visit [Models Page](https://console.x.ai/team/default/models) on xAI Console.

## Model Input and Output

Each model can have one or multiple input and output capabilities.
The input capabilities refer to which type(s) of prompt can the model accept in the request message body.
The output capabilities refer to which type(s) of completion will the model generate in the response message body.

This is a prompt example for models with `text` input capability:

```json
[
  {
    "role": "system",
    "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."
  },
  {
    "role": "user",
    "content": "What is the meaning of life, the universe, and everything?"
  }
]
```

This is a prompt example for models with `text` and `image` input capabilities:

```json
[
  {
    "role": "user",
    "content": [
      {
        "type": "image_url",
        "image_url": {
          "url": "data:image/jpeg;base64,<base64_image_string>",
          "detail": "high"
        }
      },
      {
        "type": "text",
        "text": "Describe what's in this image."
      }
    ]
  }
]
```

This is a prompt example for models with `text` input and `image` output capabilities:

```json
// The entire request body
{
  "model": "grok-4",
  "prompt": "A cat in a tree",
  "n": 4
}
```

## Context Window

The context window determines the maximum amount of tokens accepted by the model in the prompt.

For more information on how token is counted, visit [Consumption and Rate Limits](/developers/rate-limits).

If you are sending the entire conversation history in the prompt for use cases like chat assistant, the sum of all the prompts in your conversation history must be no greater than the context window.

## Cached prompt tokens

Trying to run the same prompt multiple times? You can now use cached prompt tokens to incur less cost on repeated prompts. By reusing stored prompt data, you save on processing expenses for identical requests. Enable caching in your settings and start saving today!

The caching is automatically enabled for all requests without user input. You can view the cached prompt token consumption in [the `"usage"` object](/developers/rate-limits#checking-token-consumption).

For details on the pricing, please refer to the pricing table above, or on [xAI Console](https://console.x.ai).


===/developers/quickstart===
#### Getting Started

# Getting Started

Welcome! In this guide, we'll walk you through the basics of using the xAI API.

## Step 1: Create an xAI Account

First, you'll need to create an xAI account to access xAI API. Sign up for an account [here](https://accounts.x.ai/sign-up?redirect=cloud-console).

Once you've created an account, you'll need to load it with credits to start using the API.

## Step 2: Generate an API Key

Create an API key via the [API Keys Page](https://console.x.ai/team/default/api-keys) in the xAI API Console.

After generating an API key, we need to save it somewhere safe! We recommend you export it as an environment variable in your terminal or save it to a `.env` file.

```bash
export XAI_API_KEY="your_api_key"
```

## Step 3: Make your first request

With your xAI API key exported as an environment variable, you're ready to make your first API request.

Let's test out the API using `curl`. Paste the following directly into your terminal.

```bash
curl https://api.x.ai/v1/responses \\
-H "Content-Type: application/json" \\
-H "Authorization: Bearer $XAI_API_KEY" \\
-m 3600 \\
-d '{
    "input": [
        {
            "role": "system",
            "content": "You are Grok, a highly intelligent, helpful AI assistant."
        },
        {
            "role": "user",
            "content": "What is the meaning of life, the universe, and everything?"
        }
    ],
    "model": "grok-4-1-fast-reasoning"
}'
```

## Step 4: Make a request from Python or Javascript

As well as a native xAI Python SDK, the majority of our APIs are fully compatible with the OpenAI SDK (and the Anthropic SDK, although this is now deprecated). For example, we can make the same request from Python or JavaScript like so:

**Anthropic SDK Deprecated**: The Anthropic SDK compatibility is fully deprecated. Please migrate to the [Responses API](/developers/rest-api-reference/inference/chat#create-new-response) or [gRPC](/developers/grpc-api-reference).

```pythonXAI
# In your terminal, first run:
# pip install xai-sdk

import os

from xai_sdk import Client
from xai_sdk.chat import user, system

client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    timeout=3600, # Override default timeout with longer timeout for reasoning models
)

chat = client.chat.create(model="grok-4-1-fast-reasoning")
chat.append(system("You are Grok, a highly intelligent, helpful AI assistant."))
chat.append(user("What is the meaning of life, the universe, and everything?"))

response = chat.sample()
print(response.content)
```

```pythonOpenAISDK
# In your terminal, first run:

# pip install openai

import os
import httpx
from openai import OpenAI

XAI_API_KEY = os.getenv("XAI_API_KEY")
client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(3600.0), # Override default timeout with longer timeout for reasoning models
)

completion = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[
        {
            "role": "system",
            "content": "You are Grok, a highly intelligent, helpful AI assistant."
        },
        {
            "role": "user",
            "content": "What is the meaning of life, the universe, and everything?"
        },
    ],
)

print(completion.output[0].content)
```

```javascriptAISDK
// In your terminal, first run:
// pnpm add ai @ai-sdk/xai

import { xai } from '@ai-sdk/xai';
import { generateText } from 'ai';

const result = await generateText({
    model: xai.responses('grok-4'),
    system: 'You are Grok, a highly intelligent, helpful AI assistant.',
    prompt: 'What is the meaning of life, the universe, and everything?',
});

console.log(result.text);
```

```javascriptOpenAISDK
// In your terminal, first run:
// npm install openai

import OpenAI from 'openai';

const client = new OpenAI({
    apiKey: "your_api_key",
    baseURL: "https://api.x.ai/v1",
    timeout: 360000, // Override default timeout with longer timeout for reasoning models
});

const response = await client.responses.create({
    model: "grok-4-1-fast-reasoning",
    input: [
        {
            role: "system",
            content:
            "You are Grok, a highly intelligent, helpful AI assistant.",
        },
        {
            role: "user",
            content:
            "What is the meaning of life, the universe, and everything?",
        },
    ],
});

console.log(response.output[0].content);
```

```bash
curl https://api.x.ai/v1/chat/completions \\
-H "Content-Type: application/json" \\
-H "Authorization: Bearer $XAI_API_KEY" \\
-m 3600 \\
-d '{
    "messages": [
        {
            "role": "system",
            "content": "You are Grok, a highly intelligent, helpful AI assistant."
        },
        {
            "role": "user",
            "content": "What is the meaning of life, the universe, and everything?"
        }
    ],
    "model": "grok-4-1-fast-reasoning"
}'
```

Certain models also support [Structured Outputs](/developers/model-capabilities/text/structured-outputs), which allows you to enforce a schema for the LLM output.

For an in-depth guide about using Grok for text responses, check out our [Text Generation Guide](/developers/model-capabilities/text/generate-text).

## Step 5: Use Grok to analyze images

Certain grok models can accept both text AND images as an input. For example:

```pythonXAI
import os

from xai_sdk import Client
from xai_sdk.chat import user, image

client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    timeout=3600, # Override default timeout with longer timeout for reasoning models
)

chat = client.chat.create(model="grok-4")
chat.append(
    user(
        "What's in this image?",
        image("https://science.nasa.gov/wp-content/uploads/2023/09/web-first-images-release.png")
    )
)

response = chat.sample()
print(response.content)
```

```pythonOpenAISDK
import os
import httpx
from openai import OpenAI

XAI_API_KEY = os.getenv("XAI_API_KEY")
image_url = "https://science.nasa.gov/wp-content/uploads/2023/09/web-first-images-release.png"

client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(3600.0), # Override default timeout with longer timeout for reasoning models
)

completion = client.responses.create(
    model="grok-4",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_image",
                    "image_url": image_url,
                    "detail": "high",
                },
                {
                    "type": "input_text",
                    "text": "What's in this image?",
                },
            ],
        },
    ],
)
print(completion.output[0].content)
```

```javascriptAISDK
import { xai } from '@ai-sdk/xai';
import { generateText } from 'ai';

const imageUrl =
'https://science.nasa.gov/wp-content/uploads/2023/09/web-first-images-release.png';

const result = await generateText({
    model: xai.responses('grok-4'),
    messages: [
        {
            role: 'user',
            content: [
                { type: 'image', image: imageUrl },
                { text: "What's in this image?", type: 'text' },
            ],
        },
    ],
});

console.log(result.text);
```

```javascriptOpenAISDK
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: process.env.XAI_API_KEY,
    baseURL: "https://api.x.ai/v1",
    timeout: 360000, // Override default timeout with longer timeout for reasoning models
});

const image_url =
"https://science.nasa.gov/wp-content/uploads/2023/09/web-first-images-release.png";

const completion = await client.responses.create({
    model: "grok-4",
    input: [
        {
            role: "user",
            content: [
                {
                    type: "input_image",
                    image_url: image_url,
                    detail: "high",
                },
                {
                    type: "input_text",
                    text: "What's in this image?",
                },
            ],
        },
    ],
});

console.log(completion.output[0].content);
```

```bash
curl https://api.x.ai/v1/responses \\
-H "Content-Type: application/json" \\
-H "Authorization: Bearer $XAI_API_KEY" \\
-m 3600 \\
-d '{
    "model": "grok-4",
    "input": [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_image",
                    "image_url": "https://science.nasa.gov/wp-content/uploads/2023/09/web-first-images-release.png",
                    "detail": "high"
                },
                {
                    "type": "input_text",
                    "text": "Describe this image"
                }
            ]
        }
    ]
}'
```

And voila! Grok will tell you exactly what's in the image:

> This image is a photograph of a region in space, specifically a part of the Carina Nebula, captured by the James Webb Space Telescope. It showcases a stunning view of interstellar gas and dust, illuminated by young, hot stars. The bright points of light are stars, and the colorful clouds are composed of various gases and dust particles. The image highlights the intricate details and beauty of star formation within a nebula.

To learn how to use Grok vision for more advanced use cases, check out our [Image Understanding](/developers/model-capabilities/images/understanding).


===/developers/rate-limits===
#### Key Information

# Consumption and Rate Limits

The cost of using our API is based on token consumption. We charge different prices based on token category:

* **Prompt text, audio and image tokens** - Charged at prompt token price
* **Cached prompt tokens** - Charged at cached prompt token price
* **Completion tokens** - Charged at completion token price
* **Reasoning tokens** - Charged at completion token price

Visit [Models and Pricing](../models) for general pricing, or [xAI Console](https://console.x.ai) for pricing applicable to your team.

Each `grok` model has different rate limits. To check your team's rate limits, you can visit [xAI Console Models Page](https://console.x.ai/team/default/models).

## Basic unit to calculate consumption — Tokens

A token is the basic unit of prompt size for model inference and pricing purposes. It consists of one or more character(s)/symbol(s).

When a Grok model handles your request, an input prompt will be decomposed into a list of tokens through a tokenizer.
The model will then make inference based on the prompt tokens, and generate completion tokens.
After the inference is completed, the completion tokens will be aggregated into a completion response sent back to you.

Our system will add additional formatting tokens to the input/output token, and if you selected a reasoning model, additional reasoning tokens will be added into the total token consumption as well.
Your actual consumption will be reflected either in the `usage` object returned in the API response, or in Usage Explorer on the [xAI Console](https://console.x.ai).

You can use [Tokenizer](https://console.x.ai/team/default/tokenizer) on xAI Console to visualize tokens a given text prompt, or use [Tokenize text](/developers/rest-api-reference/inference/other#tokenize-text) endpoint on the API.

### Text tokens

Tokens can be either of a whole word, or smaller chunks of character combinations. The more common a word is, the more likely it would be a whole token.

For example, Flint is broken down into two tokens, while Michigan is a whole token.

In another example, most words are tokens by themselves, but "drafter" is broken down into "dra" and "fter", and "postmaster" is broken down into "post" and "master".

For a given text/image/etc. prompt or completion sequence, different tokenizers may break it down into different lengths of lists.

Different Grok models may also share or use different tokenizers. Therefore, **the same prompt/completion sequence may not have the same amount of tokens across different models.**

The token count in a prompt/completion sequence should be approximately linear to the sequence length.

### Image prompt tokens

Each image prompt will take between 256 to 1792 tokens, depending on the size of the image. The image + text token count must be less than the overall context window of the model.

### Estimating consumption with tokenizer on xAI Console or through API

The tokenizer page or API might display less token count than the actual token consumption. The
inference endpoints would automatically add pre-defined tokens to help our system process the
request.

On xAI Console, you can use the [tokenizer page](https://console.x.ai/team/default/tokenizer) to estimate how many tokens your text prompt will consume. For example, the following message would consume 5 tokens (the actual consumption may vary because of additional special tokens added by the system).

Message body:

```json
[
  {
    "role": "user",
    "content": "How is the weather today?"
  }
]
```

Tokenize result on Tokenizer page:

You can also utilize the [Tokenize Text](/developers/rest-api-reference/inference/other#tokenize-text) API endpoint to tokenize the text, and count the output token array length.

### Cached prompt tokens

When you send the same prompt multiple times, we may cache your prompt tokens. This would result in reduced cost for these tokens at the cached token rate, and a quicker response.

The prompt is cached using prefix matching, using cache for the exact prefix matches in the subsequent requests. However, the cache size might be limited and distributed across different clusters.

You can also specify `x-grok-conv-id: <A constant uuid4 ID>` in the HTTP request header, to increase the likelihood of cache hit in the subsequent requests using the same header.

### Reasoning tokens

The model may use reasoning to process your request. The reasoning content is returned in the response's `reasoning_content` field. The reasoning token consumption will be counted separately from `completion_tokens`, but will be counted in the `total_tokens`.

The reasoning tokens will be charged at the same price as `completion_tokens`.

`grok-4` does not return `reasoning_content`

## Hitting rate limits

To request a higher rate limit, please email support@x.ai with your anticipated volume.

For each tier, there is a maximum amount of requests per minute and tokens per minute. This is to ensure fair usage by all users of the system.

Once your request frequency has reached the rate limit, you will receive error code `429` in response.

You can either:

* Upgrade your team to higher tiers
* Change your consumption pattern to send fewer requests

## Checking token consumption

In each completion response, there is a `usage` object detailing your prompt and completion token count. You might find it helpful to keep track of it, in order to avoid hitting rate limits or having cost surprises. You can view more details of the object on our [API Reference](/developers/rest-api-reference).

```json
"usage": {
    "prompt_tokens": 199,
    "completion_tokens": 1,
    "total_tokens": 200,
    "prompt_tokens_details": {
        "text_tokens": 199,
        "audio_tokens": 0,
        "image_tokens": 0,
        "cached_tokens": 163
    },
    "completion_tokens_details": {
        "reasoning_tokens": 0,
        "audio_tokens": 0,
        "accepted_prediction_tokens": 0,
        "rejected_prediction_tokens": 0
    },
    "num_sources_used": 0,
    "cost_in_usd_ticks": 158500
}
```

The `cost_in_usd_ticks` field expresses the total cost to perform the inference, in 1/10,000,000,000 US dollar.

**Note:** The `usage.prompt_tokens_details.text_tokens` is the total text input token, which includes `cached_tokens` and non-cached text tokens.

You can also check with the xAI or OpenAI SDKs (Anthropic SDK is deprecated).

```pythonXAI
import os

from xai_sdk import Client
from xai_sdk.chat import system, user

client = Client(api_key=os.getenv("XAI_API_KEY"))

chat = client.chat.create(
model="grok-4-1-fast-reasoning",
messages=[system("You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy.")]
)
chat.append(user("What is the meaning of life, the universe, and everything?"))

response = chat.sample()
print(response.usage)
```

```pythonOpenAISDK
import os
from openai import OpenAI

XAI_API_KEY = os.getenv("XAI_API_KEY")
client = OpenAI(base_url="https://api.x.ai/v1", api_key=XAI_API_KEY)

completion = client.chat.completions.create(
model="grok-4-1-fast-reasoning",
messages=[
{
"role": "system",
"content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy.",
},
{
"role": "user",
"content": "What is the meaning of life, the universe, and everything?",
},
],
)

if completion.usage:
print(completion.usage.to_json())
```

```javascriptOpenAISDK
import OpenAI from "openai";
const openai = new OpenAI({
apiKey: "<api key>",
baseURL: "https://api.x.ai/v1",
});

const completion = await openai.chat.completions.create({
model: "grok-4-1-fast-reasoning",
messages: [
{
role: "system",
content:
"You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy.",
},
{
role: "user",
content:
"What is the meaning of life, the universe, and everything?",
},
],
});

console.log(completion.usage);
```


===/developers/regions===
#### Key Information

# Regional Endpoints

By default, you can access our API at `https://api.x.ai`. This is the most suitable endpoint for most customers,
as the request will be automatically routed by us to be processed in the region with lowest latency for your request.

For example, if you are based in US East Coast and send your request to `https://api.x.ai`, your request will be forwarded
to our `us-east-1` region and we will try to process it there first. If there is not enough computing resource in `us-east-1`,
we will send your request to other regions that are geographically closest to you and can handle the request.

## Using a regional endpoint

If you have specific data privacy requirements that would require the request to be processed within a specified region,
you can leverage our regional endpoint.

You can send your request to `https://<region-name>.api.x.ai`. For the same example, to send request from US East Coast to `us-east-1`,
you will now send the request to `https://us-east-1.api.x.ai`. If for some reason, we cannot handle your request in `us-east-1`, the request will fail.

## Example of using regional endpoints

If you want to use a regional endpoint, you need to specify the endpoint url when making request with SDK. In xAI SDK, this is specified through the `api_host` parameter.

For example, to send request to `us-east-1`:

```pythonWithoutSDK
import os

from xai_sdk import Client
from xai_sdk.chat import user

client = Client(
    api_key=os.getenv("XAI_API_KEY"),
    api_host="us-east-1.api.x.ai" # Without the https://
)

chat = client.chat.create(model="grok-4-1-fast-reasoning")
chat.append(user("What is the meaning of life?"))

completion = chat.sample()
```

```pythonOpenAISDK
from openai import OpenAI

client = OpenAI(
    api_key=XAI_API_KEY,
    base_url="https://us-east-1.api.x.ai/v1",
)

completion = client.chat.completions.create(
    model="grok-4-1-fast-reasoning",
    messages=[
        {"role": "user", "content": "What is the meaning of life?"}
    ]
)
```

```javascriptOpenAISDK
import OpenAI from "openai";

const client = new OpenAI({
    apiKey: XAI_API_KEY,
    baseURL: "https://us-east-1.api.x.ai/v1",
});

const completion = await client.chat.completions.create({
    model: "grok-4-1-fast-reasoning",
    messages: [
        { role: "user", content: "What is the meaning of life?" }
    ]
});
```

```bash
curl https://us-east-1.api.x.ai/v1/chat/completions \\
-H "Content-Type: application/json" \\
-H "Authorization: Bearer $XAI_API_KEY" \\
-d '{
    "messages": [
        {
            "role": "user",
            "content": "What is the meaning of life, the universe, and everything?"
        }
    ],
    "model": "grok-4-1-fast-reasoning",
    "stream": false
}'
```

## Model availability across regions

While we strive to make every model available across all regions, there could be occasions where some models are not
available in some regions.

By using the global `https://api.x.ai` endpoint, you would have access to all models available to your team, since we
route your request automatically. If you're using a regional endpoint, please refer to [xAI Console](https://console.x.ai)
for the available models to your team in each region, or [Models and Pricing](../models) for the publicly available models.


===/developers/release-notes===
#### Release Notes

# Release Notes

Stay up to date with the latest changes to the xAI API.

# January 2026

### Video Generation & Next-Gen Image Generation

[Video Generation](/developers/model-capabilities/video/generation) and a revamped [Image Generation](/developers/model-capabilities/images/generation) are now available.

### Batch API is released

[Batch API](/developers/advanced-api-usage/batch-api) is available for all customers. It enables efficient batch processing of multiple requests, providing a better experience for users who need to submit large volumes of requests at once.

# December 2025

### Grok Voice Agent API is released

Grok Voice Agent API is generally available. Visit [Grok Voice Agent API](/developers/model-capabilities/audio/voice) for guidance on using the API.

# November 2025

### Grok 4.1 Fast is available in Enterprise API

You can now use Grok 4.1 Fast in the [xAI Enterprise API](https://x.ai/api). For more details, check out [our blogpost](https://x.ai/news/grok-4-1-fast).

### Agent tools adapt to Grok 4.1 Fast models and tool prices dropped

* You can now use Grok 4.1 Fast models with the agent tools, check out the [documentation of agent tools](/developers/tools/overview) to get started.
* The price of agent tools drops by up to 50% to no more than $5 per 1000 successful calls, see the new prices at [the pricing page](/developers/models#tools-pricing).

### Files API is generally available

You can now upload files and use them in chat conversations with the Files API. For more details, check out [our guide on Files](/developers/files).

### New Tools Available

* **Collections Search Tool**: You can now search through uploaded knowledge bases (collections) in chat conversations via the API. For more details, check out the [docs](/developers/tools/collections-search).
* **Remote MCP Tools**: You can now use tools from remote MCP servers in chat conversations via the API. For more details, check out the [docs](/developers/tools/remote-mcp).
* **Mixing client-side and server-side tools**: You can now mix client-side and server-side tools in the same chat conversation. For more details, check out the [docs](/developers/tools/advanced-usage#mixing-server-side-and-client-side-tools).

# October 2025

### Tools are now generally available

New agentic server-side tools including `web_search`, `x_search` and `code_execution` are available. For more details, check out [our guide on using Tools](/developers/tools/overview).

# September 2025

### Responses API is generally available

You can now use our stateful Responses API to process requests.

# August 2025

### Grok Code Fast 1 is released

We have released our first Code Model to be used with code editors.

### Collections API is released

You can upload files, create embeddings, and use them for inference with our Collections API.

# July 2025

### Grok 4 is released

You can now use Grok 4 via our API or on https://grok.com.

# June 2025

### Management API is released

You can manage your API keys via Management API at
`https://management-api.x.ai`.

# May 2025

### Cached prompt is now available

You can now use cached prompt to save on repeated prompts. For
more info, see [models](/developers/models).

### Live Search is available on API

Live search is now available on API. Users can generate
completions with queries on supported data sources.

# April 2025

### Grok 3 models launch on API

Our latest flagship `Grok 3` models are now generally available via
the API. For more info, see [models](/developers/models).

# March 2025

### Image Generation Model available on API

The image generation model is available on API. Visit
[Image Generations](/developers/model-capabilities/images/generation) for more details on using the model.

# February 2025

### Audit Logs

Team admins can now view audit logs on [console.x.ai](https://console.x.ai).

# January 2025

### Docs Dark Mode

Released dark mode support on docs.x.ai

### Status Page

Check service statuses across all xAI products at
[status.x.ai](https://status.x.ai/).

# December 2024

### Replit & xAI

Replit Agents can now integrate with xAI! Start empowering your agents with Grok.
Check out the [announcement](https://x.com/Replit/status/1874211039258333643) for more information.

### Tokenizer Playground Understanding tokens can be hard. Check out

[console.x.ai](https://console.x.ai) to get a better understanding of what counts as a token.

### Structured Outputs

We're excited to announce that Grok now supports structured outputs. Grok can
now format responses in a predefined, organized format rather than free-form text. 1. Specify the
desired schema

```
{
    "name": "movie_response",
    "schema": {
        "type": "object",
        "properties": {
            "title": { "type": "string" },
            "rating": { "type": "number" },
        },
        "required": [ "title", "rating" ],
        "additionalProperties": false
    },
    "strict": true
}
```

2. Get the desired data

```
{
  "title": "Star Wars",
  "rating": 8.6
}
```

Start building more reliable applications. Check out the [docs](/developers/model-capabilities/text/structured-outputs) for more information.

### Released the new grok-2-1212 and grok-2-vision-1212 models A month ago, we launched the public

beta of our enterprise API with grok-beta and grok-vision-beta. We’re adding [grok-2-1212 and
grok-2-vision-1212](/developers/models), offering better accuracy, instruction-following,
and multilingual capabilities.

# November 2024

### LangChain & xAI Our API is now available through LangChain! - Python Docs:

https://python.langchain.com/integrations/providers/xai/ - Javascript Docs:
https://js.langchain.com/integrations/chat/xai/

What are you going to build?

### API Public Beta

We are happy to announce the immediate availability of our API, which
gives developers programmatic access to our Grok series of foundation models. To get started, head
to [console.x.ai](https://console.x.ai/) and sign up to create an account. We are excited to see
what developers build using Grok.


===/developers/rest-api-reference/collections/collection===
#### Collections API

# Collection Management

The base URL for `collection` management is shared with [Management API](/developers/rest-api-reference/management) at `https://management-api.x.ai/`.
You have to authenticate using **xAI Management API Key** with the header `Authorization: Bearer <your xAI Management API key>`.

For more details on provisioning xAI Management API key and using Management API, you can visit

***

## POST /v1/collections

API endpoint for POST requests to /v1/collections.

```
Method: POST
Path: /v1/collections
```

***

## GET /v1/collections

API endpoint for GET requests to /v1/collections.

```
Method: GET
Path: /v1/collections
```

***

## GET /v1/collections/\{collection\_id}

API endpoint for GET requests to /v1/collections/\{collection\_id}.

```
Method: GET
Path: /v1/collections/{collection_id}
```

***

## DELETE /v1/collections/\{collection\_id}

API endpoint for DELETE requests to /v1/collections/\{collection\_id}.

```
Method: DELETE
Path: /v1/collections/{collection_id}
```

***

## PUT /v1/collections/\{collection\_id}

API endpoint for PUT requests to /v1/collections/\{collection\_id}.

```
Method: PUT
Path: /v1/collections/{collection_id}
```

***

## POST /v1/collections/\{collection\_id}/documents/\{file\_id}

API endpoint for POST requests to /v1/collections/\{collection\_id}/documents/\{file\_id}.

```
Method: POST
Path: /v1/collections/{collection_id}/documents/{file_id}
```

***

## GET /v1/collections/\{collection\_id}/documents

API endpoint for GET requests to /v1/collections/\{collection\_id}/documents.

```
Method: GET
Path: /v1/collections/{collection_id}/documents
```

***

## GET /v1/collections/\{collection\_id}/documents/\{file\_id}

API endpoint for GET requests to /v1/collections/\{collection\_id}/documents/\{file\_id}.

```
Method: GET
Path: /v1/collections/{collection_id}/documents/{file_id}
```

***

## PATCH /v1/collections/\{collection\_id}/documents/\{file\_id}

API endpoint for PATCH requests to /v1/collections/\{collection\_id}/documents/\{file\_id}.

```
Method: PATCH
Path: /v1/collections/{collection_id}/documents/{file_id}
```

***

## DELETE /v1/collections/\{collection\_id}/documents/\{file\_id}

API endpoint for DELETE requests to /v1/collections/\{collection\_id}/documents/\{file\_id}.

```
Method: DELETE
Path: /v1/collections/{collection_id}/documents/{file_id}
```

***

## GET /v1/collections/\{collection\_id}/documents:batchGet

API endpoint for GET requests to /v1/collections/\{collection\_id}/documents:batchGet.

```
Method: GET
Path: /v1/collections/{collection_id}/documents:batchGet
```


===/developers/rest-api-reference/collections===
#### Collections API

# Collections REST API Overview

The Collections API allows you to manage your Collections `documents` and `collections` programmatically.

The base url for `collection` management is shared with [Management API](/developers/rest-api-reference/management) at `https://management-api.x.ai/v1/`. You have to authenticate using **xAI Management API Key** with the header `Authorization: Bearer <your xAI Management API key>`.

For more details on provisioning xAI Management API key and using Management API, you can visit

.

The base url for searching within `collections` is shared with [REST API](/developers/rest-api-reference) at `https://api.x.ai`. You have to authenticate with the header `Authorization: Bearer <your xAI API key>`.

* [Collection Management](/developers/rest-api-reference/collections/collection)
* [Search in Collections](/developers/rest-api-reference/collections/search)


===/developers/rest-api-reference/collections/search===
#### Collections API

# Search in Collections

The base url for searching `collections` is shared with [REST API](/developers/rest-api-reference) at `https://api.x.ai`. You have to authenticate using **xAI API Key** with the header `Authorization: Bearer <your xAI API key>`.

***

## POST /v1/documents/search

API endpoint for POST requests to /v1/documents/search.

```
Method: POST
Path: /v1/documents/search
```


===/developers/rest-api-reference/files/download===
#### Files API

# Download

***

## POST /v1/files:download

API endpoint for POST requests to /v1/files:download.

```
Method: POST
Path: /v1/files:download
```


===/developers/rest-api-reference/files/manage===
#### Files API

# Manage

***

## GET /v1/files

API endpoint for GET requests to /v1/files.

```
Method: GET
Path: /v1/files
```

***

## GET /v1/files/\{file\_id}

API endpoint for GET requests to /v1/files/\{file\_id}.

```
Method: GET
Path: /v1/files/{file_id}
```

***

## PUT /v1/files/\{file\_id}

API endpoint for PUT requests to /v1/files/\{file\_id}.

```
Method: PUT
Path: /v1/files/{file_id}
```

***

## DELETE /v1/files/\{file\_id}

API endpoint for DELETE requests to /v1/files/\{file\_id}.

```
Method: DELETE
Path: /v1/files/{file_id}
```


===/developers/rest-api-reference/files===
#### Files API

# Files REST API Overview

The Files API allows you to upload, manage, and download files for use with Grok models. Files can be attached to chat messages for document understanding, or added to collections for semantic search.

The base URL for all file operations is `https://api.x.ai`. You have to authenticate with the header `Authorization: Bearer <your xAI API key>`.

* [Upload](/developers/rest-api-reference/files/upload)
* [Manage](/developers/rest-api-reference/files/manage)
* [Download](/developers/rest-api-reference/files/download)


===/developers/rest-api-reference/files/upload===
#### Files API

# Upload

***

## POST /v1/files

API endpoint for POST requests to /v1/files.

```
Method: POST
Path: /v1/files
```

***

## POST /v1/files/batch\_upload

API endpoint for POST requests to /v1/files/batch\_upload.

```
Method: POST
Path: /v1/files/batch_upload
```

***

## POST /v1/files/batch\_upload/\{batch\_job\_id}:complete

API endpoint for POST requests to /v1/files/batch\_upload/\{batch\_job\_id}:complete.

```
Method: POST
Path: /v1/files/batch_upload/{batch_job_id}:complete
```

***

## POST /v1/files:initialize

API endpoint for POST requests to /v1/files:initialize.

```
Method: POST
Path: /v1/files:initialize
```

***

## POST /v1/files:uploadChunks

API endpoint for POST requests to /v1/files:uploadChunks.

```
Method: POST
Path: /v1/files:uploadChunks
```


===/developers/rest-api-reference/inference/batches===
#### Inference API

# Batches

***

## POST /v1/batches

API endpoint for POST requests to /v1/batches.

```
Method: POST
Path: /v1/batches
```

***

## GET /v1/batches

API endpoint for GET requests to /v1/batches.

```
Method: GET
Path: /v1/batches
```

***

## GET /v1/batches/\{batch\_id}

API endpoint for GET requests to /v1/batches/\{batch\_id}.

```
Method: GET
Path: /v1/batches/{batch_id}
```

***

## GET /v1/batches/\{batch\_id}/requests

API endpoint for GET requests to /v1/batches/\{batch\_id}/requests.

```
Method: GET
Path: /v1/batches/{batch_id}/requests
```

***

## POST /v1/batches/\{batch\_id}/requests

API endpoint for POST requests to /v1/batches/\{batch\_id}/requests.

```
Method: POST
Path: /v1/batches/{batch_id}/requests
```

***

## GET /v1/batches/\{batch\_id}/results

API endpoint for GET requests to /v1/batches/\{batch\_id}/results.

```
Method: GET
Path: /v1/batches/{batch_id}/results
```

***

## POST /v1/batches/\{batch\_id}:cancel

API endpoint for POST requests to /v1/batches/\{batch\_id}:cancel.

```
Method: POST
Path: /v1/batches/{batch_id}:cancel
```


===/developers/rest-api-reference/inference/chat===
#### Inference API

# Chat

***

## POST /v1/chat/completions

API endpoint for POST requests to /v1/chat/completions.

```
Method: POST
Path: /v1/chat/completions
```

***

## POST /v1/responses

API endpoint for POST requests to /v1/responses.

```
Method: POST
Path: /v1/responses
```

***

## GET /v1/responses/\{response\_id}

API endpoint for GET requests to /v1/responses/\{response\_id}.

```
Method: GET
Path: /v1/responses/{response_id}
```

***

## DELETE /v1/responses/\{response\_id}

API endpoint for DELETE requests to /v1/responses/\{response\_id}.

```
Method: DELETE
Path: /v1/responses/{response_id}
```

***

## GET /v1/chat/deferred-completion/\{request\_id}

API endpoint for GET requests to /v1/chat/deferred-completion/\{request\_id}.

```
Method: GET
Path: /v1/chat/deferred-completion/{request_id}
```


===/developers/rest-api-reference/inference/images===
#### Inference API

# Images

***

## POST /v1/images/generations

API endpoint for POST requests to /v1/images/generations.

```
Method: POST
Path: /v1/images/generations
```

***

## POST /v1/images/edits

API endpoint for POST requests to /v1/images/edits.

```
Method: POST
Path: /v1/images/edits
```


===/developers/rest-api-reference/inference/legacy===
#### Inference API

# Legacy & Deprecated

***

## POST /v1/completions

API endpoint for POST requests to /v1/completions.

```
Method: POST
Path: /v1/completions
```

***

**Deprecated**: The Anthropic SDK compatibility is fully deprecated. Please migrate to the [Responses API](/developers/rest-api-reference/inference/chat#create-new-response) or [gRPC](/developers/grpc-api-reference).

## POST /v1/messages

API endpoint for POST requests to /v1/messages.

```
Method: POST
Path: /v1/messages
```

***

**Deprecated**: The Anthropic SDK compatibility is fully deprecated. Please migrate to the [Responses API](/developers/rest-api-reference/inference/chat#create-new-response) or [gRPC](/developers/grpc-api-reference).

## POST /v1/complete

API endpoint for POST requests to /v1/complete.

```
Method: POST
Path: /v1/complete
```


===/developers/rest-api-reference/inference/models===
#### Inference API

# Models

***

## GET /v1/models

API endpoint for GET requests to /v1/models.

```
Method: GET
Path: /v1/models
```

***

## GET /v1/models/\{model\_id}

API endpoint for GET requests to /v1/models/\{model\_id}.

```
Method: GET
Path: /v1/models/{model_id}
```

***

## GET /v1/language-models

API endpoint for GET requests to /v1/language-models.

```
Method: GET
Path: /v1/language-models
```

***

## GET /v1/language-models/\{model\_id}

API endpoint for GET requests to /v1/language-models/\{model\_id}.

```
Method: GET
Path: /v1/language-models/{model_id}
```

***

## GET /v1/image-generation-models

API endpoint for GET requests to /v1/image-generation-models.

```
Method: GET
Path: /v1/image-generation-models
```

***

## GET /v1/image-generation-models/\{model\_id}

API endpoint for GET requests to /v1/image-generation-models/\{model\_id}.

```
Method: GET
Path: /v1/image-generation-models/{model_id}
```


===/developers/rest-api-reference/inference/other===
#### Inference API

# Other

***

## GET /v1/api-key

API endpoint for GET requests to /v1/api-key.

```
Method: GET
Path: /v1/api-key
```

***

## POST /v1/tokenize-text

API endpoint for POST requests to /v1/tokenize-text.

```
Method: POST
Path: /v1/tokenize-text
```


===/developers/rest-api-reference/inference===
#### Inference API

# Inference REST API Overview

The xAI Inference REST API is a robust, high-performance RESTful interface designed for seamless integration into existing systems.
It offers advanced AI capabilities with full compatibility with the OpenAI REST API.

The base for all routes is at `https://api.x.ai`. For all routes, you have to authenticate with the header `Authorization: Bearer <your xAI API key>`.

* [Chat](/developers/rest-api-reference/inference/chat)
* [Images](/developers/rest-api-reference/inference/images)
* [Videos](/developers/rest-api-reference/inference/videos)
* [Models](/developers/rest-api-reference/inference/models)
* [Files](/developers/rest-api-reference/files)
* [Batches](/developers/rest-api-reference/inference/batches)
* [Other](/developers/rest-api-reference/inference/other)
* [Legacy & Deprecated](/developers/rest-api-reference/inference/legacy)


===/developers/rest-api-reference/inference/videos===
#### Inference API

# Videos

***

## POST /v1/videos/generations

API endpoint for POST requests to /v1/videos/generations.

```
Method: POST
Path: /v1/videos/generations
```

***

## POST /v1/videos/edits

API endpoint for POST requests to /v1/videos/edits.

```
Method: POST
Path: /v1/videos/edits
```

***

## GET /v1/videos/\{request\_id}

API endpoint for GET requests to /v1/videos/\{request\_id}.

```
Method: GET
Path: /v1/videos/{request_id}
```


===/developers/rest-api-reference/management/audit===
#### Management API

# Audit Logs

***

## GET /audit/teams/\{teamId}/events

API endpoint for GET requests to /audit/teams/\{teamId}/events.

```
Method: GET
Path: /audit/teams/{teamId}/events
```


===/developers/rest-api-reference/management/auth===
#### Management API

# Accounts and Authorization

***

## POST /auth/teams/\{teamId}/api-keys

API endpoint for POST requests to /auth/teams/\{teamId}/api-keys.

```
Method: POST
Path: /auth/teams/{teamId}/api-keys
```

***

## GET /auth/teams/\{teamId}/api-keys

API endpoint for GET requests to /auth/teams/\{teamId}/api-keys.

```
Method: GET
Path: /auth/teams/{teamId}/api-keys
```

***

## PUT /auth/api-keys/\{api\_key\_id}

API endpoint for PUT requests to /auth/api-keys/\{api\_key\_id}.

```
Method: PUT
Path: /auth/api-keys/{api_key_id}
```

***

## DELETE /auth/api-keys/\{apiKeyId}

API endpoint for DELETE requests to /auth/api-keys/\{apiKeyId}.

```
Method: DELETE
Path: /auth/api-keys/{apiKeyId}
```

***

## GET /auth/api-keys/\{apiKeyId}/propagation

API endpoint for GET requests to /auth/api-keys/\{apiKeyId}/propagation.

```
Method: GET
Path: /auth/api-keys/{apiKeyId}/propagation
```

***

## GET /auth/teams/\{teamId}/models

API endpoint for GET requests to /auth/teams/\{teamId}/models.

```
Method: GET
Path: /auth/teams/{teamId}/models
```

***

## GET /auth/teams/\{teamId}/endpoints

API endpoint for GET requests to /auth/teams/\{teamId}/endpoints.

```
Method: GET
Path: /auth/teams/{teamId}/endpoints
```

***

## GET /auth/management-keys/validation

API endpoint for GET requests to /auth/management-keys/validation.

```
Method: GET
Path: /auth/management-keys/validation
```


===/developers/rest-api-reference/management/billing===
#### Management API

# Billing Management

***

## GET /v1/billing/teams/\{team\_id}/billing-info

API endpoint for GET requests to /v1/billing/teams/\{team\_id}/billing-info.

```
Method: GET
Path: /v1/billing/teams/{team_id}/billing-info
```

***

## POST /v1/billing/teams/\{team\_id}/billing-info

API endpoint for POST requests to /v1/billing/teams/\{team\_id}/billing-info.

```
Method: POST
Path: /v1/billing/teams/{team_id}/billing-info
```

***

## GET /v1/billing/teams/\{team\_id}/invoices

API endpoint for GET requests to /v1/billing/teams/\{team\_id}/invoices.

```
Method: GET
Path: /v1/billing/teams/{team_id}/invoices
```

***

## GET /v1/billing/teams/\{team\_id}/payment-method

API endpoint for GET requests to /v1/billing/teams/\{team\_id}/payment-method.

```
Method: GET
Path: /v1/billing/teams/{team_id}/payment-method
```

***

## POST /v1/billing/teams/\{team\_id}/payment-method/default

API endpoint for POST requests to /v1/billing/teams/\{team\_id}/payment-method/default.

```
Method: POST
Path: /v1/billing/teams/{team_id}/payment-method/default
```

***

## GET /v1/billing/teams/\{team\_id}/postpaid/invoice/preview

API endpoint for GET requests to /v1/billing/teams/\{team\_id}/postpaid/invoice/preview.

```
Method: GET
Path: /v1/billing/teams/{team_id}/postpaid/invoice/preview
```

***

## GET /v1/billing/teams/\{team\_id}/postpaid/spending-limits

API endpoint for GET requests to /v1/billing/teams/\{team\_id}/postpaid/spending-limits.

```
Method: GET
Path: /v1/billing/teams/{team_id}/postpaid/spending-limits
```

***

## POST /v1/billing/teams/\{team\_id}/postpaid/spending-limits

API endpoint for POST requests to /v1/billing/teams/\{team\_id}/postpaid/spending-limits.

```
Method: POST
Path: /v1/billing/teams/{team_id}/postpaid/spending-limits
```

***

## GET /v1/billing/teams/\{team\_id}/prepaid/balance

API endpoint for GET requests to /v1/billing/teams/\{team\_id}/prepaid/balance.

```
Method: GET
Path: /v1/billing/teams/{team_id}/prepaid/balance
```

***

## POST /v1/billing/teams/\{team\_id}/prepaid/top-up

API endpoint for POST requests to /v1/billing/teams/\{team\_id}/prepaid/top-up.

```
Method: POST
Path: /v1/billing/teams/{team_id}/prepaid/top-up
```

***

## POST /v1/billing/teams/\{team\_id}/usage

API endpoint for POST requests to /v1/billing/teams/\{team\_id}/usage.

```
Method: POST
Path: /v1/billing/teams/{team_id}/usage
```


===/developers/rest-api-reference/management===
#### Management API

# Management REST API Overview

The Management API allows you to perform operations on your team programmatically. You
need a [management key](https://console.x.ai/team/default/management-keys) in
order to use this API. The base URL for all endpoints is `https://management-api.x.ai`.

The Management API serves as a dedicated interface to the xAI platform, empowering developers and teams to
programmatically manage their xAI API teams.

For example, users can provision their API key, handle access controls,
and perform team-level operations like creating, listing, updating, or deleting keys and associated access control lists
(ACLs). This API also facilitates oversight of billing aspects, including monitoring prepaid credit balances and usage
deductions, ensuring seamless scalability and cost transparency for Grok model integrations.

To get started, go to [xAI Console](https://console.x.ai). On users page, make sure your xAI account has
`Management Keys` Read + Write permission, and obtain your Management API key on the settings page. If you don't see
any of these options, please ask your team administrator to enable the appropriate permissions.

* [Accounts and Authorization](/developers/rest-api-reference/management/auth)
* [Billing Management](/developers/rest-api-reference/management/billing)
* [Audit Logs](/developers/rest-api-reference/management/audit)


===/developers/tools/advanced-usage===
#### Tools

# Advanced Usage

In this section, we explore advanced usage patterns for agentic tool calling, including:

* **[Use Client-side Tools](#mixing-server-side-and-client-side-tools)** - Combine server-side agentic tools with your own client-side tools for specialized functionality that requires local execution.
* **[Multi-turn Conversations](#multi-turn-conversations-with-preservation-of-agentic-state)** - Maintain context across multiple turns in agentic tool-enabled conversations, allowing the model to build upon previous research and tool results for more complex, iterative problem-solving
* **[Requests with Multiple Active Tools](#tool-combinations)** - Send requests with multiple server-side tools active simultaneously, enabling comprehensive analysis with web search, X search, and code execution tools working together
* **[Image Integration](#using-images-in-the-context)** - Include images in your tool-enabled conversations for visual analysis and context-aware searches

&#x20;Advanced tool usage patterns are not yet supported in the Vercel AI SDK. Please use the xAI SDK or OpenAI SDK for this functionality.

## Mixing Server-Side and Client-Side Tools

You can combine server-side agentic tools (like web search and code execution) with custom client-side tools to create powerful hybrid workflows. This approach lets you leverage the model's reasoning capabilities with server-side tools while adding specialized functionality that runs locally in your application.

### How It Works

The key difference when mixing server-side and client-side tools is that **server-side tools are executed automatically by xAI**, while **client-side tools require developer intervention**:

1. Define your client-side tools using [standard function calling patterns](/developers/tools/function-calling)
2. Include both server-side and client-side tools in your request
3. **xAI automatically executes any server-side tools** the model decides to use (web search, code execution, etc.)
4. **When the model calls client-side tools, execution pauses** - xAI returns the tool calls to you instead of executing them
5. **Detect and execute client-side tool calls yourself**, then append the results back to continue the conversation
6. **Repeat this process** until the model generates a final response with no additional client-side tool calls

### Understanding `max_turns` with Client-Side Tools

When using [the `max_turns` parameter](/developers/tools/tool-usage-details#limiting-tool-call-turns) with mixed server-side and client-side tools, it's important to understand that **`max_turns` only limits the assistant/server-side tool call turns within a single request**.

When the model decides to invoke a client-side tool, the agent execution **pauses and yields control back to your application**. This means:

* The current request completes, and you receive the client-side tool call(s) to execute
* After you execute the client-side tool and append the result, you make a **new follow-up request**
* This follow-up request starts with a fresh `max_turns` count

In other words, client-side tool invocations act as "checkpoints" that reset the turn counter. If you set `max_turns=5` and the agent performs 3 server-side tool calls before requesting a client-side tool, the subsequent request (after you provide the client-side tool result) will again allow up to 5 server-side tool turns.

### Practical Example

Given a local client-side function `get_weather` to get the weather of a specified city, the model can use this client-side tool and the web-search tool to determine the weather in the base city of the 2025 NBA champion.

### Using the xAI SDK

You can determine whether a tool call is a client-side tool call by using `xai_sdk.tools.get_tool_call_type` against a tool call from the `response.tool_calls` list.
For more details, check [Identifying Tool Call Types](/developers/tools/tool-usage-details#identifying-tool-call-types).

1. Import the dependencies, and define the client-side tool.

   ```pythonXAI
   import os
   import json

   from xai_sdk import Client
   from xai_sdk.chat import user, tool, tool_result
   from xai_sdk.tools import web_search, get_tool_call_type

   client = Client(api_key=os.getenv("XAI_API_KEY"))

   # Define client-side tool
   def get_weather(city: str) -> str:
       """Get the weather for a given city."""
       # In a real app, this would query your database
       return f"The weather in {city} is sunny."

   # Tools array with both server-side and client-side tools
   tools = [
       web_search(),
       tool(
           name="get_weather",
           description="Get the weather for a given city.",
           parameters={
               "type": "object",
               "properties": {
                   "city": {
                       "type": "string",
                       "description": "The name of the city",
                   }
               },
               "required": ["city"]
           },
       ),
   ]

   model = "grok-4-1-fast-reasoning"
   ```

2. Perform the tool loop with conversation continuation:
   * You can either use `previous_response_id` to continue the conversation from the last response.

     ```pythonXAI
     # Create chat with both server-side and client-side tools
     chat = client.chat.create(
         model=model,
         tools=tools,
         store_messages=True,
     )
     chat.append(
         user(
             "What is the weather in the base city of the team that won the "
             "2025 NBA championship?"
         )
     )

     while True:
         client_side_tool_calls = []
         for response, chunk in chat.stream():
             for tool_call in chunk.tool_calls:
                 if get_tool_call_type(tool_call) == "client_side_tool":
                     client_side_tool_calls.append(tool_call)
                 else:
                     print(
                         f"Server-side tool call: {tool_call.function.name} "
                         f"with arguments: {tool_call.function.arguments}"
                     )

         if not client_side_tool_calls:
             break

         chat = client.chat.create(
             model=model,
             tools=tools,
             store_messages=True,
             previous_response_id=response.id,
         )

         for tool_call in client_side_tool_calls:
             print(
                 f"Client-side tool call: {tool_call.function.name} "
                 f"with arguments: {tool_call.function.arguments}"
             )
             args = json.loads(tool_call.function.arguments)
             result = get_weather(args["city"])
             chat.append(tool_result(result))

     print(f"Final response: {response.content}")
     ```

   * Alternatively, you can use the encrypted content to continue the conversation.

     ```pythonXAI
     # Create chat with both server-side and client-side tools
     chat = client.chat.create(
         model=model,
         tools=tools,
         use_encrypted_content=True,
     )
     chat.append(
         user(
             "What is the weather in the base city of the team that won the "
             "2025 NBA championship?"
         )
     )

     while True:
         client_side_tool_calls = []
         for response, chunk in chat.stream():
             for tool_call in chunk.tool_calls:
                 if get_tool_call_type(tool_call) == "client_side_tool":
                     client_side_tool_calls.append(tool_call)
                 else:
                     print(
                         f"Server-side tool call: {tool_call.function.name} "
                         f"with arguments: {tool_call.function.arguments}"
                     )

         chat.append(response)

         if not client_side_tool_calls:
             break

         for tool_call in client_side_tool_calls:
             print(
                 f"Client-side tool call: {tool_call.function.name} "
                 f"with arguments: {tool_call.function.arguments}"
             )
             args = json.loads(tool_call.function.arguments)
             result = get_weather(args["city"])
             chat.append(tool_result(result))

     print(f"Final response: {response.content}")
     ```

You will see an output similar to the following:

```
Server-side tool call: web_search with arguments: {"query":"Who won the 2025 NBA championship?","num_results":5}
Client-side tool call: get_weather with arguments: {"city":"Oklahoma City"}
Final response: The Oklahoma City Thunder won the 2025 NBA championship. The current weather in Oklahoma City is sunny.
```

### Using the OpenAI SDK

You can determine whether a tool call is a client-side tool call by checking the `type` field of an output entry from the `response.output` list.
For more details, see [Identifying Tool Call Types](/developers/tools/tool-usage-details#identifying-tool-call-types).

1. Import the dependencies, and define the client-side tool.

   ```pythonOpenAISDK
   import os
   import json

   from openai import OpenAI

   client = OpenAI(
       api_key=os.getenv("XAI_API_KEY"),
       base_url="https://api.x.ai/v1",
   )

   # Define client-side tool
   def get_weather(city: str) -> str:
       """Get the weather for a given city."""
       # In a real app, this would query your database
       return f"The weather in {city} is sunny."

   model = "grok-4-1-fast-reasoning"
   tools = [
       {
           "type": "function",
           "name": "get_weather",
           "description": "Get the weather for a given city.",
           "parameters": {
               "type": "object",
               "properties": {
                   "city": {
                       "type": "string",
                       "description": "The name of the city",
                   },
               },
               "required": ["city"],
           },
       },
       {
           "type": "web_search",
       },
   ]
   ```

2. Perform the tool loop:

   * You can either use `previous_response_id`.

     ```pythonOpenAISDK
     response = client.responses.create(
         model=model,
         input=(
             "What is the weather in the base city of the team that won the "
             "2025 NBA championship?"
         ),
         tools=tools,
     )

     while True:
         tool_outputs = []
         for item in response.output:
             if item.type == "function_call":
                 print(f"Client-side tool call: {item.name} with arguments: {item.arguments}")
                 args = json.loads(item.arguments)
                 weather = get_weather(args["city"])
                 tool_outputs.append(
                     {
                         "type": "function_call_output",
                         "call_id": item.call_id,
                         "output": weather,
                     }
                 )
             elif item.type in (
                 "web_search_call",
                 "x_search_call", 
                 "code_interpreter_call",
                 "file_search_call",
                 "mcp_call"
             ):
                 print(
                     f"Server-side tool call: {item.name} with arguments: {item.arguments}"
                 )

         if not tool_outputs:
             break

         response = client.responses.create(
             model=model,
             tools=tools,
             input=tool_outputs,
             previous_response_id=response.id,
         )

     print("Final response:", response.output[-1].content[0].text)
     ```

   * or using the encrypted content

     ```pythonOpenAISDK
     input_list = [
         {
             "role": "user",
             "content": (
                 "What is the weather in the base city of the team that won the "
                 "2025 NBA championship?"
             ),
         }
     ]

     response = client.responses.create(
         model=model,
         input=input_list,
         tools=tools,
         include=["reasoning.encrypted_content"],
     )

     while True:
         input_list.extend(response.output)
         tool_outputs = []
         for item in response.output:
             if item.type == "function_call":
                 print(f"Client-side tool call: {item.name} with arguments: {item.arguments}")
                 args = json.loads(item.arguments)
                 weather = get_weather(args["city"])
                 tool_outputs.append(
                     {
                         "type": "function_call_output",
                         "call_id": item.call_id,
                         "output": weather,
                     }
                 )
             elif item.type in (
                 "web_search_call",
                 "x_search_call", 
                 "code_interpreter_call",
                 "file_search_call",
                 "mcp_call"
             ):
                 print(
                     f"Server-side tool call: {item.name} with arguments: {item.arguments}"
                 )

         if not tool_outputs:
             break

         input_list.extend(tool_outputs)
         response = client.responses.create(
             model=model,
             input=input_list,
             tools=tools,
             include=["reasoning.encrypted_content"],
         )

     print("Final response:", response.output[-1].content[0].text)
     ```

## Multi-turn Conversations with Preservation of Agentic State

When using agentic tools, you may want to have multi-turn conversations where follow-up prompts maintain all agentic state, including the full history of reasoning, tool calls, and tool responses. This is possible using the stateful API, which provides seamless integration for preserving conversation context across multiple interactions. There are two options to achieve this outlined below.

### Store the Conversation History Remotely

You can choose to store the conversation history remotely on the xAI server, and every time you want to continue the conversation, you can pick up from the last response where you want to resume from.

There are only 2 extra steps:

1. Add the parameter `store_messages=True` when making the first agentic request. This tells the service to store the entire conversation history on xAI servers, including the model's reasoning, server-side tool calls, and corresponding responses.
2. Pass `previous_response_id=response.id` when creating the follow-up conversation, where `response` is the response returned by `chat.sample()` or `chat.stream()` from the conversation that you wish to continue.

Note that the follow-up conversation does not need to use the same tools, model parameters, or any other configuration as the initial conversation—it will still be fully hydrated with the complete agentic state from the previous interaction.

```pythonXAI
import os

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import web_search, x_search
client = Client(api_key=os.getenv("XAI_API_KEY"))
# First turn.
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",  # reasoning model
    tools=[web_search(), x_search()],
    store_messages=True,
)
chat.append(user("What is xAI?"))
print("\\n\\n##### First turn #####\\n")
for response, chunk in chat.stream():
    print(chunk.content, end="", flush=True)
print("\\n\\nUsage for first turn:", response.server_side_tool_usage)

# Second turn.
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",  # reasoning model
    tools=[web_search(), x_search()],
    # pass the response id of the first turn to continue the conversation
    previous_response_id=response.id,
)

chat.append(user("What is its latest mission?"))
print("\\n\\n##### Second turn #####\\n")
for response, chunk in chat.stream():
    print(chunk.content, end="", flush=True)
print("\\n\\nUsage for second turn:", response.server_side_tool_usage)
```

### Append the Encrypted Agentic Tool Calling States

There is another option for the ZDR (Zero Data Retention) users, or the users who don't want to use the above option, that is to let the xAI server also return
the encrypted reasoning and the encrypted tool output besides the final content to the client side, and those encrypted contents can be included as a part of the context
in the next turn conversation.

Here are the extra steps you need to take for this option:

1. Add the parameter `use_encrypted_content=True` when making the first agentic request. This tells the service to return the entire conversation history to the client side, including the model's reasoning (encrypted), server-side tool calls, and corresponding responses (encrypted).
2. Append the response to the conversation you wish to continue before making the call to `chat.sample()` or `chat.stream()`.

```pythonXAI
import os

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import web_search, x_search
client = Client(api_key=os.getenv("XAI_API_KEY"))
# First turn.
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",  # reasoning model
    tools=[web_search(), x_search()],
    use_encrypted_content=True,
)
chat.append(user("What is xAI?"))
print("\\n\\n##### First turn #####\\n")
for response, chunk in chat.stream():
    print(chunk.content, end="", flush=True)
print("\\n\\nUsage for first turn:", response.server_side_tool_usage)

chat.append(response)

print("\\n\\n##### Second turn #####\\n")
chat.append(user("What is its latest mission?"))
# Second turn.
for response, chunk in chat.stream():
    print(chunk.content, end="", flush=True)
print("\\n\\nUsage for second turn:", response.server_side_tool_usage)
```

For more details about stateful responses, please check out [this guide](/developers/model-capabilities/text/generate-text).

## Tool Combinations

Equipping your requests with multiple tools is straightforward—simply include the tools you want to activate in the `tools` array of your request. The model will intelligently orchestrate between them based on the task at hand.

### Suggested Tool Combinations

Here are some common patterns for combining tools, depending on your use case:

| If you're trying to... | Consider activating... | Because... |
|------------------------|----------------------|------------|
| **Research & analyze data** | Web Search + Code Execution | Web search gathers information, code execution analyzes and visualizes it |
| **Aggregate news & social media** | Web Search + X Search | Get comprehensive coverage from both traditional web and social platforms |
| **Extract insights from multiple sources** | Web Search + X Search + Code Execution | Collect data from various sources then compute correlations and trends |
| **Monitor real-time discussions** | X Search + Web Search | Track social sentiment alongside authoritative information |

```pythonXAI
from xai_sdk.tools import web_search, x_search, code_execution

# Example tool combinations for different scenarios
research_setup = [web_search(), code_execution()]
news_setup = [web_search(), x_search()]
comprehensive_setup = [web_search(), x_search(), code_execution()]
```

```pythonWithoutSDK
research_setup = {
  "tools": [
    {"type": "web_search"},
    {"type": "code_interpreter"}
  ]
}

news_setup = {
  "tools": [
    {"type": "web_search"},
    {"type": "x_search"}
  ]
}

comprehensive_setup = {
  "tools": [
    {"type": "web_search"},
    {"type": "x_search"},
    {"type": "code_interpreter"}
  ]
}
```

### Using Tool Combinations in Different Scenarios

1. When you want to search for news on the Internet, you can activate all search tools:
   * Web search tool
   * X search tool

```pythonXAI
import os

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import web_search, x_search

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",  # reasoning model
    tools=[
        web_search(),
        x_search(),
    ],
    include=["verbose_streaming"],
)

chat.append(user("what is the latest update from xAI?"))

is_thinking = True
for response, chunk in chat.stream():
    # View the server-side tool calls as they are being made in real-time
    for tool_call in chunk.tool_calls:
        print(f"\\nCalling tool: {tool_call.function.name} with arguments: {tool_call.function.arguments}")
    if response.usage.reasoning_tokens and is_thinking:
        print(f"\\rThinking... ({response.usage.reasoning_tokens} tokens)", end="", flush=True)
    if chunk.content and is_thinking:
        print("\\n\\nFinal Response:")
        is_thinking = False
    if chunk.content and not is_thinking:
        print(chunk.content, end="", flush=True)

print("\\n\\nCitations:")
print(response.citations)
print("\\n\\nUsage:")
print(response.usage)
print(response.server_side_tool_usage)
print("\\n\\nServer Side Tool Calls:")
print(response.tool_calls)
```

```pythonOpenAISDK
import os
from openai import OpenAI

api_key = os.getenv("XAI_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://api.x.ai/v1",
)

response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[
        {
            "role": "user",
            "content": "what is the latest update from xAI?",
        },
    ],
    tools=[
        {
            "type": "web_search",
        },
        {
            "type": "x_search",
        },
    ],
)

print(response)
```

```pythonRequests
import os
import requests

url = "https://api.x.ai/v1/responses"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}"
}
payload = {
    "model": "grok-4-1-fast-reasoning",
    "input": [
        {
            "role": "user",
            "content": "what is the latest update from xAI?"
        }
    ],
    "tools": [
        {
            "type": "web_search",
        },
        {
            "type": "x_search",
        }
    ]
}
response = requests.post(url, headers=headers, json=payload)
print(response.json())
```

```bash
curl https://api.x.ai/v1/responses \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer $XAI_API_KEY" \\
  -d '{
  "model": "grok-4-1-fast-reasoning",
  "input": [
    {
      "role": "user",
      "content": "What is the latest update from xAI?"
    }
  ],
  "tools": [
    {
      "type": "web_search"
    },
    {
      "type": "x_search"
    }
  ]
}'
```

2. When you want to collect up-to-date data from the Internet and perform calculations based on the Internet data, you can choose to activate:
   * Web search tool
   * Code execution tool

```pythonXAI
import os

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import web_search, code_execution

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",  # reasoning model
    # research_tools
    tools=[
        web_search(),
        code_execution(),
    ],
    include=["verbose_streaming"],
)

chat.append(user("What is the average market cap of the companies with the top 5 market cap in the US stock market today?"))

# sample or stream the response...
```

```pythonOpenAISDK
import os
from openai import OpenAI

api_key = os.getenv("XAI_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://api.x.ai/v1",
)

response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[
        {
            "role": "user",
            "content": "What is the average market cap of the companies with the top 5 market cap in the US stock market today?",
        },
    ],
    # research_tools
    tools=[
        {
            "type": "web_search",
        },
        {
            "type": "code_interpreter",
        },
    ],
)

print(response)
```

```pythonRequests
import os
import requests

url = "https://api.x.ai/v1/responses"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}"
}
payload = {
    "model": "grok-4-1-fast-reasoning",
    "input": [
        {
            "role": "user",
            "content": "What is the average market cap of the companies with the top 5 market cap in the US stock market today?"
        }
    ],
    # research_tools
    "tools": [
        {
            "type": "web_search",
        },
        {
            "type": "code_interpreter",
        },
    ]
}
response = requests.post(url, headers=headers, json=payload)
print(response.json())
```

```bash
curl https://api.x.ai/v1/responses \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer $XAI_API_KEY" \\
  -d '{
  "model": "grok-4-1-fast-reasoning",
  "input": [
    {
      "role": "user",
      "content": "What is the average market cap of the companies with the top 5 market cap in the US stock market today?"
    }
  ],
  "tools": [
    {
      "type": "web_search"
    },
    {
      "type": "code_interpreter"
    }
  ]
}'
```

## Using Images in the Context

You can bootstrap your requests with an initial conversation context that includes images.

In the code sample below, we pass an image into the context of the conversation before initiating an agentic request.

```pythonXAI
import os

from xai_sdk import Client
from xai_sdk.chat import image, user
from xai_sdk.tools import web_search, x_search

# Create the client and define the server-side tools to use
client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",  # reasoning model
    tools=[web_search(), x_search()],
    include=["verbose_streaming"],
)

# Add an image to the conversation
chat.append(
    user(
        "Search the internet and tell me what kind of dog is in the image below.",
        "And what is the typical lifespan of this dog breed?",
        image(
            "https://pbs.twimg.com/media/G3B7SweXsAAgv5N?format=jpg&name=900x900"
        ),
    )
)

is_thinking = True
for response, chunk in chat.stream():
    # View the server-side tool calls as they are being made in real-time
    for tool_call in chunk.tool_calls:
        print(f"\\nCalling tool: {tool_call.function.name} with arguments: {tool_call.function.arguments}")
    if response.usage.reasoning_tokens and is_thinking:
        print(f"\\rThinking... ({response.usage.reasoning_tokens} tokens)", end="", flush=True)
    if chunk.content and is_thinking:
        print("\\n\\nFinal Response:")
        is_thinking = False
    if chunk.content and not is_thinking:
        print(chunk.content, end="", flush=True)

print("\\n\\nCitations:")
print(response.citations)
print("\\n\\nUsage:")
print(response.usage)
print(response.server_side_tool_usage)
print("\\n\\nServer Side Tool Calls:")
print(response.tool_calls)
```


===/developers/tools/citations===
#### Tools

# Citations

The agent tools API provides two types of citation information: **All Citations** (a complete list of all sources encountered) and **Inline Citations** (markdown-style links embedded directly in the response text).

## All Citations

The `citations` attribute on the `response` object provides a comprehensive list of URLs for all sources the agent encountered during its search process. This list is **always returned by default** — no additional configuration is required.

Citations are automatically collected from successful tool executions and provide full traceability of the agent's information sources. They are returned when the agentic request completes.

Note that not every URL in this list will necessarily be directly referenced in the final answer. The agent may examine a source during its research process and determine it is not sufficiently relevant to the user's query, but the URL will still appear in this list for transparency.

```pythonWithoutSDK
response.citations
```

```output
[
'https://x.com/i/user/1912644073896206336',
'https://x.com/i/status/1975607901571199086',
'https://x.ai/news',
'https://docs.x.ai/developers/release-notes',
...
]
```

## Inline Citations

Inline citations are **markdown-style links** (e.g., `[[1]](https://x.ai/news)`) inserted directly into the response text at the points where the model references sources. In addition to these visible links, **structured metadata** is available on the response object with precise positional information.

**Important**: Enabling inline citations does not guarantee that the model will cite sources on every answer. The model decides when and where to include citations based on the context and nature of the query.

### Enabling Inline Citations

Inline citations are returned by default with the Responses API. For the xAI SDK, you can explicitly request them with `include=["inline_citations"]`:

```bash customLanguage="bash"
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
  "model": "grok-4-1-fast-reasoning",
  "input": [
    {"role": "user", "content": "What is xAI?"}
  ],
  "tools": [{"type": "web_search"}]
}'
```

```python customLanguage="pythonXAI"
import os

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import web_search, x_search

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    tools=[
        web_search(),
        x_search(),
    ],
    include=["inline_citations"],  # Enable inline citations
)

chat.append(user("What is xAI?"))
response = chat.sample()

# Access the response text (includes inline citation markdown)
print(response.content)
```

```python customLanguage="pythonOpenAISDK"
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[
        {"role": "user", "content": "What is xAI?"}
    ],
    tools=[
        {"type": "web_search"},
    ],
)

# Get the message output with inline citations
for item in response.output:
    if item.type == "message":
        for content in item.content:
            if content.type == "output_text":
                print(content.text)
```

```javascript customLanguage="javascriptAISDK"
import { xai } from '@ai-sdk/xai';
import { generateText } from 'ai';

const { text, sources } = await generateText({
  model: xai.responses('grok-4-1-fast-reasoning'),
  prompt: 'What is xAI?',
  tools: {
    web_search: xai.tools.webSearch(),
  },
});

// Text includes inline citation markdown
console.log(text);

// Sources contain all citation URLs
console.log('Sources:', sources);
```

```javascript customLanguage="javascriptOpenAISDK"
import OpenAI from 'openai';

const client = new OpenAI({
  apiKey: process.env.XAI_API_KEY,
  baseURL: 'https://api.x.ai/v1',
});

const response = await client.responses.create({
  model: 'grok-4-1-fast-reasoning',
  input: [
    { role: 'user', content: 'What is xAI?' }
  ],
  tools: [{ type: 'web_search' }],
});

// Get the message with inline citations
for (const item of response.output) {
  if (item.type === 'message') {
    for (const content of item.content) {
      if (content.type === 'output_text') {
        console.log(content.text);
      }
    }
  }
}
```

### Markdown Citation Format

When inline citations are enabled, the model will insert markdown-style citation links directly into the response text:

```output
The latest announcements from xAI, primarily from their official X account (@xai) and website (x.ai/news), date back to November 19, 2025.[[1]](https://x.ai/news/)[[2]](https://x.ai/)[[3]](https://x.com/i/status/1991284813727474073)
```

When rendered as markdown, this displays as clickable links:

> The latest announcements from xAI, primarily from their official X account (@xai) and website (x.ai/news), date back to November 19, 2025.[\[1\]](https://x.ai/news/)[\[2\]](https://x.ai/)[\[3\]](https://x.com/i/status/1991284813727474073)

The format is `[[N]](url)` where:

* `N` is the sequential display number for the citation **starting from 1**
* `url` is the source URL

**Citation numbering**: Citation numbers always start from 1 and increment sequentially. If the same source is cited again later in the response, the original citation number will be reused.

## Accessing Structured Inline Citation Data

Structured inline citation data provides precise positional information about each citation in the response text.

### Response Format

Each citation annotation contains:

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"url_citation"` |
| `url` | string | The source URL |
| `start_index` | int | Character position where the citation starts in the response text |
| `end_index` | int | Character position where the citation ends (exclusive) |
| `title` | string | The citation number (e.g., "1", "2") |

```python customLanguage="pythonXAI"
# After streaming or sampling completes, access the structured inline citations:
for citation in response.inline_citations:
    print(f"Citation [{citation.id}]:")
    print(f"  Position: {citation.start_index} to {citation.end_index}")
    
    # Check citation type
    if citation.HasField("web_citation"):
        print(f"  Web URL: {citation.web_citation.url}")
    elif citation.HasField("x_citation"):
        print(f"  X URL: {citation.x_citation.url}")
```

```python customLanguage="pythonOpenAISDK"
# Access annotations from the response
for item in response.output:
    if item.type == "message":
        for content in item.content:
            if content.type == "output_text":
                for annotation in content.annotations:
                    print(f"Citation [{annotation.title}]:")
                    print(f"  URL: {annotation.url}")
                    print(f"  Position: {annotation.start_index} to {annotation.end_index}")
```

```javascript customLanguage="javascriptAISDK"
import { xai } from '@ai-sdk/xai';
import { streamText } from 'ai';

const { fullStream } = streamText({
  model: xai.responses('grok-4-1-fast-reasoning'),
  prompt: 'What is xAI?',
  tools: {
    web_search: xai.tools.webSearch(),
  },
});

// Access sources as they stream in
for await (const part of fullStream) {
  if (part.type === 'source' && part.sourceType === 'url') {
    console.log(`Citation: ${part.url}`);
  }
}
```

```javascript customLanguage="javascriptOpenAISDK"
// Access annotations from the response
for (const item of response.output) {
  if (item.type === 'message') {
    for (const content of item.content) {
      if (content.type === 'output_text') {
        for (const annotation of content.annotations) {
          console.log(`Citation [${annotation.title}]:`);
          console.log(`  URL: ${annotation.url}`);
          console.log(`  Position: ${annotation.start_index} to ${annotation.end_index}`);
        }
      }
    }
  }
}
```

```output
Citation [1]:
  Position: 37 to 76
  Web URL: https://x.ai/news/grok-4-fast
Citation [2]:
  Position: 124 to 171
  X URL: https://x.com/xai/status/1234567890
```

### Using Position Indices

The `start_index` and `end_index` values follow Python slice convention:

* **`start_index`**: Character position of the first `[` of the citation
* **`end_index`**: Character position immediately *after* the closing `)` (exclusive)

Extract the exact citation markdown from the response text using a simple slice:

```python customLanguage="pythonXAI"
content = response.content

for citation in response.inline_citations:
    # Extract the markdown link from the response text
    citation_text = content[citation.start_index:citation.end_index]
    print(f"Citation text: {citation_text}")
```

## Streaming Inline Citations

During streaming, inline citations are accumulated and available on the final response. The markdown links appear in real-time in the `chunk.content` as the model generates text:

```python customLanguage="pythonXAI"
for response, chunk in chat.stream():
    # Markdown links appear in chunk.content in real-time
    if chunk.content:
        print(chunk.content, end="", flush=True)
    
    # Inline citations can also be accessed per-chunk during streaming
    for citation in chunk.inline_citations:
        print(f"\nNew citation: [{citation.id}]")

# After streaming, access all accumulated inline citations
print("\n\nAll inline citations:")
for citation in response.inline_citations:
    url = ""
    if citation.HasField("web_citation"):
        url = citation.web_citation.url
    elif citation.HasField("x_citation"):
        url = citation.x_citation.url
    print(f"  [{citation.id}] {url}")
```


===/developers/tools/code-execution===
#### Tools

# Code Execution Tool

The code execution tool enables Grok to write and execute Python code in real-time, dramatically expanding its capabilities beyond text generation. This powerful feature allows Grok to perform precise calculations, complex data analysis, statistical computations, and solve mathematical problems that would be impossible through text alone.

## Key Capabilities

* **Mathematical Computations**: Solve complex equations, perform statistical analysis, and handle numerical calculations with precision
* **Data Analysis**: Process datasets, and extract insights from the prompt
* **Financial Modeling**: Build financial models, calculate risk metrics, and perform quantitative analysis
* **Scientific Computing**: Handle scientific calculations, simulations, and data transformations
* **Code Generation & Testing**: Write, test, and debug Python code snippets in real-time

## When to Use Code Execution

The code execution tool is particularly valuable for:

* **Numerical Problems**: When you need exact calculations rather than approximations
* **Data Processing**: Analyzing complex data from the prompt
* **Complex Logic**: Multi-step calculations that require intermediate results
* **Verification**: Double-checking mathematical results or validating assumptions

## SDK Support

The code execution tool is available across multiple SDKs and APIs with different naming conventions:

| SDK/API | Tool Name | Description |
|---------|-----------|-------------|
| xAI SDK | `code_execution` | Native xAI SDK implementation |
| OpenAI Responses API | `code_interpreter` | Compatible with OpenAI's API format |
| Vercel AI SDK | `xai.tools.codeExecution()` | Vercel AI SDK integration |

This tool is also supported in all Responses API compatible SDKs.

## Implementation Example

Below are comprehensive examples showing how to integrate the code execution tool across different platforms and use cases.

### Basic Calculations

```pythonXAI
import os

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import code_execution

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",  # reasoning model
    tools=[code_execution()],
    include=["verbose_streaming"],
)

# Ask for a mathematical calculation
chat.append(user("Calculate the compound interest for $10,000 at 5% annually for 10 years"))

is_thinking = True
for response, chunk in chat.stream():
    # View the server-side tool calls as they are being made in real-time
    for tool_call in chunk.tool_calls:
        print(f"\\nCalling tool: {tool_call.function.name} with arguments: {tool_call.function.arguments}")
    if response.usage.reasoning_tokens and is_thinking:
        print(f"\\rThinking... ({response.usage.reasoning_tokens} tokens)", end="", flush=True)
    if chunk.content and is_thinking:
        print("\\n\\nFinal Response:")
        is_thinking = False
    if chunk.content and not is_thinking:
        print(chunk.content, end="", flush=True)

print("\\n\\nCitations:")
print(response.citations)
print("\\n\\nUsage:")
print(response.usage)
print(response.server_side_tool_usage)
print("\\n\\nServer Side Tool Calls:")
print(response.tool_calls)
```

```pythonOpenAISDK
import os
from openai import OpenAI

api_key = os.getenv("XAI_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://api.x.ai/v1",
)

response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[
        {
            "role": "user",
            "content": "Calculate the compound interest for $10,000 at 5% annually for 10 years",
        },
    ],
    tools=[
        {
            "type": "code_interpreter",
        },
    ],
)

print(response)
```

```pythonRequests
import os
import requests

url = "https://api.x.ai/v1/responses"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}"
}
payload = {
    "model": "grok-4-1-fast-reasoning",
    "input": [
        {
            "role": "user",
            "content": "Calculate the compound interest for $10,000 at 5% annually for 10 years"
        }
    ],
    "tools": [
        {
            "type": "code_interpreter",
        }
    ]
}
response = requests.post(url, headers=headers, json=payload)
print(response.json())
```

```bash
curl https://api.x.ai/v1/responses \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer $XAI_API_KEY" \\
  -d '{
  "model": "grok-4-1-fast-reasoning",
  "input": [
    {
      "role": "user",
      "content": "Calculate the compound interest for $10,000 at 5% annually for 10 years"
    }
  ],
  "tools": [
    {
      "type": "code_interpreter"
    }
  ]
}'
```

```javascriptAISDK
import { xai } from '@ai-sdk/xai';
import { generateText } from 'ai';

const { text } = await generateText({
  model: xai.responses('grok-4-1-fast-reasoning'),
  prompt: 'Calculate the compound interest for $10,000 at 5% annually for 10 years',
  tools: {
    code_execution: xai.tools.codeExecution(),
  },
});

console.log(text);
```

### Data Analysis

```pythonXAI
import os
from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import code_execution

client = Client(api_key=os.getenv("XAI_API_KEY"))

# Multi-turn conversation with data analysis
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",  # reasoning model
    tools=[code_execution()],
    include=["verbose_streaming"],
)

# Step 1: Load and analyze data
chat.append(user("""
I have sales data for Q1-Q4: [120000, 135000, 98000, 156000].
Please analyze this data and create a visualization showing:
1. Quarterly trends
2. Growth rates
3. Statistical summary
"""))

print("##### Step 1: Data Analysis #####\\n")

is_thinking = True
for response, chunk in chat.stream():
    # View the server-side tool calls as they are being made in real-time
    for tool_call in chunk.tool_calls:
        print(f"\\nCalling tool: {tool_call.function.name} with arguments: {tool_call.function.arguments}")
    if response.usage.reasoning_tokens and is_thinking:
        print(f"\\rThinking... ({response.usage.reasoning_tokens} tokens)", end="", flush=True)
    if chunk.content and is_thinking:
        print("\\n\\nAnalysis Results:")
        is_thinking = False
    if chunk.content and not is_thinking:
        print(chunk.content, end="", flush=True)

print("\\n\\nCitations:")
print(response.citations)
print("\\n\\nUsage:")
print(response.usage)
print(response.server_side_tool_usage)

chat.append(response)

# Step 2: Follow-up analysis
chat.append(user("Now predict Q1 next year using linear regression"))

print("\\n\\n##### Step 2: Prediction Analysis #####\\n")

is_thinking = True
for response, chunk in chat.stream():
    # View the server-side tool calls as they are being made in real-time
    for tool_call in chunk.tool_calls:
        print(f"\\nCalling tool: {tool_call.function.name} with arguments: {tool_call.function.arguments}")
    if response.usage.reasoning_tokens and is_thinking:
        print(f"\\rThinking... ({response.usage.reasoning_tokens} tokens)", end="", flush=True)
    if chunk.content and is_thinking:
        print("\\n\\nPrediction Results:")
        is_thinking = False
    if chunk.content and not is_thinking:
        print(chunk.content, end="", flush=True)

print("\\n\\nCitations:")
print(response.citations)
print("\\n\\nUsage:")
print(response.usage)
print(response.server_side_tool_usage)
print("\\n\\nServer Side Tool Calls:")
print(response.tool_calls)
```

```javascriptAISDK
import { xai } from '@ai-sdk/xai';
import { generateText } from 'ai';

// Step 1: Load and analyze data
const step1 = await generateText({
  model: xai.responses('grok-4-1-fast-reasoning'),
  prompt: \`I have sales data for Q1-Q4: [120000, 135000, 98000, 156000].
Please analyze this data and create a visualization showing:
1. Quarterly trends
2. Growth rates
3. Statistical summary\`,
  tools: {
    code_execution: xai.tools.codeExecution(),
  },
});

console.log('##### Step 1: Data Analysis #####');
console.log(step1.text);

// Step 2: Follow-up analysis using previousResponseId
const step2 = await generateText({
  model: xai.responses('grok-4-1-fast-reasoning'),
  prompt: 'Now predict Q1 next year using linear regression',
  tools: {
    code_execution: xai.tools.codeExecution(),
  },
  providerOptions: {
    xai: {
      previousResponseId: step1.response.id,
    },
  },
});

console.log('##### Step 2: Prediction Analysis #####');
console.log(step2.text);
```

## Best Practices

### 1. **Be Specific in Requests**

Provide clear, detailed instructions about what you want the code to accomplish:

```pythonWithoutSDK
# Good: Specific and clear
"Calculate the correlation matrix for these variables and highlight correlations above 0.7"

# Avoid: Vague requests  
"Analyze this data"
```

### 2. **Provide Context and Data Format**

Always specify the data format and any constraints on the data, and provide as much context as possible:

```pythonWithoutSDK
# Good: Includes data format and requirements
"""
Here's my CSV data with columns: date, revenue, costs
Please calculate monthly profit margins and identify the best-performing month.
Data: [['2024-01', 50000, 35000], ['2024-02', 55000, 38000], ...]
"""
```

### 3. **Use Appropriate Model Settings**

* **Temperature**: Use lower values (0.0-0.3) for mathematical calculations
* **Model**: Use reasoning models like `grok-4-1-fast-reasoning` for better code generation

## Common Use Cases

### Financial Analysis

```pythonWithoutSDK
# Portfolio optimization, risk calculations, option pricing
"Calculate the Sharpe ratio for a portfolio with returns [0.12, 0.08, -0.03, 0.15] and risk-free rate 0.02"
```

### Statistical Analysis

```pythonWithoutSDK
# Hypothesis testing, regression analysis, probability distributions
"Perform a t-test to compare these two groups and interpret the p-value: Group A: [23, 25, 28, 30], Group B: [20, 22, 24, 26]"
```

### Scientific Computing

```pythonWithoutSDK
# Simulations, numerical methods, equation solving
"Solve this differential equation using numerical methods: dy/dx = x^2 + y, with initial condition y(0) = 1"
```

## Limitations and Considerations

* **Execution Environment**: Code runs in a sandboxed Python environment with common libraries pre-installed
* **Time Limits**: Complex computations may have execution time constraints
* **Memory Usage**: Large datasets might hit memory limitations
* **Package Availability**: Most popular Python packages (NumPy, Pandas, Matplotlib, SciPy) are available
* **File I/O**: Limited file system access for security reasons

## Security Notes

* Code execution happens in a secure, isolated environment
* No access to external networks or file systems
* Temporary execution context that doesn't persist between requests
* All computations are stateless and secure


===/developers/tools/collections-search===
#### Tools

# Collections Search Tool

The collections search tool enables Grok to search through your uploaded knowledge bases (collections), allowing it to retrieve relevant information from your documents to provide more accurate and contextually relevant responses. This tool is particularly powerful for analyzing complex documents like financial reports, legal contracts, or technical documentation, where Grok can autonomously search through multiple documents and synthesize information to answer sophisticated analytical questions.

For an introduction to Collections, please check out the [Collections documentation](/developers/files/collections).

## Key Capabilities

* **Document Retrieval**: Search across uploaded files and collections to find relevant information
* **Semantic Search**: Find documents based on meaning and context, not just keywords
* **Knowledge Base Integration**: Seamlessly integrate your proprietary data with Grok's reasoning
* **RAG Applications**: Power retrieval-augmented generation workflows
* **Multi-format Support**: Search across PDFs, text files, CSVs, and other supported formats

## When to Use Collections Search

The collections search tool is particularly valuable for:

* **Enterprise Knowledge Bases**: When you need Grok to reference internal documents and policies
* **Financial Analysis**: Analyzing SEC filings, earnings reports, and financial statements across multiple documents
* **Customer Support**: Building chatbots that can answer questions based on your product documentation
* **Research & Due Diligence**: Synthesizing information from academic papers, technical reports, or industry analyses
* **Compliance & Legal**: Ensuring responses are grounded in your official guidelines and regulations
* **Personal Knowledge Management**: Organizing and querying your personal document collections

## SDK Support

The collections search tool is available across multiple SDKs and APIs with different naming conventions:

| SDK/API | Tool Name | Description |
|---------|-----------|-------------|
| xAI SDK | `collections_search` | Native xAI SDK implementation |
| OpenAI Responses API | `file_search` | Compatible with OpenAI's API format |

This tool is also supported in all Responses API compatible SDKs.

## Implementation Example

### End-to-End Financial Analysis Example

This comprehensive example demonstrates analyzing Tesla's SEC filings using the collections search tool. It covers:

1. Creating a collection for document storage
2. Uploading multiple financial documents concurrently (10-Q and 10-K filings)
3. Using Grok with collections search to analyze and synthesize information across documents in an agentic manner
4. Enabling code execution to allow the model to perform calculations and mathematical analysis effectively should it be needed.
5. Receiving cited responses and tool usage information

This pattern is applicable to any document analysis workflow where you need to search through and reason over multiple documents.

```pythonXAI
import asyncio
import os

import httpx

from xai_sdk import AsyncClient
from xai_sdk.chat import user
from xai_sdk.proto import collections_pb2
from xai_sdk.tools import code_execution, collections_search

TESLA_10_Q_PDF_URL = "https://ir.tesla.com/_flysystem/s3/sec/000162828025045968/tsla-20250930-gen.pdf"
TESLA_10_K_PDF_URL = "https://ir.tesla.com/_flysystem/s3/sec/000162828025003063/tsla-20241231-gen.pdf"


async def main():
    client = AsyncClient(api_key=os.getenv("XAI_API_KEY"), management_api_key=os.getenv("XAI_MANAGEMENT_API_KEY"))

    # Step 1: Create a collection for Tesla SEC filings
    response = await client.collections.create("tesla-sec-filings")
    print(f"Created collection: {response.collection_id}")

    # Step 2: Upload documents to the collection concurrently
    async def upload_document(
        url: str, name: str, collection_id: str, http_client: httpx.AsyncClient
    ) -> None:
        pdf_response = await http_client.get(url, timeout=30.0)
        pdf_content = pdf_response.content

        print(f"Uploading {name} document to collection")
        response = await client.collections.upload_document(
            collection_id=collection_id,
            name=name,
            data=pdf_content,
        )

        # Poll until document is processed and ready for search
        response = await client.collections.get_document(response.file_metadata.file_id, collection_id)
        print(f"Waiting for document {name} to be processed")
        while response.status != collections_pb2.DOCUMENT_STATUS_PROCESSED:
            await asyncio.sleep(3)
            response = await client.collections.get_document(response.file_metadata.file_id, collection_id)

        print(f"Document {name} processed")

    # Upload both documents concurrently
    async with httpx.AsyncClient() as http_client:
        await asyncio.gather(
            upload_document(TESLA_10_Q_PDF_URL, "tesla-10-Q-2024.pdf", response.collection_id, http_client),
            upload_document(TESLA_10_K_PDF_URL, "tesla-10-K-2024.pdf", response.collection_id, http_client),
        )

    # Step 3: Create a chat with collections search enabled
    chat = client.chat.create(
        model="grok-4-1-fast-reasoning",  # Use a reasoning model for better analysis
        tools=[
            collections_search(
                collection_ids=[response.collection_id],
            ),
            code_execution(),
        ],
        include=["verbose_streaming"],
    )

    # Step 4: Ask a complex analytical question that requires searching multiple documents
    chat.append(
        user(
            "How many consumer vehicles did Tesla produce in total in 2024 and 2025? "
            "Show your working and cite your sources."
        )
    )

    # Step 5: Stream the response and display reasoning progress
    is_thinking = True
    async for response, chunk in chat.stream():
        # View server-side tool calls as they happen
        for tool_call in chunk.tool_calls:
            print(f"\\nCalling tool: {tool_call.function.name} with arguments: {tool_call.function.arguments}")
        if response.usage.reasoning_tokens and is_thinking:
            print(f"\\rThinking... ({response.usage.reasoning_tokens} tokens)", end="", flush=True)
        if chunk.content and is_thinking:
            print("\\n\\nFinal Response:")
            is_thinking = False
        if chunk.content and not is_thinking:
            print(chunk.content, end="", flush=True)
        latest_response = response

    # Step 6: Review citations and tool usage
    print("\\n\\nCitations:")
    print(latest_response.citations)
    print("\\n\\nUsage:")
    print(latest_response.usage)
    print(latest_response.server_side_tool_usage)
    print("\\n\\nTool Calls:")
    print(latest_response.tool_calls)


if __name__ == "__main__":
    asyncio.run(main())
```

```pythonOpenAISDK
import os
from openai import OpenAI

# Using OpenAI SDK with xAI API (requires pre-created collection)
api_key = os.getenv("XAI_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://api.x.ai/v1",
)

# Note: You must create the collection and upload documents first using either the xAI console (console.x.ai) or the xAI SDK
# The collection_id below should be replaced with your actual collection ID
response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[
        {
            "role": "user",
            "content": "How many consumer vehicles did Tesla produce in total in 2024 and 2025? Show your working and cite your sources.",
        },
    ],
    tools=[
        {
            "type": "file_search",
            "vector_store_ids": ["your_collection_id_here"],  # Replace with actual collection ID
            "max_num_results": 10
        },
        {"type": "code_interpreter"},  # Enable code execution for calculations
    ],
)

print(response)
```

```javascriptAISDK
import { createOpenAI } from '@ai-sdk/openai';
import { streamText } from 'ai';

const openai = createOpenAI({
  baseURL: 'https://api.x.ai/v1',
  apiKey: process.env.XAI_API_KEY,
});

const result = streamText({
  model: openai('grok-4-1-fast-reasoning'),
  prompt: 'What documents do you have access to?',
  tools: {
    file_search: openai.tools.fileSearch({
      vectorStoreIds: ['your-vector-store-id'],
      maxNumResults: 5,
    }),
  },
});
```

```pythonRequests
import os
import requests

# Using raw requests (requires pre-created collection)
url = "https://api.x.ai/v1/responses"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}"
}
payload = {
    "model": "grok-4-1-fast-reasoning",
    "input": [
        {
            "role": "user",
            "content": "How many consumer vehicles did Tesla produce in total in 2024 and 2025? Show your working and cite your sources."
        }
    ],
    "tools": [
        {
            "type": "file_search",
            "vector_store_ids": ["your_collection_id_here"],  # Replace with actual collection ID
            "max_num_results": 10,
        },
        {"type": "code_interpreter"}  # Enable code execution for calculations
    ]
}
response = requests.post(url, headers=headers, json=payload)
print(response.json())
```

```bash
# Using curl (requires pre-created collection)
curl https://api.x.ai/v1/responses \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer $XAI_API_KEY" \\
  -d '{
  "model": "grok-4-1-fast-reasoning",
  "input": [
    {
      "role": "user",
      "content": "How many consumer vehicles did Tesla produce in total in 2024 and 2025? Show your working and cite your sources."
    }
  ],
  "tools": [
    {
      "type": "file_search",
      "vector_store_ids": ["your_collection_id_here"],
      "max_num_results": 10
    },
    {
      "type": "code_interpreter"
    }
  ]
}'
```

## Example Output

When you run the Python xAI SDK example above, you'll see output like this showing the complete workflow from collection creation to the final analyzed response:

```output
Created collection: collection_3be0eec8-ee8e-4a18-a9d4-fb70a3150d64
Uploading tesla-10-K-2024.pdf document to collection
Uploading tesla-10-Q-2024.pdf document to collection
Waiting for document tesla-10-K-2024.pdf to be processed
Waiting for document tesla-10-Q-2024.pdf to be processed
Document tesla-10-Q-2024.pdf processed
Document tesla-10-K-2024.pdf processed

Thinking... (199 tokens)
Calling tool: collections_search with arguments: {"query":"Tesla total vehicle production 2024","limit":10}
Thinking... (370 tokens)
Calling tool: collections_search with arguments: {"query":"Tesla total vehicles produced 2024","limit":5}
Thinking... (370 tokens)
Calling tool: collections_search with arguments: {"query":"Tesla vehicles produced 2025 Q1 Q2 Q3","limit":5}
Thinking... (477 tokens)
Calling tool: collections_search with arguments: {"query":"Tesla production and deliveries 2024 all quarters","limit":10}
Thinking... (477 tokens)
Calling tool: collections_search with arguments: {"query":"Tesla production and deliveries 2025 Q1 Q2 Q3","limit":10}
Thinking... (569 tokens)
Calling tool: collections_search with arguments: {"query":"Tesla total production 2024 full year consumer vehicles","limit":5}
Thinking... (776 tokens)
Calling tool: collections_search with arguments: {"query":"Tesla annual vehicle production 2024 total","limit":5}
Thinking... (1148 tokens)
Calling tool: collections_search with arguments: {"query":"Tesla Q4 2024 production and deliveries","limit":5}
Thinking... (1240 tokens)
Calling tool: collections_search with arguments: {"query":"Tesla Q1 2024 vehicle production","limit":3}
Thinking... (1240 tokens)
Calling tool: collections_search with arguments: {"query":"Tesla Q2 2024 vehicle production","limit":3}
Thinking... (1240 tokens)
Calling tool: collections_search with arguments: {"query":"Tesla Q3 2024 vehicle production","limit":3}
Thinking... (1240 tokens)
Calling tool: collections_search with arguments: {"query":"Tesla Q4 2024 vehicle production","limit":3}
Thinking... (2804 tokens)
Calling tool: collections_search with arguments: {"query":"Tesla vehicle production nine months 2024","limit":5}
Thinking... (3352 tokens)

Final Response:
### Working

To answer this question, I used the collections_search tool to query Tesla's official 
financial filings (10-K and 10-Q reports) for production numbers. Tesla reports vehicle 
production and deliveries quarterly, and consumer vehicles refer to passenger vehicles 
like Model 3, Model Y, Model S, Model X, and Cybertruck (excluding Tesla Semi or other 
non-consumer products).

#### Step 1: 2024 Production
Based on Tesla's official quarterly production and delivery reports (aggregated from SEC 
filings and press releases referenced in the collections), Tesla produced **1,773,443 
consumer vehicles in 2024**.
  - Q1 2024: 433,371 produced
  - Q2 2024: 410,831 produced
  - Q3 2024: 469,796 produced
  - Q4 2024: 459,445 produced

#### Step 2: 2025 Production
The Q3 2025 10-Q filing explicitly states: "In 2025, we produced approximately 1,220,000 
consumer vehicles [...] through the third quarter."
  - This is the sum of Q1, Q2, and Q3 2025 production
  - Q4 2025 data is not available as of November 13, 2025

#### Step 3: Total for 2024 and 2025
- 2024 full year: 1,773,443
- 2025 (through Q3): 1,220,000
- **Total: 2,993,443 consumer vehicles**

Citations:
['collections://collection_3be0eec8-ee8e-4a18-a9d4-fb70a3150d64/files/file_d4d1a968-9037-4caa-8eca-47a1563f28ab', 
 'collections://collection_3be0eec8-ee8e-4a18-a9d4-fb70a3150d64/files/file_ff41a42e-6cdc-4ca1-918a-160644d52704']

Usage:
completion_tokens: 1306
prompt_tokens: 383265
total_tokens: 387923
prompt_text_tokens: 383265
reasoning_tokens: 3352
cached_prompt_text_tokens: 177518

{'SERVER_SIDE_TOOL_COLLECTIONS_SEARCH': 13}


Tool Calls:
... (omitted for brevity)
```

### Understanding Collections Citations

When using the collections search tool, citations follow a special URI format that uniquely identifies the source documents:

```
collections://collection_id/files/file_id
```

For example:

```
collections://collection_3be0eec8-ee8e-4a18-a9d4-fb70a3150d64/files/file_d4d1a968-9037-4caa-8eca-47a1563f28ab
```

**Format Breakdown:**

* **`collections://`**: Protocol identifier indicating this is a collection-based citation
* **`collection_id`**: The unique identifier of the collection that was searched (e.g., `collection_3be0eec8-ee8e-4a18-a9d4-fb70a3150d64`)
* **`files/`**: Path segment indicating file-level reference
* **`file_id`**: The unique identifier of the specific document file that was referenced (e.g., `file_d4d1a968-9037-4caa-8eca-47a1563f28ab`)

These citations represent all the documents from your collections that Grok referenced during its search and analysis. Each citation points to a specific file within a collection, allowing you to trace back exactly which uploaded documents contributed to the final response.

### Key Observations

1. **Autonomous Search Strategy**: Grok autonomously performs 13 different searches across the documents, progressively refining queries to find specific quarterly and annual production data.

2. **Reasoning Process**: The output shows reasoning tokens accumulating (199 → 3,352 tokens), demonstrating how the model thinks through the problem before generating the final response.

3. **Cited Sources**: All information is grounded in the uploaded documents with specific file citations, ensuring transparency and verifiability.

4. **Structured Analysis**: The final response breaks down the methodology, shows calculations, and clearly states assumptions and limitations (e.g., Q4 2025 data not yet available).

5. **Token Efficiency**: Notice the high number of cached prompt tokens (177,518) - this demonstrates how the collections search tool efficiently reuses context across multiple queries.

## Combining Collections Search with Web Search/X-Search

One of the most powerful patterns is combining the collections search tool with web search/x-search to answer questions that require both your internal knowledge base and real-time external information. This enables sophisticated analysis that grounds responses in your proprietary data while incorporating current market intelligence, news, and public sentiment.

### Example: Internal Data + Market Intelligence

Building on the Tesla example above, let's analyze how market analysts view Tesla's performance based on the production numbers from our internal documents:

```pythonXAI
import asyncio

import httpx

from xai_sdk import AsyncClient
from xai_sdk.chat import user
from xai_sdk.proto import collections_pb2
from xai_sdk.tools import code_execution, collections_search, web_search, x_search

# ... (collection creation and document upload same as before)

async def hybrid_analysis(client: AsyncClient, collection_id: str, model: str) -> None:
    # Enable collections search, web search, and code execution
    chat = client.chat.create(
        model=model,
        tools=[
            collections_search(
                collection_ids=[collection_id],
            ),
            web_search(),  # Enable web search for external data
            x_search(),  # Enable x-search for external data
            code_execution(),  # Enable code execution for calculations
        ],
        include=["verbose_streaming"],
    )

    # Ask a question that requires both internal and external information
    chat.append(
        user(
            "Based on Tesla's actual production figures in my documents (collection), what is the "
            "current market and analyst sentiment on their 2024-2025 vehicle production performance?"
        )
    )

    is_thinking = True
    async for response, chunk in chat.stream():
        for tool_call in chunk.tool_calls:
            print(f"\\nCalling tool: {tool_call.function.name} with arguments: {tool_call.function.arguments}")
        if response.usage.reasoning_tokens and is_thinking:
            print(f"\\rThinking... ({response.usage.reasoning_tokens} tokens)", end="", flush=True)
        if chunk.content and is_thinking:
            print("\\n\\nFinal Response:")
            is_thinking = False
        if chunk.content and not is_thinking:
            print(chunk.content, end="", flush=True)
        latest_response = response

    print("\\n\\nCitations:")
    print(latest_response.citations)
    print("\\n\\nTool Usage:")
    print(latest_response.server_side_tool_usage)
```

### How It Works

When you provide both `collections_search()` and `web_search()`/`x_search()` tools, Grok autonomously determines the optimal search strategy:

1. **Internal Analysis First**: Searches your uploaded Tesla SEC filings to extract actual production numbers
2. **External Context Gathering**: Performs web/x-search searches to find analyst reports, market sentiment, and production expectations
3. **Synthesis**: Combines both data sources to provide a comprehensive analysis comparing actual performance against market expectations
4. **Cited Sources**: Returns citations from both your internal documents (using `collections://` URIs) and external web sources (using `https://` URLs)

### Example Output Pattern

```output
Thinking... (201 tokens)
Calling tool: collections_search with arguments: {"query":"Tesla vehicle production figures 2024 2025","limit":20}
Thinking... (498 tokens)
Calling tool: collections_search with arguments: {"query":"Tesla quarterly vehicle production and deliveries 2024 2025","limit":20}
Thinking... (738 tokens)
Calling tool: web_search with arguments: {"query":"Tesla quarterly vehicle production and deliveries 2024 2025","num_results":10}
Thinking... (738 tokens)
Calling tool: web_search with arguments: {"query":"market and analyst sentiment Tesla vehicle production performance 2024 2025","num_results":10}
Thinking... (1280 tokens)

Final Response 
... (omitted for brevity)
```

### Use Cases for Hybrid Search

This pattern is valuable for:

* **Market Analysis**: Compare internal financial data with external market sentiment and competitor performance
* **Competitive Intelligence**: Analyze your product performance against industry reports and competitor announcements
* **Compliance Verification**: Cross-reference internal policies with current regulatory requirements and industry standards
* **Strategic Planning**: Ground business decisions in both proprietary data and real-time market conditions
* **Customer Research**: Combine internal customer data with external reviews, social sentiment, and market trends


===/developers/tools/function-calling===
#### Tools

# Function Calling

Define custom tools that the model can invoke during a conversation. The model requests the call, you execute it locally, and return the result. This enables integration with databases, APIs, and any external system.

With streaming, the function call is returned in whole in a single chunk, not streamed across chunks.

## How It Works

1. Define tools with a name, description, and JSON schema for parameters
2. Include tools in your request
3. Model returns a `tool_call` when it needs external data
4. Execute the function locally and return the result
5. Model continues with your result

## Quick Start

```bash customLanguage="bash"
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
  "model": "grok-4-1-fast-reasoning",
  "input": [
    {"role": "user", "content": "What is the temperature in San Francisco?"}
  ],
  "tools": [
    {
      "type": "function",
      "name": "get_temperature",
      "description": "Get current temperature for a location",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {"type": "string", "description": "City name"},
          "unit": {"type": "string", "enum": ["celsius", "fahrenheit"], "default": "fahrenheit"}
        },
        "required": ["location"]
      }
    }
  ]
}'
```

```pythonXAI
import os
import json

from xai_sdk import Client
from xai_sdk.chat import user, tool, tool_result

client = Client(api_key=os.getenv("XAI_API_KEY"))

# Define tools
tools = [
    tool(
        name="get_temperature",
        description="Get current temperature for a location",
        parameters={
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"], "default": "fahrenheit"}
            },
            "required": ["location"]
        },
    ),
]

chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    tools=tools,
)
chat.append(user("What is the temperature in San Francisco?"))
response = chat.sample()

# Handle tool calls
if response.tool_calls:
    chat.append(response)
    for tc in response.tool_calls:
        args = json.loads(tc.function.arguments)
        # Execute your function
        result = {"location": args["location"], "temperature": 59, "unit": args.get("unit", "fahrenheit")}
        chat.append(tool_result(json.dumps(result)))
    
    response = chat.sample()

print(response.content)
```

```pythonOpenAISDK
import os
import json
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

tools = [
    {
        "type": "function",
        "name": "get_temperature",
        "description": "Get current temperature for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City name"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"], "default": "fahrenheit"}
            },
            "required": ["location"]
        },
    },
]

response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[{"role": "user", "content": "What is the temperature in San Francisco?"}],
    tools=tools,
)

# Handle function calls
for item in response.output:
    if item.type == "function_call":
        args = json.loads(item.arguments)
        result = {"location": args["location"], "temperature": 59, "unit": args.get("unit", "fahrenheit")}
        
        response = client.responses.create(
            model="grok-4-1-fast-reasoning",
            input=[{"type": "function_call_output", "call_id": item.call_id, "output": json.dumps(result)}],
            tools=tools,
            previous_response_id=response.id,
        )

for item in response.output:
    if item.type == "message":
        print(item.content[0].text)
```

```javascriptAISDK
import { xai } from '@ai-sdk/xai';
import { streamText, tool } from 'ai';
import { z } from 'zod';

const result = streamText({
  model: xai.responses('grok-4-1-fast-reasoning'),
  tools: {
    getTemperature: tool({
      description: 'Get current temperature for a location',
      parameters: z.object({
        location: z.string().describe('City name'),
        unit: z.enum(['celsius', 'fahrenheit']).default('fahrenheit'),
      }),
      execute: async ({ location, unit }) => ({
        location,
        temperature: unit === 'fahrenheit' ? 59 : 15,
        unit,
      }),
    }),
  },
  prompt: 'What is the temperature in San Francisco?',
});

for await (const chunk of result.fullStream) {
  if (chunk.type === 'text-delta') {
    process.stdout.write(chunk.text);
  }
}
```

## Defining Tools with Pydantic

Use Pydantic models for type-safe parameter schemas:

```pythonXAI
from typing import Literal
from pydantic import BaseModel, Field
from xai_sdk.chat import tool

class TemperatureRequest(BaseModel):
    location: str = Field(description="City and state, e.g. San Francisco, CA")
    unit: Literal["celsius", "fahrenheit"] = Field("fahrenheit", description="Temperature unit")

class CeilingRequest(BaseModel):
    location: str = Field(description="City and state, e.g. San Francisco, CA")

# Generate JSON schema from Pydantic models
tools = [
    tool(
        name="get_temperature",
        description="Get current temperature for a location",
        parameters=TemperatureRequest.model_json_schema(),
    ),
    tool(
        name="get_ceiling",
        description="Get current cloud ceiling for a location",
        parameters=CeilingRequest.model_json_schema(),
    ),
]
```

```pythonOpenAISDK
from typing import Literal
from pydantic import BaseModel, Field

class TemperatureRequest(BaseModel):
    location: str = Field(description="City and state, e.g. San Francisco, CA")
    unit: Literal["celsius", "fahrenheit"] = Field("fahrenheit", description="Temperature unit")

class CeilingRequest(BaseModel):
    location: str = Field(description="City and state, e.g. San Francisco, CA")

tools = [
    {
        "type": "function",
        "name": "get_temperature",
        "description": "Get current temperature for a location",
        "parameters": TemperatureRequest.model_json_schema(),
    },
    {
        "type": "function",
        "name": "get_ceiling",
        "description": "Get current cloud ceiling for a location",
        "parameters": CeilingRequest.model_json_schema(),
    },
]
```

## Handling Tool Calls

When the model wants to use your tool, execute the function and return the result:

```pythonXAI
import json

def get_temperature(location: str, unit: str = "fahrenheit") -> dict:
    # In production, call a real weather API
    temp = 59 if unit == "fahrenheit" else 15
    return {"location": location, "temperature": temp, "unit": unit}

def get_ceiling(location: str) -> dict:
    return {"location": location, "ceiling": 15000, "unit": "ft"}

tools_map = {
    "get_temperature": get_temperature,
    "get_ceiling": get_ceiling,
}

chat.append(user("What's the weather in Denver?"))
response = chat.sample()

# Process tool calls
if response.tool_calls:
    chat.append(response)
    
    for tool_call in response.tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        
        result = tools_map[name](**args)
        chat.append(tool_result(json.dumps(result)))
    
    response = chat.sample()

print(response.content)
```

```pythonOpenAISDK
import json

def get_temperature(location: str, unit: str = "fahrenheit") -> dict:
    temp = 59 if unit == "fahrenheit" else 15
    return {"location": location, "temperature": temp, "unit": unit}

tools_map = {"get_temperature": get_temperature}

# Process function calls
for item in response.output:
    if item.type == "function_call":
        name = item.name
        args = json.loads(item.arguments)
        
        if name not in tools_map:
            output = json.dumps({"error": f"Unknown function: {name}"})
        else:
            output = json.dumps(tools_map[name](**args))
        
        response = client.responses.create(
            model="grok-4-1-fast-reasoning",
            input=[{"type": "function_call_output", "call_id": item.call_id, "output": output}],
            tools=tools,
            previous_response_id=response.id,
        )

for item in response.output:
    if item.type == "message":
        print(item.content[0].text)
```

## Combining with Built-in Tools

Function calling works alongside built-in agentic tools. The model can use web search, then call your custom function:

```pythonXAI
from xai_sdk.chat import tool
from xai_sdk.tools import web_search, x_search

tools = [
    web_search(),                    # Built-in: runs on xAI servers
    x_search(),                      # Built-in: runs on xAI servers  
    tool(                            # Custom: runs on your side
        name="save_to_database",
        description="Save research results to the database",
        parameters={
            "type": "object",
            "properties": {
                "data": {"type": "string", "description": "Data to save"}
            },
            "required": ["data"]
        },
    ),
]

chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    tools=tools,
)
```

```pythonOpenAISDK
tools = [
    {"type": "web_search"},          # Built-in
    {"type": "x_search"},            # Built-in
    {                                # Custom
        "type": "function",
        "name": "save_to_database",
        "description": "Save research results to the database",
        "parameters": {
            "type": "object",
            "properties": {
                "data": {"type": "string", "description": "Data to save"}
            },
            "required": ["data"]
        },
    },
]
```

When mixing tools:

* **Built-in tools** execute automatically on xAI servers
* **Custom tools** pause execution and return to you for handling

See [Advanced Usage](/developers/tools/advanced-usage#mixing-server-side-and-client-side-tools) for complete examples with tool loops.

## Tool Choice

Control when the model uses tools:

| Value | Behavior |
|-------|----------|
| `"auto"` | Model decides whether to call a tool (default) |
| `"required"` | Model must call at least one tool |
| `"none"` | Disable tool calling |
| `{"type": "function", "function": {"name": "..."}}` | Force a specific tool |

## Parallel Function Calling

By default, parallel function calling is enabled — the model can request multiple tool calls in a single response. Process all of them before continuing:

```pythonWithoutSDK
# response.tool_calls may contain multiple calls
for tool_call in response.tool_calls:
    result = tools_map[tool_call.function.name](**json.loads(tool_call.function.arguments))
    # Append each result...
```

Disable with `parallel_tool_calls: false` in your request.

## Tool Schema Reference

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier (max 200 tools per request) |
| `description` | Yes | What the tool does — helps the model decide when to use it |
| `parameters` | Yes | JSON Schema defining function inputs |

### Parameter Schema

```json
{
  "type": "object",
  "properties": {
    "location": {
      "type": "string",
      "description": "City name"
    },
    "unit": {
      "type": "string",
      "enum": ["celsius", "fahrenheit"],
      "default": "celsius"
    }
  },
  "required": ["location"]
}
```

## Complete Vercel AI SDK Example

The Vercel AI SDK handles tool definition, execution, and the request/response loop automatically:

```javascriptAISDK
import { xai } from '@ai-sdk/xai';
import { streamText, tool, stepCountIs } from 'ai';
import { z } from 'zod';

const result = streamText({
  model: xai.responses('grok-4-1-fast-reasoning'),
  tools: {
    getCurrentTemperature: tool({
      description: 'Get current temperature for a location',
      parameters: z.object({
        location: z.string().describe('City and state, e.g. San Francisco, CA'),
        unit: z.enum(['celsius', 'fahrenheit']).default('fahrenheit'),
      }),
      execute: async ({ location, unit }) => ({
        location,
        temperature: unit === 'fahrenheit' ? 59 : 15,
        unit,
      }),
    }),
    getCurrentCeiling: tool({
      description: 'Get current cloud ceiling for a location',
      parameters: z.object({
        location: z.string().describe('City and state'),
      }),
      execute: async ({ location }) => ({
        location,
        ceiling: 15000,
        ceiling_type: 'broken',
        unit: 'ft',
      }),
    }),
  },
  stopWhen: stepCountIs(5),
  prompt: "What's the temperature and cloud ceiling in San Francisco?",
});

for await (const chunk of result.fullStream) {
  switch (chunk.type) {
    case 'text-delta':
      process.stdout.write(chunk.text);
      break;
    case 'tool-call':
      console.log(`Tool call: ${chunk.toolName}`, chunk.args);
      break;
    case 'tool-result':
      console.log(`Tool result: ${chunk.toolName}`, chunk.result);
      break;
  }
}
```


===/developers/tools/overview===
#### Tools

# Overview

The xAI API supports **tool calling**, enabling Grok to perform actions beyond generating text—like searching the web, executing code, querying your data, or calling your own custom functions. Tools extend what's possible with the API and let you build powerful, interactive applications.

## Types of Tools

The xAI API offers two categories of tools:

| Type | Description | Examples |
|------|-------------|----------|
| **Built-in Tools** | Server-side tools managed by xAI that execute automatically | Web Search, X Search, Code Interpreter, Collections Search |
| **Function Calling** | Custom functions you define that the model can invoke | Database queries, API calls, custom business logic |

Built-in tools run on xAI's servers—you provide the tool configuration, and the API handles execution and returns results. Function calling lets you define your own tools that the model can request, giving you full control over what happens when they're invoked.

## Pricing

Tool requests are priced based on two components: **token usage** and **tool invocations**. Since the model may call multiple tools to answer a query, costs scale with complexity.

For more details on Tools pricing, please check out [the pricing page](/developers/models#tools-pricing).

## How It Works

When you provide tools to a request, the xAI API can use them to gather information or perform actions:

1. **Analyzes the query** and determines what information or actions are needed
2. **Decides what to do next**: Make a tool call, or provide a final answer
3. **Executes the tool** (for built-in tools) or returns a tool call request (for function calling)
4. **Processes results** and continues until sufficient information is gathered
5. **Returns the final response** with citations where applicable

## Quick Start

```bash customLanguage="bash"
curl https://api.x.ai/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $XAI_API_KEY" \
  -d '{
  "model": "grok-4-1-fast-reasoning",
  "stream": true,
  "input": [
    {
      "role": "user",
      "content": "What are the latest updates from xAI?"
    }
  ],
  "tools": [
    { "type": "web_search" },
    { "type": "x_search" },
    { "type": "code_interpreter" }
  ]
}'
```

```pythonXAI
import os

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import web_search, x_search, code_execution

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    tools=[
        web_search(),
        x_search(),
        code_execution(),
    ],
)

chat.append(user("What are the latest updates from xAI?"))

for response, chunk in chat.stream():
    if chunk.content:
        print(chunk.content, end="", flush=True)

print("\nCitations:", response.citations)
```

```pythonOpenAISDK
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1",
)

response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[
        {"role": "user", "content": "What are the latest updates from xAI?"}
    ],
    tools=[
        {"type": "web_search"},
        {"type": "x_search"},
        {"type": "code_interpreter"},
    ],
    stream=True,
)

for event in response:
    if hasattr(event, 'delta') and hasattr(event.delta, 'content'):
        print(event.delta.content, end="", flush=True)
```

```javascriptAISDK
import { xai } from '@ai-sdk/xai';
import { streamText } from 'ai';

const { fullStream } = streamText({
  model: xai.responses('grok-4-1-fast-reasoning'),
  prompt: 'What are the latest updates from xAI?',
  tools: {
    web_search: xai.tools.webSearch(),
    x_search: xai.tools.xSearch(),
    code_execution: xai.tools.codeExecution(),
  },
});

for await (const part of fullStream) {
  if (part.type === 'text-delta') {
    process.stdout.write(part.text);
  } else if (part.type === 'source' && part.sourceType === 'url') {
    console.log(`Citation: ${part.url}`);
  }
}
```

```javascriptOpenAISDK
import OpenAI from "openai";

const client = new OpenAI({
  apiKey: process.env.XAI_API_KEY,
  baseURL: "https://api.x.ai/v1",
});

const stream = await client.responses.create({
  model: "grok-4-1-fast-reasoning",
  input: [
    { role: "user", content: "What are the latest updates from xAI?" }
  ],
  tools: [
    { type: "web_search" },
    { type: "x_search" },
    { type: "code_interpreter" },
  ],
  stream: true,
});

for await (const event of stream) {
  if (event.delta?.content) {
    process.stdout.write(event.delta.content);
  }
}
```

## Citations

The API automatically returns source URLs for information gathered via tools. See [Citations](/developers/tools/citations) for details on accessing and using citation data.

## Next Steps

* **[Function Calling](/developers/tools/function-calling)** - Define custom tools the model can call
* **[Web Search](/developers/tools/web-search)** - Search the web and browse pages
* **[X Search](/developers/tools/x-search)** - Search X posts, users, and threads
* **[Code Execution](/developers/tools/code-execution)** - Execute Python code in a sandbox
* **[Collections Search](/developers/tools/collections-search)** - Query your uploaded documents
* **[Citations](/developers/tools/citations)** - Access source URLs and inline citations


===/developers/tools/remote-mcp===
#### Tools

# Remote MCP Tools

Remote MCP Tools allow Grok to connect to external MCP (Model Context Protocol) servers, extending its capabilities with custom tools from third parties or your own implementations. Simply specify a server URL and optional configuration - xAI manages the MCP server connection and interaction on your behalf.

## SDK Support

Remote MCP tools are supported in the xAI native SDK and the OpenAI compatible Responses API.

The `require_approval` and `connector_id` parameters in the OpenAI Responses API are not currently supported.

## Configuration

To use remote MCP tools, you need to configure the connection to your MCP server in the tools array of your request.

| Parameter | Required | Description |
|-----------|-------------------|-------------|
| `server_url` | Yes | The URL of the MCP server to connect to. Only Streaming HTTP and SSE transports are supported. |
| `server_label` | No | A label to identify the server (used for tool call prefixing) |
| `server_description` | No | A description of what the server provides |
| `allowed_tool_names` | No | List of specific tool names to allow (empty allows all) |
| `authorization` | No | A token that will be set in the Authorization header on requests to the MCP server |
| `extra_headers` | No | Additional headers to include in requests |

### Basic MCP Tool Usage

```pythonXAI
import os

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import mcp

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    tools=[
        mcp(server_url="https://mcp.deepwiki.com/mcp"),
    ],
    include=["verbose_streaming"],
)

chat.append(user("What can you do with https://github.com/xai-org/xai-sdk-python?"))

is_thinking = True
for response, chunk in chat.stream():
    # View the server-side tool calls as they are being made in real-time
    for tool_call in chunk.tool_calls:
        print(f"\\nCalling tool: {tool_call.function.name} with arguments: {tool_call.function.arguments}")
    if response.usage.reasoning_tokens and is_thinking:
        print(f"\\rThinking... ({response.usage.reasoning_tokens} tokens)", end="", flush=True)
    if chunk.content and is_thinking:
        print("\\n\\nFinal Response:")
        is_thinking = False
    if chunk.content and not is_thinking:
        print(chunk.content, end="", flush=True)

print("\\n\\nUsage:")
print(response.usage)
print(response.server_side_tool_usage)
print("\\n\\nServer Side Tool Calls:")
print(response.tool_calls)
```

```pythonOpenAISDK
import os
from openai import OpenAI

api_key = os.getenv("XAI_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://api.x.ai/v1",
)

response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[
        {
            "role": "user",
            "content": "What can you do with https://github.com/xai-org/xai-sdk-python?",
        },
    ],
    tools=[
        {
            "type": "mcp",
            "server_url": "https://mcp.deepwiki.com/mcp",
            "server_label": "deepwiki",
        }
    ],
)

print(response)
```

```pythonRequests
import os
import requests

url = "https://api.x.ai/v1/responses"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}"
}
payload = {
    "model": "grok-4-1-fast-reasoning",
    "input": [
        {
            "role": "user",
            "content": "What can you do with https://github.com/xai-org/xai-sdk-python?"
        }
    ],
    "tools": [
        {
            "type": "mcp",
            "server_url": "https://mcp.deepwiki.com/mcp",
            "server_label": "deepwiki",
        }
    ]
}
response = requests.post(url, headers=headers, json=payload)
print(response.json())
```

```bash
curl https://api.x.ai/v1/responses \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer $XAI_API_KEY" \\
  -d '{
  "model": "grok-4-1-fast-reasoning",
  "input": [
    {
      "role": "user",
      "content": "What can you do with https://github.com/xai-org/xai-sdk-python?"
    }
  ],
  "tools": [
    {
        "type": "mcp",
        "server_url": "https://mcp.deepwiki.com/mcp",
        "server_label": "deepwiki"
    }
  ]
}'
```

## Tool Enablement and Access Control

When you configure a Remote MCP Tool without specifying `allowed_tool_names`, all tool definitions exposed by the MCP server are automatically injected into the model's context. This means the model gains access to every tool that the MCP server provides, allowing it to use any of them during the conversation.

For example, if an MCP server exposes 10 different tools and you don't specify `allowed_tool_names`, all 10 tool definitions will be available to the model. The model can then choose to call any of these tools based on the user's request and the tool descriptions.

Use the `allowed_tool_names` parameter to selectively enable only specific tools from an MCP server. This can give you several key benefits:

* **Better Performance**: Reduce context overhead by limiting tool definitions the model needs to consider
* **Reduced Risk**: For example, restrict access to tools that only perform read-only operations to prevent the model from modifying data

```pythonXAI
# Enable only specific tools from a server with many available tools
mcp(
    server_url="https://comprehensive-tools.example.com/mcp",
    allowed_tool_names=["search_database", "format_data"]
)
```

Instead of giving the model access to every tool the server offers, this approach keeps Grok focused and efficient while ensuring it has exactly the capabilities it needs.

## Multi-Server Support

Enable multiple MCP servers simultaneously to create a rich ecosystem of specialized tools:

```pythonXAI
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    tools=[
        mcp(server_url="https://mcp.deepwiki.com/mcp", server_label="deepwiki"),
        mcp(server_url="https://your-custom-tools.com/mcp", server_label="custom"),
        mcp(server_url="https://api.example.com/tools", server_label="api-tools"),
    ],
)
```

Each server can provide different capabilities - documentation tools, API integrations, custom business logic, or specialized data processing - all accessible within a single conversation.

## Best Practices

* **Provide clear server metadata**: Use descriptive `server_label` and `server_description` when configuring multiple MCP servers to help the model understand each server's purpose and select the right tools
* **Filter tools appropriately**: Use `allowed_tool_names` to restrict access to only necessary tools, especially when servers have many tools since the model must keep all available tool definitions in context
* **Use secure connections**: Always use HTTPS URLs and implement proper authentication mechanisms on your MCP server
* **Provide Examples**: While the model can generally figure out what tools to use based on the tool descriptions and the user request it may help to provide examples in the prompt


===/developers/tools/streaming-and-sync===
#### Tools

# Streaming & Synchronous Requests

Agentic requests can be executed in either streaming or synchronous mode. This page covers both approaches and how to use them effectively.

## Streaming Mode (Recommended)

We strongly recommend using streaming mode when using agentic tool calling. It provides:

* **Real-time observability** of tool calls as they happen
* **Immediate feedback** during potentially long-running requests
* **Reasoning token counts** as the model thinks

### Streaming Example

```pythonXAI
import os

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import code_execution, web_search, x_search

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    tools=[
        web_search(),
        x_search(),
        code_execution(),
    ],
    include=["verbose_streaming"],
)

chat.append(user("What are the latest updates from xAI?"))

is_thinking = True
for response, chunk in chat.stream():
    # View server-side tool calls in real-time
    for tool_call in chunk.tool_calls:
        print(f"\\nCalling tool: {tool_call.function.name}")
    if response.usage.reasoning_tokens and is_thinking:
        print(f"\\rThinking... ({response.usage.reasoning_tokens} tokens)", end="", flush=True)
    if chunk.content and is_thinking:
        print("\\n\\nFinal Response:")
        is_thinking = False
    if chunk.content and not is_thinking:
        print(chunk.content, end="", flush=True)

print("\\nCitations:", response.citations)
```

```javascriptAISDK
import { xai } from '@ai-sdk/xai';
import { streamText } from 'ai';

const { fullStream } = streamText({
  model: xai.responses('grok-4-1-fast-reasoning'),
  prompt: 'What are the latest updates from xAI?',
  tools: {
    web_search: xai.tools.webSearch(),
    x_search: xai.tools.xSearch(),
    code_execution: xai.tools.codeExecution(),
  },
});

for await (const part of fullStream) {
  if (part.type === 'tool-call') {
    console.log(\`Calling tool: \${part.toolName}\`);
  } else if (part.type === 'text-delta') {
    process.stdout.write(part.text);
  } else if (part.type === 'source' && part.sourceType === 'url') {
    console.log(\`Citation: \${part.url}\`);
  }
}
```

## Synchronous Mode

For simpler use cases or when you want to wait for the complete agentic workflow to finish before processing the response, you can use synchronous requests:

```pythonXAI
import os

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import code_execution, web_search, x_search

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    tools=[
        web_search(),
        x_search(),
        code_execution(),
    ],
)

chat.append(user("What is the latest update from xAI?"))

# Get the final response in one go once it's ready
response = chat.sample()

print("Final Response:")
print(response.content)

print("\\nCitations:")
print(response.citations)

print("\\nUsage:")
print(response.usage)
print(response.server_side_tool_usage)
```

```javascriptAISDK
import { xai } from '@ai-sdk/xai';
import { generateText } from 'ai';

// Synchronous request - waits for complete response
const { text, sources } = await generateText({
  model: xai.responses('grok-4-1-fast-reasoning'),
  prompt: 'What is the latest update from xAI?',
  tools: {
    web_search: xai.tools.webSearch(),
    x_search: xai.tools.xSearch(),
    code_execution: xai.tools.codeExecution(),
  },
});

console.log('Final Response:');
console.log(text);

console.log('\\nCitations:');
console.log(sources);
```

Synchronous requests will wait for the entire agentic process to complete before returning. This is simpler for basic use cases but provides less visibility into intermediate steps.

## Using Tools with Responses API

We also support using the Responses API in both streaming and non-streaming modes:

```pythonXAI
import os

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import web_search, x_search

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    store_messages=True,  # Enable Responses API
    tools=[
        web_search(),
        x_search(),
    ],
)

chat.append(user("What is the latest update from xAI?"))
response = chat.sample()

print(response.content)
print(response.citations)

# The response id can be used to continue the conversation
print(response.id)
```

```pythonOpenAISDK
import os
from openai import OpenAI

api_key = os.getenv("XAI_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://api.x.ai/v1",
)

response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[
        {
            "role": "user",
            "content": "what is the latest update from xAI?",
        },
    ],
    tools=[
        {
            "type": "web_search",
        },
        {
            "type": "x_search",
        },
    ],
)

print(response)
```

```bash
curl https://api.x.ai/v1/responses \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer $XAI_API_KEY" \\
  -d '{
  "model": "grok-4-1-fast-reasoning",
  "input": [
    {
      "role": "user",
      "content": "what is the latest update from xAI?"
    }
  ],
  "tools": [
    {
      "type": "web_search"
    },
    {
      "type": "x_search"
    }
  ]
}'
```

## Accessing Tool Outputs

By default, server-side tool call outputs are not returned since they can be large. However, you can opt-in to receive them:

### xAI SDK

| Tool | Value for `include` field |
|------|---------------------------|
| `"web_search"` | `"web_search_call_output"` |
| `"x_search"` | `"x_search_call_output"` |
| `"code_execution"` | `"code_execution_call_output"` |
| `"collections_search"` | `"collections_search_call_output"` |
| `"attachment_search"` | `"attachment_search_call_output"` |
| `"mcp"` | `"mcp_call_output"` |

```pythonXAI
import os
from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import code_execution

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    tools=[
        code_execution(),
    ],
    include=["code_execution_call_output"],
)
chat.append(user("What is the 100th Fibonacci number?"))

# stream or sample the response...
```

### Responses API

| Tool | Responses API tool name | Value for `include` field |
|------|-------------------------|---------------------------|
| `"web_search"` | `"web_search"` | `"web_search_call.action.sources"` |
| `"code_execution"` | `"code_interpreter"` | `"code_interpreter_call.outputs"` |
| `"collections_search"` | `"file_search"` | `"file_search_call.results"` |
| `"mcp"` | `"mcp"` | Always returned in Responses API |


===/developers/tools/tool-usage-details===
#### Tools

# Tool Usage Details

This page covers the technical details of how tool calls are tracked, billed, and how to understand token usage in agentic requests.

## Real-time Server-side Tool Calls

When streaming agentic requests, you can observe **every tool call decision** the model makes in real-time via the `tool_calls` attribute on the `chunk` object:

```pythonWithoutSDK
for tool_call in chunk.tool_calls:
    print(f"\nCalling tool: {tool_call.function.name} with arguments: {tool_call.function.arguments}")
```

**Note**: Only the tool call invocations are shown — **server-side tool call outputs are not returned** in the API response. The agent uses these outputs internally to formulate its final response.

## Server-side Tool Calls vs Tool Usage

The API provides two related but distinct metrics for server-side tool executions:

### `tool_calls` - All Attempted Calls

```pythonWithoutSDK
response.tool_calls
```

Returns a list of all **attempted** tool calls made during the agentic process. Each entry contains:

* `id`: Unique identifier for the tool call
* `function.name`: The name of the specific server-side tool called
* `function.arguments`: The parameters passed to the server-side tool

This includes **every tool call attempt**, even if some fail.

### `server_side_tool_usage` - Successful Calls (Billable)

```pythonWithoutSDK
response.server_side_tool_usage
```

Returns a map of successfully executed tools and their invocation counts. This represents only the tool calls that returned meaningful responses and **determines your billing**.

```output
{'SERVER_SIDE_TOOL_X_SEARCH': 3, 'SERVER_SIDE_TOOL_WEB_SEARCH': 2}
```

## Tool Call Function Names vs Usage Categories

The function names in `tool_calls` represent the precise name of the tool invoked, while the entries in `server_side_tool_usage` provide a high-level categorization that aligns with the original tool passed in the `tools` array.

| Usage Category | Function Name(s) |
|----------------|------------------|
| `SERVER_SIDE_TOOL_WEB_SEARCH` | `web_search`, `web_search_with_snippets`, `browse_page` |
| `SERVER_SIDE_TOOL_X_SEARCH` | `x_user_search`, `x_keyword_search`, `x_semantic_search`, `x_thread_fetch` |
| `SERVER_SIDE_TOOL_CODE_EXECUTION` | `code_execution` |
| `SERVER_SIDE_TOOL_VIEW_X_VIDEO` | `view_x_video` |
| `SERVER_SIDE_TOOL_VIEW_IMAGE` | `view_image` |
| `SERVER_SIDE_TOOL_COLLECTIONS_SEARCH` | `collections_search` |
| `SERVER_SIDE_TOOL_MCP` | `{server_label}.{tool_name}` if `server_label` provided, otherwise `{tool_name}` |

## When Tool Calls and Usage Differ

In most cases, `tool_calls` and `server_side_tool_usage` will show the same tools. However, they can differ when:

* **Failed tool executions**: The model attempts to browse a non-existent webpage, fetch a deleted X post, or encounters other execution errors
* **Invalid parameters**: Tool calls with malformed arguments that can't be processed
* **Network or service issues**: Temporary failures in the tool execution pipeline

The agentic system handles these failures gracefully, updating its trajectory and continuing with alternative approaches when needed.

**Billing Note**: Only successful tool executions (`server_side_tool_usage`) are billed. Failed attempts are not charged.

## Understanding Token Usage

Agentic requests have unique token usage patterns compared to standard chat completions:

### `completion_tokens`

Represents **only the final text output** of the model. This is typically much smaller than you might expect, as the agent performs all its intermediate reasoning and tool orchestration internally.

### `prompt_tokens`

Represents the **cumulative input tokens** across all inference requests made during the agentic process. Each request includes the full conversation history up to that point, which grows as the agent progresses.

While this can result in higher `prompt_tokens` counts, agentic requests benefit significantly from **prompt caching**. The majority of the prompt remains unchanged between steps, allowing for efficient caching.

### `reasoning_tokens`

Represents the tokens used for the model's internal reasoning process. This includes planning tool calls, analyzing results, and formulating responses, but excludes the final output tokens.

### `cached_prompt_text_tokens`

Indicates how many prompt tokens were served from cache rather than recomputed. Higher values indicate better cache utilization and lower costs.

### `prompt_image_tokens`

Represents tokens from visual content that the agent processes. These are counted separately from text tokens. If no images or videos are processed, this value will be zero.

## Limiting Tool Call Turns

The `max_turns` parameter allows you to control the maximum number of assistant/tool-call turns the agent can perform during a single request.

### Understanding Turns vs Tool Calls

**Important**: `max_turns` does **not** directly limit the number of individual tool calls. Instead, it limits the number of assistant turns in the agentic loop. During a single turn, the model may invoke multiple tools in parallel.

A "turn" represents one iteration of the agentic reasoning loop:

1. The model analyzes the current context
2. The model decides to call one or more tools (potentially in parallel)
3. Tools execute and return results
4. The model processes the results

```pythonXAI
import os

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import web_search, x_search

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    tools=[
        web_search(),
        x_search(),
    ],
    max_turns=3,  # Limit to 3 assistant/tool-call turns
)

chat.append(user("What is the latest news from xAI?"))
response = chat.sample()
print(response.content)
```

### When to Use `max_turns`

| Use Case | Recommended `max_turns` | Tradeoff |
|----------|------------------------|----------|
| **Quick lookups** | 1-2 | Fastest response, may miss deeper insights |
| **Balanced research** | 3-5 | Good balance of speed and thoroughness |
| **Deep research** | 10+ or unset | Most comprehensive, longer latency and higher cost |

### Default Behavior

If `max_turns` is not specified, the server applies a global default cap. When the agent reaches the limit, it will stop making additional tool calls and generate a final response based on information gathered so far.

## Identifying Tool Call Types

To determine whether a returned tool call is a client-side tool that needs local execution:

### Using xAI SDK

Use the `get_tool_call_type` function:

```pythonXAI
from xai_sdk.tools import get_tool_call_type

for tool_call in response.tool_calls:
    print(get_tool_call_type(tool_call))
```

| Tool call types | Description |
|---------------|-------------|
| `"client_side_tool"` | Client-side tool call - requires local execution |
| `"web_search_tool"` | Web-search tool - handled by xAI server |
| `"x_search_tool"` | X-search tool - handled by xAI server |
| `"code_execution_tool"` | Code-execution tool - handled by xAI server |
| `"collections_search_tool"` | Collections-search tool - handled by xAI server |
| `"mcp_tool"` | MCP tool - handled by xAI server |

### Using Responses API

Check the `type` field of output entries (`response.output[].type`):

| Types | Description |
|-------|-------------|
| `"function_call"` | Client-side tool - requires local execution |
| `"web_search_call"` | Web-search tool - handled by xAI server |
| `"x_search_call"` | X-search tool - handled by xAI server |
| `"code_interpreter_call"` | Code-execution tool - handled by xAI server |
| `"file_search_call"` | Collections-search tool - handled by xAI server |
| `"mcp_call"` | MCP tool - handled by xAI server |


===/developers/tools/web-search===
#### Tools

# Web Search

The Web Search tool enables Grok to search the web in real-time and browse web pages to find information. This powerful tool allows the model to search the internet, access web pages, and extract relevant information to answer queries with up-to-date content.

## SDK Support

| SDK/API | Tool Name |
|---------|-----------|
| xAI SDK | `web_search` |
| OpenAI Responses API | `web_search` |
| Vercel AI SDK | `xai.tools.webSearch()` |

This tool is also supported in all Responses API compatible SDKs.

## Basic Usage

```pythonXAI
import os

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import web_search

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",  # reasoning model
    tools=[web_search()],
    include=["verbose_streaming"],
)

chat.append(user("What is xAI?"))

is_thinking = True
for response, chunk in chat.stream():
    for tool_call in chunk.tool_calls:
        print(f"\\nCalling tool: {tool_call.function.name} with arguments: {tool_call.function.arguments}")
    if response.usage.reasoning_tokens and is_thinking:
        print(f"\\rThinking... ({response.usage.reasoning_tokens} tokens)", end="", flush=True)
    if chunk.content and is_thinking:
        print("\\n\\nFinal Response:")
        is_thinking = False
    if chunk.content and not is_thinking:
        print(chunk.content, end="", flush=True)

print("\\n\\nCitations:")
print(response.citations)
```

```pythonOpenAISDK
import os
from openai import OpenAI

api_key = os.getenv("XAI_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://api.x.ai/v1",
)

response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[
        {
            "role": "user",
            "content": "What is xAI?",
        },
    ],
    tools=[
        {
            "type": "web_search",
        },
    ],
)

print(response)
```

```javascriptAISDK
import { xai } from '@ai-sdk/xai';
import { generateText } from 'ai';

const { text, sources } = await generateText({
  model: xai.responses('grok-4-1-fast-reasoning'),
  prompt: 'What is xAI?',
  tools: {
    web_search: xai.tools.webSearch(),
  },
});

console.log(text);
console.log('Citations:', sources);
```

```bash
curl https://api.x.ai/v1/responses \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer $XAI_API_KEY" \\
  -d '{
  "model": "grok-4-1-fast-reasoning",
  "input": [
    {
      "role": "user",
      "content": "What is xAI?"
    }
  ],
  "tools": [
    {
      "type": "web_search"
    }
  ]
}'
```

## Web Search Parameters

| Parameter | Description |
|-----------|-------------|
| `allowed_domains` | Only search within specific domains (max 5) |
| `excluded_domains` | Exclude specific domains from search (max 5) |
| `enable_image_understanding` | Enable analysis of images found during browsing |

### Only Search in Specific Domains

Use `allowed_domains` to make the web search **only** perform the search and web browsing on web pages that fall within the specified domains.

`allowed_domains` cannot be set together with `excluded_domains` in the same request.

```pythonXAI
import os

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import web_search

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    tools=[
        web_search(allowed_domains=["grokipedia.com"]),
    ],
)

chat.append(user("What is xAI?"))
# stream or sample the response...
```

```pythonOpenAISDK
response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[{"role": "user", "content": "What is xAI?"}],
    tools=[
        {
            "type": "web_search",
            "filters": {"allowed_domains": ["grokipedia.com"]},
        },
    ],
)
```

```javascriptAISDK
const { text } = await generateText({
  model: xai.responses('grok-4-1-fast-reasoning'),
  prompt: 'What is xAI?',
  tools: {
    web_search: xai.tools.webSearch({
      allowedDomains: ['grokipedia.com'],
    }),
  },
});
```

### Exclude Specific Domains

Use `excluded_domains` to prevent the model from including the specified domains in any web search tool invocations.

```pythonXAI
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    tools=[
        web_search(excluded_domains=["grokipedia.com"]),
    ],
)
```

```pythonOpenAISDK
response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[{"role": "user", "content": "What is xAI?"}],
    tools=[
        {
            "type": "web_search",
            "filters": {"excluded_domains": ["grokipedia.com"]},
        },
    ],
)
```

### Enable Image Understanding

Setting `enable_image_understanding` to true equips the agent with access to the `view_image` tool, allowing it to analyze images encountered during the search process.

When enabled, you will see `SERVER_SIDE_TOOL_VIEW_IMAGE` in `response.server_side_tool_usage` along with the number of times it was called.

Enabling this parameter for Web Search will also enable the image understanding for X Search tool if it's also included in the request.

```pythonXAI
import os

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import web_search

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    tools=[
        web_search(enable_image_understanding=True),
    ],
)

chat.append(user("What is included in the image in xAI's official website?"))
# stream or sample the response...
```

```pythonOpenAISDK
response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[
        {
            "role": "user",
            "content": "What is included in the image in xAI's official website?",
        },
    ],
    tools=[
        {
            "type": "web_search",
            "enable_image_understanding": True,
        },
    ],
)
```

```javascriptAISDK
const { text } = await generateText({
  model: xai.responses('grok-4-1-fast-reasoning'),
  prompt: "What is included in the image in xAI's official website?",
  tools: {
    web_search: xai.tools.webSearch({
      enableImageUnderstanding: true,
    }),
  },
});
```

## Citations

For details on how to retrieve and use citations from search results, see the [Citations](/developers/tools/citations) page.


===/developers/tools/x-search===
#### Tools

# X Search

The X Search tool enables Grok to perform keyword search, semantic search, user search, and thread fetch on X (formerly Twitter). This powerful tool allows the model to access real-time social media content, analyze posts, and gather insights from X's vast data.

## SDK Support

| SDK/API | Tool Name |
|---------|-----------|
| xAI SDK | `x_search` |
| OpenAI Responses API | `x_search` |
| Vercel AI SDK | `xai.tools.xSearch()` |

This tool is also supported in all Responses API compatible SDKs.

## Basic Usage

```pythonXAI
import os

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import x_search

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",  # reasoning model
    tools=[x_search()],
    include=["verbose_streaming"],
)

chat.append(user("What are people saying about xAI on X?"))

is_thinking = True
for response, chunk in chat.stream():
    for tool_call in chunk.tool_calls:
        print(f"\\nCalling tool: {tool_call.function.name} with arguments: {tool_call.function.arguments}")
    if response.usage.reasoning_tokens and is_thinking:
        print(f"\\rThinking... ({response.usage.reasoning_tokens} tokens)", end="", flush=True)
    if chunk.content and is_thinking:
        print("\\n\\nFinal Response:")
        is_thinking = False
    if chunk.content and not is_thinking:
        print(chunk.content, end="", flush=True)

print("\\n\\nCitations:")
print(response.citations)
```

```pythonOpenAISDK
import os
from openai import OpenAI

api_key = os.getenv("XAI_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://api.x.ai/v1",
)

response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[
        {
            "role": "user",
            "content": "What are people saying about xAI on X?",
        },
    ],
    tools=[
        {
            "type": "x_search",
        },
    ],
)

print(response)
```

```javascriptAISDK
import { xai } from '@ai-sdk/xai';
import { generateText } from 'ai';

const { text, sources } = await generateText({
  model: xai.responses('grok-4-1-fast-reasoning'),
  prompt: 'What are people saying about xAI on X?',
  tools: {
    x_search: xai.tools.xSearch(),
  },
});

console.log(text);
console.log('Citations:', sources);
```

```bash
curl https://api.x.ai/v1/responses \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer $XAI_API_KEY" \\
  -d '{
  "model": "grok-4-1-fast-reasoning",
  "input": [
    {
      "role": "user",
      "content": "What are people saying about xAI on X?"
    }
  ],
  "tools": [
    {
      "type": "x_search"
    }
  ]
}'
```

## X Search Parameters

| Parameter | Description |
|-----------|-------------|
| `allowed_x_handles` | Only consider posts from specific X handles (max 10) |
| `excluded_x_handles` | Exclude posts from specific X handles (max 10) |
| `from_date` | Start date for search range (ISO8601 format) |
| `to_date` | End date for search range (ISO8601 format) |
| `enable_image_understanding` | Enable analysis of images in posts |
| `enable_video_understanding` | Enable analysis of videos in posts |

### Only Consider Posts from Specific Handles

Use `allowed_x_handles` to consider X posts only from a given list of X handles. The maximum number of handles you can include is 10.

`allowed_x_handles` cannot be set together with `excluded_x_handles` in the same request.

```pythonXAI
import os

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import x_search

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    tools=[
        x_search(allowed_x_handles=["elonmusk"]),
    ],
)

chat.append(user("What is the current status of xAI?"))
# stream or sample the response...
```

```pythonOpenAISDK
response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[{"role": "user", "content": "What is the current status of xAI?"}],
    tools=[
        {
            "type": "x_search",
            "allowed_x_handles": ["elonmusk"],
        },
    ],
)
```

```javascriptAISDK
const { text } = await generateText({
  model: xai.responses('grok-4-1-fast-reasoning'),
  prompt: 'What is the current status of xAI?',
  tools: {
    x_search: xai.tools.xSearch({
      allowedXHandles: ['elonmusk'],
    }),
  },
});
```

### Exclude Posts from Specific Handles

Use `excluded_x_handles` to prevent the model from including X posts from the specified handles in any X search tool invocations. The maximum number of handles you can exclude is 10.

```pythonXAI
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    tools=[
        x_search(excluded_x_handles=["elonmusk"]),
    ],
)
```

```pythonOpenAISDK
response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[{"role": "user", "content": "What is the current status of xAI?"}],
    tools=[
        {
            "type": "x_search",
            "excluded_x_handles": ["elonmusk"],
        },
    ],
)
```

```javascriptAISDK
const { text } = await generateText({
  model: xai.responses('grok-4-1-fast-reasoning'),
  prompt: 'What is the current status of xAI?',
  tools: {
    x_search: xai.tools.xSearch({
      excludedXHandles: ['elonmusk'],
    }),
  },
});
```

### Date Range

You can restrict the date range of search data used by specifying `from_date` and `to_date`. This limits the data to the period from `from_date` to `to_date`, including both dates.

Both fields need to be in ISO8601 format, e.g., "YYYY-MM-DD". If you're using the xAI Python SDK, the `from_date` and `to_date` fields can be passed as `datetime.datetime` objects.

```pythonXAI
import os
from datetime import datetime

from xai_sdk import Client
from xai_sdk.chat import user
from xai_sdk.tools import x_search

client = Client(api_key=os.getenv("XAI_API_KEY"))
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    tools=[
        x_search(
            from_date=datetime(2025, 10, 1),
            to_date=datetime(2025, 10, 10),
        ),
    ],
)

chat.append(user("What is the current status of xAI?"))
# stream or sample the response...
```

```pythonOpenAISDK
response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[{"role": "user", "content": "What is the current status of xAI?"}],
    tools=[
        {
            "type": "x_search",
            "from_date": "2025-10-01",
            "to_date": "2025-10-10",
        },
    ],
)
```

```javascriptAISDK
const { text } = await generateText({
  model: xai.responses('grok-4-1-fast-reasoning'),
  prompt: 'What is the current status of xAI?',
  tools: {
    x_search: xai.tools.xSearch({
      fromDate: '2025-10-01',
      toDate: '2025-10-10',
    }),
  },
});
```

### Enable Image Understanding

Setting `enable_image_understanding` to true allows the agent to analyze images in X posts encountered during the search process.

```pythonXAI
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    tools=[
        x_search(enable_image_understanding=True),
    ],
)
```

```pythonOpenAISDK
response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[{"role": "user", "content": "Find X posts with images about AI"}],
    tools=[
        {
            "type": "x_search",
            "enable_image_understanding": True,
        },
    ],
)
```

```javascriptAISDK
const { text } = await generateText({
  model: xai.responses('grok-4-1-fast-reasoning'),
  prompt: 'Find X posts with images about AI',
  tools: {
    x_search: xai.tools.xSearch({
      enableImageUnderstanding: true,
    }),
  },
});
```

### Enable Video Understanding

Setting `enable_video_understanding` to true allows the agent to analyze videos in X posts. This is only available for X Search (not Web Search).

```pythonXAI
chat = client.chat.create(
    model="grok-4-1-fast-reasoning",
    tools=[
        x_search(enable_video_understanding=True),
    ],
)
```

```pythonOpenAISDK
response = client.responses.create(
    model="grok-4-1-fast-reasoning",
    input=[{"role": "user", "content": "Find X posts with videos about AI"}],
    tools=[
        {
            "type": "x_search",
            "enable_video_understanding": True,
        },
    ],
)
```

```javascriptAISDK
const { text } = await generateText({
  model: xai.responses('grok-4-1-fast-reasoning'),
  prompt: 'Find X posts with videos about AI',
  tools: {
    x_search: xai.tools.xSearch({
      enableVideoUnderstanding: true,
    }),
  },
});
```

## Citations

For details on how to retrieve and use citations from search results, see the [Citations](/developers/tools/citations) page.


===/grok/apps/google-drive===
#### Grok Business / Enterprise

# Google Drive Integration with Grok

## Overview: Connect Google Drive to Grok

Seamlessly search and reference your Google Drive files directly in Grok chats. This integration lets Grok access your team's shared files and your personal files to provide more accurate, grounded responses—reducing hallucinations and helping you work faster.

Powered by xAI's Collections API, the connector indexes files securely while respecting Google Drive permissions. Grok only retrieves content you can view. Files you don't have permission to view are never indexed or returned.

**Key benefits**:

* Get summaries, analyses, or answers with direct citations to your files.
* No need to manually upload or attach files. Grok searches automatically when relevant.
* Query files by content or metadata (filename, folder, owner, modification dates).

This feature is available in Grok Business and Enterprise plans. xAI doesn't use customer Google Drive data to train its models.

## Using Google Drive Files in Grok Chats

Once connected, Grok automatically searches relevant files—no extra steps needed.

**Examples of what to ask**:

* "Summarize the Q4 sales report from the Finance team documents."
* "What does our employee handbook say about remote work policies according to our company documents?"
* "Summarize my Go-to-market strategy document."

**Grok will**:

* Search content and metadata.
* Provide answers with inline citations linking back to the source file.
* Reason over multiple files when needed.

## Setting Up the Integration

Setup combines admin configuration for team shared files and optional user connections for personal files.

### Admin Setup: Enable for Shared Files

Team admins configure the connector once at the workspace level.

**Prerequisites**:

* You must be a Grok Business or Enterprise team admin.
* You must have purchased Grok Business or Enterprise licenses for your team.

**Steps**:

1. Log in to the xAI Console and go to **[Grok Business Apps](https://console.x.ai/team/default/grok-business/apps)**
2. Click **[Add to team](https://console.x.ai/team/default/grok-business/apps?add-connector-type=CONNECTOR_TYPE_GOOGLE_DRIVE)** for the Google Drive app.
3. Specify your Google Workspace domain.
4. Choose who can use the connector: everyone in the workspace or specific allowed users.
5. Sign in with your Google account and grant permissions. The OAuth authentication provides a secure way to allow access without sharing passwords.

Once connected, Grok immediately begins syncing files accessible to the admin's account. Shared files become available to authorized users right away.

Admins can later edit allowed users or remove the connector entirely from the same settings page.

### User Setup: Connect Your Personal Drive

End users can optionally connect their own Google Drive for searching their private files.

**Steps**:

1. On grok.com, go to **[Settings > Connected apps](https://grok.com/?_s=grok-business-connected-apps)**.
2. Select **Google Drive > Connect**.
3. Sign in with your Google account and grant permissions.
4. Your private files will sync and become searchable in your Grok chats.

To disconnect: Return to **[Settings > Connected apps](https://grok.com/?_s=grok-business-connected-apps)** and revoke access.

## Managing Your Integration

* Admins can view sync status and the list of users who have authenticated with Google Drive from **[Apps Settings page](https://console.x.ai/team/default/grok-business/apps)**.
* Admins or members can disconnect anytime to stop syncing their files.

## How Indexing and Syncing Works

* Initial sync starts immediately after admin setup.
* Ongoing: Grok checks for changes (new/updated/deleted files, permission changes) every hour.
* Permissions are always enforced. Grok only shows you files you can view in Google Drive.
* No inclusion/exclusion rules beyond the admin's initial access scope and user permissions.

**Supported file formats**:

Grok indexes a wide range of common file types from Google Drive, including native Google formats, Microsoft Office documents, PDFs, code files, and more.

| Category | File Formats |
|----------|--------------|
| Documents & Presentations | Google Docs, Sheets, and Slides, Microsoft Word (.doc, .docx), Microsoft Excel (.xls, .xlsx, including macro-enabled workbooks), Microsoft PowerPoint (.ppt, .pptx, including macro-enabled presentations and slideshows), Microsoft Outlook (.msg, .pst), PDFs, OpenDocument Text (.odt), Rich Text Format (.rtf), EPUB e-books |
| Data & Structured Files | CSV (comma-separated values), JSON, XML |
| Web & Markup | HTML, CSS, Markdown (.md) |
| Code Files | Python, JavaScript, TypeScript, C/C++ header and source files, SQL, YAML, TOML, Shell scripts, Ruby, Scala, Swift, Kotlin, Lua, PHP, Perl |
| Notebooks | Jupyter Notebooks (.ipynb), Google Colab notebooks |
| Email & Other | Email messages (.eml, RFC822 format), Plain text (.txt), TeXmacs |

## Limitations

* For files exceeding 128MB, Grok only indexes the first 128 MB of content.
* Sync checks hourly. Some recent changes may take up to an hour to appear.
* Only supported file types are indexed and are searchable (see list above)

## Frequently Asked Questions

**1. Why aren't my files appearing?**

Wait up to an hour for sync, or check permissions in Google Drive.

**2. Do I need to connect my personal Drive?**

No, shared files work via admin setup. Connect personal for your private files only.

**3. Can Grok edit files?**

No, read-only access for search and reference.

**4. How do I see which files were used?**

Grok includes citations in responses.

For troubleshooting or white-glove onboarding, please contact xAI support via .


===/grok/faq===
#### FAQ

# FAQ - Grok Website / Apps

While the documentation is mainly meant for our API users, you can find some commonly asked questions here for our consumer-facing website/apps.

## How can I link my X account sign-in/subscription to my xAI account?

On [Grok Website](https://grok.com), go to Settings -> Account. Click on Connect your X Account button. This will take you to X's SSO page to add X account as a sign-in method for xAI.

xAI will be able to retrieve your X subscription status and grant relevant benefits after linking.

You can manage your sign-in methods at https://accounts.x.ai.

## How do I add/remove other sign-in methods or link my X subscription?

You can add/remove your sign-in methods at https://accounts.x.ai. Your account must have at least one sign-in method.

Linking or signing up with X account will automatically link your X account subscription status with xAI, which can be used on https://grok.com.

## I signed-up to Grok / xAI API with my X account, why is xAI still asking for my email?

When you sign up with X, you will be prompted with the following:

As X does not provide the email address, you can have different emails on your X account and xAI account.

## I have issues using X, can I reach out to xAI for help?

While xAI provides the Grok in X service on X.com and X apps, it does not have operational oversight of X's service. You can contact X via their [Help Center](https://help.x.com/) or message [@premium on X](https://x.com/premium).

## How can I delete the account?

Your xAI account can be deleted by following the steps at [xAI Accounts](https://accounts.x.ai/account). If you are using the same account to access our API, your API access will be removed as well.

You can restore your account within 30 days by logging in again and confirming restoration.

## How do I unsubscribe?

If you have subscribed to SuperGrok, you can go to https://grok.com -> Settings -> Billing to manage your subscription (purchased from Grok Website), [Request a refund for app](https://support.apple.com/118223) (purchased from Apple App Store), or [Cancel, pause or change a subscription on Google Play](https://support.google.com/googleplay/answer/7018481) (purchased from Google Play).

If you have subscribed to X Premium, X (not xAI) would be responsible for processing refund where required by law. You can [submit a refund request from X](https://help.x.com/forms/x-refund-request). See more details regarding X Premium subscriptions on [X Help Center](https://help.x.com/using-x/x-premium).


===/grok/faq/team-management===
#### FAQ

# Team Management

## What are teams?

Teams are the level at which xAI tracks API usage, processes billing, and issues invoices.

* If you’re the team creator and don’t need a new team, you can rename your Personal Team and add members instead of creating a new one.
* Each team has **roles**:
  * **Admin**: Can modify team name, billing details, and manage members.
  * **Member**: Cannot make these changes.
  * The team creator is automatically an Admin.

## Which team am I on?

When you sign up for xAI, you’re automatically assigned to a **Personal Team**, which you can view the top bar of [xAI Console](https://console.x.ai).

## How can I manage teams and team members?

### Create a Team

1. Click the dropdown menu in the xAI Console.
2. Select **+ Create Team**.
3. Follow the on-screen instructions. You can edit these details later.

### Rename or Describe a Team

Admins can update the team name and description on the [Settings page](https://console.x.ai/team/default/settings).

### Manage Team Members

Admins can add or remove members by email on the [Users page](https://console.x.ai/team/default/users).

* Assign members as **Admin** or **Member**.
* If a user is removed, their API keys remain with the team.

### Delete a Team

Deleting a team removes its prepaid credits.

To permanently delete a team:

1. Go to the [Settings page](https://console.x.ai/team/default/settings).
2. Follow the instructions under **Delete Team**.

## How to automatically add users to team with my organization's email domain?

Admins can enable automatic team joining for users with a shared email domain:

1. Go to the [Settings page](https://console.x.ai/team/default/settings).
2. Add the domain under **Verified Domains**.
3. Add a `domain-verification` key to your domain’s DNS TXT record to verify ownership.

Users signing up with a verified domain email will automatically join the team.


===/grok/management===
#### Grok Business / Enterprise

# License & User Management

**The Grok Business overview page at [console.x.ai](https://console.x.ai) is your central hub for handling team licenses and user invitations.** As a team admin or user with appropriate permissions, you can buy licenses, invite new members, and manage access to ensure smooth collaboration.

Access this page by logging into [console.x.ai](https://console.x.ai) and navigating to the overview section. Note that actions like purchasing or provisioning require specific permissions—see the [Permissions](#permissions-and-troubleshooting) section for details.

## Purchasing Licenses

Expand your team's capabilities by buying additional licenses directly from the overview page.

Available license types:

* **SuperGrok:** Standard business access with enhanced quotas and features.
* **SuperGrok Heavy:** Upgraded performance for demanding workloads.

To purchase:

1. On the overview page, select the license type and quantity.
2. Enter payment details if prompted <em>(requires billing read-write permissions)</em>.
3. Confirm the purchase—licenses will be added to your available pool for assignment.

Purchased licenses become immediately available for provisioning to users.

&#x20;Ensure your team's billing is set up correctly to avoid
interruptions. Visit [Billing Settings](https://console.x.ai/team/default/billing) for more
details.

## Inviting Users

Invite new team members to join your Grok Business workspace with a simple email invitation process.

To invite:

1. On the overview page, click "Invite users to Grok Business".
2. Enter the users' email addresses.
3. Select a license type to auto-provision upon acceptance <em>(requires team read-write permissions)</em>.
4. Send the invitation—the user will receive an email with a link to activate their account.

Invited users gain access to the team workspace and basic team read permissions. (the latter is to allow for sharing conversations with your team members)

View invited users in the "Pending invitations" list on the overview page. As long as you have unassigned licenses available, they will be automatically provisioned when the user accepts.

## Assigning and Revoking Licenses

Once licenses are purchased or available, assign them to users for full team workspace access.

To assign:

1. From the overview page, select a user from your team list.
2. Choose an available license and assign it—access activates immediately.

To revoke:

1. Click the "..." for the user and choose "Unassign License" from the dropdown.
2. Confirm the action—the license returns to your available pool, and the user's will no longer have access to your team's workspace.

Revocations take effect instantly, so ensure that you communicate changes to affected users.

&#x20;Revoking a license removes team workspace access. Users will
retain personal workspace functionality.

## Canceling Licenses

Reduce your team's commitment by canceling unused licenses.

To cancel:

1. On the overview page, select the license type and quantity to cancel.
2. Submit the cancellation request <em>(requires billing read-write permissions)</em>.

Cancellations may take a few days to process, and eligible refunds will be issued to your billing method. Canceled licenses are removed from your pool once processed.

## Permissions and Troubleshooting

Most management actions require specific role-based permissions:

* **Billing Read-Write:** Needed to purchase or cancel licenses.
* **Team Read-Write:** Needed to invite users or assign/revoke licenses.

These are typically granted only to team admins. If you lack permissions:

* Contact your team admin to request actions like license assignment or purchases.
* Admins can adjust permissions via the overview page's role settings.

If you encounter issues, such as invitations not provisioning due to insufficient licenses, purchase more or revoke unused ones first.

&#x20;For white-glove support, Enterprise upgrades, or permission issues, contact xAI sales at .


===/grok/organization===
#### Grok Business / Enterprise

# Organization Management

**Organizations provide a higher-level governance structure for enterprise customers, encompassing multiple console teams under unified IT controls.** Available only to Enterprise tier subscribers, organizations enable centralized management of users, teams, and security features like SSO.

Access the organization dashboard by visiting [console.x.ai/organization](https://console.x.ai/organization). This page is restricted to organization admins.

&#x20;Organizations are exclusive to the Enterprise tier. Contact xAI
sales to upgrade if needed.

## Understanding Organizations

An organization acts as an overarching entity that groups related console teams, ideal for large enterprises with multiple business units or departments.

Key features:

* **Domain Association:** Link your organization to a specific email domain (e.g., @yourcompany.com). Any user signing up or logging in with an email from this domain is automatically associated with the organization.
* **User Visibility:** Organization admins can view a comprehensive list of all associated users across teams on the `/organization` page.
* **Team Association:** Teams created by organization members are automatically linked to the organization and displayed in the dashboard for oversight.

This structure supports a multi-team architecture, allowing independent Grok Business or API teams while maintaining centralized governance, such as uniform access controls and auditing.

## Viewing Users and Teams

To view users:

1. Navigate to [console.x.ai/organization](https://console.x.ai/organization).
2. Scroll to the "Users" section for a list of all domain-associated users, including their team affiliations and access status.

To view teams:

1. In the same dashboard, access the "Teams" section.
2. Review associated console teams, their members, and high-level usage metrics.

Use these views to ensure compliance, spot inactive accounts, or identify growth needs.

## Setting Up SSO

Secure and streamline logins by integrating Single Sign-On (SSO) with your preferred Identity Provider (IdP).

To configure SSO:

1. On the `/organization` page, click "Configure SSO".
2. Choose your IdP from the supported list (e.g., Okta, Azure AD, Google Workspace).
3. Follow the self-guided, IdP-specific instructions provided—each includes step-by-step setup, metadata exchange, and attribute mapping details.
4. Save your configuration and test SSO to confirm the functionality.

SSO setup is straightforward and tailored to common providers, ensuring quick deployment.

## Activating SSO and User Impact

Once configured, SSO will be activated and enforced organization-wide.

Post-activation:

* Users must log in via SSO on their next access.
* If a user selects "Log in with email" and enters a domain-associated address, (e.g., @yourcompany.com) the system automatically detects it and redirects to your IdP for authentication.
* Non-domain emails (e.g., @differentcompany.com) fall back to standard login methods.

This ensures seamless, secure access without disrupting workflows.

&#x20;Notify your users in advance about the SSO rollout to minimize
support queries.

## Setting up SCIM

Automate user provisioning and deprovisioning by integrating System for Cross-domain Identity Management (SCIM) with your Identity Provider (IdP). Follow these steps to set up SCIM effectively.

### Step 1: Configure Groups in Your IdP

1. On the `/organization` page, click "Setup SCIM".
2. Follow the IdP-specific steps provided to sync your groups.
3. Create as many groups as needed in your IdP—typically named something like `xai-admin`, `xai-supergrok-heavy`, `xai-supergrok`, or whatever fits your organizational structure.
   This step ensures your groups are ready for mapping and synchronization with xAI.

### Step 2: Map Groups to Roles in xAI

Map your IdP groups to the available roles in xAI.

* The out-of-the-box roles include Admin, SuperGrok Heavy, SuperGrok, and Member (the default role assigned to users without any specified group).
* If you require more granular roles beyond these, contact your xAI representative to explore custom setup options—these standard roles are usually sufficient for most organizations.
  This mapping aligns your IdP groups with xAI's role-based access controls.

### Step 3: Map Roles to Teams, Permissions, and Licenses

Assign your mapped roles to appropriate resources.

* Map roles to teams (usually just one primary team, but you may have more).
* Assign any relevant permissions.
* Typically, associate a license with the role.

This step customizes access and entitlements based on your organizational needs.

### Step 4: Preview and Activate SCIM

Before finalizing, review the changes.

* We provide a preview of what your organization will look like after activation.
* Confirm that members are assigned to the correct roles, those roles have the appropriate level of authorization, and the right licenses are applied.
* Once you feel confident everything is correct, click **"Activate"** to make SCIM your default provisioning system.

This verification ensures a smooth transition.

&#x20;SCIM is very disruptive. Users might lose or gain access to resources
they did not have before. Notify your organization that you are undergoing this transition and
**verify everything is correct during the preview stage before proceeding.**

## Need Help?

For assistance with organization setup, SSO troubleshooting, or Enterprise features, contact xAI sales at [x.ai/grok/business/enquire](https://x.ai/grok/business/enquire).


===/grok/user-guide===
#### Grok Business / Enterprise

# Grok.com User Guide

**Grok Business provides dedicated workspaces for personal and team use, with enhanced privacy and sharing controls.** Switch between workspaces to access team-specific features and ensure your conversations are protected under business plan terms.

A team workspace offers:

* Privacy guarantees as outlined in xAI's [terms of service](https://x.ai/legal/terms-of-service-enterprise).
* Full benefits of SuperGrok (or SuperGrok Heavy for upgraded licenses).
* Secure sharing of conversations limited to active team members.

## Workspaces Overview

Grok Business features two types of workspaces:

* **Personal Workspace:** For individual use, available unless disabled by your organization.
* **Team Workspace:** For collaborative work within your team, accessible only with an active license.

To switch between workspaces, use the workspace selector in the bottom left navigation on grok.com. Ensure you are in the correct workspace before starting new conversations.

&#x20;You can only access the team workspace when you have an
active license. If you lack access, contact your team admin.

## Privacy and Benefits

In your team workspace, enjoy enterprise-grade privacy protections as detailed in xAI's [terms of service](https://x.ai/legal/terms-of-service-enterprise). This includes data handling and, for the Enterprise tier, custom retention policies tailored for business use.

Additionally, unlock the full capabilities of SuperGrok, including higher usage quotas and advanced features. If your organization has an upgraded license, you may access SuperGrok Heavy for even more powerful performance.

Some users may not see a personal workspace. This indicates your organization has disabled
personal workspaces via an enterprise license. To enable or disable personal workspaces, reach out
to xAI sales for an Enterprise plan.

## Sharing Conversations

Sharing is restricted to your team for security:

* Share conversations only with team members who have active licenses.
* Share links are only accessible to licensed team members.
* If sent to non-team members or unlicensed team members, the link will not open.

To share a conversation:

1. Open the conversation in your team workspace.
2. Click the share button and select team members.
3. Generate and distribute the secure link.

View all shared conversations in your history at [https://grok.com/history?tab=shared-with-me](https://grok.com/history?tab=shared-with-me).

## Activating Your License

To activate or manage your license:

1. Visit your Grok Business overview at [console.x.ai](https://console.x.ai).
2. Press "Assign license" and select your license type.
3. If you encounter access issues or lack permissions, contact your team admin for assistance.

Once activated, your team workspace will become available on grok.com.

&#x20;For white-glove support and Enterprise features, contact xAI sales at .

