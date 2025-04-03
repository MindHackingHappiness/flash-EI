import { OpenAI } from 'openai';
import dotenv from 'dotenv';
import fs from 'fs/promises';
import axios from 'axios';
import { encoding_for_model } from 'tiktoken';

// Load environment variables
dotenv.config();

// Model pricing information (per 1K tokens)
const MODEL_PRICING = {
  'gpt-4': { input: 0.03, output: 0.06 },
  'gpt-4-turbo': { input: 0.01, output: 0.03 },
  'gpt-3.5-turbo': { input: 0.0015, output: 0.002 }
};

// Default configuration
const DEFAULT_CONFIG = {
  modelName: process.env.MODEL_NAME || 'gpt-4',
  temperature: parseFloat(process.env.TEMPERATURE || '0.7'),
  maxTokens: parseInt(process.env.MAX_TOKENS || '1000', 10),
  enableCache: process.env.ENABLE_CACHE === 'true'
};

/**
 * EI Harness JavaScript Client
 * A lightweight client for using the MHH EI superprompt with OpenAI
 */
class EIHarness {
  constructor(config = {}) {
    // Merge default config with user-provided config
    this.config = { ...DEFAULT_CONFIG, ...config };
    
    // Validate API key
    if (!process.env.OPENAI_API_KEY && !config.apiKey) {
      throw new Error('OpenAI API key is required. Set it in .env file or pass it in the constructor.');
    }
    
    // Initialize OpenAI client
    this.openai = new OpenAI({
      apiKey: config.apiKey || process.env.OPENAI_API_KEY
    });
    
    // Initialize usage tracking
    this.usage = {
      promptTokens: 0,
      completionTokens: 0,
      totalTokens: 0,
      cached: false,
      cost: {
        promptCost: 0,
        completionCost: 0,
        totalCost: 0
      }
    };
    
    // Initialize superprompt
    this.superprompt = null;
    
    // Initialize tokenizer
    this.tokenizer = null;
  }
  
  /**
   * Initialize the client by loading the superprompt
   */
  async init() {
    try {
      // Load the superprompt
      this.superprompt = await this._loadSuperprompt();
      
      // Initialize the tokenizer for the selected model
      this.tokenizer = encoding_for_model(this._getEncodingModel(this.config.modelName));
      
      return true;
    } catch (error) {
      console.error('Error initializing EI Harness:', error);
      throw error;
    }
  }
  
  /**
   * Generate a response using the EI superprompt
   * @param {string} userInput - The user's input message
   * @returns {Promise<string>} - The generated response
   */
  async generate(userInput) {
    if (!this.superprompt) {
      await this.init();
    }
    
    try {
      // Reset usage for this request
      this._resetUsage();
      
      // Prepare the messages
      const messages = [
        { role: 'system', content: this.superprompt },
        { role: 'user', content: userInput }
      ];
      
      // Count tokens in the prompt
      const promptTokens = this._countTokens(this.superprompt + userInput);
      this.usage.promptTokens = promptTokens;
      
      // Generate completion
      const response = await this.openai.chat.completions.create({
        model: this.config.modelName,
        messages: messages,
        temperature: this.config.temperature,
        max_tokens: this.config.maxTokens,
        cache: this.config.enableCache
      });
      
      // Update usage information
      this._updateUsage(response.usage);
      
      // Return the generated text
      return response.choices[0].message.content;
    } catch (error) {
      console.error('Error generating response:', error);
      throw error;
    }
  }
  
  /**
   * Get usage information for the last request
   * @returns {Object} - Usage information
   */
  getUsageInfo() {
    return {
      usage: {
        prompt_tokens: this.usage.promptTokens,
        completion_tokens: this.usage.completionTokens,
        total_tokens: this.usage.totalTokens
      },
      cost: {
        prompt_cost: this.usage.cost.promptCost,
        completion_cost: this.usage.cost.completionCost,
        total_cost: this.usage.cost.totalCost
      },
      cached: this.usage.cached,
      model: this.config.modelName
    };
  }
  
  /**
   * Load the MHH EI superprompt
   * @returns {Promise<string>} - The superprompt text
   */
  async _loadSuperprompt() {
    try {
      // First try to load from local file
      try {
        const localPrompt = await fs.readFile('../mhh-ei-lite/mhh_ei_for_ai_model.md', 'utf8');
        return localPrompt;
      } catch (localError) {
        // If local file not found, fetch from GitHub
        console.log('Local superprompt not found, fetching from GitHub...');
        const response = await axios.get(
          'https://raw.githubusercontent.com/MindHackingHappiness/MHH-EI-for-AI-Language-Enabled-Emotional-Intelligence-and-Theory-of-Mind-Algorithms/main/mhh_ei_for_ai_model.md'
        );
        return response.data;
      }
    } catch (error) {
      console.error('Error loading superprompt:', error);
      throw new Error('Failed to load the EI superprompt');
    }
  }
  
  /**
   * Reset usage tracking for a new request
   */
  _resetUsage() {
    this.usage = {
      promptTokens: 0,
      completionTokens: 0,
      totalTokens: 0,
      cached: false,
      cost: {
        promptCost: 0,
        completionCost: 0,
        totalCost: 0
      }
    };
  }
  
  /**
   * Update usage information based on API response
   * @param {Object} usage - Usage information from OpenAI API
   */
  _updateUsage(usage) {
    // Update token counts
    this.usage.completionTokens = usage.completion_tokens;
    this.usage.totalTokens = usage.total_tokens;
    
    // Check if the request was cached
    this.usage.cached = usage.prompt_tokens < this.usage.promptTokens;
    
    // Calculate costs
    const pricing = MODEL_PRICING[this.config.modelName] || MODEL_PRICING['gpt-3.5-turbo'];
    
    // If cached, apply 50% discount on prompt tokens
    const effectivePromptTokens = this.usage.cached 
      ? this.usage.promptTokens * 0.5 
      : this.usage.promptTokens;
    
    this.usage.cost.promptCost = (effectivePromptTokens / 1000) * pricing.input;
    this.usage.cost.completionCost = (this.usage.completionTokens / 1000) * pricing.output;
    this.usage.cost.totalCost = this.usage.cost.promptCost + this.usage.cost.completionCost;
  }
  
  /**
   * Count tokens in a string
   * @param {string} text - The text to count tokens for
   * @returns {number} - The number of tokens
   */
  _countTokens(text) {
    if (!this.tokenizer) {
      return 0;
    }
    
    const tokens = this.tokenizer.encode(text);
    return tokens.length;
  }
  
  /**
   * Get the encoding model name for tiktoken
   * @param {string} modelName - The OpenAI model name
   * @returns {string} - The encoding model name
   */
  _getEncodingModel(modelName) {
    if (modelName.includes('gpt-4')) {
      return 'gpt-4';
    } else if (modelName.includes('gpt-3.5')) {
      return 'gpt-3.5-turbo';
    } else {
      return 'gpt-3.5-turbo';
    }
  }
}

export default EIHarness;
