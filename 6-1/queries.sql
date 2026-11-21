-- =========================================================
-- 핵심 쿼리 15개 (실행 결과: results/Q01.png ~ Q15.png)
-- 기본 조회 4 / 조인 4 / 집계 3 / 서브쿼리 1 / 수정·삭제 2 / 인덱스 1
-- =========================================================

-- ---------- 기본 조회 ----------

-- Q1. 가격이 18000원 이상인 도서의 제목과 가격을 비싼 순으로 조회 (WHERE + ORDER BY)
SELECT title, price FROM book WHERE price >= 18000 ORDER BY price DESC;

-- Q2. 아직 반납되지 않은(대여 중인) 대여 기록 조회 (IS NULL)
SELECT * FROM rental WHERE returned_at IS NULL;

-- Q3. 가장 저렴한 도서 3권 조회 (ORDER BY + LIMIT)
-- [참고] LIMIT은 SQLite/MySQL/PostgreSQL 공통, 표준 SQL은 FETCH FIRST 3 ROWS ONLY
SELECT title, author, price FROM book ORDER BY price ASC LIMIT 3;

-- Q4. 2025년 2월 이후 가입한 회원을 이름 가나다순으로 조회
SELECT name, email, created_at FROM member WHERE created_at >= '2025-02-01' ORDER BY name ASC;

-- ---------- 조인 ----------

-- Q5. [INNER JOIN] 도서 제목과 카테고리 이름을 함께 조회
SELECT b.id, b.title, b.author, c.name AS category_name
FROM book b
INNER JOIN category c ON b.category_id = c.id;

-- Q6. [INNER JOIN 3중] 누가 어떤 책을 언제 대여했는지 조회
SELECT m.name AS member_name, b.title AS book_title, r.rented_at, r.status
FROM rental r
INNER JOIN member m ON r.member_id = m.id
INNER JOIN book b   ON r.book_id   = b.id;

-- Q7. [LEFT JOIN] 모든 카테고리와 소속 도서 조회 (도서 없는 카테고리도 NULL로 포함)
SELECT c.name AS category_name, b.title AS book_title
FROM category c
LEFT JOIN book b ON c.id = b.category_id;

-- Q8. [LEFT JOIN] 전체 회원과 대여 기록 조회 (대여 이력 없는 회원도 NULL로 포함)
SELECT m.name AS member_name, m.email, r.rented_at, r.status
FROM member m
LEFT JOIN rental r ON m.id = r.member_id;

-- ---------- 집계 ----------

-- Q9. 카테고리별 등록된 도서 권수와 평균 가격 (COUNT, AVG + GROUP BY)
SELECT c.name AS category_name, COUNT(b.id) AS book_count, AVG(b.price) AS avg_price
FROM category c
INNER JOIN book b ON c.id = b.category_id
GROUP BY c.id, c.name;

-- Q10. 회원별 총 대여 횟수 (많은 순 정렬)
SELECT m.name AS member_name, COUNT(r.id) AS total_rentals
FROM member m
INNER JOIN rental r ON m.id = r.member_id
GROUP BY m.id, m.name
ORDER BY total_rentals DESC;

-- Q11. 대여 상태(RETURNED / RENTED)별 건수
SELECT status, COUNT(*) AS count
FROM rental
GROUP BY status;

-- ---------- 서브쿼리 ----------

-- Q12. 전체 도서 평균 가격보다 비싼 도서 조회 (스칼라 서브쿼리)
SELECT title, author, price
FROM book
WHERE price > (SELECT AVG(price) FROM book);

-- ---------- 수정 / 삭제 ----------

-- Q13. [UPDATE] 1번 회원이 대여 중인 5번 도서를 지금 시각으로 반납 처리
-- [SQLite 전용] DATETIME('now','localtime') (MySQL: NOW(), PostgreSQL: CURRENT_TIMESTAMP)
UPDATE rental
SET returned_at = DATETIME('now', 'localtime'), status = 'RETURNED'
WHERE member_id = 1 AND book_id = 5 AND status = 'RENTED';

-- 검증: returned_at이 채워지고 status가 RETURNED인지 확인
SELECT * FROM rental WHERE member_id = 1 AND book_id = 5;

-- Q14. [DELETE] 대여 기록이 없는 9번 도서 삭제
-- (대여 기록이 있는 도서를 지우면 FK 제약으로 실패한다 → bonus.sql 참고)
DELETE FROM book WHERE id = 9;

-- 검증: 결과 0행이면 삭제 완료
SELECT * FROM book WHERE id = 9;

-- ---------- 인덱스 ----------

-- Q15. 회원별 대여 이력/대여 상태 조회용 복합 인덱스
-- 적용 이유: WHERE member_id = ? (AND status = 'RENTED') 조회와 member-rental JOIN이 자주 쓰여, 전체 스캔 대신 인덱스로 바로 찾기 위함
-- [SQLite 전용] IF NOT EXISTS (MySQL은 CREATE INDEX에서 미지원)
CREATE INDEX IF NOT EXISTS idx_rental_member_status ON rental(member_id, status);

-- 검증 1: 인덱스가 생성되었는지 [SQLite 전용 PRAGMA]
PRAGMA index_list('rental');

-- 검증 2: 실제 조회에 인덱스가 쓰이는지 → "USING INDEX idx_rental_member_status" 확인
-- [SQLite 전용] EXPLAIN QUERY PLAN (MySQL/PostgreSQL: EXPLAIN)
EXPLAIN QUERY PLAN
SELECT * FROM rental WHERE member_id = 1 AND status = 'RENTED';
