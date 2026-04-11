# 🏠   [Go Main](../../README.md)   🏠
- [SQL (관계형 DB)](#sql-관계형-db)
- [NoSQL (비관계형 DB)](#nosql-비관계형-db)
- [NoSQL 의 종류](#nosql-의-종류)
- [SQL vs NoSQL](#sql-vs-nosql)
- [CAP 이론](#cap-이론)
- [선택 기준](#선택-기준)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# SQL (관계형 DB)
- **정형화된 Schema** 를 기반으로 데이터를 테이블에 저장한다.
- 관계(Relationship) 를 이용해 데이터를 연결한다.
- **ACID** 를 보장한다.
- 대표 DBMS : MySQL, PostgreSQL, Oracle, SQL Server

<br><br><br>

# NoSQL (비관계형 DB)
- **Not Only SQL** 의 약자이다.
- Schema 가 유연하거나 없다.
- 대용량 데이터와 분산 환경에서 강점을 보인다.
- 수평 확장 (Scale-Out) 이 용이하다.
- **BASE (Basically Available, Soft state, Eventually consistent)** 를 따른다.

<br><br><br>

# NoSQL 의 종류

### 1. Key-Value Store
- `Key : Value` 의 단순한 구조.
- 가장 단순하면서 빠른 성능을 제공한다.
- 대표 : **Redis**, Memcached, DynamoDB
- 사용 예 : 세션 저장, 캐시

### 2. Document Store
- JSON, BSON 형태의 Document 로 데이터를 저장한다.
- Schema 가 유연하다.
- 대표 : **MongoDB**, CouchDB
- 사용 예 : CMS, 블로그, 상품 카탈로그

### 3. Column-Family Store
- 컬럼 단위로 데이터를 저장한다.
- 대용량 데이터의 분산 저장에 강점을 가진다.
- 대표 : **Cassandra**, HBase
- 사용 예 : 로그 분석, 시계열 데이터

### 4. Graph Database
- 노드(Node) 와 관계(Edge) 로 데이터를 표현한다.
- 복잡한 관계를 표현하는 데 유리하다.
- 대표 : **Neo4j**, Amazon Neptune
- 사용 예 : SNS 친구 관계, 추천 시스템

<br><br><br>

# SQL vs NoSQL

| 구분 | SQL | NoSQL |
|---|---|---|
| **Schema** | 고정 Schema | 유연한 Schema |
| **데이터 구조** | 테이블 (Row / Column) | Key-Value, Document, Column, Graph |
| **관계** | JOIN 으로 관계 표현 | 관계 표현이 제한적 |
| **확장** | 수직 확장 (Scale-Up) | 수평 확장 (Scale-Out) |
| **트랜잭션** | ACID 보장 | 보통 BASE |
| **일관성** | 강한 일관성 | 최종 일관성 |
| **언어** | SQL (표준화) | DB 마다 다름 |
| **사용 예** | 금융, 회계 등 정합성 중요 | 로그, 빅데이터, 실시간 분석 |

<br><br><br>

# CAP 이론
- 분산 시스템에서 다음 3 가지를 **동시에 모두 만족할 수 없다** 는 이론이다.

### C - Consistency (일관성)
- 모든 노드가 같은 시점에 같은 데이터를 보여야 한다.

### A - Availability (가용성)
- 모든 요청에 대해 정상 응답을 반환해야 한다.

### P - Partition Tolerance (분할 허용성)
- 네트워크 분할 (노드 간 통신 장애) 이 발생해도 시스템이 동작해야 한다.

### 실제 선택
- 분산 시스템에서는 **P 가 필수** 이므로, 실제로는 **CP** 와 **AP** 중에 선택하는 경우가 많다.
- **CP** : MongoDB, HBase, Redis
- **AP** : Cassandra, CouchDB, DynamoDB

<br><br><br>

# 선택 기준

### SQL 을 사용해야 할 때
- 데이터의 **정합성** 이 매우 중요한 경우 (금융, 결제)
- 관계가 명확하고 복잡한 쿼리가 필요한 경우
- Schema 가 자주 바뀌지 않는 경우

### NoSQL 을 사용해야 할 때
- **대용량** 데이터를 다룰 경우
- Schema 가 유연해야 하는 경우 (자주 바뀌거나 정해지지 않음)
- **수평 확장** 이 필요한 경우
- 빠른 읽기/쓰기가 중요한 경우 (실시간 분석, 로그)

<br><br><br>

# 면접 예상 질문
- **Q. SQL 과 NoSQL 의 차이점은?**
  - SQL 은 고정된 Schema 를 기반으로 테이블 형태로 데이터를 저장하며 ACID 를 보장하고 JOIN 을 이용한 복잡한 쿼리에 강점이 있습니다. NoSQL 은 유연한 Schema 를 가지며 수평 확장이 용이하고 대용량 데이터와 빠른 읽기/쓰기에 강점이 있습니다.

- **Q. 어떤 상황에서 NoSQL 을 선택하나요?**
  - Schema 가 자주 바뀌거나 유연해야 할 때, 대용량 데이터를 처리하고 수평 확장이 필요할 때, 또는 빠른 읽기/쓰기가 중요한 로그나 실시간 분석 시스템에서 주로 사용합니다.

- **Q. CAP 이론에 대해 설명해주세요.**
  - 분산 시스템에서 일관성(Consistency), 가용성(Availability), 분할 허용성(Partition Tolerance) 을 모두 만족할 수 없다는 이론입니다. 네트워크 분할이 발생할 수 있는 현실에서 P 는 필수이므로, 실제로는 CP 또는 AP 중 선택하게 됩니다.

- **Q. BASE 는 무엇인가요?**
  - NoSQL 에서 주로 따르는 특성으로, **Basically Available** (기본적인 가용성), **Soft state** (상태가 변할 수 있음), **Eventually consistent** (최종 일관성) 을 의미합니다. ACID 보다 일관성을 완화하고 가용성을 높인 접근입니다.

- **Q. MongoDB 와 MySQL 중 무엇을 선택하시겠어요?**
  - 서비스의 요구사항에 따라 다릅니다. 데이터의 정합성과 관계가 중요한 금융 서비스라면 MySQL 을, Schema 가 유연해야 하고 대용량 문서 데이터를 다루는 CMS 나 로그 시스템이라면 MongoDB 를 선택하겠습니다. 실무에서는 두 가지를 **용도별로 함께 사용** 하는 경우도 많습니다.
