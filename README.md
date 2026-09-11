# 📖 BookHub - 도서 리뷰 및 추천 플랫폼

> **React 18**과 **Supabase**를 활용하여 구현한 SPA(Single Page Application) 기반 도서 리뷰 및 추천 웹 애플리케이션입니다.  
> 사용자는 다양한 책의 리뷰를 둘러보고, 직접 읽은 도서를 등록/수정/삭제하며 관리할 수 있습니다.  
> 컴포넌트 기반 UI 설계, 단방향 데이터 흐름, 비동기 상태 처리(로딩/성공/실패/빈 상태) 및 RLS 기반 보안 권한 제어를 충실하게 구현했습니다.
> **배포 URL**: https://codyssey-ashen.vercel.app/
---
#  로컬 설치 및 실행 방법 (Getting Started)

## 1. 레포지토리 클론 (Clone)

```bash
git clone [https://github.com/사용자계정/레포지토리이름.git](https://github.com/사용자계정/레포지토리이름.git)
cd 레포지토리이름

```

## 2. 의존성 패키지 설치 (Install Dependencies)

```bash
npm install

```

## 3. 환경 변수 설정 (`.env`)

프로젝트 루트 경로에 `.env` 파일을 생성하고 Supabase API 키를 설정합니다.

```env
VITE_SUPABASE_URL=YOUR_SUPABASE_URL
VITE_SUPABASE_ANON_KEY=YOUR_SUPABASE_ANON_KEY

```

## 4. 로컬 개발 서버 실행 (Run Development Server)

```bash
npm run dev

```

실행 후 브라우저에서 `http://localhost:5173`으로 접속합니다.



##  기술 스택 (Tech Stack)

### **Frontend**
- **Framework**: React 18 (Vite)
- **Routing**: React Router v6
- **State Management**: React Context API (전역 인증 상태), Custom Hooks
- **Styling**: Inline Style (Component-based Styling)

### **Backend & Database**
- **Backend Service**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth
- **Security**: Row Level Security (RLS) Policy

### **Deployment**
- **Hosting**: Vercel

---

## 📁 프로젝트 폴더 구조 (Directory Structure)

```text
react_project/
├── node_modules/         # 의존성 패키지 폴더
├── public/               # 정적 리소스 파일
├── src/                  # 소스 코드 메인 디렉토리
│   ├── assets/           # 이미지, 폰트 등 정적 자원
│   ├── components/       # 재사용 가능한 공통 UI 컴포넌트
│   │   ├── Button.jsx        # 공통 버튼
│   │   ├── Card.jsx          # 도서 카드 UI
│   │   ├── EmptyState.jsx    # 빈 데이터 안내 UI
│   │   ├── ErrorState.jsx    # 에러 및 재시도 UI
│   │   ├── Header.jsx        # 상단 네비게이션바
│   │   ├── Layout.jsx        # 공통 레이아웃
│   │   ├── Loading.jsx       # 로딩 스피너 UI
│   │   └── ProtectedRoute.jsx# 비로그인 접근 제한 인가 컴포넌트
│   ├── context/          # 전역 상태 관리
│   │   └── AuthContext.jsx   # 로그인 유저 상태 및 인증 함수
│   ├── hooks/            # 커스텀 훅 (비동기 통신 및 로직 분리)
│   │   ├── useItems.js       # 전체 도서 목록 조회 훅
│   │   └── useItemDetail.js # 도서 상세 단건 조회 훅
│   ├── lib/              # 외부 라이브러리 설정
│   │   └── supabase.js      # Supabase Client 객체 초기화
│   ├── pages/            # 라우트 단위 페이지 컴포넌트
│   │   ├── HomePage.jsx     # 메인 랜딩 페이지
│   │   ├── ItemListPage.jsx # 도서 목록 페이지
│   │   ├── ItemDetailPage.jsx# 도서 상세 페이지
│   │   ├── ItemNewPage.jsx  # 도서 작성 폼 페이지
│   │   ├── ItemEditPage.jsx # 도서 수정 폼 페이지
│   │   ├── LoginPage.jsx    # 로그인 / 회원가입 페이지
│   │   └── NotFoundPage.jsx # 404 예외 처리 페이지
│   ├── App.css           # 앱 전역 컴포넌트 스타일
│   ├── App.jsx           # 최상위 라우터 구성
│   ├── index.css         # 전역 기본 및 메인 스타일 (바탕색, 테마 설정)
│   └── main.jsx          # React 애플리케이션 진입점
├── .env                  # 환경 변수 설정 파일 (Supabase URL/Key)
├── .env.example          # 환경 변수 샘플 예시 파일
├── .gitignore            # Git 버전 관리 제외 파일 목록 (.env 등 포함)
├── eslint.config.js      # ESLint 코드 정적 분석 설정
├── index.html            # HTML 메인 템플릿
├── package-lock.json     # 패키지 의존성 잠금 파일
├── package.json          # 프로젝트 정보 및 의존성 라이브러리 목록
├── README.md             # 프로젝트 기술 문서 및 설명서
└── vite.config.js        # Vite 번들러 및 개발 서버 설정
```

---

## 🔄 애플리케이션 실행 및 데이터 흐름 (Data Flow)

```text
[index.html] (#root)
     │
     ▼
[main.jsx] ── (AuthProvider 전역 주입)
     │
     ▼
  [App.jsx] ── (React Router 주소 매핑 & ProtectedRoute 인가)
     │
     ▼
[Layout.jsx] ── (공통 Header 렌더링 + <Outlet/> 영역에 페이지 매핑)
     │
     ▼
[ItemListPage.jsx] ◄── [useItems.js] ◄── [lib/supabase.js] (비동기 DB 조회)
     │                     └─ (isLoading, error, items 데이터 수령)
     ▼
  [Card.jsx] (Props 형태로 도서 데이터를 하향 전달받아 최종 UI 렌더링)

```

## 애플리케이션 실행 및 데이터 흐름 요약

1. 진입점과 컴포넌트 마운트 (index.html ➔ main.jsx ➔ App.jsx)

브라우저가 index.html을 읽고 main.jsx를 실행합니다

main.jsx가 React 앱을 띄우며 App.jsx를 호출, App.jsx의 라우터가 현재 주소(예: /items)에 맞는 페이지(ItemListPage)와 그 안의 재사용 컴포넌트(Header, Card 등)를 화면에 로드

2. 렌더링 후 비동기 데이터 통신 (useEffect / 커스텀 훅)

컴포넌트들이 화면에 켜지고 난 후, 백그라운드에서 useItems 훅의 useEffect가 동작하여 Supabase DB로 비동기 요청

이때 데이터가 오기 전까지는 <Loading/> 컴포넌트를 먼저 보여줌

3. 데이터 수신 및 하향 전달 (State ➔ Props)

Supabase에서 받아온 모든 컬럼 데이터(제목, 이미지, 카테고리 등)가 items State에 저장!

이 데이터를 자식 컴포넌트인 <Card ... title="{item.title}"/> 형태의 Props로 하향 전달하여 최종 화면을 완성!

4. 데이터 추가/수정/삭제 (State & Event Handler)

사용자가 글을 입력하거나 버튼을 누르면 onChange, handleSubmit 같은 이벤트 핸들러 함수가 실행

핸들러 안에서 formData나 isSubmitting 같은 State를 변경하며, 변경된 State를 바탕으로 React가 화면을 리렌더링하고 DB 업데이트를 처리.

5. 전역 인증 상태 유지 (AuthContext)

로그인/로그아웃 상태, 현재 유저 정보(user)는 페이지를 이동할 때마다 끊기면 안 되므로, 최상단에서 AuthContext가 전역으로 계속 상태를 유지 및 방송하는 역할

덕분에 어느 페이지에 있든 useAuth()만 불러오면 로그인 여부 확인 및 작성자 본인 확인(수정/삭제 버튼 조건부 렌더링)을 수행할 수 있음!


### 2. 세부 데이터 전달 3단계
**① 백엔드 ➔ 프론트엔드 (데이터 조회 흐름)**
사용자 접근: 사용자가 /items 페이지로 이동

커스텀 훅 실행: ItemListPage가 마운트되며 useItems() 커스텀 훅을 호출!

API 통신: useItems 내부의 useEffect가 실행되어 supabase.from('items').select('*')로 Supabase DB에 데이터를 요청

상태 업데이트 & 하향 전달:

수신 전: isLoading = true ➔ ItemListPage가 <Loading/> 컴포넌트를 선언적으로 반환

수신 완료: items State 세팅 ➔ ItemListPage가 .map()을 통해 자식 컴포넌트인 <Card/>에 Props로 데이터를 내려주어 최종 화면을 렌더링

**② 프론트엔드 ➔ 백엔드 (데이터 등록/수정 흐름)**
사용자 입력 (Controlled Input): ItemNewPage에서 폼 입력 시 onChange 이벤트가 발생하여 formData State를 즉시 갱신

폼 제출 (Event): '등록하기' 버튼 클릭 시 handleSubmit 핸들러가 e.preventDefault()로 기본 동작(새로고침)을 차단

제출 중 상태 락 (State Lock): isSubmitting = true로 변경하여 중복 제출을 방지하고 버튼을 비활성화

API 전송: supabase.from('items').insert([formData])를 호출해 원격 DB에 데이터를 저장.

라우팅 이동: 성공 시 navigate('/items')로 목록 페이지로 이동하고, 최신 DB 데이터를 다시 조회하여 화면을 업데이트

**③ 전역 데이터 흐름 (Context API)**
최상위 공급: AuthContext.jsx가 앱 최상단(main.jsx)을 감싸 중앙 상태를 관리

상태 공유 & 인출: 로그인 유저 정보(user)를 관리하며, Header나 ItemDetailPage에서 useAuth() 훅으로 필요한 정보를 인출

권한 기반 렌더링: ItemDetailPage에서 user.id === item.user_id를 검사하여 작성자 본인일 때만 '수정'/'삭제' 버튼을 조건부 렌더링
---

## ✨ 핵심 기능 및 특징

1. **SPA 기반 6개 라우트 구성 (`React Router v6`)**
* 중첩 라우팅(`Layout`/`Outlet`)과 `ProtectedRoute`를 통한 접근 권한 제어 적용.


2. **Supabase 연동 CRUD 및 RLS 데이터 보안**
* 게시글 등록, 조회, 수정, 삭제 기능 구현.
* Supabase RLS 정책과 백엔드 단 `.select()` 검증 기법을 조합하여 본인이 작성한 게시글만 삭제 가능하도록 인가 로직 강화.


3. **일관된 비동기 UX 패턴**
* `Loading`, `ErrorState`, `EmptyState` 공통 UI 컴포넌트를 모듈화하여 비동기 상태(로딩/성공/실패/빈데이터)를 선언적으로 처리.


4. **커스텀 훅(`Custom Hooks`)을 통한 데이터 로직 분리**
* `useItems()`, `useItemDetail()` 커스텀 훅으로 API 통신 로직을 은닉하여 컴포넌트 가독성 증대.


## 🎁 보너스 과제 구현 항목

1. **전역 상태 관리 (`Context API`)**
   - `AuthContext.jsx`를 통해 로그인 사용자 세션 및 인증 함수를 최상단에서 전역 관리.

2. **Supabase Auth 및 보호 라우트 (`ProtectedRoute`)**
   - 로그인/회원가입 흐름 구현.
   - 인가되지 않은 사용자의 접근(`/items/new`, `/items/:id/edit`)을 자동 차단하는 `ProtectedRoute` 적용.

3. **성공적인 성능 최적화 (`React.memo`)**
   - `Card.jsx` 컴포넌트에 `React.memo`를 적용하여 부모 컴포넌트 렌더링 시 전달되는 `props`가 변경되지 않았다면 자식 컴포넌트의 불필요한 리렌더링을 차단.
---

## 🚨 트러블슈팅 (Troubleshooting)

### React 19와 React Router v6 간 호환성 이슈 및 Invalid Hook Call 에러 해결

#### 1. 문제 상황 (Issue)

Vite 기반 React 프로젝트에서 `react-router-dom`을 활용한 라우팅 구조 구축 중 개발 서버 렌더링 시 브라우저 콘솔에 다음과 같은 런타임 에러가 발생하며 앱이 정상 실행되지 않음.

```text
Invalid hook call. Hooks can only be called inside of the body of a function component.
Uncaught TypeError: Cannot read properties of null (reading 'useRef')
An error occurred in the <BrowserRouter> component.

```

#### 2. 원인 분석 (Root Cause)

* **React 19 및 React Router v6 간 내부 참조 이슈**: `npm create vite@latest` 실행 시 최신 스펙인 `React v19.x`가 기본 설치되었으나, `react-router-dom v6` 내부의 `useRef` 및 Hook 인스턴스가 React 19의 내부 Context 구조와 정상적으로 바인딩되지 않음.
* **패키지 참조 오류**: `node_modules` 내부에서 React 모듈 참조가 널(null) 상태로 남아 참조 에러가 발생함.

#### 3. 해결 과정 (Resolution)

1. **의존성 버전 다운그레이드 (`package.json`)**: 가장 안정적이고 호환성이 검증된 **React 18.3.x** 및 **React Router 6.x** 조합으로 교체.
```json
{
  "dependencies": {
    "@supabase/supabase-js": "^2.48.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.28.0"
  }
}

```


2. **`node_modules` 및 Lock 파일 완전 초기화 후 재설치**:
```bash
rmdir /s /q node_modules
del package-lock.json
npm cache clean --force
npm install

```



#### 4. 교훈 및 배운 점 (Key Takeaway)

* 프로젝트 초기화 시 자동 생성되는 라이브러리 버전이 생태계의 기존 보조 라이브러리들과 호환되는지 사전 점검의 필요성을 파악함.
* `Invalid Hook Call` 에러 발생 시 단순 코드 구문 오류 외에도 패키지 버전에 따른 인스턴스 미스매치 가능성을 고려해야 함을 학습함.

---
