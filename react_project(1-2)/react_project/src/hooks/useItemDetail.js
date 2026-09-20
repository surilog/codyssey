import { useState, useEffect, useCallback } from 'react';
import { supabase } from '../lib/supabase';

export function useItemDetail(id){
    // 상세 정보를 가져올 아이템의 고유 식별자(id)를 외부로부터 넘겨 받음
    const [item, setItem] = useState(null);
    //여러 개를 담는 목록은 배열[]로 시작하지만, 상세 정보는 단 하나의 데이터 객체{id:1, title: ..}이거나 데이터가 없는 상태므로 null초기화
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchItem = useCallback(async () => {
        if (!id) return;//id가 없으면 DB요청을 보내지 않고 즉시 중단(안전 장치)
        setIsLoading(true);
        setError(null);

        try {
            const {data, error} = await supabase
                .from('items')
                .select('*')
                .eq('id', id) // sql의 WHERE id = id 조건과 동일
                .single(); // 결과를 배열이 아닌 객체{} 형태로 받음.

            if (error) throw error;
            setItem(data);
        }
        catch (err) {
            setError(err.message || '상세 데이터를 불러오는 중 오류가 발생했습니다.');
        }
        finally {
            setIsLoading(false);
        }
    },[id]);
    // 의존성 배열 등록, id가 변경될 때만 fetchItem 함수를 재생성

    // fetchItem 함수가 바뀌면 (즉, id가 바뀌면 ) 새로 DB통신 진행
    useEffect(()=> {
        fetchItem();
    },[fetchItem]);
    return { item, isLoading, error, refetch: fetchItem};
}