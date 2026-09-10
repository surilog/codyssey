/*
전체 시스템에서의 역할

사용자 인증 관문: 사용자가 서비스를 이용하기 위해 계정을 확인하거나 새로 생성하는 입구

useAuth()와 화면의 연결고리: 이전 시간에 만든 AuthContext의 signIn, signUp 함수를 실제 UI(입력창, 버튼)와 연결함

페이지 전환 매개체: 인증 처리가 완료되면 useNavigate를 통해 메인 서비스 화면(/items)으로 자동으로 보냄
*/


import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Input from '../components/Input';
import Button from '../components/Button';

export default function LoginPage(){
  const [isSignUp, setIsSignUp] = useState(false);//isSignUp: false면 로그인 모드, true면 회원가입 모드로 전환되는 핵심 스위치 변수
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [nickname, setNickname] = useState('');
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { signIn, signUp } = useAuth();//useAuth(): 중앙 저장소(AuthContext)에서 로그인/회원가입 요청 함수를 가져옴
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault(); //새로고침 방지
    setError(null);
    //기본 피수값 검증
    if (!email || !password) {
      setError('이메일과 비밀번호를 입력해 주세요.');
      return;
    }
    //회원가입 모드일 때만 닉네임 검증
    if (isSignUp && !nickname.trim()) {
      setError('닉네임을 입력해 주세요.');
      return;
    }

    setIsSubmitting(true);

    try {
      if (isSignUp) {
        //회원가입 요청(Supabase)
        const { error } = await signUp(email, password, nickname);
        if (error) throw error;
        alert('회원가입 성공! 로그인 상태로 전환됩니다.');
        navigate('/items');
      } else {
        //로그인 요청
        const { error } = await signIn(email, password);
        if (error) throw error;
        navigate('/items');
      }
    } catch (err) {
      setError(err.message || '인증 처리에 실패했습니다.');
    } finally {
      setIsSubmitting(false);//// 성공/실패 모두 제출 상태 해제
    }
  };
  //조건부 검증: isSignUp 상태에 따라 닉네임 입력 여부를 유연하게 검사
//모드별 비동기 분기: isSignUp 값에 따라 signUp() 또는 signIn() 함수를 선택하여 실행

  return (
    <div style={{ maxWidth: '400px', margin: '3rem auto', padding: '2rem', border: '1px solid #ccc', borderRadius: '8px' }}>
      <h2>{isSignUp ? ' 회원가입' : ' 로그인'}</h2>
      {error && <p style={{ color: 'red', fontSize: '0.85rem' }}> {error}</p>}

      <form onSubmit={handleSubmit}>
        {isSignUp && (
          <Input
            label="닉네임"
            value={nickname}
            onChange={(e) => setNickname(e.target.value)}
            placeholder="화면에 표시될 이름"
          />
        )}
        <Input
          label="이메일 (아이디)"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="example@email.com"
        />
        <Input
          label="비밀번호"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="6자리 이상"
        />

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginTop: '1.5rem' }}>
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? '처리 중...' : isSignUp ? '가입 완료' : '로그인'}
          </Button>
          <Button type="button" variant="secondary" onClick={() => setIsSignUp(!isSignUp)}>
            {isSignUp ? '이미 계정이 있으신가요? 로그인' : '계정이 없으신가요? 회원가입'}
          </Button>
        </div>
      </form>
    </div>
  );
}