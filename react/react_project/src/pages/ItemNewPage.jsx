import { useState } from 'react';
import { useNavigate} from 'react-router-dom'; // 클릭 한번으로 다른 주소로 이동하기 위해 사용
import { supabase } from '../lib/supabase';
import { useAuth } from '../context/AuthContext'; //  useAuth 추가
import Input from '../components/Input';
import Button from '../components/Button';



export default function ItemNewPage() {
    const { user } = useAuth(); //. 현재 로그인 사용자 가져옴
    const navigate = useNavigate();

    // Controlled Input 을 위한 Form Local State
    // 제어 컴포넌트: <Input> or <textarea>의 값을 State로 직접 제어. => 입력 창에 글자 칠때마다 State가 갱신되어 실시간 값 파악
    const [title, setTitle] = useState('');
    const [category, setCategory]= useState('');
    const [imageUrl, setImageUrl] = useState(''); // 1. 이미지 URL State 추가
    const [description, setDescription] = useState('');
    
    // UX 및 유효성 검증를 위한 상태
    const [error, setErrors] = useState({}); //error"{title:'제목을입력해주세요.'}처럼 각 입력 항목별 에러 메시지를 객체로 저장
    const [isSubmitting, setIsSubmitting] = useState(false);// isSubmitting:서버로 데이터를 전송중인지 나타냄(false)
    const [submitError, setSubmitError] = useState(null);// DB저장시 통신 오류가 발생했을 때 보여줄 전체 에러 메시지

    //폼 제출 전 유효성 검사 필요
    const validate = () => {
        const newErrors = {};
        if (!title.trim()) newErrors.title = '제목을 입력해주세요.';
        if (!category.trim()) newErrors.category = '카테고리를 입력해주세요.';
        if (!description.trim()) newErrors.description = '설명을 입력해주세요.';
        // .trim : 문자열 앞뒤의 공백 제거=> 스페이스만 쳐서 제출하는 것을 막음
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
        //객체안에 에러키가 하나도 없어야 통과
    };
    
    // submit 헨들러
    const handleSubmit = async (e) => {
        e.preventDefault(); // 기본 폼 제출(페이지 새로고침) 방지
        //form은 제출 시 페이지 전체를 새로고침. BUT SPA에서는 이 기본 동작을 막아야 state와 화면이 유지.

        if (!validate()) return;//검사 실패시 통신 중단
        if (!user) {
            setSubmitError('로그인이 필요합니다.');
            return;
    }
        setIsSubmitting(true);
        setSubmitError(null);
        try {
        // Supabase Create (Insert) 요청 - user_id 포함
            const { error } = await supabase.from('items').insert([
                {
                title,
                category,
                image_url: imageUrl,
                description,
                user_id: user.id, // 로그인한 사용자의 UUID 전달
                },
            ]);

            if (error) throw error;

            navigate('/items');
        } 
        catch (err) {
        setSubmitError(err.message || '등록에 실패했습니다.');
        } 
        finally {
        setIsSubmitting(false);
        }
    };
    //
    return(
        <div style={{ maxWidth: '500px', margin: '0 auto'}}>
            <h2> 새 아이템 등록 </h2>

            {submitError && (<p style={{color: 'red', marginBottom: '1rem'}}> {submitError}</p>)}

            <form onSubmit={handleSubmit}>
                <Input
                    label="도서 제목"
                    placeholder="예: 위로는 서툴수록 좋다(이정훈)"
                    value={title}
                    onChange={(e)=> setTitle(e.target.value)}
                    error={error.title}//앞 validate()에서 저장된 에러 구문 존재 시 input컴포넌트로 전달=> 입력창:빨간색 문구출력
                />
                <Input 
                    label="카테고리"
                    placeholder="예: IT/개발, 소설, 자기계발, 인문"
                    value={category}
                    onChange={(e)=> setCategory(e.target.value)}
                    error={error.category}
                />
                <Input
                    label="책 표지 이미지 URL (선택)"
                    placeholder="https://example.com/book-cover.jpg"
                    value={imageUrl}
                    onChange={(e) => setImageUrl(e.target.value)}
                />
                <div style={{ marginBottom: '1rem', display: 'flex', flexDirection: 'column',gap: '0.3rem'}}>
                    <label>설명</label>
                    <textarea
                        rows="4"
                        placeholder="상세 내용을 입력하세요"
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                        style={{
                            padding: '0.5rem',
                            borderRadius: '4px',
                            border: error.description ? '1px solid red' : '1px solid #ccc',
                        }}/>
                        {error.description && (
                            <span style={{color: 'red', fontSize: '0.8rem'}}>{error.description}</span>)}
                </div>

                <div style={{display: 'flex', gap: '0.5rem', marginTop: '1.5rem'}}>
                    <Button type="submit" disabled={isSubmitting}>  
                        {isSubmitting ? '등록 중...' : '등록하기'}
                    </Button>
                    <Button variant="secondary" onClick={()=> navigate('/items')}>
                        취소
                    </Button>
                </div>            
            </form>
        </div>
    )
}