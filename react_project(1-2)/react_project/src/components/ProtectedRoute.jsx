/*
비로그인 사용자가 주소창에 /items/new나 /items/1/edit를 직접 입력해서 접근할 때 로그인 페이지로 가로채는 보호 장치
즉, 보호 라우터 컴포넌트임
*/

import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Loading from './Loading';

export default function ProtectedRoute({ children }){
  const { user, isLoading } = useAuth();

  if (isLoading) return <Loading message="인증 상태 확인 중..." />;

  // 로그인하지 않은 경우 로그인 페이지로 리다이렉트
  if (!user) {
    alert('로그인이 필요한 서비스입니다.');
    return <Navigate to="/login" replace />;
  }

  return children;
}