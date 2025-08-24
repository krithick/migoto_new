# simple_token_logger.py
import json
import logging
from datetime import datetime
from typing import Any, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

token_logger = logging.getLogger('azure_tokens')

def log_token_usage(response: Any, operation: str, user_id: Optional[str] = None):
    """
    Simple function to log token usage from Azure OpenAI response
    Works for both chat completions and embeddings
    """
    try:
        if hasattr(response, 'usage') and response.usage:
            usage = response.usage
            
            # Check if it's embeddings (no completion tokens) or chat completion
            is_embedding = not hasattr(usage, 'completion_tokens') or usage.completion_tokens is None
            
            if is_embedding:
                # Embeddings only have prompt_tokens and total_tokens
                log_data = {
                    "timestamp": datetime.now().isoformat(),
                    "operation": operation,
                    "user_id": user_id,
                    "prompt_tokens": usage.prompt_tokens,
                    "total_tokens": usage.total_tokens,
                    "model": getattr(response, 'model', 'unknown'),
                    "type": "embedding"
                }
                
                # Log as JSON for easy parsing later
                token_logger.info(f"TOKEN_USAGE: {json.dumps(log_data)}")
                
                # Console output for embeddings
                print(f"🔤 {operation}: {usage.total_tokens} tokens (embedding)")
                
            else:
                # Chat completion has prompt + completion tokens
                log_data = {
                    "timestamp": datetime.now().isoformat(),
                    "operation": operation,
                    "user_id": user_id,
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens,
                    "model": getattr(response, 'model', 'unknown'),
                    "type": "chat_completion"
                }
                
                # Log as JSON for easy parsing later  
                token_logger.info(f"TOKEN_USAGE: {json.dumps(log_data)}")
                
                # Console output for chat
                print(f"🔢 {operation}: {usage.total_tokens} tokens (prompt: {usage.prompt_tokens}, completion: {usage.completion_tokens})")
            
    except Exception as e:
        print(f"Failed to log tokens: {e}")

def log_embedding_usage(response: Any, operation: str, texts_count: int, user_id: Optional[str] = None):
    """
    Specialized function for embedding usage with additional context
    """
    try:
        log_token_usage(response, operation, user_id)
        
        # Additional embedding-specific info
        print(f"📝 Processed {texts_count} text chunks for embeddings")
        
    except Exception as e:
        print(f"Failed to log embedding usage: {e}")
