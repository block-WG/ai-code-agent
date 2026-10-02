# 1) 필요한 도구 가져오기
import os
import anthropic
from dotenv import load_dotenv

# 2) .env 파일 내용을 환경변수로 불러오기
load_dotenv()

# 3) .env에 적어둔 모델 이름 읽기
model = os.environ["AGENT_MODEL"]

# 4) Claude 클라이언트 만들기 (API 키는 환경변수에서 자동으로 읽습니다)
client = anthropic.Anthropic()

# 5) Claude에게 메시지 보내기
response = client.messages.create(
    model=model,
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello World"}],
)

# 6) 결과 출력
print(response.content[0].text)
print(response.usage)