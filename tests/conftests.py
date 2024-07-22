import pytest

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
    monkeypatch.setattr('openai_utils.OpenAI', MockOpenAI)
    monkeypatch.setattr('youtube_utils.YouTubeTranscriptApi', MockYouTubeTranscriptApi)
    monkeypatch.setattr('youtube_utils.build', MockYouTubeBuilder)