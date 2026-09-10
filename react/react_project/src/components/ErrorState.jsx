export default function ErrorState({ message, onRetry}){
    return(
        <div style = {{padding: '2rem', textAlign: 'center', color: 'red'}}>
            <p>⚠️ {message || '오류가 발생했습니다.'}</p>
            {onRetry && <button onClick={onRetry}>다시 시도</button>}
        </div>
    );
}