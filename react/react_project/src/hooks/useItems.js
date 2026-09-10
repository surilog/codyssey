import {useState, useEffect, useCallback } from 'react';
import { supabase } from '../lib/supabase';
{/*컴포넌트 내부에 데이터 조회 로직을 일일이 작성할 필요 없이, 
이 훅 하나만 불러오면 [데이터 목록, 로딩 상태, 에러 상태, 새로고침 기능]을 한 번에 관리 
-hook:은 Supabase 데이터베이스에 특정 이벤트(데이터 추가, 수정, 삭제)가 발생했을 때, 
외부 URL(API 서버, Serverless Function 등)로 HTTP POST 요청을 자동으로 보내주는 기능


*/} 
export function useItems(){
    //-----------------const [상태변수, 상태변경함수] = useState(초기값) 설정 구간-----------------------------------

    const [items, setItems] = useState([]); //DM에서 받아온 아이템 목록
    // items: 화면에 그려줄 데이터(읽기 전용)
    // set이름(수정함수)를 쓴 이유 =>  setItems(새로운 값)을 통해 데이터를 바꾸고 화면을 다시 그리게 함
    // 요약: ustState([])는 [데이터 값, 수정함수] 모양의 2개짜리 배열 생성
    // const[itmes,setItems]는 그 배열에서 0번째 값을 items에 1번째 함수를 setItems에 꺼내놓음
    //변수 이름 관례상 [이름, set이름]으로 사용

    const [isLoading, setIsLoading] = useState(true); // 로딩 중 여부 (초기값 :true)
    // useState 함수는 [true, setIsLoading함수] 배열을 리턴
    // 이때 isLoading 의 값은 true
    const [error, setError] = useState(null); //발생한 에러 메시지
// 비동기 데이터 통신 시 사용자 경험(UX)을 위해 필수적인 3가지 상태(데이터, 로딩, 에러)를 준비

    const fetchItems = useCallback(async () =>{
        //useCallback: 컴포넌트가 리랜덩링될 때마다 fetchItems 함수가 새로 생성되는 것을 방지하여 무한 루프 방지 및 메모리 최저화 수행
        setIsLoading(true);
        setError(null);
        try{
            const { data, error } = await supabase
                .from('items') // items 테이블 선택
                .select('*') // 모든 컬럼 조회
                .order('created_at',{ ascending: false  }); //생성일 기준 내림차순(최신순) 정렬
            if (error) throw error;
            setItems(data || []);
        }
        catch (err) {
            setError(err.message || '데이터를 불러오는 중 오류가 발생했습니다.');
        }
        finally{
            setIsLoading(false);//성공 실패 여부 상관 없이 로딩 종료
        }
    },[]);

    // SELECT * FROM items ORDER BY created_at DESC와 동일하게 작동
    // try-catch-finally : 통신 전 로딩 시작(true) -> 통신 결과 처리 -> 예외 발생 시 에러 저장 -> 작업 완료 후 로딩 종료(false)

    useEffect(() => { // 화면에 컴포넌트가 처음 등장할 때 자동으로 fetchItems() 호출 => DB에서 데이터 받아옴
        fetchItems();

    }, [fetchItems]);

    return { items, isLoading, error, refetch: fetchItems};
    // 훅을 호출하는 컴포넌트에게 객체 형태로 필요한 상태값을 내보냄.
    // 특히 refetch: fetchItems로 이름을 변경하여 내보내어 => 외부에서 "새로고침 버튼" 클릭 시 통신을 다시 요청 할 수 있음
}