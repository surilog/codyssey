// ==========================================
// 1. DOM 요소 선택 및 이벤트 등록 기본
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  console.log('DOM 로드 완료');

  // ==========================================
  // 2. 다크 모드 토글 기능 (localStorage 연동)
  // ==========================================
  const themeToggleBtn = document.querySelector('#theme-toggle');
  
  // 저장된 테마 불러오기
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    document.documentElement.setAttribute('data-theme', savedTheme);
  }

  // 버튼 클릭 시 테마 전환
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme');
      const targetTheme = currentTheme === 'dark' ? 'light' : 'dark';
      
      document.documentElement.setAttribute('data-theme', targetTheme);
      localStorage.setItem('theme', targetTheme);
    });
  }

  // ==========================================
  // 3. 스크롤에 따른 Top 버튼 표시/숨김
  // ==========================================
  const scrollTopBtn = document.querySelector('#scroll-top');

  window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
      scrollTopBtn?.classList.add('show');
    } else {
      scrollTopBtn?.classList.remove('show');
    }
  });

  scrollTopBtn?.addEventListener('click', () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });

  // ==========================================
  // 4. IntersectionObserver 활용 스크롤 애니메이션
  // ==========================================
  const sections = document.querySelectorAll('section');

  const observerOptions = {
    root: null,
    threshold: 0.15
  };

  const sectionObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target); // 한 번 등장 후 관찰 해제
      }
    });
  }, observerOptions);

  sections.forEach(section => {
    section.classList.add('fade-in');
    sectionObserver.observe(section);
  });
});


// ==========================================
// 4. GitHub API 연동 (async/await & fetch)
// ==========================================
const GITHUB_USERNAME = 'surilog'; // 본인의 GitHub 아이디로 수정하세요.

async function fetchGithubProjects() {
  const projectListContainer = document.querySelector('#project-list');
  if (!projectListContainer) return;

  try {
    // 1. GitHub API 호출 (사용자의 최근 6개 저장소 가져오기)
    // [1. 로딩 중] -> HTML에 작성된 로딩 메시지가 노출되어 있는 상태
    const response = await fetch(`https://api.github.com/users/${GITHUB_USERNAME}/repos?sort=updated&per_page=6`);

    // HTTP 응답 상태 체크
    if (!response.ok) {
      throw new Error(`HTTP 에러 발생! 상태 코드: ${response.status}`);
    }

    const repos = await response.json();

    // 2. 받아온 데이터가 빈 배열인 경우 (빈 상태 처리)
    if (repos.length === 0) {
      projectListContainer.innerHTML = '<p class="empty">공개된 프로젝트 저장소가 없습니다.</p>';
      return;
    }

    // 3. 데이터를 성공적으로 받아온 경우 (카드 생성 및 출력) , HTML 카드로 덮어씌움
    projectListContainer.innerHTML = repos.map(repo => `
      <article class="project-card">
        <h3>${repo.name}</h3>
        <p>${repo.description ? repo.description : '프로젝트 설명이 없습니다.'}</p>
        <div class="repo-info">
          <span>⭐ ${repo.stargazers_count}</span>
          <span>💻 ${repo.language || 'N/A'}</span>
        </div>
        <a href="${repo.html_url}" target="_blank" rel="noopener noreferrer">GitHub 방문하기 →</a>
      </article>
    `).join('');

  } catch (error) {
    // 4. 에러 처리 (네트워크 오류, 잘못된 계정명 등)
    console.error('GitHub API 연동 실패:', error);
    projectListContainer.innerHTML = `
      <div class="error-box">
        <p>프로젝트를 불러오는데 실패했습니다.</p>
        <button type="button" onclick="fetchGithubProjects()">다시 시도</button>
      </div>
    `;
  }
}

// 페이지 로드 시 실행
document.addEventListener('DOMContentLoaded', () => {
  fetchGithubProjects();
});

// 1. 내비게이션 스티키 (스크롤 60px)
const header = document.querySelector('header');
window.addEventListener('scroll', () => {
  if (window.scrollY > 60) {
    header?.classList.add('scrolled');
  } else {
    header?.classList.remove('scrolled');
  }
});

// ==========================================
// Contact 폼 유효성 검사 (이벤트 -> 상태 -> DOM 업데이트)
// ==========================================
const contactForm = document.querySelector('#contact-form');

if (contactForm) {
  contactForm.addEventListener('submit', (e) => {
    e.preventDefault(); // 기본 폼 제출(페이지 새로고침) 방지

    // 1. DOM 요소 가져오기
    const nameInput = document.querySelector('#name');
    const emailInput = document.querySelector('#email');
    const messageInput = document.querySelector('#message');

    const nameError = document.querySelector('#name-error');
    const emailError = document.querySelector('#email-error');
    const messageError = document.querySelector('#message-error');
    const successMsg = document.querySelector('#form-success');

    // 2. 상태(Errors) 객체 정의 (초기화)
    const errors = {
      name: '',
      email: '',
      message: ''
    };

    // 성공 메시지 초기화
    successMsg.textContent = '';

    // 3. 유효성 검사 규칙 (상태 데이터 업데이트)
    // 이름 검증
    if (!nameInput.value.trim()) {
      errors.name = '이름을 입력해 주세요.';
    }

    // 이메일 검증 (정규표현식)
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailInput.value.trim()) {
      errors.email = '이메일을 입력해 주세요.';
    } else if (!emailRegex.test(emailInput.value.trim())) {
      errors.email = '올바른 이메일 형식이 아닙니다. (예: user@domain.com)';
    }

    // 메시지 검증
    if (!messageInput.value.trim()) {
      errors.message = '메시지 내용을 입력해 주세요.';
    }

    // 4. DOM 업데이트 (상태 객체 기반 UI 반영)
    // 이름 UI 업데이트
    nameError.textContent = errors.name;
    nameInput.classList.toggle('invalid', Boolean(errors.name));

    // 이메일 UI 업데이트
    emailError.textContent = errors.email;
    emailInput.classList.toggle('invalid', Boolean(errors.email));

    // 메시지 UI 업데이트
    messageError.textContent = errors.message;
    messageInput.classList.toggle('invalid', Boolean(errors.message));

    // 5. 에러가 하나도 없는 경우 제출 성공 처리
    const isValid = !errors.name && !errors.email && !errors.message;
    
    if (isValid) {
      successMsg.textContent = ' 성공적으로 메시지가 전송되었습니다!';
      contactForm.reset(); // 입력 폼 초기화
    }
  });
}


// ==========================================
// 햄버거 메뉴 토글 (모바일)
// ==========================================
const hamburgerBtn = document.querySelector('#hamburger-btn');
const navMenu = document.querySelector('#nav-menu');

if (hamburgerBtn && navMenu) {
  // 1. 햄버거 버튼 클릭 시 active 클래스 토글
  hamburgerBtn.addEventListener('click', () => {
    navMenu.classList.toggle('active');
  });

  // 2. 모바일 메뉴의 링크를 클릭하면 메뉴창 닫기
  const navLinks = navMenu.querySelectorAll('a');
  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      navMenu.classList.remove('active');
    });
  });
}