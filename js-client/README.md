# EI Harness JavaScript Client

A lightweight JavaScript client for using the MHH EI superprompt with OpenAI's API.

## Features

- **Simple API**: Clean, Promise-based API for easy integration
- **Superprompt Loading**: Automatically loads the MHH EI superprompt
- **Token Counting**: Accurately counts tokens for cost estimation
- **Cost Tracking**: Provides detailed cost estimates for API calls
- **Caching Support**: Leverages OpenAI's API-level caching for cost savings
- **Environment Variables**: Easy configuration via .env file

## Installation

1. Make sure you have Node.js installed (version 18+ recommended)

2. Navigate to the js-client directory:
   ```bash
   cd EI-harness-lite/js-client
   ```

3. Install dependencies:
   ```bash
   npm install
   ```

4. Create a `.env` file with your OpenAI API key:
   ```bash
   cp .env.example .env
   # Then edit .env with your favorite text editor to add your API key
   ```

## Usage

### Basic Example

```javascript
import EIHarness from './index.js';

async function main() {
  // Create a new instance of EIHarness
  const harness = new EIHarness({
    apiKey: 'your-openai-api-key', // Or set in .env file
    modelName: 'gpt-4',            // Optional, defaults to gpt-4
    temperature: 0.7,              // Optional
    maxTokens: 1000,               // Optional
    enableCache: true              // Optional, enables OpenAI's API-level caching
  });
  
  // Initialize the client (loads the superprompt)
  await harness.init();
  
  // Generate a response
  const response = await harness.generate("How would someone feel if their friend forgot their birthday?");
  console.log(response);
  
  // Get usage information
  const usageInfo = harness.getUsageInfo();
  console.log(`Total tokens: ${usageInfo.usage.total_tokens}`);
  console.log(`Estimated cost: $${usageInfo.cost.total_cost.toFixed(6)}`);
}

main();
```

### Running the Example

```bash
node example.js
```

## Configuration

You can configure the client either through the constructor or using environment variables in a `.env` file:

| Constructor Option | Environment Variable | Default | Description |
|--------------------|----------------------|---------|-------------|
| `apiKey`           | `OPENAI_API_KEY`     | -       | Your OpenAI API key (required) |
| `modelName`        | `MODEL_NAME`         | `gpt-4` | The OpenAI model to use |
| `temperature`      | `TEMPERATURE`        | `0.7`   | Controls randomness (0-1) |
| `maxTokens`        | `MAX_TOKENS`         | `1000`  | Maximum tokens in the response |
| `enableCache`      | `ENABLE_CACHE`       | `true`  | Whether to use OpenAI's API-level caching |

## API Reference

### `new EIHarness(config)`

Creates a new instance of the EI Harness client.

**Parameters:**
- `config` (Object, optional): Configuration options

### `async init()`

Initializes the client by loading the superprompt.

**Returns:**
- Promise that resolves to `true` when initialization is complete

### `async generate(userInput)`

Generates a response using the EI superprompt.

**Parameters:**
- `userInput` (String): The user's input message

**Returns:**
- Promise that resolves to the generated response string

### `getUsageInfo()`

Gets usage information for the last request.

**Returns:**
- Object containing token counts, cost estimates, and caching information

## OpenAI API-Level Caching

This client leverages OpenAI's API-level caching feature, which provides a 50% discount on input tokens when the same prompt is used within an hour. This is particularly valuable for the superprompt, which can be quite large.

When caching is enabled (the default):
1. The system generates a deterministic cache ID based on the request parameters
2. OpenAI recognizes identical requests and applies the discount
3. The usage information clearly indicates when caching is being applied

You can disable caching by setting `enableCache: false` in the constructor or `ENABLE_CACHE=false` in the `.env` file.
