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