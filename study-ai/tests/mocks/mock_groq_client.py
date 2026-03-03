"""Mock Groq Client

Provides deterministic LLM responses for testing without API calls.
"""

from unittest.mock import Mock, MagicMock
from mocks.sample_materials import MOCK_LLM_RESPONSES


class MockGroqClient:
    """Mock Groq client that returns predefined responses."""
    
    def __init__(self, response_type="extract_concepts"):
        """
        Initialize mock client.
        
        Args:
            response_type: Type of response to return (extract_concepts, generate_summary, etc.)
        """
        self.response_type = response_type
        self.call_count = 0
        self.chat = MockChat(self)
    
    def set_response_type(self, response_type):
        """Change the response type."""
        self.response_type = response_type
    
    def get_response(self):
        """Get the mock response."""
        self.call_count += 1
        return MOCK_LLM_RESPONSES.get(self.response_type, {}).get("response", "")


class MockChat:
    """Mock chat interface."""
    
    def __init__(self, client):
        self.client = client
        self.completions = MockCompletions(client)


class MockCompletions:
    """Mock completions interface."""
    
    def __init__(self, client):
        self.client = client
    
    def create(self, model=None, messages=None, **kwargs):
        """Mock create method."""
        response_text = self.client.get_response()
        
        # Create mock response object
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = response_text
        
        return mock_response


class MockGroqClientWithErrors(MockGroqClient):
    """Mock Groq client that simulates errors for testing error handling."""
    
    def __init__(self, error_type="rate_limit", fail_count=2):
        """
        Initialize mock client with errors.
        
        Args:
            error_type: Type of error to simulate (rate_limit, timeout, api_error)
            fail_count: Number of times to fail before succeeding
        """
        super().__init__()
        self.error_type = error_type
        self.fail_count = fail_count
        self.attempt_count = 0
    
    def get_response(self):
        """Get response, potentially raising errors."""
        self.attempt_count += 1
        
        if self.attempt_count <= self.fail_count:
            # Simulate error
            if self.error_type == "rate_limit":
                raise Exception("Rate limit exceeded. Please try again later.")
            elif self.error_type == "timeout":
                raise Exception("Request timeout. Please try again.")
            elif self.error_type == "api_error":
                raise Exception("API error occurred.")
        
        # Success after retries
        return super().get_response()


def create_mock_groq_client(response_sequence=None):
    """
    Create a mock Groq client with a sequence of responses.
    
    Args:
        response_sequence: List of response types to return in order
    
    Returns:
        Mock Groq client
    """
    if response_sequence is None:
        response_sequence = ["extract_concepts"]
    
    client = MockGroqClient()
    responses = [MOCK_LLM_RESPONSES[rt]["response"] for rt in response_sequence]
    
    # Create a generator that cycles through responses
    response_iter = iter(responses)
    
    def get_next_response():
        try:
            return next(response_iter)
        except StopIteration:
            # Cycle back to first response
            return responses[0]
    
    # Override get_response to use the sequence
    original_get_response = client.get_response
    client.get_response = get_next_response
    
    return client


# Example usage:
if __name__ == "__main__":
    # Test basic mock
    client = MockGroqClient("extract_concepts")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "Extract concepts"}]
    )
    print("Response:", response.choices[0].message.content[:100])
    
    # Test with errors
    error_client = MockGroqClientWithErrors("rate_limit", fail_count=2)
    try:
        error_client.get_response()  # Should fail
    except Exception as e:
        print(f"Expected error: {e}")
    
    try:
        error_client.get_response()  # Should fail again
    except Exception as e:
        print(f"Expected error: {e}")
    
    # Third attempt should succeed
    success_response = error_client.get_response()
    print(f"Success after retries: {success_response[:50]}")
