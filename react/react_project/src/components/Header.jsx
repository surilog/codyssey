import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Button from './Button';

export default function Header() {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await signOut();
      alert('로그아웃 되었습니다.');
      navigate('/items');
    } catch (err) {
      console.error('로그아웃 실패:', err);
    }
  };

  return (
    <header
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '1rem 0',
        borderBottom: '1px solid #eee',
        marginBottom: '2rem',
      }}
    >
      {/* 1. 좌측 메뉴 (기존 메뉴 유지) */}
      <nav style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
        <Link to="/" style={{ fontWeight: 'bold', textDecoration: 'none', color: '#333' }}>
          📚 BookHub
        </Link>
        <Link to="/items" style={{ textDecoration: 'none', color: '#555' }}>
          📖 도서 목록
        </Link>
        {/* 로그인한 사용자에게만 새 글 작성 메뉴 노출 */}
        {user && (
          <Link to="/items/new" style={{ textDecoration: 'none', color: '#555' }}>
            ✏️ 책 등록하기
          </Link>
        )}
      </nav>

      {/* 2. 우측 로그인 / 회원정보 영역 */}
      <div>
        {user ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
            <span style={{ fontSize: '0.85rem', color: '#666' }}>
              👤 {user.user_metadata?.nickname || user.email}님
            </span>
            <Button variant="secondary" onClick={handleLogout}>
              로그아웃
            </Button>
          </div>
        ) : (
          <Button onClick={() => navigate('/login')}>
            🔑 로그인
          </Button>
        )}
      </div>
    </header>
  );
}