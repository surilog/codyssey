/*전체 시스템에서의 역할
전역 인증 상태 공급원: 로그인한 사용자 정보, 로딩 여부, 그리고 로그인/회원가입/로그아웃 함수를 앱 전체의 모든 컴포넌트에 공급

실시간 로그인 상태 동기화: 
브라우저 탭을 새로고침하거나, 다른 탭에서 로그아웃을 해도 Supabase의 이벤트 리스너를 통해 실시간으로 사용자 정보를 최신 상태로 유지

접근 제어(Protected Route): 로그인한 유저만 접속할 수 있는 페이지(예: 마이페이지, 작성/수정 페이지)를 판단하는 기준 데이터를 제공. 

위 구조를 쓰지 않으면 user상태를 App.js에서 선언한 뒤 모든 하위 컴포넌트(Header등)에게 매번 Props로 계속 내려줘야함
Context API 적용 후: 최상위에서 <AuthProvider>로 한 번만 감싸두면,
==> 어떤 컴포넌트든 const { user, signOut } = useAuth(); 한 줄만 써서 즉시 사용자 정보와 인증 함수를 불러와 사용가능.
*/


import {createContext, useContext, useEffect, useState} from 'react';
import {supabase} from '../lib/supabase';

const AuthContext =createContext({});//컴포넌트 트리 전체에 공유할 '데이터 저장소(빈 상자)'를 생성
export function AuthProvider({children}){
    //{ children }: <AuthProvider><App/></AuthProvider>처럼 이 컴포넌트로 감싸진 하위 모든 태그(컴포넌트)들을 의미
    const [user, setUser] = useState(null);
    const [isLoading, setIsloading] = useState(true);

    useEffect(()=>{
        //현재 로그인 세션 확인
        supabase.auth.getSession().then(({data: {session}})=>{
            //getSession(): 웹 브라우저의 로컬 스토리지에 기존 로그인 토큰이 남아있는지 확인하여 자동 로그인 처리를 수행
            setUser(session?.user ?? null);
//session?.user ?? null: 옵셔널 체이닝(?.)과 널 병합 연산자(??)를 사용, session이 있으면 session.user를 저장하고 없으면 null
            setIsloading(false);
        });
    
    // 로그인/로그아웃 상태 변화 실시간감지
    const {data : {subscription}} = supabase.auth.onAuthStateChange((_event, session)=>{
//onAuthStateChange(): 사용자가 로그인, 로그아웃, 토큰 갱신 등의 행동을 할 때 Supabase가 이를 감지하여 인자로 전달된 콜백 함수를 실시간으로 실행
        setUser(session?.user?? null);
        setIsloading(false);
    });

    return () => subscription.unsubscribe();
    //subscription.unsubscribe(): 메모리 누수를 방지하기 위해 이 컴포넌트가 사라질 때 이벤트 리스너 구독을 해제
},[]);


    // 로그인 (이메일 비밀번호)
    const signIn = (email, password) => {
        return supabase.auth.signInWithPassword({email, password});
    };
    //회원가입 (닉네임 메타데이터와 함께 저장)
    const signUp = (email, password, nickname) => {
        return supabase.auth.signUp({
            email,
            password,
            options: {
                data: {nickname},// Supabase auth.users의 user_metadata에 저장됨
            },
        });
    };
    //로그아웃
    const signOut = () => {
        return supabase.auth.signOut();
    };

    return(
        <AuthContext.Provider value={{user, isLoading,signIn,signUp,signOut}}>{children}</AuthContext.Provider>
    );
    //<AuthContext.Provider value="{...}">: value에 넣어둔 객체(user, signIn 등)를 하위 컴포넌트들에게 공유
}

export const useAuth = () => useContext(AuthContext);

//useAuth(): 다른 컴포넌트에서 useContext(AuthContext)를 일일이 쓰지 않고, 
// useAuth() 한 줄만 호출하면 바로 접근할 수 있도록 만든 전용 커스텀 훅