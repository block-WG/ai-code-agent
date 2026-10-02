# 트러블슈팅 기록

> 구현하면서 실제로 겪은 에러와 실수를 **증상 → 원인 → 해결 → 배운 점** 순서로 기록합니다.
> 설계는 `DESIGN.md`, 진행 과정은 `PROGRESS.md`에서 관리합니다.

## 목록

| 번호 | 날짜 | 분류 | 제목 | 키워드 |
|---|---|---|---|---|
| [#001](#001-원격-저장소-주소에-이메일을-넣어-push-실패) | 2026-10-02 | Git | 원격 저장소 주소에 이메일을 넣어 push 실패 | `Repository not found` |
| [#002](#002-이미-등록된-origin을-다시-추가해서-실패) | 2026-10-02 | Git | 이미 등록된 origin을 다시 추가해서 실패 | `remote origin already exists` |
| [#003](#003-공개하지-않을-파일이-첫-커밋에-포함됨) | 2026-10-02 | Git | 공개하지 않을 파일이 첫 커밋에 포함됨 | `git rm --cached`, `commit --amend` |
| [#004](#004-편집기의-저장-안-된-내용이-파일-수정본을-덮어씀) | 2026-10-02 | 편집기 | 편집기의 저장 안 된 내용이 파일 수정본을 덮어씀 | IntelliJ, 동시 수정 |

---

## #001. 원격 저장소 주소에 이메일을 넣어 push 실패

- **날짜**: 2026-10-02
- **분류**: Git / GitHub
- **키워드**: `Repository not found`

### 증상
GitHub에 저장소를 만든 뒤 처음 push 하는 과정에서 실패했다.

```powershell
git remote add origin https://github.com/이메일주소/ai-code-agent.git
git push -u origin main
```

```
remote: Repository not found.
fatal: repository 'https://github.com/이메일주소/ai-code-agent.git/' not found
```

### 원인
저장소 주소의 계정 자리에 GitHub **사용자 이름(username)** 이 아니라 **로그인 이메일**을 넣었다.
GitHub 저장소 주소는 `https://github.com/사용자이름/저장소이름.git` 형식이며, 이메일은 로그인할 때만 쓰인다.
존재하지 않는 주소를 가리키고 있었기 때문에 GitHub가 저장소를 찾지 못했다.

### 해결
이미 등록된 원격 주소를 올바른 주소로 변경한 뒤 다시 push 했다.

```powershell
git remote set-url origin https://github.com/사용자이름/ai-code-agent.git
git remote -v          # 주소가 바뀌었는지 확인
git push -u origin main
```

### 배운 점
- 저장소 주소는 직접 입력하지 말고 GitHub 저장소 페이지의 복사 버튼으로 가져온다.
- `Repository not found`는 저장소가 없을 때뿐 아니라 **주소가 틀렸을 때**, **권한이 없는 계정으로 로그인했을 때**도 같은 메시지로 나온다. 먼저 `git remote -v`로 주소부터 확인한다.

---

## #002. 이미 등록된 origin을 다시 추가해서 실패

- **날짜**: 2026-10-02
- **분류**: Git
- **키워드**: `remote origin already exists`

### 증상
#001의 잘못된 주소를 고치려고 올바른 주소로 `git remote add`를 다시 실행했더니 실패했다.

```powershell
git remote add origin https://github.com/사용자이름/ai-code-agent.git
```

```
error: remote origin already exists.
```

### 원인
`git remote add`는 **새 이름을 등록**하는 명령이다.
`origin`이라는 이름은 #001에서 (잘못된 주소로) 이미 등록되어 있었기 때문에 같은 이름으로 다시 추가할 수 없었다.
주소가 틀렸더라도 등록 자체는 성공한 상태였다.

### 해결
추가(`add`)가 아니라 주소 변경(`set-url`)을 사용했다.

```powershell
git remote set-url origin https://github.com/사용자이름/ai-code-agent.git
git remote -v
```

### 배운 점
| 하려는 일 | 명령 |
|---|---|
| 원격 저장소를 처음 등록 | `git remote add origin 주소` |
| 등록된 주소를 수정 | `git remote set-url origin 주소` |
| 현재 등록 상태 확인 | `git remote -v` |
| 등록을 지우고 다시 시작 | `git remote remove origin` |

---

## #003. 공개하지 않을 파일이 첫 커밋에 포함됨

- **날짜**: 2026-10-02
- **분류**: Git
- **키워드**: `git rm --cached`, `git commit --amend`

### 증상
첫 커밋을 만든 뒤, 공개 저장소에 올리지 않기로 한 개인 메모 파일이 커밋에 들어가 있는 것을 발견했다.
에러 메시지는 없었고, push 하기 전에 커밋에 포함된 파일 목록을 확인하다가 알게 되었다.

```powershell
git ls-tree -r --name-only HEAD   # 커밋에 포함된 파일 목록
```

### 원인
`.gitignore`에 해당 파일을 적지 않은 상태에서 `git add .`을 실행했다.
`git add .`은 `.gitignore`에 없는 모든 파일을 커밋 대상에 올린다.

### 해결
아직 push 하기 전이었으므로, 새 커밋을 추가하지 않고 **첫 커밋 자체를 고쳐 써서** 이력에 남지 않게 했다.

1. `.gitignore`에 제외 규칙을 추가한다.
2. 아래 명령을 실행한다.

```powershell
git rm --cached 파일이름           # git 관리 대상에서만 제외 (실제 파일은 남음)
git add .gitignore
git commit --amend -m "커밋 메시지"  # 직전 커밋을 고쳐 씀
git ls-tree -r --name-only HEAD     # 빠졌는지 확인
```

### 배운 점
- `git rm --cached`는 파일을 지우지 않고 **추적만 해제**한다. `--cached`를 빼면 실제 파일도 삭제된다.
- 파일을 삭제하는 커밋을 새로 추가하면 **이전 커밋에는 파일이 그대로 남는다.** 이력에서 없애려면 커밋 자체를 고쳐야 한다.
- `git commit --amend`는 **push 하기 전**에만 안전하다. 이미 올린 커밋을 고치면 원격과 이력이 어긋난다.
- 공개 저장소에 처음 push 하기 전에는 `git status`와 `git ls-tree`로 올라갈 파일을 반드시 확인한다.

---

## #004. 편집기의 저장 안 된 내용이 파일 수정본을 덮어씀

- **날짜**: 2026-10-02
- **분류**: 편집기 (IntelliJ)
- **키워드**: 동시 수정, 저장 안 된 버퍼

### 증상
`PROGRESS.md`에 추가한 내용이 커밋에 들어가지 않았다.
커밋 후 변경량을 확인하니 수십 줄이 바뀌어야 하는데 한 줄만 바뀌어 있었다.

```powershell
git show --stat HEAD
```

```
 PROGRESS.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

또한 파일 첫 줄에 의도하지 않은 글자(`4e`)가 들어간 채로 이전 커밋에 올라가 있었다.

### 원인
같은 파일이 두 곳에서 동시에 수정되었다.

1. IntelliJ에 `PROGRESS.md`가 열려 있었고, 실수로 입력된 글자가 **저장되지 않은 상태**로 남아 있었다.
2. 그 사이 편집기 밖의 다른 도구가 같은 파일을 디스크에서 수정했다.
3. 이후 IntelliJ에서 저장하면서, IntelliJ가 메모리에 갖고 있던 **예전 내용**이 디스크의 최신 내용을 덮어썼다.

### 해결
1. IntelliJ에서 해당 파일 탭을 닫았다.
2. 빠진 내용을 다시 반영했다.
3. 커밋 전에 변경량이 예상과 맞는지 확인하고 push 했다.

```powershell
git diff --stat      # 커밋 전: 바뀐 줄 수 확인
git show --stat HEAD # 커밋 후: 실제로 들어간 변경 확인
```

### 배운 점
- 편집기 밖에서 파일을 수정할 때는 편집기에서 그 파일을 먼저 저장하고 닫는다.
- 커밋 메시지에 적은 내용이 실제로 들어갔는지는 `git show --stat`으로 확인한다. 메시지와 실제 변경이 다를 수 있다.
- 의도하지 않은 입력을 막으려면 커밋 전에 `git diff`로 변경 내용을 훑어본다.

---

## 작성 양식

새 항목을 추가할 때 아래를 복사해서 사용하고, 맨 위 목록 표에도 한 줄을 추가한다.

```markdown
## #000. 제목

- **날짜**: YYYY-MM-DD
- **분류**: Git / Python / API / DB / 편집기 / 프론트엔드
- **키워드**: 에러 메시지의 핵심 문구

### 증상
무엇을 하다가 어떤 일이 일어났는지. 실행한 명령과 에러 메시지 원문.

### 원인
왜 그런 일이 일어났는지.

### 해결
무엇을 어떻게 해서 해결했는지. 실행한 명령.

### 배운 점
다음에 같은 일을 피하려면 무엇을 해야 하는지.
```
