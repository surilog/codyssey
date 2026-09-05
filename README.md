#  웹 포트폴리오 웹사이트

시맨틱 마크업과 바닐라 자바스크립트를 활용하여 제작한 개인 소개 및 프로젝트 포트폴리오 웹사이트입니다.

##  배포 링크
- **웹사이트 URL**: https://github.com/surilog/codyssey/tree/main/B1-1%EC%9B%B9%ED%8E%98%EC%9D%B4%EC%A7%80%20%EC%A0%9C%EC%9E%91

##  사용 기술 (Tech Stack)
- **HTML5**: 시맨틱 태그 기반의 접근성 고려 마크업
- **CSS3**: Flexbox & Grid 레이아웃, CSS 변수 활용 다크모드, 반응형 미디어 쿼리
- **JavaScript (ES6+)**: DOM 조작, IntersectionObserver 애니메이션, Fetch API 비동기 통신

##  주요 기능
1. **반응형 레이아웃**: 모바일, 태블릿, PC 화면 크기에 맞춘 가변 레이아웃
2. **다크 모드 지원**: 사용자 테마 선택 및 `localStorage`를 활용한 설정 유지
3. **GitHub API 연동**: `async/await` 및 `fetch`를 활용한 최신 프로젝트 저장소 실시간 데이터 로드
4. **부드러운 스크롤 & Top 버튼**: 사용자 경험(UX)을 향상시키는 스크롤 인터랙션

##  트러블슈팅 (Troubleshooting)

### 1. 반응형 레이아웃 깨짐 및 가로 스크롤 발생 문제
![레이아웃 파손 에러 화면](images/error1.png)

* **문제 현상 (Issue)**
  - GitHub Pages 배포 및 브라우저 확인 시, 상단 헤더와 메인 섹션, 푸터가 세로로 적층되지 않고 가로 한 줄로 배치되어 화면 우측으로 길게 늘어나는 현상 발생
  - 모바일 디바이스 접속 시 반응형으로 전환되지 않고 요소들이 찌그러짐

* **원인 분석 (Root Cause)**
  - `index.html` 내부에 `<header>` 태그가 중첩(`Header inside Header`)되어 들어가고, `<nav>` 내비게이션 태그가 중복으로 작성됨
  - 부모 `<header>`의 `position: relative` 기준점 누락으로 인해 모바일 햄버거 메뉴(`nav ul.active`)의 `position: absolute` 설정이 레이아웃 위치를 탈탈 이탈시킴
  - `<head>` 태그 내 반응형 필수 메타 태그인 `<meta name="viewport" content="width=device-width, initial-scale=1.0">` 설정 점검 필요

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
  - GitHub Pages 자동 빌드 과정에서 `fatal: No url found for submodule path 'codyssey' in .gitmodules` 에러 발생하며 빌드 실패

* **원인 분석 (Root Cause)**
  - 프로젝트 하위 폴더 내부에 독립적인 `.git` 숨김 폴더가 남아있어 Git이 이를 일반 폴더가 아닌 **'중첩된 Git 저장소(Embedded Git Repository)'** 및 서브모듈로 인식함

* **해결 방법 (Solution)**
  - PowerShell 터미널을 통해 하위 폴더 내부의 `.git` 폴더 및 깨진 캐시 추적 삭제 후 재푸시
    ```powershell
    # 중첩된 .git 폴더 삭제
    Remove-Item -Recurse -Force codyssey\.git

    # Git 캐시 초기화 및 일반 폴더 재등록
    git rm -r --cached codyssey
    git add .
    git commit -m "fix: convert embedded repo to normal folder"
    git push origin main
    ```