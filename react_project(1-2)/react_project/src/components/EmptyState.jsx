export default function EmptyState({ message = '등록된 데이터가 없습니다.'}){
    return(
        <div style = {{padding: '2rem', textAlign: 'center', color: '#666'}}>
            <p> {message}</p>
        </div>
    );
}