//추가 과제 Hero 타이핑 효과
const typingText = document.querySelector('#typing-text');
const textToType = "환영합니다! 보안과 웹 기술을 공부하는 개발자 공간입니다.";
let index = 0;

function typeEffect() {
  if (typingText && index < textToType.length) {
    typingText.textContent += textToType.charAt(index);
    index++;
    setTimeout(typeEffect, 80); // 속도 조절 (80ms)
  }
}
typeEffect();

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
    threshold: 0.2
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
// 4. GitHub API 연동 (async/await & fetch) js/main.js (API 연동 + filter() 함수 작성)
// ==========================================
const GITHUB_USERNAME = 'surilog'; // 본인의 GitHub 아이디로 수정하세요.

let allProjects = []; // API로 원본 데이터를 받아올 전역 배열

async function fetchGitHubRepos() {
  const projectList = document.querySelector('#project-list');
  try {
    const response = await fetch(`https://api.github.com/users/surilog/repos`);
    if (!response.ok) throw new Error('불러오기 실패');
    
    allProjects = await response.json(); // 원본 데이터 저장
    renderProjects(allProjects); // 전체 카드 렌더링
  } catch (err) {
    projectList.innerHTML = `<p class="error-box">데이터를 불러오지 못했습니다.</p>`;
  }
}

// 프로젝트 카드 렌더링 함수
function renderProjects(projects) {
  const projectList = document.querySelector('#project-list');
  
  if (projects.length === 0) {
    projectList.innerHTML = `<p class="empty">해당 언어의 프로젝트가 없습니다.</p>`;
    return;
  }

  projectList.innerHTML = projects.map(repo => `
    <div class="project-card">
      <h3>${repo.name}</h3>
      <div class="repo-info">
        <span>⭐ ${repo.stargazers_count}</span>
        <span>💻 ${repo.language || 'N/A'}</span>
      </div>
      <a href="${repo.html_url}" target="_blank" rel="noopener noreferrer">GitHub 방문하기 →</a>
    </div>
  `).join('');
}

// 필터링 버튼 클릭 이벤트 처리 (Array.prototype.filter 사용)
const filterButtons = document.querySelectorAll('.filter-btn');
filterButtons.forEach(btn => {
  btn.addEventListener('click', (e) => {
    filterButtons.forEach(b => b.classList.remove('active'));
    e.target.classList.add('active');

    const selectedLang = e.target.dataset.lang;

    if (selectedLang === 'all') {
      renderProjects(allProjects);
    } else {
      // array.filter() 핵심 사용 구문
      const filtered = allProjects.filter(repo => repo.language === selectedLang);
      renderProjects(filtered);
    }
  });
});

fetchGitHubRepos();

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
    e.preventDefault(); // 기본 페이지 새로고침 방지

    // 1. 유효성 검사 로직 (기존 작성 코드 유지)
    const nameInput = document.querySelector('#name');
    const emailInput = document.querySelector('#email');
    const messageInput = document.querySelector('#message');
    const successMsg = document.querySelector('#form-success');

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    let isValid = true;

    // 간단한 유효성 체크 예시
    if (!nameInput.value.trim() || !emailRegex.test(emailInput.value.trim()) || !messageInput.value.trim()) {
      isValid = false;
    }

    // 2. 유효성 검사 성공 시 실제 메일 전송 (Formspree 비동기 요청)
    if (isValid) {
      // 로딩 상태 표시
      successMsg.style.color = '#0066cc';
      successMsg.textContent = '메일을 전송 중입니다...';

      // 폼 데이터 객체 생성
      const formData = new FormData(contactForm);

      // Fetch API를 활용한 HTTP POST 요청
      fetch(contactForm.action, {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json' // Formspree에 JSON 응답을 요청
        }
      })
      .then(response => {
        if (response.ok) {
          // 전송 성공 UI 업데이트
          successMsg.style.color = '#52c41a';
          successMsg.textContent = '🎉 성공적으로 메시지가 실제 이메일로 전송되었습니다!';
          contactForm.reset(); // 입력 폼 초기화
        } else {
          // 서버 응답 에러 처리
          throw new Error('전송 실패');
        }
      })
      .catch(error => {
        // 네트워크 또는 에러 발생 시 UI 업데이트
        successMsg.style.color = '#ff4d4f';
        successMsg.textContent = '메일 전송 중 오류가 발생했습니다. 다시 시도해 주세요.';
      });
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