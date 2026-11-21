
-- 보너스: 데이터 정합성 깨뜨려 보기 (FK / CHECK 제약 동작 확인)
-- 각 문장은 실패해야 정상 결과: results/bonus_fk.txt
-- FK는 "가리키는 행이 있으면 부모를 지울 수 없고, 없는 부모를 가리킬 수도 없다"는 규칙이다. 상태값(RENTED/RETURNED)과는 상관없다.
-- FK(외래키)를 의미 : 다른 테이블의 키를 가져와 쓰는 칼럼 / PK(기본키) : 그 테이블 안에서 각 행을 구별하는 내 번호

PRAGMA foreign_keys = ON;  -- [SQLite 전용] 이 연결에서 FK 검사 활성화

-- B1. 존재하지 않는 회원(999)으로 대여 기록 입력
--  → FOREIGN KEY constraint failed
--  이유: rental.member_id는 member.id를 참조하는데 member에 id=999가 없다.
--  해결: 회원을 먼저 INSERT한 뒤(부모 → 자식 순서) 그 id로 대여 기록을 넣는다.
INSERT INTO rental (member_id, book_id, rented_at, status)
VALUES (999, 1, '2025-04-01 10:00:00', 'RENTED');

-- B2. 존재하지 않는 카테고리(99)로 도서 입력
--  → FOREIGN KEY constraint failed
--  해결: category에 카테고리를 먼저 추가하거나, 존재하는 category_id를 사용한다.
INSERT INTO book (category_id, title, author, price, published_date)
VALUES (99, '없는 카테고리 책', '홍길동', 10000, '2024-01-01');

-- B3. 대여 기록이 있는 1번 도서 삭제
--  → FOREIGN KEY constraint failed
--  이유: rental에 book_id=1을 참조하는 행이 남아 있어, 지우면 '주인 없는 대여 기록'이 생긴다.
--  해결: 참조하는 rental을 먼저 처리(삭제/보관)하거나, 설계 시 ON DELETE 정책을 정한다.
DELETE FROM book WHERE id = 1;


-- [추가 예시를 통해 생각]
--B3에서 1번 책을 꼭 지워야 한다면, 어떤 순서로 무엇을 실행해야 하나?
-- 1.1번책을 지우려면 자식(rental)을 먼저 지우고 book에서 지워야한다.
--  DELETE FROM rental WHERE book_id =1; 하고 DELETE FROM book WHERE id=1; 하면 됨!
--확인 SELECT * FROM rental where member_id =1; 


-- [추가 예시로 공부] 장도윤(9번 회원)은 DELETE FROM member WHERE id = 9;로 지울 수 있을까? 김철수(1번 회원)는? 각각 이유는?

SELECT * FROM rental where member_id =9; -- 를 통해 member는 여전히 부모테이블이지만 9번을 가리키는 자식 행이 하나도 없어서 지울 수 있음을 확인함!
SELECT * FROM rental where member_id =1; -- 를 통해 rental에 1번을 가리키는 행이 2개나 있음을 확인했으니 바로 지울 수 없음을 확인. 그 2행을 먼저 지우면 지울 수 있음!

-- B4. 허용되지 않은 status 값(오타) 입력
--  → CHECK constraint failed
--  해결: 'RENTED' 또는 'RETURNED'만 사용한다.
INSERT INTO rental (member_id, book_id, rented_at, status)
VALUES (1, 1, '2025-04-01 10:00:00', 'RETRUNED');

-- 참고: PRAGMA foreign_keys = OFF 상태에서는 B1~B3이 그대로 들어가 버린다.
-- SQLite는 FK 검사가 기본 OFF라서, 연결할 때마다 켜야 한다.

-- B5. FK를 끈 상태(OFF)에서 실험하다 들어간 고아 데이터 찾기 & 정리
-- FK 규칙을 어긴 행 찾기 → 정리 전: 4행 (rental 1건, book 3건)
PRAGMA foreign_key_check;

-- 고아 데이터 삭제 (자식 rental → book 순서)
PRAGMA foreign_keys = ON;
DELETE FROM rental WHERE member_id = 999;
DELETE FROM book WHERE category_id = 99;

-- 정리 후 확인 → 0행이면 정상
PRAGMA foreign_key_check;

-- 행 수 확인 → book 9, rental 10
SELECT 'book', COUNT(*) FROM book UNION ALL SELECT 'rental', COUNT(*) FROM rental;




-- 보너스 1(같은 요구를 JOIN과 서브쿼리로 풀기)
-- 요구: 대여 기록이 한 번도 없는 회원 찾기
-- JOIN
SELECT m.id, m.name, m.email
FROM member m
LEFT JOIN rental r ON m.id = r.member_id 
WHERE r.member_id  IS NULL;

-- 서브쿼리
SELECT id, name, email
FROM member 
WHERE id NOT IN (SELECT member_id FROM rental);

-- NOT EXISTS활용 (상관 서브쿼리)
SELECT m.id, m.name, m.email
FROM member m
WHERE NOT EXISTS (SELECT 1 FROM rental r WHERE m.id = r.member_id);

-- NOT IN 사용시 NULL 주의 근거!
SELECT 9 NOT IN (1, 2, NULL);

-- [비교]
-- 1. 가독성: 서브쿼리
-- 이유: 쿼리를 읽었을 때 요구사항과 가장 비슷하게 읽힘
-- JOIN은 "NULL이면 대여기록이 없다"는 해석이 한 번 더 필요했음
-- 2. 꺼낼 수 있는 컬럼(요구가 "회원 이름과 대여일을 같이 보여 줘"로 바뀐다면)
-- JOIN은 FROM 바로 뒤에 member 테이블과 rental테이블이 있기 때문에 꺼낼 수 있음 / 서브 쿼리는 FROM 바로 뒤에는 member테이블만 존재하고 괄호 안에 rental테이블이 존재하니 꺼낼 수 없음
-- 즉 조건으로 걸러내기만 할 때는 서브쿼리가 , 두 테이블 컬럼을 함께 보여줄때는 JOIN이 적합함을 알 수 있음!
-- 3.NOT IN의 주의점 : 서브쿼리 결과에 NULL이 하나라도 있으면 결과를 알 수 없다(모름)으로 판단되서 에러도 없이 아무런 값도 나오지 않게 된다.
-- 이번에는 rental.member_id의 rental테이블에서 "member_id INTEGER NOT NULL" 제약을 넣어줘서 애초에 NULL이 들어갈 수 없어서 문제가 없었지만 NULL이 들어갈 가능성이 있다면 NOT EXISTS를 쓰는 편이 안전!


-- [보너스3] 핵심지표 3개 정의

-- 1. 인기도서 TOP 3
-- 목적: 인기도서를 파악해 빌리려는 사람이 기다리지 않게 하기위해서

SELECT b.title, count(r.id) AS rental_count
FROM rental r
INNER JOIN book b ON r.book_id = b.id
GROUP BY r.book_id ,b.title
ORDER BY rental_count DESC 
LIMIT 3;

-- 2. 카테고리별 대여 건수
-- 목적:각 카테고리별 대여 건수를 파악해 인기 있는 카테고리를 파악해 사람들이 좋아하는 책의 카테고리를 알기 위해서
SELECT c.name AS category_name, COUNT(r.id) AS rental_count
FROM rental r
INNER JOIN book b ON r.book_id = b.id  -- 대여 건수는 rental에 카테고리 이름은 category에 있지만 둘을 이어주는 것은 book의 category_id에 있음
INNER JOIN category c ON b.category_id = c.id  
GROUP BY b.category_id ,c.name
ORDER BY rental_count DESC;

-- 3. 연체 중인 회원 목록 (아직 반납 안 했고, 대여 후 7일 초과) - member, rental, book 테이블 활용
-- => rental이 FOREIGN KEY (member_id) REFERENCES member(id),
--             FOREIGN KEY (book_id) REFERENCES book(id)
-- 위와 같이 연결되어 있으니 rental로 두 테이블을 연결해줘야 함
-- 목적: 연체중인 회원들을 파악해 다른 회원이 원하는 책을 읽을 수 있게 하기 위해
-- [SQLite 전용] JULIANDAY()로 날짜 차이(일수) 계산 (MySQL: DATEDIFF, PostgreSQL: 날짜끼리 뺄셈)
SELECT m.name AS member_name, m.phone, b.title AS book_title, r.rented_at,
       CAST(JULIANDAY('now') - JULIANDAY(r.rented_at) AS INTEGER) AS overdue_days
FROM rental r
INNER JOIN member m ON r.member_id = m.id
INNER JOIN book b   ON r.book_id   = b.id
WHERE r.status = 'RENTED'                                  -- 조건 1: 아직 반납 안 함
  AND JULIANDAY('now') - JULIANDAY(r.rented_at) > 7        -- 조건 2: 연체 기준 7일 초과
ORDER BY overdue_days DESC;

