# 🏠   [Go Main](../../README.md)   🏠
- [Index 란?](#index-란)
- [Index 의 자료구조](#index-의-자료구조)
- [Index 의 종류](#index-의-종류)
- [Index 의 장단점](#index-의-장단점)
- [Index 를 사용해야 할 때](#index-를-사용해야-할-때)
- [Index 가 동작하지 않는 경우](#index-가-동작하지-않는-경우)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# Index 란?
- 데이터베이스 테이블의 검색 성능을 향상시키기 위한 **자료구조** 이다.
- 책의 **목차** 에 비유할 수 있다. 목차를 통해 원하는 내용을 빠르게 찾을 수 있듯이, Index 를 통해 원하는 레코드를 빠르게 찾을 수 있다.
- 실제 데이터가 저장된 테이블과는 별도의 저장 공간에 `(Key, Pointer)` 형태로 저장된다.

<br><br><br>

# Index 의 자료구조

### 1. B-Tree / B+Tree
- 대부분의 RDBMS 에서 사용되는 Index 자료구조이다.
- **균형 트리** 로, 모든 리프 노드까지의 거리가 동일해 검색 시간이 일정하다 `O(log N)`.
- **B+Tree** 는 리프 노드끼리 Linked List 로 연결되어 있어 **범위 검색** 에 유리하다.
- 등치(=) 검색과 범위(>, <, BETWEEN) 검색 모두에 적합하다.

### 2. Hash Index
- Hash Table 기반으로, 등치 검색 `O(1)` 에 매우 빠르다.
- 단점 : 범위 검색과 정렬에 사용할 수 없다.
- MySQL 의 MEMORY 엔진 등에서 사용한다.

<br><br><br>

# Index 의 종류

### Clustered Index (클러스터드 인덱스)
- **실제 데이터** 가 Index 순서대로 정렬되어 저장된다.
- 테이블당 **하나만** 존재할 수 있다.
- 보통 **기본키(PK)** 에 자동으로 생성된다.
- 범위 검색에 매우 빠르다.

### Non-Clustered Index (논클러스터드 인덱스 / Secondary Index)
- Index 는 정렬되어 있지만, **실제 데이터는 정렬되지 않는다.**
- Index 가 실제 데이터의 위치를 가리키는 포인터를 저장한다.
- 테이블당 **여러 개** 생성 가능하다.

### Unique Index
- 중복을 허용하지 않는 Index.
- PK, UNIQUE 제약조건에 자동 생성된다.

### Composite Index (복합 Index)
- 여러 컬럼을 묶어서 만드는 Index.
- Index 의 **순서가 중요하다.** `(A, B)` 로 만든 Index 는 `A` 만으로 검색할 수 있지만, `B` 만으로는 사용할 수 없다.

<br><br><br>

# Index 의 장단점

### 장점
- **검색 속도** 가 매우 빨라진다 (특히 `WHERE`, `JOIN`, `ORDER BY`).
- 시스템의 전체 부하를 줄일 수 있다.

### 단점
- **추가 저장 공간** 이 필요하다 (보통 테이블 크기의 10% 정도).
- **INSERT, UPDATE, DELETE** 시 Index 도 함께 갱신되어야 해 쓰기 성능이 저하된다.
- 잘못 설계하면 오히려 성능이 떨어질 수 있다.

<br><br><br>

# Index 를 사용해야 할 때
- 데이터가 많고 **조회가 빈번한** 컬럼
- `WHERE` 절에 자주 사용되는 컬럼
- `JOIN` 에 사용되는 컬럼 (특히 외래키)
- `ORDER BY`, `GROUP BY` 에 자주 사용되는 컬럼
- **Cardinality 가 높은** 컬럼 (값의 종류가 다양한 컬럼)

### Index 를 피해야 할 때
- 데이터가 적은 테이블
- `INSERT / UPDATE / DELETE` 가 빈번한 테이블
- Cardinality 가 낮은 컬럼 (예 : 성별, 불리언 값)

<br><br><br>

# Index 가 동작하지 않는 경우
- Index 컬럼에 **함수나 연산** 을 사용할 때 : `WHERE YEAR(created_at) = 2024`
- **데이터 타입이 다른** 값으로 비교할 때 (암묵적 형변환)
- `LIKE '%keyword'` 처럼 **앞에 와일드카드** 가 있을 때
- `OR` 연산자 사용 시 (일부 경우)
- `NOT`, `!=`, `<>` 등 부정 조건
- 복합 Index 에서 **선행 컬럼** 을 조건에 사용하지 않을 때

<br><br><br>

# 면접 예상 질문
- **Q. Index 를 사용하면 항상 빠른가요?**
  - 아닙니다. Index 는 조회 성능을 향상시키지만, 데이터 변경 (INSERT / UPDATE / DELETE) 시 Index 도 함께 갱신되어야 해 쓰기 성능이 저하됩니다. 또한 Cardinality 가 낮거나 데이터가 적은 테이블에서는 오히려 느려질 수 있습니다.

- **Q. B-Tree 가 아닌 Hash Index 를 쓰지 않는 이유는?**
  - Hash Index 는 등치 검색에는 빠르지만 범위 검색이나 정렬에 사용할 수 없습니다. 실무에서는 범위 조건이 많기 때문에 대부분의 RDBMS 가 B-Tree (정확히는 B+Tree) 를 기본 자료구조로 사용합니다.

- **Q. Clustered Index 와 Non-Clustered Index 의 차이는?**
  - Clustered Index 는 실제 데이터가 Index 순서대로 저장되어 있어 한 테이블에 하나만 존재할 수 있고 범위 검색이 빠릅니다. Non-Clustered Index 는 데이터의 위치를 가리키는 포인터를 저장하며 한 테이블에 여러 개 생성할 수 있습니다.

- **Q. 복합 Index `(A, B, C)` 에서 `B` 만으로 검색하면 Index 를 타나요?**
  - 아니요. 복합 Index 는 왼쪽부터 순서대로 사용되어야 하므로, 선행 컬럼인 `A` 가 조건에 포함되지 않으면 Index 를 사용할 수 없습니다. `A`, `A + B`, `A + B + C` 조합만 Index 를 탈 수 있습니다.

- **Q. Cardinality 가 무엇이고 왜 중요한가요?**
  - Cardinality 는 컬럼에 저장된 값의 **고유한 개수** 입니다. Cardinality 가 높을수록 (예 : 주민번호) Index 로 필터링할 수 있는 행이 많아 효율적이고, 낮을수록 (예 : 성별) Index 의 효용이 떨어집니다.
