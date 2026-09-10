import { Link } from 'react-router-dom';
// react-router-dom에서 페이지 이동용 컴포넌트인 Link를 불러옴. Link는 페이지 간 이동을 위한 컴포넌트
// <a> 태그와 유사하지만, 페이지를 새로고침하지 않고 SPA 방식으로 이동 가능. Link 컴포넌트는 to 속성을 사용하여 이동할 경로를 지정.
// SPA(Single Page Application)에서 페이지 이동 시 전체 페이지를 새로고침하지 않고, 필요한 부분만 업데이트하여 빠른 사용자 경험 제공
export default function NotFoundPage() {
    return(
        <div>
            <h2> 404 Not Found </h2>
            <p> 요청하신 페이지를 찾을 수 없습니다.</p>
            <Link to="/">홈으로 이동</Link>
        </div>
    );
}