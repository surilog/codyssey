/*
1. 전체 시스템에서의 역할 및 구조적 선택 이유

전체 시스템에서의 역할: URL 주소창의 파라미터(:id)를 받아 단일 데이터의 세부 내용을 표시 &수정 페이지 이동 및 삭제 요청을 진행

구조적 선택 이유:

비동기 로직 분리 (useItemDetail): 데이터 조회 로직을 커스텀 훅으로 위임하여 
=> UI 컴포넌트에는 오직 렌더링과 이벤트 핸들러만 남겨 깔끔한 코드를 유지

안전한 삭제 UX (Confirmation & Lock): window.confirm으로 사용자의 실수를 방지하고,
 삭제 진행 중에는 disabled={isDeleting} 처리를 통해 중복 클릭을 막아 백엔드 다중 요청을 방지

*/


import { useState } from "react";
import {useParams, Link, useNavigate} from "react-router-dom";
 //react-router-dom에서 useParams를 import합니다. useParams는 URL 파라미터를 가져오는 훅.
// userParams(훅)은 URL에서 동적 세그먼트(예: /items/:id)로 전달된 값을 가져오는 데 사용.
// 이 훅을 사용하면 컴포넌트 내에서 URL 파라미터를 쉽게 접근가능. react-router라이브러리 기능
//useParams(): URL 주소창의 변수(예: /items/45에서 45)를 읽어와 id로 가져옴
import { supabase } from "../lib/supabase";
import { useItemDetail } from "../hooks/useItemDetail";
//useItemDetail(id): 받아온 id를 커스텀 훅에 넘겨 해당 아이템만 Supabase에서 조회
import Loading from "../components/Loading";
import ErrorState from "../components/ErrorState";
import Button from "../components/Button";
import { useAuth } from '../context/AuthContext';


export default function ItemDetailPage() {
    const {id} = useParams(); 
    // useParams를 호출하여 URL 파라미터를 가져옵니다. 여기서는 id라는 변수안에 URL에서 전달된 id 값을 할당.
    // JavaScript의 구조 분해 할당 문법을 사용해 그 객체 안에서 id라는 키(Key) 값만 바로 뽑아내어 id 변수에 담은 것
    // ex) URL 경로(/items/123)에서 :id 값(123)을 추출
    const navigate =useNavigate();
    //삭제 후 목록 페이지,수정페이지 진입할 때 프로그래밍 방식으로 경로 전환
    const { user } = useAuth(); // 현재 로그인한 사용자 정보
    const { item, isLoading, error, refetch } = useItemDetail(id);

    console.log('1. 현재 로그인 user:', user);
    console.log('2. 불러온 item:', item);
    console.log('3. id 비교 결과:', user?.id, '===', item?.user_id, '👉', user?.id === item?.user_id);
    //추출한 ID를 훅에 전달=> 데이터 가져오고, 로딩,에러,리프레시상태  받아옴
    const [isDeleting, setIsDeleting] = useState(false);
    //삭제진행중인지 추적
    // 현재 로그인한 사용자 ID와 글의 user_id가 같은지 확인
   
    //Delete (삭제) 핸들러
    const handleDelete = async () => {
        const isConfirmed = window.confirm('정말로 이 아이템을 삭제하시겠습니까?');
        if(!isConfirmed) return;

        setIsDeleting(true);

        try{
            //Supabase Delete(삭제) 요청
            const {data,error} =await supabase
                .from('items')
                .delete()
                .eq('id',id)
                .select();
    //: Supabase items 테이블에서 현재 페이지의 id와 일치하는 행(Row)을 삭제. (SQL: DELETE FROM items WHERE id = id)

            if(error) throw error;

            if (!data || data.length === 0) {
            alert('삭제 권한이 없거나 이미 삭제된 게시글입니다.');
            return;
    }
            alert('성공적으로 삭제되었습니다.')
            navigate('/items'); //삭제 후 사라진 상세 페이지에 남지 않도록 목록 화면으로 리다이렉트
        }
        catch(err){
            alert(`삭제 실패: ${err.message}`);
        }
        finally{
            setIsDeleting(false)
        }
    }

//얼리리턴
    if (isLoading) return <Loading message="상세 정보를 불러오는 중..." />;
    if (error) return <ErrorState message={error} onRetry={refetch}/>;
    if (!item) return <ErrorState message="존재하지 않는 아이템입니다."/>;
    //안전장치 먼저 설정! 아래 렌더링 코드에서는 item.title, item.description 등을 item이 존재함을 확신=> 안전하게 사용

    const isOwner = true;
    //const isOwner = user && item && user.id === item.user_id;
    // ItemDetailPage.jsx 내부 렌더링 예시
return (
  <div style={{ maxWidth: '800px', margin: '3rem auto', padding: '0 1rem' }}>
    <div style={{
      display: 'flex',
      gap: '2.5rem',
      padding: '2.5rem',
      backgroundColor: '#ffffff',
      borderRadius: '16px',
      border: '1px solid #e2e8f0',
      boxShadow: '0 10px 25px -5px rgba(0,0,0,0.05)'
    }}>
      {/* 커버 이미지 */}
      <img
        src={item.image_url || 'https://placehold.co/200x280?text=No+Cover'}
        alt={item.title}
        style={{
          width: '210px',
          height: '290px',
          objectFit: 'cover',
          borderRadius: '8px',
          boxShadow: '0 8px 16px rgba(0,0,0,0.12)',
          flexShrink: 0
        }}
      />

      {/* 상세 내용 */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        <div>
          <span style={{
            fontSize: '0.8rem',
            fontWeight: '600',
            color: '#2563eb',
            backgroundColor: '#eff6ff',
            padding: '0.25rem 0.75rem',
            borderRadius: '20px'
          }}>
            {item.category}
          </span>
          <h1 style={{ fontSize: '1.8rem', fontWeight: '800', color: '#0f172a', margin: '0.8rem 0 1rem 0' }}>
            {item.title}
          </h1>
          <p style={{ fontSize: '0.95rem', color: '#334155', lineHeight: '1.7', whiteSpace: 'pre-wrap' }}>
            {item.description}
          </p>
        </div>

        {/* 버튼 영역 */}
        {isOwner && (
          <div style={{ display: 'flex', gap: '0.75rem', marginTop: '2rem', paddingTop: '1.25rem', borderTop: '1px solid #f1f5f9' }}>
            <button
              onClick={() => navigate(`/items/${id}/edit`)}
              style={{
                padding: '0.6rem 1.2rem',
                backgroundColor: '#2563eb',
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                fontWeight: '600',
                fontSize: '0.9rem',
                cursor: 'pointer'
              }}
            >
              ✏️ 수정하기
            </button>
            <button
              onClick={handleDelete}
              disabled={isDeleting}
              style={{
                padding: '0.6rem 1.2rem',
                backgroundColor: '#ef4444',
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                fontWeight: '600',
                fontSize: '0.9rem',
                cursor: 'pointer',
                opacity: isDeleting ? 0.6 : 1
              }}
            >
              {isDeleting ? '삭제 중...' : '🗑️ 삭제하기'}
            </button>
          </div>
        )}
      </div>
    </div>
  </div>
);
}

{/*사용자 경로(라우팅)의 완결점: /items/123 형태의 동적 주소를 받아 해당 123에 맞는 데이터를 Supabase에서 가져와 렌더링하고
     다시 목록(/items)으로 돌아갈 수 있는 링크를 제공. */}