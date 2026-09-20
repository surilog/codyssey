import {Outlet} from 'react-router-dom';
import Header from './Header';
//react-router-dom에서 Outlet을 import합니다. Outlet은 중첩된 라우트의 렌더링 위치를 지정하는 컴포넌트.
// 중첩 라우팅 구조에서 자식 라우트(각 데이터 페이지, 홈 페이지등)이 들어갈 구멍(자리)역할.
//같은 폴더내의 상단바/메뉴 담당인 Header 컴포넌트를 가져옴
export default function Layout() {
    return(
        <div style={{
      minHeight: '100vh',
      backgroundColor: '#faf9f5', // 🎨 밝고 따뜻한 북 카페 감성 배경
      color: '#2d3748',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
    }}>
      {/* 고정 상단 헤더 */}
      <Header />

      {/* 본문 콘텐츠 영역 */}
      <main style={{
        maxWidth: '1080px',
        margin: '0 auto',
        padding: '2rem 1.5rem 4rem 1.5rem'
      }}>
        <Outlet />
      </main>
    </div>
    );
}

/* 모든 페이지에서 공통으로 사용되는 상단 헤더 레이아웃 */