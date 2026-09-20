import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {supabase} from '../lib/supabase';
import { useItemDetail } from "../hooks/useItemDetail";
import Input from '../components/Input';
import Button from "../components/Button";
import Loading from "../components/Loading";
import ErrorState from "../components/ErrorState";


export default function ItemEditPage() {
    const {id} = useParams();//URL 파라미터에서 현재 아이템의 id를 추출(예: "3")
    const navigate = useNavigate();//페이지 이동을 수행하는 라우터 함수
    const {item, isLoading: isFetching, error:fetchError}= useItemDetail(id);
    // useItemDetail 커스텀 훅에서 isloading과 error이름을 각각 isFetching, fetchError로변경
    //이유: 제출 시 발생할 submitError와 이름 충돌 방지

    //Form local state (사용자가 입력창에 적는 값을 기억)
    const [title, setTitle] =useState('');
    const [category, setCategory] = useState('')
    const [description, setDescription] = useState('')

    //UX State(폼 유효성 검사, 제출 상태 , 에러관리)
    const [errors, setErrors] = useState({});
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submitError, setSubmitError] = useState(null);

    // ▲ 화면을 갱신하는 2가지 종류의 상태를 선언

    //기존 데이터 불러오고 성공시 State채우기
    useEffect(() => {
        if(item){
            setTitle(item.title || '');
            setCategory(item.category || '');
            setDescription(item.description || '');
        }
    },[item]); // 의존성 배열 등록, item가 변경될 때만 useEffect 함수를 다시실행
{/*useItemDetail 훅이 비동기 통신을 완료하여 item 객체에 값이 들어오면 => 
    그 즉시 FormState(title,category,description)의 초기값을 기존 DB 데이터로 채워주는 핵심 훅! 
    
1.최초 렌더링 시: DB에서 데이터 가져오는 중 item은 null. useEffect가 일단 실행되지만 if (item) 조건에 걸려 아무 일도 X.

2.비동기 통신 완료 시: DB에서 데이터를 다 받아오면 item에 { id: 3, title: '테스트', ... } 값이 들어옴

3.의존성 배열 감지: React가 "어? [item] 값이 바뀌었네?" 하고 감지하여 useEffect 내부 코드를 다시 실행.

4.State 바인딩: setTitle, setCategory가 실행되면서 수정 폼의 입력창에 기존 데이터가 채워짐.
    
    
    */}

    //=========================폼 제출전 유효성 검사====================================
    const validate = () => {
        const newErrors = {};
        if(!title.trim()) newErrors.title = '제목을 입력해주세요.';
        if(!category.trim()) newErrors.category = '카테고리를 입력해주세요';
        if(!description.trim())newErrors.description = '설명을 입력해주세요';
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };
//.trim() => 공백만 입력 방지 + errors객체에 담아 UI로 에러 메시지를 띄움

    const handleSubmit = async(e) => {
        e.preventDefault(); //업데이트 할때 페이지 전체가 업데이트 되면 안되나까 금지시키고
        if (!validate()) return; //유효성 검사 실패하면 수정 요청 보내지 않고 중단

        setIsSubmitting(true);
        setSubmitError(null); //이전 에러 초기화

        try{
            //Supabase Update(수정) 요청
            const {error} = await supabase
                .from('items')
                .update({title, category, description}) //전달받은 필드값 수정
                .eq('id', id);
                //Update items SET  WHERE id = '3
            if (error) throw error;

            navigate(`/items/${id}`); //템플릿 리터럴 적용(백틱)
        }
        catch(err){
            setSubmitError(err.message || '수정에 실패했습니다.')
        }
        finally{
            setIsSubmitting(false);// 성공/실패 여부와 상관없이 제출 상태 해제
        }
    }; // 백엔드 DB와 비동기 수정 통신을 처리하고 상태 변경 및 페이지 이동을 지시! 


    //랜더링 영역
    if (isFetching) return <Loading message = "기존 데이터를 불러오는중..."/>
    if (fetchError) return <ErrorState message={fetchError}/>;

{/*▲React에서는 데이터를 가져오는 과정에서 예외 상황(로딩 중, 에러 발생 등)을 가장 먼저 처리하여 함수를 일찍 종료시키는 
'얼리 리턴(Early Return)' 패턴을 자주 사용

위의 두 조건 만족 시에만 메인 폼 UI렌더링
*/}

    return (
        <div style={{maxWidth: '500px', margin: '0 auto'}}> 
            <h2>아이템 수정 (ID: {id})</h2>
        
            {submitError && // &&: 조건부 랜더링
            (<p style={{color :'red', marginBottom: '1rem'}}>{submitError}</p>)}
            {/*summitError가 null이거나 빈값이면  <p>태그를 번혀 랜더링하지 않음 */}

            <form onSubmit={handleSubmit}> 
                {/*왜 button onClick 대신 form onSubmit을 쓸까? 
<Button type="submit">은 not only 클릭but 사용자가 입력 창에서 Enter키를 눌렀을 때도 수정 요청(handleSubmit)이 자동으로 실행
웹 표준 접근성과 폼 사용자 경험(UX) 측면에서 훨씬 form onSumvit이 더 좋음*/}
                <Input
                    label="제목"
                    value={title}
                    onChange={(e)=>setTitle(e.target.value)}
                    error={errors.title}
/*
value={title}: React의 title State 값을 Input의 화면 텍스트로 보냄.

onChange={(e) => setTitle(e.target.value)}:사용자가 키보드로 한 글자 칠 때마다 setTitle을 실행=> React State를 즉시 업데이트

error={errors.title}: 유효성 검사(validate()) 결과 빈값일 경우 전달되는 에러 메시지("제목을 입력해주세요.")를 전달 */


                />

                <Input
                    label="카테고리"
                    value={category}
                    onChange={(e)=>setCategory(e.target.value)}
                    error={errors.category}
                />
       

            <div style={{marginBottom: '1rem', display: 'flex', flexDirection: 'column',gap: '0.3rem'}}>
                <label>설명</label>
                <textarea
                    rows="4"
                    value={description}
                    onChange={(e)=>setDescription(e.target.value)}
                    style={{
                        padding: '0.5rem',
                        borderRadius: '4px',
                        border: errors.description ? '1px solid red' : '1px solid #ccc',
                    }}
                />
                {errors.description && (
                    <span style={{ color: 'red', fontSize: '0.8rem'}}>{errors.description}</span>
                )}    
            </div>

            <div style={{display: 'flex', gap: '0.5rem', marginTop: '1.5rem'}}>
                <Button type="submit" disabled={isSubmitting}>
{/*disabled={isSubmitting}: DB 수정 요청 중일 때는 버튼 클릭을 막아=>
사용자가 실수로 버튼을 여러 번 연속으로 눌러 중복 요청이 나가는 것을 방지 */}
                    {isSubmitting ? '수정 중 ...' : '수정 완료'}
                </Button>
                <Button variant="secondary" onClick={() => navigate(`/items/${id}`)}>
                    취소
                    {/*[취소] 버튼: 수정 작업을 포기하고 원래의 상세 화면 경로로 돌아감 */}
                </Button>
            </div>
        </form>
    </div>
    );
}