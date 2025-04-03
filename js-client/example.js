import EIHarness from './index.js';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

/**
 * Example usage of the EI Harness JavaScript client
 */
async function main() {
  try {
    // Create a new instance of EIHarness
    const harness = new EIHarness({
      // You can override config here or use .env file
      // apiKey: 'your-api-key',
      // modelName: 'gpt-4',
      // temperature: 0.7,
      // maxTokens: 1000,
      // enableCache: true
    });
    
    // Initialize the client (loads the superprompt)
    await harness.init();
    console.log('EI Harness initialized successfully');
    
    // Example user input
    const userInput = "How would someone feel if their friend forgot their birthday?";
    console.log(`\nUser: ${userInput}`);
    
    // Generate a response
    console.log('\nGenerating response...');
    const response = await harness.generate(userInput);
    
    // Display the response
    console.log(`\nAI: ${response}`);
    
    // Get and display usage information
    const usageInfo = harness.getUsageInfo();
    console.log('\nUsage Information:');
    console.log(`Model: ${usageInfo.model}`);
    console.log(`Prompt tokens: ${usageInfo.usage.prompt_tokens}`);
    console.log(`Completion tokens: ${usageInfo.usage.completion_tokens}`);
    console.log(`Total tokens: ${usageInfo.usage.total_tokens}`);
    console.log(`Prompt cost: $${usageInfo.cost.prompt_cost.toFixed(6)}`);
    console.log(`Completion cost: $${usageInfo.cost.completion_cost.toFixed(6)}`);
    console.log(`Total cost: $${usageInfo.cost.total_cost.toFixed(6)}`);
    console.log(`Cached: ${usageInfo.cached}`);
    
  } catch (error) {
    console.error('Error:', error.message);
  }
}

// Run the example
main();
