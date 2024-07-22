import pytest
from unittest.mock import MagicMock

class MockOpenAI:
    class ChatCompletion:
        @staticmethod
        def create(*args, **kwargs):
            class MockResponse:
                class Choice:
                    def __init__(self):
                        self.message = type('obj', (object,), {'content': 'Mocked summary'})

                choices = [Choice()]

            return MockResponse()

class MockYouTubeTranscriptApi:
    @staticmethod
    def get_transcript(video_id):
        return [{"text": "Mocked transcript"}]

class MockYouTubeBuilder:
    def __init__(self, *args, **kwargs):
        pass

    def videos(self):
        class MockVideos:
            @staticmethod
            def list(*args, **kwargs):
                class MockExecute:
                    @staticmethod
                    def execute():
                        return {
                            'items': [{
                                'snippet': {
                                    'title': 'Mocked Title',
                                    'description': 'Mocked Description',
                                    'channelTitle': 'Mocked Channel',
                                    'channelId': 'MockedChannelId',
                                    'publishedAt': '2023-01-01T00:00:00Z'
                                },
                                'statistics': {
                                    'viewCount': '1000',
                                    'likeCount': '100',
                                    'commentCount': '10'
                                }
                            }]
                        }
                return MockExecute()
        return MockVideos()

@pytest.fixture(autouse=True)
def mock_dependencies(monkeypatch):
    monkeypatch.setattr('youtube_utils.YouTubeTranscriptApi', MockYouTubeTranscriptApi)
    monkeypatch.setattr('youtube_utils.build', MockYouTubeBuilder)

    # Mock os.getenv to return dummy API keys
    def mock_getenv(key, default=None):
        if key == "YOUTUBE_API_KEY":
            return "dummy_youtube_api_key"
        elif key == "OPENAI_API_KEY":
            return "dummy_openai_api_key"
        return default

    monkeypatch.setattr('os.getenv', mock_getenv)

    # Mock OpenAI client initialization
    mock_openai_client = MagicMock()
    mock_openai_client.chat.completions.create.return_value = MockOpenAI.ChatCompletion.create()
    monkeypatch.setattr('openai_utils.get_openai_client', lambda: mock_openai_client)