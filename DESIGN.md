# AI 코딩 에이전트 툴 — 프로젝트 개요 및 설계 초안

> 상태: 초안 (v0.2) · 작성일: 2026-09-23 · 수정일: 2026-10-01
> 이 문서는 구현하면서 계속 갱신하는 living doc입니다. Phase가 끝날 때마다 "진행상황" 섹션을 업데이트하세요.
>
> **v0.2 변경 (2026-10-01)**: AI 제공사는 Claude(Anthropic) 유지로 확정. 모델을 `claude-opus-5` → 운영 `claude-opus-5-5` + 개발 `claude-haiku-4-5` 2단 구성으로 변경, 모델·비용 정책(12장)과 결정 이력(13장) 추가.

## 1. 프로젝트 개요

**한 줄 요약**: 내 컴퓨터에서 자연어로 지시하면 파일을 읽고/쓰고 bash 명령을 실행해주는, Claude Code 스타일의 미니 AI 코딩 에이전트를 직접 만든다.

**목적**
- 에이전틱 AI(도구 호출 루프, 승인 게이트, 스트리밍 UI)를 직접 구현해보며 개념을 체득
- 풀스택 경험 (Python 백엔드 + PostgreSQL + React 프론트) 확장
- 완성 후에는 실제로 내 작은 반복 작업(리팩터링 보조, 로그 분석 등)에 써먹는 것도 목표

**비목표 (초기 범위 제외)**
- 멀티유저/인증/권한 관리
- 프로덕션급 배포, 오토스케일링
- 완전 자율 실행 (승인 없이 위험한 작업 자동 수행)

## 2. 핵심 컨셉

사용자가 채팅으로 작업을 지시하면, 에이전트가 스스로 필요한 툴(파일 읽기/쓰기, bash 실행, git 조회)을 호출해가며 작업을 수행하고, 그 과정을 프론트엔드에 실시간 스트리밍으로 보여준다. 파일 쓰기·bash 실행처럼 되돌리기 어려운 작업은 사용자 승인을 받은 뒤에만 실행한다.

```
사용자 지시 (채팅)
    │
    ▼
Backend: 에이전트 루프 (Anthropic Tool Runner)
    │  ├─ 필요시 툴 호출 (read_file / write_file / run_bash / git_diff)
    │  ├─ 위험한 툴은 승인 대기 상태로 멈춤 → 프론트에 승인 요청 이벤트 전송
    │  └─ 결과를 다시 모델에 넣고 다음 턴 진행 (반복)
    │
    ▼
Frontend: 대화 스트림 + 툴 호출 로그 + 승인 모달 실시간 표시
```

## 3. 기술 스택

| 영역 | 선택 | 이유 |
|---|---|---|
| 백엔드 | Python + FastAPI | Anthropic 공식 Python SDK와 궁합 좋음, 비동기 스트리밍(SSE) 처리 용이 |
| AI 연동 | Anthropic SDK + `client.beta.messages.tool_runner`<br>모델: 개발 `claude-haiku-4-5` / 품질확인·완성 `claude-opus-5-5` (12장) | 에이전트 루프를 SDK가 대신 돌려줌 (직접 while문 안 짜도 됨). 툴 사용 안정성이 높아 첫 에이전트 디버깅에 유리 |
| DB | PostgreSQL + SQLAlchemy + Alembic | 요구사항대로 고정. 세션/메시지/툴호출 이력 저장 |
| 프론트엔드 | Next.js (React + TypeScript) + Tailwind | SSE/WebSocket 스트리밍 UI 구현 용이, 컴포넌트 재사용 |
| 실행 격리 | 로컬 서브프로세스로 시작 → 추후 Docker 컨테이너로 격리 검토 | bash 툴의 위험도 때문에 단계적으로 강화 |
| 로컬 개발환경 | Docker Compose (postgres + backend + frontend) | 원클릭 기동 |

## 4. 데이터 모델 초안 (PostgreSQL)

```
sessions
  id (PK), title, created_at

messages
  id (PK), session_id (FK), role ('user'|'assistant'|'system'),
  content (text), created_at

tool_calls
  id (PK), message_id (FK), tool_name, input_json, output_json,
  status ('pending'|'approved'|'denied'|'executed'|'error'),
  requires_approval (bool), created_at, resolved_at
```

## 5. MVP 툴 설계 (4종)

| 툴 | 설명 | 승인 필요 |
|---|---|---|
| `read_file(path)` | 파일 내용 읽기 | 아니오 |
| `write_file(path, content)` | 파일 생성/덮어쓰기 | 예 |
| `run_bash(command)` | 셸 명령 실행 (타임아웃 필수) | 예 |
| `git_status()` / `git_diff()` | 현재 저장소 상태 조회 | 아니오 |

> 초기엔 작업 대상 디렉토리를 프로젝트 루트 하위로 제한(화이트리스트 경로)해서 실수로 엉뚱한 곳을 건드리는 걸 방지.

## 6. 백엔드 API 초안

- `POST /sessions` — 새 세션 생성
- `POST /sessions/{id}/messages` — 사용자 메시지 전송, SSE로 에이전트 응답/툴호출 스트리밍
- `GET /sessions/{id}` — 세션 히스토리 조회
- `POST /tool-calls/{id}/approve` / `POST /tool-calls/{id}/deny` — 승인 대기 중인 툴 호출 처리

## 7. 프론트엔드 화면 초안

- 좌측 사이드바: 세션 목록
- 메인: 채팅 스트림 (사용자 메시지 / 에이전트 응답 / 툴 호출 로그 카드)
- 승인 대기 시: 인라인 카드 또는 모달로 "이 명령을 실행할까요?" + 승인/거부 버튼

## 8. 디렉토리 구조 제안

```
ai-code-agent/
  backend/
    app/
      main.py              # FastAPI 엔트리포인트
      agent/
        tools.py           # 툴 정의 (@beta_tool)
        runner.py          # tool_runner 래핑, 승인 게이트 로직
      db/
        models.py          # SQLAlchemy 모델
        session.py
      api/
        routes_sessions.py
        routes_messages.py
    alembic/
    pyproject.toml
  frontend/
    (Next.js 앱: app/, components/, lib/)
  docker-compose.yml
  DESIGN.md               # 이 문서
  PROGRESS.md             # 진행상황 로그 (Phase별)
```

## 9. 개발 단계 (마일스톤)

- **Phase 0 — 스캐폴딩**: FastAPI/Next.js/Postgres 기본 골격, Claude API "Hello World" 호출 확인
- **Phase 1 — 읽기 전용 에이전트**: `read_file`, `git_status`/`git_diff` 툴만 연결, 승인 없이 자동 실행되는 대화형 에이전트
- **Phase 2 — 쓰기/실행 + 승인 게이트**: `write_file`, `run_bash` 추가, 승인 모달 UI 완성
- **Phase 3 — 영속화 + 스트리밍 완성**: 세션/메시지/툴호출 DB 저장, SSE 스트리밍 UI 다듬기
- **Phase 4 (선택) — 확장**: MCP 서버로 툴 분리, 서브에이전트(멀티에이전트) 실험

## 10. 리스크 / 고려사항

- **보안**: `run_bash`가 로컬 PC에서 임의 명령을 실행할 수 있으므로 화이트리스트 경로·타임아웃·(가능하면) 컨테이너 격리 필수
- **비용**: 개발/디버깅은 `claude-haiku-4-5`, 품질 확인 때만 `claude-opus-5-5`(`effort: low`부터). 예산·한도는 12장 참고
- **무한 루프 과금**: 툴 호출 루프가 끝나지 않으면 호출마다 대화 전체를 다시 보내 비용이 급증 → 최대 반복 횟수 제한 + Console 지출 한도 설정
- **스트리밍 상태관리**: SSE 이벤트 종류(텍스트 델타/툴호출/승인요청/완료)를 프론트에서 일관되게 파싱하는 부분이 은근히 손이 감

## 11. 다음 액션

1. **Claude Console 준비** (platform.claude.com)
   1. **Settings → Workspaces → Create workspace**: 이름 `ai-code-agent`
      - Default 워크스페이스에는 지출 한도를 걸 수 없으므로 전용 워크스페이스를 만든다 (워크스페이스 생성은 조직 관리자만 가능)
   2. 만든 워크스페이스의 **Spend limits** 탭: 월 한도 **$20** + 알림 설정
   3. **Settings → API keys → Create key**
      | 항목 | 값 | 비고 |
      |---|---|---|
      | 이름 | `ai-code-agent-toy` | |
      | 만료 | 사용자 지정 **90일** (또는 30일) | 생성 후 변경 불가. `Never`는 비권장. 만료되면 재발급 |
      | 연결된 계정 | **본인** (개인 키) | 서비스 계정은 공유·CI용 |
      | 범위 | **`ai-code-agent` 워크스페이스** | 이 워크스페이스에서만 동작 |
   4. 키(`sk-ant-...`)는 생성 화면에서 **한 번만** 보이므로 바로 `backend/.env`의 `ANTHROPIC_API_KEY`에 저장. `.env`는 반드시 `.gitignore`에 포함
   5. **Billing**에서 잔액 확인: 무료 크레딧이 있으면 Phase 0은 결제 없이 진행 가능. 없으면 크레딧 충전(최대 $20), **자동 충전(auto-reload) 끄기**
2. Phase 0 스캐폴딩 착수 — DB 생성(`createdb ai_code_agent`) → backend venv + 패키지 설치 → `.env`(키, `DATABASE_URL`) → `claude-haiku-4-5`로 "Hello World" 호출 1회 성공 → git init + `.gitignore`
3. 진행하면서 `PROGRESS.md`에 무엇을 했는지, 막힌 부분은 무엇인지 기록

## 12. 모델·비용 정책

### 12-1. 모델 구성
| 용도 | 모델 ID | 요금 (입력/출력, 100만 토큰) | 언제 |
|---|---|---|---|
| 개발·디버깅 | `claude-haiku-4-5` | $1 / $5 | Phase 0~3에서 루프·툴 연동·UI가 "돌아가는지" 확인할 때 (기본값) |
| 품질 확인·완성 | `claude-opus-5-5` | $4 / $20 | 실제 작업 품질을 볼 때, Phase 완료 시 검증 |

- 모델 ID는 `.env`(예: `AGENT_MODEL`)로 빼서 코드 수정 없이 바꿀 수 있게 한다.
- 요금은 2026-10 기준. 결제 전 Console에서 재확인.

### 12-2. 모델별 설정 차이 (같은 코드로 바꿔 끼울 때 주의)
| 항목 | `claude-haiku-4-5` | `claude-opus-5-5` |
|---|---|---|
| thinking | 기본 꺼짐. 켜려면 `budget_tokens` 방식 | **끌 수 없음**(`disabled` 보내면 400). 항상 adaptive |
| effort (`output_config.effort`) | **지원 안 함 — 보내면 에러** | `low`~`max`, **기본 `medium`**. 개발 중엔 `low` |
| 강제 툴 호출 (`tool_choice: any/tool`) | 가능 | **400 에러** → `auto` + 프롬프트로 유도 |
| 컨텍스트 | 200K | 1M |

→ 모델에 따라 요청 파라미터를 다르게 만드는 함수(예: `build_request_options(model)`)를 한 곳에 두고, 툴 루프 코드는 모델과 무관하게 유지한다.

### 12-3. 예산
- 초기 크레딧 **$20**, 자동 충전 끔 → 다 쓰면 호출이 멈출 뿐 추가 결제 없음
- 예상 (에이전트 작업 1회 = 입력 5만 + 출력 5천 토큰 가정)
  | 모델 | 1회 | $20로 |
  |---|---|---|
  | `claude-haiku-4-5` | 약 $0.075 | 약 260회 |
  | `claude-opus-5-5` | 약 $0.30 | 약 65회 |
- Phase 0~3 전체 예상 $5~20. Console Usage 화면에서 실제 1회 비용을 확인해 이 표를 갱신할 것

### 12-4. 비용 절감 규칙
1. 기본 모델은 Haiku, Opus는 필요할 때만
2. Opus는 `effort: low`부터 시작
3. 툴 루프 최대 반복 횟수 제한 (예: 20회)
4. Phase 3에서 프롬프트 캐싱 적용 (시스템 프롬프트·툴 정의·대화 앞부분 재사용 → 반복 호출 비용 절감, 학습 포인트)

## 13. 결정 이력

| 날짜 | 결정 | 이유 |
|---|---|---|
| 2026-09-23 | AI 코딩 에이전트를 토이 프로젝트로 선정, DB는 PostgreSQL | 요즘 핫한 에이전틱 AI + 풀스택 경험 |
| 2026-09-23 | 사용자가 직접 구현, Claude는 서포트 | 학습 목적 |
| 2026-09-23 | 프로젝트 전용 API 키 분리 발급 | 사용량 추적, 개별 폐기 용이 |
| 2026-10-01 | AI 제공사 **Claude 유지** | 현재 설계(`tool_runner`) 그대로 사용 가능, 툴 사용 안정성. 비교 검토한 대안: OpenAI GPT-5 mini, Mistral Devstral(더 저렴하지만 SDK 교체·루프 직접 구현 필요). 중국계 모델은 제외 |
| 2026-10-01 | 모델 2단 구성: 개발 Haiku 4.5 / 완성 Opus 5.5 | 비용 절감 + 품질 확인 분리 |
| 2026-10-01 | 크레딧 $20, 자동 충전 끔 | 토이 프로젝트 예산 상한 |
| (보류) | 모델 호출부 어댑터 구조(여러 제공사 교체 가능) | 필요해지면 Phase 4에서 검토 |
