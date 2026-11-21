-- =========================================================
-- 도서 대여 시스템 스키마 (SQLite)
-- 실행 순서: schema.sql → data.sql → queries.sql
-- 관계(1:N): category 1 ─ N book, member 1 ─ N rental, book 1 ─ N rental
-- =========================================================

-- [SQLite 전용] FK 제약은 기본 OFF이며, 연결(세션)마다 켜야 동작한다.
PRAGMA foreign_keys = ON;

-- 자식 → 부모 순서로 삭제 (FK 참조 순서 역순)
DROP TABLE IF EXISTS rental;
DROP TABLE IF EXISTS book;
DROP TABLE IF EXISTS member;
DROP TABLE IF EXISTS category;

-- 도서 카테고리
-- [SQLite 전용] AUTOINCREMENT (MySQL: AUTO_INCREMENT, PostgreSQL: SERIAL/IDENTITY)
CREATE TABLE category (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE                -- 카테고리명 중복 불가
);

-- 회원
CREATE TABLE member (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    email      TEXT NOT NULL UNIQUE,         -- 로그인 식별자, 중복 불가
    name       TEXT NOT NULL,
    phone      TEXT,                         -- 선택 입력
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 도서 (category 1 : N book)
CREATE TABLE book (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id    INTEGER NOT NULL,
    title          TEXT NOT NULL,
    author         TEXT NOT NULL,
    price          INTEGER NOT NULL CHECK (price >= 0),
    published_date DATE NOT NULL,
    FOREIGN KEY (category_id) REFERENCES category(id)
);

-- 대여 기록 (member 1 : N rental, book 1 : N rental)
CREATE TABLE rental (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id   INTEGER NOT NULL,
    book_id     INTEGER NOT NULL,
    rented_at   DATETIME NOT NULL,
    returned_at DATETIME,                    -- NULL = 아직 반납 안 함
    status      TEXT NOT NULL CHECK (status IN ('RENTED', 'RETURNED')),  -- 오타 값 입력 방지
    FOREIGN KEY (member_id) REFERENCES member(id),
    FOREIGN KEY (book_id)   REFERENCES book(id)
);
