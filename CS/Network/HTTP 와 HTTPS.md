# 🏠   [Go Main](../../README.md)   🏠
- [HTTP](#http)
- [HTTP 의 특징](#http-의-특징)
- [HTTP Method](#http-method)
- [HTTP Status Code](#http-status-code)
- [HTTPS](#https)
- [SSL/TLS Handshake](#ssltls-handshake)
- [HTTP 버전별 변화](#http-버전별-변화)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# HTTP
- **HyperText Transfer Protocol** 의 약자로, 웹에서 데이터를 주고받기 위한 응용 계층(7 계층) 프로토콜이다.
- 클라이언트가 요청(Request) 을 보내면 서버가 응답(Response) 을 반환하는 **Request-Response** 구조이다.
- 기본적으로 TCP 기반이며, 80 번 포트를 사용한다. (HTTP/3 부터는 UDP 기반의 QUIC 를 사용)

<br><br><br>

# HTTP 의 특징

### 1. Stateless (무상태)
- 각 요청은 독립적이며, 서버는 이전 요청의 상태를 저장하지 않는다.
- 장점 : 서버 구현이 단순해지고, 스케일 아웃이 쉽다.
- 단점 : 로그인 상태 등을 유지하려면 Cookie, Session, Token 등의 추가 메커니즘이 필요하다.

### 2. Connectionless (비연결성)
- 요청-응답이 끝나면 연결을 종료한다.
- 단점 : 매 요청마다 연결을 새로 맺어야 해서 오버헤드가 크다.
- HTTP/1.1 부터 **Keep-Alive** 로 연결을 재사용할 수 있게 개선되었다.

<br><br><br>

# HTTP Method

| Method | 설명 | 멱등성 | 안전 |
|---|---|---|---|
| **GET** | 리소스 조회 | O | O |
| **POST** | 리소스 생성, 데이터 처리 | X | X |
| **PUT** | 리소스 전체 수정 (없으면 생성) | O | X |
| **PATCH** | 리소스 부분 수정 | X | X |
| **DELETE** | 리소스 삭제 | O | X |
| **HEAD** | GET 과 동일하나 응답 본문 없음 | O | O |
| **OPTIONS** | 서버가 지원하는 메서드 확인 | O | O |

- **멱등성 (Idempotent)** : 같은 요청을 여러 번 보내도 결과가 동일함
- **안전 (Safe)** : 서버의 상태를 변경하지 않음

<br><br><br>

# HTTP Status Code

| 범위 | 의미 | 예시 |
|---|---|---|
| 1xx | Informational | 100 Continue |
| 2xx | Success | 200 OK, 201 Created, 204 No Content |
| 3xx | Redirection | 301 Moved Permanently, 302 Found, 304 Not Modified |
| 4xx | Client Error | 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 409 Conflict, 429 Too Many Requests |
| 5xx | Server Error | 500 Internal Server Error, 502 Bad Gateway, 503 Service Unavailable, 504 Gateway Timeout |

<br><br><br>

# HTTPS
- **HyperText Transfer Protocol Secure** 의 약자로, HTTP 에 **SSL/TLS** 를 결합해 암호화한 프로토콜이다.
- 기본 포트는 **443** 번이다.
- 제공하는 보안 기능
  1. **기밀성 (Confidentiality)** : 데이터를 암호화해 엿보는 것을 방지한다.
  2. **무결성 (Integrity)** : 데이터가 전송 중 변조되지 않았음을 보장한다.
  3. **인증 (Authentication)** : 서버(또는 클라이언트) 가 진짜임을 검증한다.

### 대칭키 vs 비대칭키
- **대칭키 (Symmetric Key)** : 송수신 측이 동일한 키를 사용. 빠르지만 키 공유가 어렵다.
- **비대칭키 (Asymmetric Key, Public Key)** : 공개키와 개인키를 사용. 안전하지만 느리다.
- HTTPS 는 **비대칭키로 대칭키를 안전하게 교환한 후, 실제 데이터는 대칭키로 암호화** 해 두 방식의 장점을 모두 활용한다.

<br><br><br>

# SSL/TLS Handshake
- HTTPS 통신 시작 시 클라이언트와 서버 간에 이루어지는 보안 협상 과정이다.

```
Client                              Server
  |                                   |
  | ---- Client Hello -------------->  |   1. 클라이언트 지원 암호화 방식, 난수 전송
  |                                   |
  | <--- Server Hello ---------------- |   2. 서버가 암호화 방식 선택, 난수 전송
  |                                   |
  | <--- Certificate ----------------- |   3. 서버 인증서 (공개키 포함) 전송
  |                                   |
  | <--- Server Hello Done ----------- |
  |                                   |
  | ---- Pre-Master Secret ---------->  |   4. 클라이언트가 공개키로 암호화한 비밀값 전송
  |                                   |
  |       (양측이 Master Secret 생성)      |
  |                                   |
  | ---- Finished ------------------->  |   5. 핸드셰이크 완료
  | <--- Finished -------------------- |
  |                                   |
  | ====== 대칭키로 암호화된 통신 시작 ====    |
```

1. **Client Hello** : 클라이언트가 지원 가능한 TLS 버전, 암호화 방식, 난수를 전송
2. **Server Hello** : 서버가 사용할 TLS 버전과 암호화 방식을 선택하고 난수를 전송
3. **Certificate** : 서버가 공개키가 포함된 인증서 전송 (CA 에서 서명)
4. **Key Exchange** : 클라이언트가 생성한 Pre-Master Secret 을 서버 공개키로 암호화해 전송
5. **Session Key 생성** : 양측이 공유한 난수와 Pre-Master Secret 으로 대칭키(Session Key) 생성
6. **Finished** : 이후 모든 통신은 대칭키로 암호화되어 이루어진다.

<br><br><br>

# HTTP 버전별 변화

| 버전 | 특징 |
|---|---|
| **HTTP/0.9** | 가장 단순, GET 만 지원 |
| **HTTP/1.0** | 헤더 도입, 상태 코드 지원, 매 요청마다 새 연결 |
| **HTTP/1.1** | Keep-Alive, Pipelining, Host 헤더, 캐싱 개선 |
| **HTTP/2** | Multiplexing, Header Compression(HPACK), Server Push, Binary Protocol |
| **HTTP/3** | UDP 기반의 **QUIC** 프로토콜 사용, 0-RTT 연결, 더 빠른 핸드셰이크 |

<br><br><br>

# 면접 예상 질문
- **Q. HTTP 와 HTTPS 의 차이는 무엇인가요?**
  - HTTP 는 평문 통신이고 HTTPS 는 SSL/TLS 를 이용해 암호화된 통신입니다. HTTPS 는 기밀성, 무결성, 인증을 제공하며 443 번 포트를 사용합니다. 초기 핸드셰이크 오버헤드가 있지만, 보안이 중요한 모든 서비스에서 사용되고 있습니다.

- **Q. HTTP 가 Stateless 라는 것은 무슨 의미인가요?**
  - 각 요청이 독립적이라는 의미로, 서버는 이전 요청의 상태를 저장하지 않습니다. 로그인 상태를 유지하려면 Cookie, Session, JWT 같은 메커니즘을 추가로 사용해야 합니다.

- **Q. HTTPS 는 왜 대칭키와 비대칭키를 모두 사용하나요?**
  - 비대칭키는 안전하지만 암복호화 비용이 크고, 대칭키는 빠르지만 키 교환이 어렵습니다. 따라서 **비대칭키로 대칭키를 안전하게 교환** 하고, **실제 데이터는 빠른 대칭키로 암호화** 해 두 방식의 장점을 모두 활용합니다.

- **Q. POST 와 PUT 의 차이는?**
  - POST 는 리소스 생성이나 서버 작업 처리에 사용되며 멱등성을 보장하지 않습니다. PUT 은 리소스 전체를 덮어쓰는 업데이트에 사용되며 멱등성을 보장합니다. 같은 PUT 요청을 여러 번 보내도 결과가 동일합니다.

- **Q. HTTP/2 와 HTTP/3 의 차이는?**
  - HTTP/2 는 TCP 기반이며 Multiplexing, HPACK 압축, Server Push 등을 지원합니다. HTTP/3 는 UDP 기반의 QUIC 프로토콜을 사용해 TCP 의 Head-of-Line Blocking 문제를 해결하고 더 빠른 연결 수립과 낮은 지연 시간을 제공합니다.

- **Q. CORS 가 무엇인가요?**
  - **Cross-Origin Resource Sharing** 의 약자로, 브라우저가 다른 출처(Origin) 의 리소스를 요청할 때 적용되는 보안 정책입니다. 서버가 `Access-Control-Allow-Origin` 과 같은 헤더를 통해 특정 출처의 요청을 허용해야 합니다.
