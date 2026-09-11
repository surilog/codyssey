import { useItems } from '../hooks/useItems.js';//Supabase 통신 및 상태(items,error등)를 한 번에 가져오는 useItems를 불러옴
import Card from '../components/Card';
import Loading from '../components/Loading';
import ErrorState from '../components/ErrorState';
import EmptyState from '../components/EmptyState';
import { Link } from 'react-router-dom'; // 1. Link import 추가!
//공통 UI컴포턴트를 불러옴

export default function ItemListPage() {
    const { items, isLoading, error, refetch } = useItems();
    //1. 로딩 상태
    if (isLoading) return <Loading message="목록 데이터를 불러오는 중..."/>;
// 2. 에러 발생했을 때
    if (error) return <ErrorState message={error} onRetry={refetch}/>;
// 3. 데이터를 성공적으로 받아왔으나 데이터가 0개일 때
    if (items.length === 0) return <EmptyState message="등록된 아이템이 없습니다."/>;

    {/*
    if-return 조건부 렌더링 덕분에, 실제 데이터를 렌더링하는 맨 아래 return문 도달 시점에는 items가 무조건 유효한 배열임이 보장
    따라서 items.map()을 실행할 때 null이나 undefined 에러가 절대 터지지 않음!
        */}
   return (
    <div style={{ maxWidth: '1080px', margin: '0 auto', padding: '2.5rem 1.5rem' }}>
      {/* 타이틀 영역 */}
      <div style={{ marginBottom: '2rem', borderBottom: '2px solid #e9ecef', paddingBottom: '1rem' }}>
        <h2 style={{ fontSize: '1.75rem', fontWeight: '800', color: '#1a1d20', margin: 0 }}>
          📚 추천 도서 목록
          <span style={{ fontSize: '1rem', color: '#6c757d', fontWeight: '500', marginLeft: '0.5rem' }}>
            ({items.length}권의 리뷰)
          </span>
        </h2>
        <p style={{ margin: '0.5rem 0 0 0', color: '#6c757d', fontSize: '0.95rem' }}>
          직접 읽고 엄선한 도서들의 리뷰와 추천 포인트를 확인해 보세요.
        </p>
      </div>

      {/* 그리드 레이아웃 (카드들이 가로로 정렬되도록 gridTemplateColumns 설정) */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', // 카드 폭을 줄여서 한 줄에 여러 개 배치
        gap: '1.75rem'
      }}>
        {items.map((item) => (
          <Link 
            key={item.id} 
            to={`/items/${item.id}`} 
            style={{ textDecoration: 'none', color: 'inherit' }}
          >
            <Card //Card컴포턴트의 Props로 넘겨줌
              id={item.id}
              title={item.title}
              description={item.description}
              category={item.category}
              imageUrl={item.image_url}
            />
          </Link>
        ))}
      </div>
    </div>
  );
}