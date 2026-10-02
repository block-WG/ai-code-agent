# AI Code Agent

자연어로 지시하면 파일을 읽고, 쓰고, 셸 명령을 실행하는 **미니 AI 코딩 에이전트**입니다.
Claude Code 같은 도구가 내부에서 어떻게 동작하는지 이해하기 위해, 에이전트 루프와 승인 게이트를 직접 구현하는 학습 프로젝트입니다.

> **현재 상태**: Phase 0(개발 환경 구성) 완료, Phase 1(읽기 전용 에이전트) 진행 예정

## 만들려는 것

사용자가 채팅으로 작업을 지시하면 에이전트가 필요한 도구를 스스로 골라 호출하고, 그 과정을 화면에 실시간으로 보여줍니다.
파일 쓰기나 명령 실행처럼 되돌리기 어려운 작업은 **사용자가 승인한 뒤에만** 실행합니다.

```
사용자 지시 (채팅)
    │
    ▼
Backend: 에이전트 루프
    │  ├─ 도구 호출 (read_file / write_file / run_bash / git_diff)
    │  ├─ 위험한 도구는 승인 대기 → 화면에 승인 요청
    │  └─ 결과를 모델에 다시 전달하고 다음 단계 진행 (반복)
    ▼
Frontend: 대화 + 도구 호출 로그 + 승인 요청을 실시간 표시
```

### 도구 (계획)

| 도구 | 설명 | 승인 필요 |
|---|---|---|
| `read_file` | 파일 내용 읽기 | 아니오 |
| `git_status` / `git_diff` | 저장소 상태 조회 | 아니오 |
| `write_file` | 파일 생성·덮어쓰기 | 예 |
| `run_bash` | 셸 명령 실행 (타임아웃 적용) | 예 |

## 기술 스택

| 영역 | 사용 기술 |
|---|---|
| 백엔드 | Python 3.13, FastAPI |
| AI | Anthropic SDK (Tool Runner), Claude Haiku 4.5 / Opus 5.5 |
| 데이터베이스 | PostgreSQL 18, SQLAlchemy, Alembic |
| 프론트엔드 | Next.js (TypeScript), Tailwind CSS |

## 진행 상황

| 단계 | 내용 | 상태 |
|---|---|---|
| Phase 0 | 개발 환경 구성, Claude API 첫 호출 | ✅ 완료 |
| Phase 1 | 읽기 전용 에이전트 (`read_file`, `git_status`, `git_diff`) | ⏳ 다음 |
| Phase 2 | 쓰기·실행 도구 + 승인 게이트 | 예정 |
| Phase 3 | 대화·도구 호출 이력 DB 저장, 실시간 스트리밍 화면 | 예정 |
| Phase 4 | 확장 (MCP 서버, 서브에이전트) | 선택 |

## 실행 방법

현재는 Claude API 연결을 확인하는 `backend/hello.py`까지 구현되어 있습니다.

### 준비물
- Python 3.13 이상
- [Claude Console](https://platform.claude.com)에서 발급한 API 키

### 설치

```powershell
git clone https://github.com/block-WG/ai-code-agent.git
cd ai-code-agent\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install fastapi uvicorn anthropic sqlalchemy alembic "psycopg[binary]" python-dotenv
```

### 환경 변수

`backend\.env` 파일을 만들고 아래 내용을 채웁니다. 이 파일은 저장소에 올라가지 않습니다.

```
ANTHROPIC_API_KEY=발급받은_API_키
AGENT_MODEL=claude-haiku-4-5
DATABASE_URL=postgresql+psycopg://postgres:비밀번호@localhost:5432/ai_code_agent
```

### 실행

```powershell
python hello.py
```

Claude의 응답과 토큰 사용량(`input_tokens`, `output_tokens`)이 출력되면 정상입니다.

## 문서

| 문서 | 내용 |
|---|---|
| [DESIGN.md](DESIGN.md) | 설계: 구조, 데이터 모델, API, 단계별 계획, 모델·비용 정책 |
| [PROGRESS.md](PROGRESS.md) | 진행 기록: 날짜별 작업 내용과 단계별 구현 방법 |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | 문제 해결 기록: 겪은 에러의 증상·원인·해결·배운 점 |

## 설계에서 신경 쓴 점

- **승인 게이트**: 읽기 도구는 자동 실행하고, 쓰기·실행 도구는 사용자 승인을 거칩니다.
- **작업 범위 제한**: 에이전트가 접근할 수 있는 경로를 프로젝트 폴더 아래로 제한합니다.
- **비용 통제**: 개발 중에는 저렴한 모델을 쓰고, 도구 호출 반복 횟수에 상한을 둡니다. 모델은 환경 변수로 교체합니다.
