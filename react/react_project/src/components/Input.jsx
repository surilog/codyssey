export default function Input({label, type = 'text', value, onChange, placeholder, error}){
{/*-label : 입력창 상단에 띄울 제목(예, 아이디, 비번)
- type = 'text': 입력창의 유형. 기본값은 일반 텍스트('text')이며, 필요에 따라 'password', 'email', 'number' 등을 전달 
- value : 현재 입력 창에 들어있는 값(상태,state)을 상위 컴포넌트로부터 받음
- onChange: 사용자가 타이핑할때 실행되는 함수 => 상위 컴포넌트의 State를 업데이트
- placeholder : 입력창이 비어있을 때 보여줄 안내 텍스트
- error: 유효성 검사 실패 시 보여줄 에러 메시지 문자열

*/}    
    return(
        <div style={{marginBottom: '1rem', display: 'flex', flexDirection: 'column', gap:'0.3rem'}}>
            {label && <label>{label}</label>}
            {/*label 값이 전달되었을 때만 <label> 태그를 출력. (라벨이 필요 없는 검색창 등에서는 안 나타남) */}
            <input
                type={type}
                value={value}
                onChange={onChange}
                placeholder={placeholder}
                style={{ padding: '0.5rem', borderRadius: '4px', border: error ? '1px solid red' : '1px solid #ccc'}}
                />
                {error && <span style={{ color: 'red', fontSize: '0.8rem'}}>{error}</span>}
        </div>
    );
}