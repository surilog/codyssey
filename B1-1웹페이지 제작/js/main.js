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