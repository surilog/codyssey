# 🌐 웹 포트폴리오 웹사이트

시맨틱 마크업과 바닐라 자바스크립트를 활용하여 제작한 개인 소개 및 프로젝트 포트폴리오 웹사이트입니다. 개발 과정에서의 구조적 설계 의도, 코디세이(Codyssey) 핵심 학습 노트 마지막으로 미약한 웹 보안 지식을 바탕으로 웹 보안 관점의 고려사항을 반영하였습니다.

##  배포 링크

* **웹사이트 URL**: [https://surilog.github.io/codyssey/](https://surilog.github.io/codyssey/)

## 사용 기술 스택 (Tech Stack)

* **HTML5**: 시맨틱 태그 기반의 웹 접근성(Accessibility) 및 SEO 고려 구조 설계
* **CSS3**: Flexbox & Grid 레이아웃, CSS 변수(`:root`, `[data-theme="dark"]`) 다크모드, 반응형 미디어 쿼리
* **JavaScript (ES6+)**: Vanilla JS DOM 조작, IntersectionObserver 스크롤 애니메이션, Contact 폼 유효성 검사, 비동기 데이터 핸들링
* **API / Services**: GitHub REST API 연동 (`fetch` / `async/await`), Formspree (실제 이메일 비동기 전송)

##  주요 화면 스크린샷

| 메인 화면 (다크모드) | 프로젝트 카드 (GitHub API) |
| --- | --- |
| <div style="text-align: center; margin: 20px 0;">
  <img src="{{ '/images/main.jpg' | relative_url }}" 
       alt="메인 화면 (다크모드)" 
       style="max-width: 80%; height: auto; border: 1px solid #ddd; border-radius: 5px;">
  <p style="font-size: 0.9em; color: #666;">[메인 화면 (다크모드)]</p>
</div> |  <img src="{{ '/images/project.jpg' | relative_url }}" 
       alt="프로젝트 카드 (GitHub API) 화면" 
       style="max-width: 80%; height: auto; border: 1px solid #ddd; border-radius: 5px;">
  <p style="font-size: 0.9em; color: #666;">[프로젝트 카드 (GitHub API) 화면]</p>
</div> |

---

##  주요 기능 및 임계값(Threshold) 설정

### 1. 주요 기능

* **반응형 레이아웃**: 모바일, 태블릿, PC 화면 크기에 맞춘 가변 레이아웃 (768px 브레이크포인트)
* **다크 모드 지원**: OS 시스템 설정 감지(`prefers-color-scheme`) 및 수동 토글 버튼 선택 상태 유지(`localStorage`)
* **Hero 타이핑 효과**: `setTimeout`과 문자열 메서드를 활용한 dynamic typing 효과
* **GitHub API 연동 & 언어별 필터링**: `async/await` 및 `Array.prototype.filter()` 기반 프로젝트 동적 카드 렌더링 (로딩/성공/에러/빈 상태 4가지 UI)
* **부드러운 스크롤 & Top 버튼**: UX 향상을 위한 스크롤 인터랙션
* **Contact 폼 및 실제 이메일 전송**: 입력값 정규식 검증 및 Formspree 비동기(`fetch`) 전송

### 2. 임계값(Threshold) 설정 명시

* **스크롤 탑 버튼 노출 기준**: 스크롤 Y축 **`300px`** 이상 이동 시 버튼 노출
* **내비게이션 스티키/배경 변경 기준**: 스크롤 Y축 **`60px`** 이상 이동 시 `.scrolled` 클래스 부여
* **스크롤 애니메이션 (IntersectionObserver)**: 요소 노출 비율 **`threshold: 0.2`** (화면 내 20% 노출 시 Fade-In 동작)

---

##  코디세이(Codyssey) 프론트엔드 핵심 개념 정리 노트

### 1. HTML 기초 및 시맨틱 태그 (Semantic Web)

#### 1-1. HTML 기본 구조 및 역할

* `<!DOCTYPE html>`: 브라우저에게 현재 문서가 HTML5 버전으로 작성되었음을 알림.
* `<html>`: HTML 문서의 시작과 끝을 나타냄.
* `<head>`: 문서에 대한 메타데이터(문자 인코딩, CSS, 타이틀 등)를 포함하며 화면에 직접 보이지 않음.
* `<body>`: 웹 페이지에 실제로 표시되는 본문 콘텐츠 영역.

#### 1-2. 시맨틱 태그 (Semantic Tags)

태그 자체에 의미를 부여하여 브라우저, 개발자, 검색엔진이 문서 구조를 명확히 이해하도록 돕는 태그.

* **시맨틱 태그 사용이 중요한 이유**:
* **SEO (검색엔진 최적화)**: 검색엔진이 웹 페이지의 헤드라인과 상하 관계를 정확히 파악하여 검색 결과 노출에 유리함.
* **Accessibility (접근성)**: 스크린 리더 등 보조 공학 기기가 웹 구조를 정확히 해석하여 시각 장애인 등의 이용을 도움.
* **Maintainability (유지보수성)**: 코드만 보고도 어느 영역이 헤더, 본문, 푸터인지 직관적으로 파악 가능.


* **주요 시맨틱 요소 비교**:
* `<header>`: 웹사이트의 로고, 제목, 검색 창 등을 포함하는 상단 영역.
* `<nav>`: 메뉴, 링크 목록 등 내비게이션 영역.
* `<main>`: 한 페이지 내의 가장 핵심적인 주요 콘텐츠 정의 (페이지당 1개 사용 권장).
* `<article>`: 블로그 포스트, 뉴스 기사처럼 독립적으로 분리하여 재사용 가능한 콘텐츠.
* `<section>`: 연관된 콘텐츠들을 하나로 묶어주는 구역.
* `<aside>`: 광고, 사이드바 등 메인 콘텐츠와 직접적인 연관성이 적은 부가 정보.
* `<footer>`: 저작권 정보, 연락처, 관련 링크 등이 위치하는 하단 영역.



---

### 2. CSS 스타일링 & 박스 모델

#### 2-1. CSS 선택자 및 연결

* **연결 방식**: `<head>` 내에 `<link rel="stylesheet" href="css/style.css">` 태그를 사용하여 외부 CSS 파일 불러오기.

#### 2-2. CSS 박스 모델 (Box Model)

모든 HTML 요소는 상자 형태의 박스 모델을 형성함.

```
+-----------------------------------+
|              Margin               |  <- 요소 외부 여백 (주변 요소와의 간격)
|  +-----------------------------+  |
|  |           Border            |  <- 테두리 (두께, 스타일, 색상)
|  |  +-----------------------+  |  |
|  |  |        Padding        |  |  |  <- 요소 내부 여백 (콘텐츠와 테두리 사이)
|  |  |  +-----------------+  |  |  |
|  |  |  |     Content     |  |  |  |  <- 실제 텍스트나 이미지가 들어가는 영역
|  |  |  +-----------------+  |  |  |
|  |  +-----------------------+  |  |
|  +-----------------------------+  |
+-----------------------------------+

```

#### 2-3. Flexbox vs Grid 레이아웃 비교

| 구분 | Flexbox (1차원) | Grid (2차원) |
| --- | --- | --- |
| **기본 방향** | 가로 또는 세로 한 방향 레이아웃 | 가로와 세로를 동시에 제어 (2D) |
| **주 목적** | 요소들을 한 줄로 정렬하고 여백을 유동적으로 배분 | 전체적인 웹 페이지의 큰 틀과 격자 구조 배치 |
| **주요 특징** | 콘텐츠 크기에 맞춰 유동적 배치 | 정해진 격자(Grid) 틀에 콘텐츠를 맞춤 |

---

### 3. JavaScript 기초 (DOM & 이벤트 제어 원리)

#### 3-1. 자바스크립트 로딩 및 변수 선언 원칙

* **`defer` 속성 사용 이유**: `<script src="..." defer>`를 사용하여 HTML 파싱을 멈추지 않고 스크립트를 다운로드한 뒤, DOM 트리가 완전히 생성된 후 실행되도록 보장하여 DOM 조작 에러를 방지함.(일반적인 `<script>`태그는 스크립트를 만나면 js를 바로 실행)
* **`const` / `let` 사용 권장 (var 금지)**:
* `var`는 함수 스코프 및 호이스팅(Hoisting)으로 인해 변수 재선언과 값의 예측이 어려워 버그를 유발함.
* `let`(재할당 가능)과 `const`(불변 상수, 기본 사용 권장)는 블록 스코프(`{}`)를 지원해 안전하고 예측 가능한 코드를 작성할 수 있음.


* **Inline 이벤트(`onclick`) 배제**: HTML과 JS의 관심사를 분리하고, 하나의 요소에 다중 이벤트를 안전하게 바인딩하며 **XSS 공격 예방 및 CSP 보안 정책 준수**를 위해 `addEventListener`를 강제함.

#### 3-2. DOM 탐색 및 내용 변경 속성 분석 (`textContent` vs `innerHTML`)

* `querySelector()` / `querySelectorAll()`: CSS 선택자 문법(`#id`, `.class`, `tag`)으로 DOM 요소를 탐색함.
* **`textContent`로 내용을 변경하는 이유**:
* **이유**: 문자열 파싱 없이 오직 순수 텍스트만 처리하므로 실행 속도가 빠름.
* **보안 목적**: 외부/사용자 입력 데이터에 `<script>` 태그 등이 포함되어 있어도 단순 문자열로 안전하게 치환하여 **XSS(Cross-Site Scripting) 공격을 차단**함.


* **`innerHTML`로 내용을 변경하는 이유**:
* **이유**: 문자열 내 포함된 HTML 마크업 태그를 브라우저가 실제로 해석해 dynamic DOM 요소 구조를 생성해야 할 때 필요함.
* **활용**: GitHub API 등 동적으로 카드 형태의 HTML 템플릿 구조를 렌더링할 때 활용함.



#### 3-3. `classList` 메서드로 스타일을 제어하는 이유 (`add`, `remove`, `toggle`)

JS에서 `element.style.color = 'red'`처럼 인라인 스타일을 직접 수정하지 않고 `classList`로 제어하는 것은 **관심사의 분리(Separation of Concerns)** 원칙을 위함임 (JS는 상태 제어, CSS는 디자인 전담).

* **`classList.add('className')`**: 특정 조건 만족 시 스타일 상태 부여 (예: 스크롤 60px 이동 시 `.scrolled` 부여, 입력 오류 시 `.error` 추가).
* **`classList.remove('className')`**: 부여했던 스타일 상태 원복 (예: 모바일 메뉴 닫기 시 `.active` 제거).
* **`classList.toggle('className')`**: 클래스의 유무에 따라 On/Off 스위칭 동작을 단 한 줄로 제어 (예: 다크 모드 전환, 햄버거 메뉴 토글).

#### 3-4. 주요 이벤트 처리 및 기본 동작 방지 (`e.preventDefault()`)

* **주요 이벤트 종류**: `click` (버튼 선택), `submit` (폼 데이터 전송), `scroll` (스크롤 감지), `input` (입력값 실시간 변화 감지).
* **`e.preventDefault()`를 사용하는 이유 (기본 동작 차단)**:
* 브라우저가 특정 HTML 태그에 대해 **미리 정해둔 고유의 동작을 취소/방지**하기 위해 사용함.


1. **`<form>` 제출 시**: 기본 동작인 '페이지 전체 새로고침 및 이동'을 막아 자바스크립트의 변수/상태(State) 초기화를 방지함. 새로고침을 차단해야만 JS로 유효성 검사를 진행하고 `fetch` API를 이용해 비동기 메시지 전송(Formspree)을 안전하게 처리할 수 있음.
2. **`<a>` 태그 클릭 시**: `href` 지정 주소로 즉시 이동하는 동작을 차단하고, 자바스크립트로 모달창을 띄우거나 부드러운 스크롤 인터랙션을 직접 구현하기 위해 사용함.
3. **우클릭/드래그 방지**: 브라우저 기본 컨텍스트 메뉴를 끄고 커스텀 메뉴를 구현하거나 콘텐츠 무단 복사를 방지할 때 활용함.



#### 3-5. 스크롤 애니메이션: Intersection Observer

| 구분 | 기존 방식 (`window.addEventListener('scroll')`) | Intersection Observer |
| --- | --- | --- |
| **실행 시점** | 스크롤할 때마다 이벤트가 끊임없이 발생 | 설정한 조건(예: 요소가 20% 보일 때) 충족 시 실행 |
| **성능** | CPU 부하가 높음 (성능 저하 위험) | 비동기 처리로 브라우저 성능 최적화 |
| **위치 계산** | 개발자가 직접 좌표 및 위치 계산 필요 | 브라우저가 자동으로 관찰 및 계산 |

#### 3-6. 다크 모드 구현 방식 비교

| 기능 | `@media (prefers-color-scheme: dark)` | `[data-theme="dark"]` |
| --- | --- | --- |
| **제어권** | OS(시스템) 설정 값을 따름 | 웹사이트 내부 버튼/토글로 제어 |
| **특징** | CSS만으로 구현 가능 | CSS + JavaScript 조합으로 구현 |
| **사용자 경험** | 사용자가 OS 설정을 변경해야만 전환됨 | 웹 내에서 언제든 자유롭게 모드 전환 가능 |

---

### 4. JavaScript 핵심 문법 & 비동기 통신

#### 4-1. 화살표 함수 & 구조 분해 할당

```javascript
// 1) 화살표 함수 (Arrow Function)
const add = (a, b) => a + b;

// 2) 구조 분해 할당 (Destructuring Assignment)
const user = { name: "surilog", language: "python", stars: 123 };
const { name, language } = user;
console.log(name, language); // surilog python

```

#### 4-2. 배열 고차 함수 (map & filter)

```javascript
// map(): 배열 내 모든 요소를 가공하여 새로운 배열 반환
const numbers = [1, 2, 3];
const doubled = numbers.map(num => num * 2); // [2, 4, 6]

// filter(): 조건식에 참(true)인 요소만 걸러내어 새로운 배열 반환
const scores = [45, 80, 95, 60];
const passScores = scores.filter(score => score >= 70); // [80, 95]

```

#### 4-3. 비동기 통신 (`fetch` & `async / await`) 및 `defer` 비교
- **`fetch()`**: 브라우저 내장 API로 지정한 URL로 비동기 HTTP 요청을 보냄.
- **`async / await` 사용 이유 (가독성 & try-catch)**:
  - 기존 `.then()` 체이닝 방식의 콜백 구조를 탈피하여, 비동기 코드를 위에서 아래로 읽히는 **동기식 코드 형태**로 직관적으로 작성 가능.
  - `await`를 통해 비동기 응답 도착 시점까지 코드 실행 순서를 제어하고, `try...catch` 구문으로 동기/비동기 에러 처리를 일관되게 수행.
- **`defer` 속성과의 차이점**:
  - `defer`는 **HTML과 외부 JS 파일의 로딩/실행 시점**을 제어하여 DOM 트리 생성 전 JS가 실행되어 발생하는 에러를 막는 HTML 속성임.
  - `async/await`는 **JS 코드 내부에서 서버 API 호출 등 비동기 요청의 응답 처리 흐름**을 제어하는 자바스크립트 문법임.

---

### 5. 바닐라 JS vs React (Virtual DOM & 랜더링)

#### 5-1. 바닐라 JS vs React 비교

| 비교 항목 | 바닐라 JS (Vanilla JS) | 리액트 (React) |
| --- | --- | --- |
| **개발 방식** | 명령형: DOM을 어떻게 직접 바꿀지 일일이 명령 | 선언형: 상태(State)에 따른 UI를 선언하면 자동 그려짐 |
| **DOM 조작** | 실제 DOM 직접 수정 (`querySelector`, `classList` 등) | 가상 DOM (Virtual DOM) 활용 후 실제 DOM 자동 반영 |
| **상태 변경** | 수동 업데이트 (이벤트 함수 내에서 화면 변경 작성) | `useState`로 상태 변경 시 자동 재렌더링 |
| **장단점** | 가볍고 직관적이나 프로젝트가 커지면 유지보수 어려움 | 상태 중심 관리로 유지보수 유리하나 학습 선행 필요 |

#### 5-2. React의 렌더링 흐름 3단계

1. **Trigger (트리거)**: 상태 변경 함수(`setState`) 호출 등으로 인해 렌더링 요청이 발생함.
2. **Render (렌더링)**: 컴포넌트를 호출하여 새로운 가상 DOM(Virtual DOM)을 생성하고, 이전 가상 DOM과 비교하여 변경된 부분을 탐색함.
3. **Commit (커밋)**: 가상 DOM에서 실제 변경된 최소한의 부분만 실제 DOM에 효율적으로 반영함.

---

##  웹 보안 관점의 과제 요구사항 깊이 보기 (Security Deep Dive)

본 과제의 기본 요구사항 속에는 단순한 기능 구현을 넘어 프론트엔드 보안 표준과 시큐어 코딩(Secure Coding) 원칙이 깊게 반영되어 있습니다.

#### ① Inline 이벤트 금지 및 `addEventListener` 바인딩

* **위협 분석 (XSS & CSP 위반)**: HTML 내 인라인 스크립트(`onclick="javascript:..."`)는 XSS 공격의 주요 통로이며 웹 표준 보안 정책인 CSP(Content Security Policy)의 `unsafe-inline` 규격을 위반함.
* **보안 대책**: 구조와 동작을 분리하고 외부 `.js` 파일에서 `addEventListener`를 사용하여 스크립트 주입 공격 차단.

#### ② `novalidate` 속성 및 JS 정규식 기반 검증

* **위협 분석 (Client-Side Validation Bypass)**: HTML5 기본 검증 속성(`type="email"`, `required`)은 브라우저 개발자 도구(F12)로 쉽게 무력화 가능.
* **보안 대책**: "사용자 입력은 절대 신뢰하지 않는다(Never Trust User Input)"는 대전제 아래, JS 정규식으로 유해 특수문자/스크립트를 1차 필터링(Sanitization)하여 전송. => 블랙 리스트 방식이라고 생각하면 좋음

#### ③ API 연동 시 DOM 파싱 제어 및 HTML Entity Escaping

* **위협 분석 (Stored XSS)**: GitHub API 등 외부에서 받아오는 데이터를 `innerHTML`로 그대로 렌더링할 경우, 저장소 설명에 주입된 악성 스크립트 태그가 실행되어 쿠키/세션이 탈취될 수 있음 (Stored XSS).

* **보안 대책**: 사용자 데이터 삽입 시 `textContent`를 사용하거나 HTML 엔티티(`&lt;`, `&gt;` 등)로 이스케이프 처리하여 단순히 '문자열'로만 인식하도록 처리. 

#### ④ 외부 링크 `rel="noopener noreferrer"` 속성 필수 적용

* **위협 분석 (Tabnabbing / Cross-Origin Hijacking)**:`target="_blank"` 속성으로 새 탭을 열 때 보안 속성이 없으면, 새로 열린 악성 페이지가 자바스크립트의 window.opener 객체 권한을 소유하게 됨.

* 이를 이용해 새 탭에서 몰래 기존에 띄워져 있던 내 포트폴리오 탭의 URL(window.opener.location)을 피싱 사이트로 바꿔치기하는 `탭내빙(Tabnabbing)` 공격에 노출됨.


* **보안 대책**: `rel="noopener"`로 `window.opener` 연결을 끊어 원래 탭의 주소 변경을 차단하고, `noreferrer`로 HTTP Referer 헤더 유출을 막아 세션 및 경로 정보 보안 유지.

---

##  트러블슈팅 (Troubleshooting)

### 1. 반응형 레이아웃 깨짐 및 가로 스크롤 발생 문제

* **문제 현상 (Issue)**
* GitHub Pages 배포 및 브라우저 확인 시, 상단 헤더와 메인 섹션, 푸터가 세로로 적층되지 않고 가로 한 줄로 배치되어 화면 우측으로 길게 늘어나는 현상 발생
* 모바일 디바이스 접속 시 반응형으로 전환되지 않고 요소들이 찌그러짐


* **원인 분석 (Root Cause)**
* `index.html` 내부에 `<header>` 태그가 중첩(`Header inside Header`)되어 들어가고, `<nav>` 내비게이션 태그가 중복으로 작성됨
* 부모 `<header>`의 `position: relative` 기준점 누락으로 인해 모바일 햄버거 메뉴(`nav ul.active`)의 `position: absolute` 설정이 레이아웃 위치를 이탈시킴
* `<head>` 태그 내 반응형 필수 메타 태그인 `<meta name="viewport" content="width=device-width, initial-scale=1.0">` 설정 누락


* **해결 방법 (Solution)**
1. **HTML 구조 정화**: 중첩된 `<header>` 및 중복 내비게이션 항목 삭제
```html
<!-- 구조 단순화 및 단일 헤더 구성 -->
<header>
  <h1><a href="#">Portfolio</a></h1>
  <button id="hamburger-btn" aria-label="메뉴 열기">...</button>
  <nav><ul id="nav-menu">...</ul></nav>
  <button id="theme-toggle">🌓 테마 변경</button>
</header>

```


2. **CSS 레이아웃 수립**: `body` 요소에 `overflow-x: hidden` 속성을 추가하여 가로 스크롤 방지 및 `header`의 `position: sticky`와 `z-index`를 재설정하여 고정 축 형성
3. **반응형 뷰포트 확보**: `<head>` 내 `viewport` 메타 태그 적용으로 기기 폭에 맞춘 반응형 분기점(768px) 정상 동작 완료



---

### 2. GitHub Pages 배포 중 서브모듈(Submodule) / 중첩 Git 에러

* **문제 현상 (Issue)**
* GitHub Pages 자동 빌드 과정에서 `fatal: No url found for submodule path 'codyssey' in .gitmodules` 에러 발생하며 빌드 실패


* **원인 분석 (Root Cause)**
* 프로젝트 하위 폴더 내부에 독립적인 `.git` 숨김 폴더가 남아있어 Git이 이를 일반 폴더가 아닌 **'중첩된 Git 저장소(Embedded Git Repository)'** 및 서브모듈로 인식함


* **해결 방법 (Solution)**
* PowerShell 터미널을 통해 하위 폴더 내부의 `.git` 폴더 및 깨진 캐시 추적 삭제 후 재푸시
```powershell
# 중첩된 .git 폴더 삭제
Remove-Item -Recurse -Force codyssey\.git

# Git 캐시 초기화 및 일반 폴더 재등록
git rm -r --cached codyssey
git add .
git commit -m "fix: convert embedded repo to normal folder"
git push origin main

```