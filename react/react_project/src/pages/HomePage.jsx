// src/pages/HomePage.jsx

import { Link } from 'react-router-dom';

export default function HomePage() {
  return (
    <div style={{ textAlign: 'center', padding: '4rem 1rem' }}>
      {/* 📚 로고 아이콘 및 메인 타이틀 */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1rem', marginBottom: '1.5rem' }}>
        <span style={{ fontSize: '3rem' }}>📚</span>
        
        <h1 style={{ 
          fontSize: '2.25rem', 
          fontWeight: '800', 
          color: '#1a1d20', // 
          margin: 0,
          letterSpacing: '-0.02em'
        }}>
          독서 여정을 함께하는 BookHub
        </h1>
      </div>

      {/* 부제목 설명 */}
      <p style={{ fontSize: '1.1rem', color: '#4a5568', lineHeight: '1.6', margin: '0 0 0.5rem 0' }}>
        인상 깊게 읽은 책을 소개하고, 함께 생각을 공유하는 공간입니다.
      </p>
      <p style={{ fontSize: '1.05rem', color: '#718096', margin: '0 0 2.5rem 0' }}>
        나만의 독서 기록을 차곡차곡 쌓아보세요!
      </p>

      {/* 둘러보기 버튼 */}
      <Link 
        to="/items" 
        style={{
          display: 'inline-block',
          padding: '0.85rem 1.75rem',
          backgroundColor: '#b45309', // 따뜻한 브라운/앰버 톤
          color: '#ffffff',
          borderRadius: '8px',
          textDecoration: 'none',
          fontWeight: '700',
          fontSize: '1rem',
          boxShadow: '0 4px 6px rgba(180, 83, 9, 0.2)'
        }}
      >
        등록된 도서 둘러보기 📖
      </Link>
    </div>
  );
}