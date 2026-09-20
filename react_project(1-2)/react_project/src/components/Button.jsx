export default function Button({ children, onClick, type = 'button', disabled = false, variant = 'primary' }){
{/*
    -children : <Button>버튼 텍스트</Button>처럼 컴포넌트 태그 사이에 넣은 내용(글자, 아이콘 등)을 받아오는 React의 특수 Prop
    -prop : 컴포넌트에 전달되는 속성값, 부모 컴포넌트에서 자식 컴포넌트로 전달되는 데이터
    -type = 'button' : 버튼의 기본 타입을 'button'으로 지정, form 안에서 submit 버튼이 아닌 일반 버튼으로 동작하도록 함
    ==> Form 제출 시 뜻하지 않게 페이지가 새로고침되는 것을 방지
    -disabled = false : 버튼의 기본 상태를 활성화로 지정, true로 설정하면 버튼이 비활성화됨
    -variant = 'primary' : 버튼 스타일 테마를 지정하는 기본 옵션으로 다른 스타일을 적용하려면 'secondary' 등으로 변경 가능
    */}    
    
    const style = {
        padding: '0.5rem 1rem',
        backgroundColor: variant === 'primary' ? '#0066cc' : '#666',
        //variant 값이 'primary'면 파란색(#0066cc), 아니면 회색(#666)을 적용
        color: '#fff',
        border: 'none',
        borderRadius: '4px',
        cursor: disabled ? 'not-allowed' : 'pointer',
        //disabled가 true면 클릭 금지 마우스 커서(not-allowed), false면 손가락 모양 커서(pointer)를 띄움
    };
    
    return(
        <button type={type} onClick={onClick} disabled={disabled} style={style}>
            {children}
        </button>
    );
    //전달받은 속성(Props)들과 생성된 style 객체를 실제 HTML <button> 태그에 전달하여 렌더링
}
