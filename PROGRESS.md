# AI 코딩 에이전트 — 진행 과정 및 구현 가이드

> 기획·설계는 `DESIGN.md`, **진행 과정과 실제 구현 방법은 이 문서**에서 관리합니다.
> 작성일: 2026-10-01 · 마지막 갱신: 2026-10-02

---

## 1. 진행 현황 요약

| Phase | 내용 | 상태 |
|---|---|---|
| **Phase 0** | 스캐폴딩 (Console 준비, venv, DB, Hello World, git) | ✅ **완료** (2026-10-02) |
| Phase 1 | 읽기 전용 에이전트 (`read_file`, `git_status`/`git_diff`) | 🔄 **진행 중** (1번 완료, 2번부터 재개) |
| Phase 2 | 쓰기/실행 + 승인 게이트 | ⏳ 대기 |
| Phase 3 | DB 영속화 + SSE 스트리밍 | ⏳ 대기 |
| Phase 4 | 확장 (MCP, 서브에이전트) — 선택 | ⏳ 대기 |

### Phase 1 세부 작업
| # | 작업 | 상태 | 비고 |
|---|---|---|---|
| 1 | 도구 호출 개념 이해 | ✅ 완료 | 2026-10-02 (아래 로그 참고) |
| 2 | 도구 요청 눈으로 확인 | ⏳ **다음 할 일** | 도구 정의를 넣어 1회 호출하고 `tool_use` 블록 출력 (`backend\tool_demo.py`) |
| 3 | 에이전트 루프 직접 작성 | ⏳ 대기 | `stop_reason`으로 분기하는 반복문 + `read_file` 도구 |
| 4 | `tool_runner`로 교체 | ⏳ 대기 | `@beta_tool` + `client.beta.messages.tool_runner` |
| 5 | 안전장치 | ⏳ 대기 | 프로젝트 폴더 밖 경로 차단, 반복 횟수 상한 |
| 6 | `git_status` / `git_diff` 도구 추가 | ⏳ 대기 | |

### Phase 0 세부 단계
| # | 단계 | 상태 | 비고 |
|---|---|---|---|
| 0 | Claude Console 준비 (워크스페이스·한도·키·충전) | ✅ 완료 | 무료 크레딧 없음 → **$5 충전** |
| 1 | backend 폴더 + 가상환경 + 패키지 설치 | ✅ 완료 | 2026-10-01 구조 점검 완료 |
| 2 | `.env` 작성 | ✅ 완료 | 파일 생성 확인 (내용은 미확인 — 키 보호) |
| 3 | PostgreSQL DB 생성 | ✅ 완료 | 2026-10-02 `ai_code_agent` 생성·목록 확인, `.env` 비밀번호 일치 확인 |
| 4 | Claude API Hello World | ✅ 완료 | 2026-10-02 `claude-haiku-4-5`, 입력 9 / 출력 21 토큰 (약 $0.0001) |
| 5 | git 초기화 + `.gitignore` + GitHub 연동 | ✅ 완료 | 2026-10-02 첫 커밋 `65fe340`, `github.com/block-WG/ai-code-agent` push |
| 6 | 이 문서(PROGRESS.md) 갱신 | ✅ 완료 | 이후에도 작업마다 계속 갱신 |

---

## 2. 진행 로그

### 2026-09-23 — 기획
- 토이 프로젝트로 "AI 코딩 에이전트(미니 Claude Code)" 선정, DB는 PostgreSQL
- 진행 방식: 사용자가 직접 구현, Claude는 서포트
- `DESIGN.md` v0.1 작성, 환경 점검 (Python 3.13.9 / Node v24.17.0 / PostgreSQL 18 서비스 실행 중 / Docker 없음)

### 2026-10-01 — 재개 및 Phase 0 착수
- **AI 제공사 결정**: Claude 유지
  - 비교 검토: OpenAI GPT-5 mini, Mistral Devstral (더 저렴하지만 SDK 교체·루프 직접 구현 필요), Gemini Flash (무료 등급은 데이터가 학습에 쓰임). 중국계 모델 제외
- **모델 구성**: 개발 `claude-haiku-4-5` / 품질 확인·완성 `claude-opus-5-5`
- **예산**: 크레딧 충전, 워크스페이스 월 한도 $20, 자동 충전 끔
- `DESIGN.md` v0.2 갱신 (12장 모델·비용 정책, 13장 결정 이력, 11장 Console 준비 절차)
- Console 준비 완료: 무료 크레딧이 없어 **$5 충전**, API 키 발급
- 1~2단계 완료, 구조 점검 결과 정상 (아래 3장)
- 3단계는 사전 점검까지 하고 **다음 세션에서 진행**

### 2026-10-02 — Phase 0 계속
- 3단계 완료: `createdb`로 `ai_code_agent` DB 생성, `psql -l`로 확인, `.env`의 `DATABASE_URL` 비밀번호 일치 확인
- 4단계(Hello World) 착수: `backend\hello.py` 파일 생성 (코드 작성 중)
- **편집기 결정: IntelliJ IDEA Ultimate** (VS Code·Anaconda와 비교 후 선택)
  - 이유: DB 도구·HTTP 클라이언트·디버거·Python 코드 분석 내장 → FastAPI + PostgreSQL + Next.js를 한 창에서 처리
  - 필요 설정: Python 플러그인 설치 → `C:\ai-code-agent` 열기 → 인터프리터를 `backend\.venv\Scripts\python.exe`로 지정
  - 5단계 `.gitignore`에 `.idea/` 추가할 것
- IntelliJ 설정 완료 (Python 플러그인, 인터프리터 `backend\.venv` 연결, `import anthropic` 정상 인식)
- **4단계 완료**: `backend\hello.py` 직접 작성 후 실행 성공
  - 흐름: `load_dotenv()` → `os.environ["AGENT_MODEL"]` → `anthropic.Anthropic()` → `client.messages.create(...)` → `content[0].text` / `usage` 출력
  - 응답: `Hello! 👋 Nice to meet you. How can I help you today?`
  - usage: `input_tokens=9`, `output_tokens=21` → 비용 약 $0.000114 (Haiku 4.5 $1/$5 기준: 9×$0.000001 + 21×$0.000005)
- **5단계 완료**: git 초기화 및 GitHub 연동
  - `.gitignore` 작성 후 `git init` (제외: `.venv/`, `.env`, `__pycache__/`, `node_modules/`, `.idea/`)
  - 이 저장소 전용 git 사용자 설정 (`git config user.name` / `user.email`, 전역 설정과 분리)
  - 첫 커밋 `65fe340` → 브랜치 `main` → `https://github.com/block-WG/ai-code-agent` 에 push
  - 이후 작업 단위마다 `git add .` → `git commit -m "..."` → `git push` 로 이력 관리
- **Phase 0 완료** → 다음은 Phase 1 (읽기 전용 에이전트)
- 문서 추가: `TROUBLESHOOTING.md`(에러 기록), `README.md`(프로젝트 소개)
- **Phase 1 착수 — 1번 작업(도구 호출 개념) 완료**
  - Claude는 도구를 직접 실행하지 못하고 "실행해 달라"는 요청만 한다. 실제 실행은 내 코드가 한다
  - 흐름: 질문 + 도구 정의 전송 → Claude가 `tool_use` 요청 → 내 코드가 실행 → `tool_result`로 회신 → Claude가 최종 답변
  - 응답의 `stop_reason`으로 구분: `tool_use`면 도구 실행 후 다시 호출, `end_turn`이면 종료
  - `tool_use`의 `id`와 `tool_result`의 `tool_use_id`가 같아야 한다 (요청과 결과를 짝짓는 번호)
  - 매 호출마다 대화 전체를 다시 보내므로 반복이 길어지면 비용이 늘어난다 → 반복 횟수 상한 필요
  - 학습 순서 결정: 도구 요청 확인 → 루프 직접 작성 → `tool_runner`로 교체 (내부 동작을 이해한 뒤 SDK 기능 사용)

---

## 3. 현재 환경 스냅샷 (2026-10-02)

### 디렉토리 구조
```
C:\ai-code-agent\
├─ .gitignore                     # git 제외 목록
├─ DESIGN.md                      # 기획·설계
├─ PROGRESS.md                    # 이 문서 (진행 과정·구현 방법)
└─ backend\
   ├─ hello.py                    # Claude API Hello World
   ├─ .venv\                      # 가상환경 (git 제외)
   └─ .env                        # 환경변수 (git 제외)
```

### 개발 도구
| 항목 | 내용 |
|---|---|
| 편집기 | IntelliJ IDEA Ultimate + Python 플러그인 (인터프리터: `backend\.venv`) |
| 저장소 | `https://github.com/block-WG/ai-code-agent` (브랜치 `main`) |

### 설치 패키지 (`backend\.venv`)
| 패키지 | 버전 |
|---|---|
| Python | 3.13.9 |
| anthropic | 1.11.0 (SDK 1.x — 0.x 시절 예제와 일부 다를 수 있음) |
| fastapi | 0.142.2 |
| uvicorn | 0.54.0 |
| SQLAlchemy | 2.1.1 |
| alembic | 1.20.0 |
| psycopg / psycopg-binary | 3.3.6 |
| python-dotenv | 1.2.4 |

### PostgreSQL
| 항목 | 상태 |
|---|---|
| 서비스 `postgresql-x64-18` | 실행 중 |
| 포트 5432 | 리스닝 |
| 도구 | `createdb.exe`, `psql.exe`, pgAdmin 4 설치됨 (`C:\Program Files\PostgreSQL\18\`) |
| `psql` PATH 등록 | 안 됨 → 전체 경로로 실행 |

---

## 4. Phase 0 구현 가이드 (단계별 상세)

### 0단계. Claude Console 준비 ✅
platform.claude.com 에서 진행.

1. **워크스페이스 생성**: Settings → Workspaces → Create workspace → 이름 `ai-code-agent`
   - Default 워크스페이스에는 지출 한도를 걸 수 없기 때문에 전용 워크스페이스를 만든다
2. **지출 한도**: 만든 워크스페이스의 Spend limits 탭 → 월 한도 $20 + 알림
3. **API 키 생성**: Settings → API keys → Create key
   | 항목 | 값 |
   |---|---|
   | 이름 | `ai-code-agent-toy` |
   | 만료 | 사용자 지정 90일 (생성 후 변경 불가, 만료되면 재발급) |
   | 연결된 계정 | 본인 (개인 키) |
   | 범위 | `ai-code-agent` 워크스페이스 |
4. 키(`sk-ant-...`)는 생성 화면에서 **한 번만** 보이므로 바로 `.env`에 저장
5. **Billing**: 잔액 확인 → 무료 크레딧 없음 → $5 충전, 자동 충전(auto-reload) 끔

> 참고: Console(API)은 Pro/Max 구독과 별개의 **선불 크레딧 + 토큰 사용량 과금**입니다.

### 1단계. backend 폴더 + 가상환경 + 패키지 ✅
PowerShell에서:
```powershell
cd C:\ai-code-agent
mkdir backend
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install fastapi uvicorn anthropic sqlalchemy alembic "psycopg[binary]" python-dotenv
```
- `Activate.ps1`이 실행 정책 오류로 막히면 한 번만:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
  ```
- 활성화되면 프롬프트 앞에 `(.venv)`가 붙는다. 이후 작업은 항상 활성화한 상태에서 진행

### 2단계. `.env` 작성 ✅
`.env`는 자동으로 생기지 않으므로 **직접 새로 만든다.**

**만드는 방법**
```powershell
cd C:\ai-code-agent\backend
New-Item .env -ItemType File
notepad .env
```
- 메모장으로 새로 저장할 때는 파일 형식을 **"모든 파일(*.*)"**로 바꿔야 `.env.txt`가 되지 않는다
- 확인: `dir -Force` 결과에 `.env`로 보여야 함

**내용**
```
ANTHROPIC_API_KEY=sk-ant-...발급받은키
AGENT_MODEL=claude-haiku-4-5
DATABASE_URL=postgresql+psycopg://postgres:비밀번호@localhost:5432/ai_code_agent
```

**작성 규칙**
- `=` 앞뒤 공백 없음, 따옴표 없음
- 비밀번호에 `@ : / #` 같은 특수문자가 있으면 URL 인코딩 (`@` → `%40`)
- 키는 이 파일에만 둔다 (채팅·코드·커밋에 넣지 않기)

### 3단계. PostgreSQL DB 생성 ✅

**사전 점검 결과 (2026-10-01)**: 서비스 실행 중, 5432 리스닝, 도구 설치 확인 → 바로 진행 가능

#### 방법 A — PowerShell (추천)
1. `Win` → "PowerShell" → Windows PowerShell 실행 (관리자 권한 불필요, VS Code/Cursor 터미널도 가능)
2. DB 생성:
   ```powershell
   & "C:\Program Files\PostgreSQL\18\bin\createdb.exe" -U postgres -E UTF8 ai_code_agent
   ```
   | 부분 | 의미 |
   |---|---|
   | `&` | 공백 있는 경로의 프로그램 실행 (PowerShell 문법) |
   | `-U postgres` | 관리자 계정으로 접속 |
   | `-E UTF8` | 한글 깨짐 방지 |
   | `ai_code_agent` | DB 이름 (`.env`의 `DATABASE_URL` 끝과 동일해야 함) |
3. `Password:` 에 PostgreSQL 설치 때 정한 `postgres` 비밀번호 입력
   - 입력 중 화면에 아무것도 안 보이는 것이 정상
   - **아무 메시지 없이 다음 줄로 넘어가면 성공**
4. 확인:
   ```powershell
   & "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -l
   ```
   - 목록에 `ai_code_agent`가 있으면 완료 (`:`가 보이면 `q`로 빠져나오기)

#### 방법 B — pgAdmin 4 (화면)
1. `Win` → "pgAdmin 4" 실행
2. Servers → PostgreSQL 18 클릭 → `postgres` 비밀번호 입력
3. Databases 우클릭 → Create → Database...
4. General 탭: Database = `ai_code_agent`, Owner = `postgres`
5. Definition 탭: Encoding = `UTF8` 확인
6. Save → 왼쪽 Databases 아래에 `ai_code_agent`가 보이면 완료

#### 자주 나오는 에러
| 메시지 | 원인·해결 |
|---|---|
| `password authentication failed for user "postgres"` | 비밀번호 오류 (기억 안 나면 재설정 필요) |
| `database "ai_code_agent" already exists` | 이미 있음 → 그대로 다음 단계 |
| `connection refused` / `could not connect` | 서비스 꺼짐 → 서비스 시작 |
| `'&' 연산자...` 구문 오류 | cmd에서 실행함 → cmd에서는 앞의 `& ` 제거 |

#### 마무리 확인
- `.env`의 `DATABASE_URL` 비밀번호가 방금 입력한 `postgres` 비밀번호와 같은지 확인

### 4단계. Claude API Hello World ✅
`backend\hello.py` 같은 파일 하나를 **직접 작성**한다. 구현할 흐름:
1. `dotenv`의 `load_dotenv()`로 `.env` 불러오기
2. `anthropic.Anthropic()`으로 클라이언트 생성 (환경변수 `ANTHROPIC_API_KEY`를 자동으로 읽음)
3. `client.messages.create(...)` 호출
   - `model`: `.env`의 `AGENT_MODEL` (`claude-haiku-4-5`)
   - `max_tokens`: 예) 1024
   - `messages`: `[{"role": "user", "content": "안녕"}]`
4. 응답의 `content[0].text`와 `usage`(입력/출력 토큰 수) 출력 → 1회 비용 감 잡기

**주의**
- Haiku 4.5에는 `effort`(`output_config.effort`)를 넣지 않는다 → 에러 (`DESIGN.md` 12-2)
- 실행은 venv 활성화 상태에서 `python hello.py`

**자주 나오는 에러**
| 증상 | 원인 |
|---|---|
| `401 authentication_error` | 키 오타, `.env`를 못 읽음 (`load_dotenv()` 위치, 실행 폴더 확인) |
| `400 ... credit balance is too low` | 충전 미반영, 키의 워크스페이스·결제 조직 불일치 |
| `404 not_found_error` (model) | 모델 ID 오타 (`claude-haiku-4-5`) |

### 5단계. git 초기화 + `.gitignore` + GitHub 연동 ✅
```powershell
cd C:\ai-code-agent
git init
```
**`git add` 전에 반드시** `C:\ai-code-agent\.gitignore` 먼저 작성:
```
.venv/
.env
__pycache__/
node_modules/
.idea/
```
- 첫 커밋 전에 `git status`로 `.env`가 목록에 **없는지** 확인

**첫 커밋과 GitHub 연결**
```powershell
git add .
git commit -m "Phase 0: 프로젝트 초기 설정 및 Claude API Hello World"
git branch -M main
git remote add origin https://github.com/사용자이름/ai-code-agent.git
git push -u origin main
```
- GitHub에서 저장소를 만들 때 README·.gitignore·license는 추가하지 않는다 (추가하면 push 시 충돌)
- 주소의 `사용자이름` 자리에는 이메일이 아니라 GitHub 사용자 이름을 넣는다
- 주소를 잘못 등록했으면 `git remote add`가 아니라 `git remote set-url origin 주소`로 고친다

### 6단계. 이 문서 갱신
- 각 단계 완료 시 1장 표의 상태와 2장 로그를 갱신
- Hello World 결과의 `usage`(토큰 수)와 Console Usage 화면의 실제 비용을 기록해서 `DESIGN.md` 12-3 예산표 보정에 활용

---

## 5. 다음 세션 시작 시 체크리스트
1. 작업 시작 전 `git pull` (다른 PC에서 올린 내용 받기)
2. IntelliJ에서 프로젝트 폴더 열기 (터미널은 `Alt + F12`)
3. **Phase 1의 2번 작업부터 재개**: 도구 정의를 넣어 1회 호출하고 `tool_use` 블록 확인
4. 작업 단위마다 `git add .` → `git commit` → `git push`
5. 에러를 겪으면 `TROUBLESHOOTING.md`에 기록

### 다른 PC에서 이어서 작업할 때 (처음 한 번)

코드와 문서는 GitHub에서 받고, git에 올리지 않은 것(가상환경, `.env`, 편집기 설정)은 그 PC에서 다시 만든다.

1. **사전 설치 확인**: Python 3.13 이상, Git, IntelliJ IDEA + Python 플러그인
2. **저장소 받기**
   ```powershell
   cd C:\
   git clone https://github.com/block-WG/ai-code-agent.git
   cd ai-code-agent
   ```
3. **이 저장소 전용 git 사용자 설정** (PC마다 따로 해야 함)
   ```powershell
   git config user.name "GitHub사용자이름"
   git config user.email "GitHub계정이메일"
   ```
4. **가상환경과 패키지**
   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install fastapi uvicorn anthropic sqlalchemy alembic "psycopg[binary]" python-dotenv
   ```
5. **`backend\.env` 새로 작성** (4장 2단계 참고)
   - API 키는 GitHub에 없으므로 직접 옮기거나 Console에서 새로 발급한다
   - 키를 메신저·메일·메모 앱으로 보내지 않는다
6. **IntelliJ 인터프리터 지정**: Project Structure → SDKs → `backend\.venv\Scripts\python.exe`
7. **확인**: `python hello.py` 실행 → 응답과 `usage`가 출력되면 준비 완료
8. PostgreSQL은 Phase 3부터 필요하므로 그때 설치한다

이후에는 어느 PC에서든 **시작할 때 `git pull`, 끝낼 때 `git push`** 만 지키면 된다.

---

## 6. 메모 (결정에 참고한 정보)
| 항목 | 내용 |
|---|---|
| 모델 요금 (100만 토큰, 입력/출력) | Haiku 4.5 $1/$5 · Opus 5.5 $4/$20 (2026-10 기준, 결제 전 재확인) |
| 예상 비용 | 에이전트 작업 1회(입력 5만+출력 5천) ≈ Haiku $0.075 / Opus 5.5 $0.30 |
| $5로 가능한 양 | Haiku 기준 에이전트 작업 약 65회, Hello World는 1회 1센트 미만 |
| 비용 안전장치 | 워크스페이스 월 한도 $20, 자동 충전 끔, 툴 루프 최대 반복 횟수 제한(Phase 1~) |
