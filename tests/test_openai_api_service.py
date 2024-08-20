"""
Unit tests for the OpenAIAPIService class.

This module contains tests to ensure the proper functioning of the OpenAIAPIService,
particularly its text summarization capabilities using the OpenAI API.
"""

from typing import Dict, Any
from unittest.mock import Mock

from services.openai_api_service import OpenAIAPIService


def test_summarize_text2(
    mock_youtube_data: Dict[str, Any],
    mock_openai_summary: str,
    mock_env_api_keys: Any,
    mock_openai_client
) -> None:
    """
    Test the summarize_text method of OpenAIAPIService. This test ensures that the OpenAIAPIService correctly calls
    the OpenAI API and processes its response when summarizing text.

    Args:
        mock_youtube_data: A dictionary containing mock YouTube video data,
            including transcript and metadata.
        mock_openai_summary: A string representing the expected summary from OpenAI.
        mock_env_api_keys: A mock object for API key management (not directly used in this test).
        mock_openai_client: Fixture responsible for mocking the OpenAI client
    """

    # Create an instance of OpenAIAPIService with the mock client
    service = OpenAIAPIService(client=mock_openai_client)

    # Set up the mock response
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = mock_openai_summary
    mock_openai_client.chat.completions.create.return_value = mock_response

    # Explanation:
    # Here, we're setting up a mock response that our mock OpenAI client will return. We structure it to match the
    # expected response format from the OpenAI API,  with the 'content' field containing our predefined mock summary.

    # Test parameters
    max_words = 300
    used_model = "gpt-3.5-turbo"

    # Prepare input data
    full_text = " ".join(mock_youtube_data["transcript"])
    metadata = mock_youtube_data["metadata"]

    # Call the method we're testing
    result = service.summarize_text(full_text, metadata, max_words, used_model)

    # Assertions
    assert result == mock_openai_summary

    # Verify that our mock function was called correctly

    # Add more specific assertions about the call parameters
    mock_openai_client.chat.completions.create.assert_called_once()
    call_args = mock_openai_client.chat.completions.create.call_args[1]
    assert call_args['model'] == used_model
    assert call_args['max_tokens'] == max_words * 4
    assert call_args['temperature'] == 0.7
    assert len(call_args['messages']) == 2
    assert call_args['messages'][0]['role'] == 'system'
    assert call_args['messages'][1]['role'] == 'user'
    assert f"Summarize the following YouTube video transcript in ~{max_words} words" in call_args['messages'][0]['content']
    assert "Video metadata:" in call_args['messages'][1]['content']
    assert "Transcript:" in call_args['messages'][1]['content']

    # Explanation of assertions:
    # These assertions verify that the OpenAIAPIService is calling the OpenAI API with the correct parameters,
    # including the right model, token limit, temperature setting, and properly formatted messages containing the
    # system prompt and user input (metadata and transcript).
