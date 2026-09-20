// src/components/Card.jsx

import { useState, memo } from 'react';

function Card({ title, category, imageUrl, description }) {
  const defaultImage = 'https://placehold.co/150x200?text=No+Cover';
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{
        display: 'flex',
        gap: '1.2rem',
        padding: '1.2rem',
        backgroundColor: '#ffffff',
        borderRadius: '12px',
        border: '1px solid #e9ecef',
        boxShadow: isHovered 
          ? '0 10px 25px -5px rgba(0, 0, 0, 0.08)'
          : '0 2px 4px rgba(0, 0, 0, 0.02)',
        transform: isHovered ? 'translateY(-4px)' : 'translateY(0)',
        transition: 'all 0.2s ease-in-out',
        cursor: 'pointer',
        height: '100%',
        boxSizing: 'border-box'
      }}
    >
      {/* 🖼️ 도서 표지 */}
      <div style={{ flexShrink: 0 }}>
        <img
          src={imageUrl || defaultImage}
          alt={title}
          style={{
            width: '95px',
            height: '135px',
            objectFit: 'cover',
            borderRadius: '6px',
            boxShadow: '0 4px 10px rgba(0, 0, 0, 0.15)',
          }}
        />
      </div>

      {/* 📄 도서 정보 */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        <div>
          <span style={{
            display: 'inline-block',
            fontSize: '0.75rem',
            fontWeight: '700',
            color: '#d97706',
            backgroundColor: '#fef3c7',
            padding: '0.2rem 0.6rem',
            borderRadius: '4px',
            marginBottom: '0.4rem'
          }}>
            {category || '도서 리뷰'}
          </span>

          <h3 style={{
            margin: '0 0 0.4rem 0',
            fontSize: '1.05rem',
            fontWeight: '700',
            color: '#1f2937',
            lineHeight: '1.4'
          }}>
            {title}
          </h3>

          <p style={{
            margin: 0,
            fontSize: '0.85rem',
            color: '#6b7280',
            lineHeight: '1.5',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            overflow: 'hidden'
          }}>
            {description}
          </p>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
          <span style={{ fontSize: '0.8rem', color: isHovered ? '#d97706' : '#9ca3af', fontWeight: '600' }}>
            리뷰 보기 →
          </span>
        </div>
      </div>
    </div>
  );
}

//  핵심: memo()로 컴포넌트를 감싸서 내보내야 성능 최적화(React.memo)가 정상적으로 동작합니다!
export default memo(Card);