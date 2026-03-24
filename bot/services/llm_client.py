"""LLM API client for generating intelligent responses."""

import httpx


class LLMClient:
    """Client for the LLM API (Qwen Code or compatible).
    
    This client handles communication with the LLM service
    for generating contextual responses to user queries.
    """
    
    def __init__(self, api_key: str, base_url: str, model: str):
        """Initialize the LLM client.
        
        Args:
            api_key: The API key for authentication.
            base_url: The base URL of the LLM API (e.g., http://localhost:42005/v1).
            model: The model name to use for completions.
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
    
    async def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate a response using the LLM.
        
        Args:
            prompt: The user's input prompt.
            context: Optional context to include in the generation.
        
        Returns:
            The generated response text.
        """
        system_message = "You are a helpful assistant for a Learning Management System. Help students understand their progress and answer questions about their labs."
        
        if context:
            system_message += f"\n\nContext:\n{context}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": prompt},
                        ],
                        "max_tokens": 500,
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "I couldn't generate a response.")
        except httpx.HTTPError:
            return "Sorry, I'm having trouble connecting to the AI service right now."
    
    async def classify_intent(self, message: str) -> str:
        """Classify the user's intent from their message.
        
        Args:
            message: The user's input message.
        
        Returns:
            The classified intent (e.g., 'scores', 'labs', 'help', 'unknown').
        """
        prompt = f"""Classify this message into one of these intents: scores, labs, help, health, start, unknown.

Message: {message}

Respond with only the intent name."""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._headers,
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 10,
                    },
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                intent = data.get("choices", [{}])[0].get("message", {}).get("content", "unknown").strip().lower()
                return intent if intent in ["scores", "labs", "help", "health", "start"] else "unknown"
        except httpx.HTTPError:
            return "unknown"
