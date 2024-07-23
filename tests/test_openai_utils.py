import pytest
from unittest.mock import patch, MagicMock
from openai_utils import summarize_text
from .test_helpers import get_mock_youtube_data,mock_openai_summary,  mock_env_api_keys


@pytest.fixture
def mock_youtube_data():
    """
    Fixture providing mock YouTube data.

    This fixture uses the get_mock_youtube_data() function from test_helpers
    to load pre-defined mock data for YouTube transcripts and metadata.

    :return: A dictionary containing mock transcript and metadata for testing.
    """
    return get_mock_youtube_data()


@patch('openai_utils.OpenAI')
def test_summarize_text(mock_openai, mock_youtube_data, mock_openai_summary, mock_env_api_keys):
    """
    Test the summarize_text function from openai_utils.

    This test uses mock objects to replace the actual OpenAI API calls,
    ensuring that the function behaves correctly without making real API requests.
    It verifies that the function correctly processes input data, makes the appropriate
    API call, and returns the expected summary.

    :param mock_openai: Mocked version of the OpenAI class
    :param mock_youtube_data: Fixture providing mock YouTube data
    :param mock_openai_summary: Fixture providing a mock OpenAI-generated summary
    :param mock_env_api_keys: Fixture setting dummy API keys in the environment, autouse=True in test_helpers.py
    """
    # Set up mock for OpenAI client
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_response = MagicMock()
    mock_response.choices[0].message.content = mock_openai_summary
    mock_client.chat.completions.create.return_value = mock_response

    # Test parameters
    max_words = 300
    used_model = "GPT-4o mini"

    # Prepare input data
    full_text = ' '.join(mock_youtube_data['transcript'])
    metadata = mock_youtube_data['metadata']

    # Call the function we're testing
    result = summarize_text(full_text, metadata, max_words, used_model)

    # Assert that the result matches our mock summary
    assert result == mock_openai_summary, "The returned summary does not match the expected mock summary"

    # Verify that our mock functions were called with the correct arguments
    mock_client.chat.completions.create.assert_called_once()

    # Check if the correct model was used
    call_args = mock_client.chat.completions.create.call_args[1]
    assert call_args['model'] == used_model, f"Expected model {used_model}, but got {call_args['model']}"

    # Check if max_tokens is set correctly (rough estimate)
    assert call_args['max_tokens'] == max_words * 4, \
        f"Expected max_tokens to be {max_words * 4}, but got {call_args['max_tokens']}"

    # Verify the content of the messages sent to the OpenAI API
    messages = call_args['messages']
    assert len(messages) == 2, f"Expected 2 messages, but got {len(messages)}"
    assert messages[0]['role'] == 'system', f"Expected first message role to be 'system', but got {messages[0]['role']}"
    assert messages[1]['role'] == 'user', f"Expected second message role to be 'user', but got {messages[1]['role']}"
    assert str(max_words) in messages[0]['content'], f"Expected {max_words} to be in the system message content"
    assert metadata['title'] in messages[1]['content'], "Expected video title to be in the user message content"
    assert full_text in messages[1]['content'], "Expected full transcript text to be in the user message content"


if __name__ == "__main__":
    pytest.main()
