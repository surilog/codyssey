export default function Loading({ message = '데이터를 불러오는 중입니다...'}){
    return(
        <div style={{padding: '2rem', textAlign: 'center'}}>
            <p>⌛{message}</p>
        </div>
    )
}