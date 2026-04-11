# 🏠   [Go Main](../../README.md)   🏠
- [REST 란?](#rest-란)
- [REST 의 6 가지 원칙](#rest-의-6-가지-원칙)
- [REST API](#rest-api)
- [REST API 설계 규칙](#rest-api-설계-규칙)
- [RESTful API 예시](#restful-api-예시)
- [GraphQL 과의 비교](#graphql-과의-비교)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# REST 란?
- **REST (REpresentational State Transfer)** 는 2000 년 로이 필딩(Roy Fielding) 이 자신의 박사 논문에서 소개한 웹 아키텍처 스타일이다.
- 웹의 자원을 **URI** 로 표현하고, **HTTP Method** 로 해당 자원에 대한 행위를 표현하는 방식이다.
- 특정 기술이나 언어에 종속되지 않으며, 이해하기 쉽고 유연하다.

<br><br><br>

# REST 의 6 가지 원칙

### 1. Client-Server
- 클라이언트와 서버의 역할을 분리한다.
- 클라이언트는 UI 를, 서버는 데이터 처리와 저장을 담당한다.
- 독립적으로 진화할 수 있다.

### 2. Stateless (무상태)
- 각 요청은 독립적이며, 서버는 클라이언트의 상태를 저장하지 않는다.
- 이전 요청과 무관하게 현재 요청만으로 처리되어야 한다.

### 3. Cacheable (캐시 가능)
- 응답은 캐시 가능한지 여부를 명시해야 한다.
- 클라이언트는 응답을 재사용해 성능을 향상시킬 수 있다.

### 4. Layered System (계층화)
- 클라이언트는 요청을 보내는 서버가 최종 서버인지, 중간 프록시인지 알 수 없다.
- 로드 밸런서, 캐시 서버 등을 통해 시스템을 확장할 수 있다.

### 5. Uniform Interface (균일한 인터페이스)
- REST 의 가장 핵심적인 원칙으로, 일관된 인터페이스를 제공한다.
- 4 가지 세부 원칙
  - Identification of Resources (자원 식별)
  - Manipulation of Resources through Representations (표현을 통한 자원 조작)
  - Self-Descriptive Messages (자기 서술적 메시지)
  - HATEOAS (Hypermedia As The Engine Of Application State)

### 6. Code-On-Demand (선택 사항)
- 서버가 실행 가능한 코드를 클라이언트에 전송할 수 있다. (예 : JavaScript)

<br><br><br>

# REST API
- REST 아키텍처 스타일을 따르는 API 이다.
- **RESTful API** 라고 부른다.
- 구성 요소
  - **Resource (자원)** : URI
  - **Verb (행위)** : HTTP Method
  - **Representation (표현)** : 자원의 상태를 표현하는 데이터 (JSON, XML, HTML 등)

<br><br><br>

# REST API 설계 규칙

### 1. URI 는 명사를 사용한다.
- ❌ `/getUser/1` → ✅ `/users/1`
- 동작은 HTTP Method 로 표현한다.

### 2. URI 는 복수형 명사를 사용한다.
- ❌ `/user/1` → ✅ `/users/1`

### 3. 계층 관계는 `/` 로 표현한다.
- ✅ `/users/1/posts/10`

### 4. URI 끝에는 `/` 를 붙이지 않는다.
- ❌ `/users/` → ✅ `/users`

### 5. 하이픈(-) 은 가독성을 위해, 언더스코어(_) 는 사용하지 않는다.
- ✅ `/user-profiles` (URI 가 길 때)

### 6. URI 는 소문자를 사용한다.

### 7. 파일 확장자는 URI 에 포함하지 않는다.
- ❌ `/users/1.json` → ✅ `Accept: application/json` 헤더 사용

### 8. 행위는 HTTP Method 로 표현한다.

| 행위 | HTTP Method | URI 예시 |
|---|---|---|
| 목록 조회 | GET | `/users` |
| 단일 조회 | GET | `/users/1` |
| 생성 | POST | `/users` |
| 전체 수정 | PUT | `/users/1` |
| 부분 수정 | PATCH | `/users/1` |
| 삭제 | DELETE | `/users/1` |

<br><br><br>

# RESTful API 예시

```
# 사용자 목록 조회
GET /users

# 특정 사용자 조회
GET /users/1

# 사용자 생성
POST /users
Body: { "name": "Raccoon", "email": "raccoon@example.com" }

# 사용자 정보 수정
PUT /users/1
Body: { "name": "Raccoon97", "email": "raccoon97@example.com" }

# 사용자 이메일만 수정
PATCH /users/1
Body: { "email": "new@example.com" }

# 사용자 삭제
DELETE /users/1

# 특정 사용자의 게시글 목록 조회
GET /users/1/posts

# 페이지네이션
GET /users?page=2&limit=20

# 정렬 및 필터링
GET /users?sort=name&filter=active
```

<br><br><br>

# GraphQL 과의 비교

| 구분 | REST | GraphQL |
|---|---|---|
| 엔드포인트 | 리소스마다 별도 | 단일 엔드포인트 |
| 데이터 조회 | 정해진 형태 | 클라이언트가 필요한 필드 선택 |
| Over/Under Fetching | 발생 가능 | 필요한 데이터만 조회 |
| 러닝커브 | 낮음 | 높음 |
| 캐싱 | HTTP 캐시 활용 | 별도 구현 필요 |

<br><br><br>

# 면접 예상 질문
- **Q. REST API 란 무엇인가요?**
  - REST 아키텍처 스타일을 따르는 API 로, URI 로 자원을 표현하고 HTTP Method 로 행위를 표현합니다. Stateless, Cacheable, Uniform Interface 등의 제약 조건을 따르며 클라이언트-서버 통신을 위한 표준적인 방식입니다.

- **Q. RESTful 하다는 것은 무엇을 의미하나요?**
  - REST 의 6 가지 원칙을 모두 준수하는 API 를 의미합니다. 특히 **Uniform Interface** 중 **Self-Descriptive Messages** 와 **HATEOAS** 원칙까지 지키는 것은 현실적으로 어려우므로, 많은 API 가 엄밀히 따지면 RESTful 하지 않고 "REST API 스타일" 에 가깝습니다.

- **Q. PUT 과 PATCH 의 차이는?**
  - PUT 은 리소스 전체를 교체하고, PATCH 는 리소스의 일부만 수정합니다. PUT 은 멱등성을 보장하지만 PATCH 는 구현 방식에 따라 다를 수 있습니다.

- **Q. REST 의 한계는?**
  - Over-fetching(필요 없는 데이터까지 받음) 과 Under-fetching(여러 번 요청해야 함) 문제가 있을 수 있습니다. 이를 해결하기 위해 GraphQL 이 등장했습니다. 또한 실시간 통신에는 WebSocket 이나 gRPC 등이 더 적합합니다.

- **Q. REST API 에서 상태 유지는 어떻게 하나요?**
  - REST 는 Stateless 이므로 서버에 상태를 저장하지 않습니다. 인증 상태는 보통 **JWT(Json Web Token)** 나 **Session + Cookie** 를 사용해 유지하며, JWT 는 토큰 자체에 정보가 담겨 있어 서버 확장에 유리합니다.
