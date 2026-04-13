# 🏠   [Go Main](../../README.md)   🏠
- [WebSocket 이란?](#websocket-이란)
- [HTTP 와 WebSocket 비교](#http-와-websocket-비교)
- [WebSocket 동작 과정](#websocket-동작-과정)
- [WebSocket 프레임 구조](#websocket-프레임-구조)
- [Socket.IO](#socketio)
- [Server-Sent Events (SSE)](#server-sent-events-sse)
- [실시간 통신 기술 비교](#실시간-통신-기술-비교)
- [활용 사례](#활용-사례)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# WebSocket 이란?
- **WebSocket** 은 클라이언트와 서버 간에 **양방향 (Full-Duplex) 통신** 을 가능하게 하는 프로토콜이다.
- 2011 년 **RFC 6455** 로 표준화되었다.
- HTTP 와 달리 한 번 연결이 수립되면 **지속적으로 연결을 유지** 하며, 양쪽에서 자유롭게 데이터를 주고받을 수 있다.
- `ws://` (비암호화) 또는 `wss://` (TLS 암호화) 스킴을 사용한다.

<br><br><br>

# HTTP 와 WebSocket 비교

| 구분 | HTTP | WebSocket |
|---|---|---|
| **통신 방식** | 단방향 (요청-응답) | 양방향 (Full-Duplex) |
| **연결 유지** | 요청마다 연결/해제 (기본) | 한 번 연결 후 지속 유지 |
| **오버헤드** | 매 요청마다 헤더 전송 | 초기 Handshake 후 헤더 오버헤드 최소화 |
| **실시간성** | Polling 으로 구현 (비효율) | 네이티브 실시간 통신 |
| **프로토콜** | `http://` / `https://` | `ws://` / `wss://` |
| **상태** | Stateless | Stateful (연결 유지) |

### HTTP Polling 의 한계
- **Short Polling** : 일정 간격으로 서버에 요청을 보내 새 데이터가 있는지 확인한다. 불필요한 요청이 많아 비효율적이다.
- **Long Polling** : 서버가 새 데이터가 생길 때까지 응답을 보류한다. Short Polling 보다 효율적이지만, 응답 후 다시 연결해야 하는 오버헤드가 있다.
- WebSocket 은 이러한 Polling 의 한계를 근본적으로 해결한다.

<br><br><br>

# WebSocket 동작 과정

### 1. Opening Handshake
- 클라이언트가 HTTP 요청으로 WebSocket 연결을 요청한다.
- `Upgrade: websocket` 헤더를 포함하여 프로토콜 전환을 요청한다.

```
// 클라이언트 요청
GET /chat HTTP/1.1
Host: server.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

```
// 서버 응답 (101 Switching Protocols)
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

- 서버가 `101 Switching Protocols` 응답을 보내면 WebSocket 연결이 수립된다.

### 2. 데이터 전송
- Handshake 이후 HTTP 가 아닌 **WebSocket 프로토콜** 로 데이터를 주고받는다.
- 클라이언트와 서버 모두 **언제든지** 메시지를 보낼 수 있다.
- 텍스트 (UTF-8) 와 바이너리 데이터를 모두 지원한다.

### 3. Closing Handshake
- 어느 한쪽이 **Close 프레임** 을 보내 연결 종료를 요청한다.
- 상대방이 Close 프레임으로 응답하면 연결이 종료된다.

<br><br><br>

# WebSocket 프레임 구조
- WebSocket 은 **프레임 (Frame)** 단위로 데이터를 전송한다.
- HTTP 와 달리 헤더가 2~14 바이트로 매우 가볍다.

| 필드 | 설명 |
|---|---|
| **FIN** | 메시지의 마지막 프레임인지 여부 (1 bit) |
| **Opcode** | 프레임 유형 (텍스트, 바이너리, Close, Ping, Pong) |
| **Mask** | 클라이언트 → 서버 데이터는 반드시 마스킹 |
| **Payload Length** | 데이터 길이 |
| **Payload Data** | 실제 전송 데이터 |

### Ping / Pong
- 연결이 유지되고 있는지 확인하기 위한 **Heartbeat** 메커니즘이다.
- 한쪽이 **Ping** 프레임을 보내면 상대방은 **Pong** 프레임으로 응답해야 한다.

<br><br><br>

# Socket.IO
- **Socket.IO** 는 WebSocket 을 기반으로 한 **라이브러리** 이다 (프로토콜이 아님).
- WebSocket 을 우선 사용하되, 지원하지 않는 환경에서는 자동으로 **Long Polling** 등으로 Fallback 한다.
- 추가 기능 :
  - **자동 재연결** : 연결이 끊어지면 자동으로 재연결을 시도한다.
  - **Room / Namespace** : 클라이언트를 그룹으로 나누어 관리할 수 있다.
  - **이벤트 기반 통신** : `emit` / `on` 으로 이벤트 이름을 지정해 통신한다.
  - **브로드캐스트** : 연결된 모든 또는 특정 클라이언트에게 메시지를 전송한다.

> **주의** : Socket.IO 클라이언트는 순수 WebSocket 서버와 통신할 수 **없고**, Socket.IO 서버도 순수 WebSocket 클라이언트와 통신할 수 **없다**. Socket.IO 는 자체 프로토콜 계층을 추가하기 때문이다.

<br><br><br>

# Server-Sent Events (SSE)
- **SSE** 는 서버에서 클라이언트로의 **단방향 실시간 통신** 을 제공한다.
- HTTP 를 기반으로 하며 별도의 프로토콜이 필요 없다.
- `text/event-stream` Content-Type 을 사용한다.

```
// 서버 응답 예시
data: {"message": "Hello"}

data: {"message": "World"}
event: notification
data: {"title": "New alert"}
```

### SSE 의 특징
- **단방향** : 서버 → 클라이언트만 가능하다.
- **자동 재연결** : 연결이 끊어지면 브라우저가 자동으로 재연결한다.
- **HTTP 기반** : 기존 HTTP 인프라 (로드 밸런서, 프록시 등) 와 호환된다.
- **텍스트만 지원** : 바이너리 데이터는 전송할 수 없다.

<br><br><br>

# 실시간 통신 기술 비교

| 구분 | WebSocket | SSE | Long Polling |
|---|---|---|---|
| **통신 방향** | 양방향 | 서버 → 클라이언트 | 양방향 (비효율) |
| **프로토콜** | WebSocket (ws/wss) | HTTP | HTTP |
| **재연결** | 직접 구현 | 자동 | 직접 구현 |
| **바이너리** | 지원 | 미지원 | 지원 |
| **브라우저 지원** | 대부분 지원 | IE 미지원 | 모두 지원 |
| **적합한 경우** | 채팅, 게임, 실시간 협업 | 알림, 피드, 주가 | 레거시 환경 |

<br><br><br>

# 활용 사례
- **실시간 채팅** : 카카오톡, Slack, Discord 등 메시지를 즉시 주고받아야 하는 서비스.
- **실시간 알림** : 푸시 알림, SNS 알림, 이메일 수신 알림.
- **금융 데이터** : 주식 시세, 암호화폐 가격 등 실시간 가격 업데이트.
- **온라인 게임** : 플레이어 간 실시간 상호작용.
- **실시간 협업** : Google Docs, Figma 등 다수 사용자가 동시에 편집하는 서비스.
- **IoT** : 센서 데이터 실시간 모니터링.

<br><br><br>

# 면접 예상 질문
- **Q. WebSocket 과 HTTP 의 차이점은?**
  - HTTP 는 **요청-응답** 기반의 단방향 통신이고, WebSocket 은 한 번 연결 후 **양방향 (Full-Duplex)** 으로 데이터를 주고받을 수 있습니다. HTTP 는 매 요청마다 헤더를 보내야 하지만, WebSocket 은 초기 Handshake 이후 가벼운 프레임으로 통신하므로 오버헤드가 적습니다.

- **Q. WebSocket 연결은 어떻게 수립되나요?**
  - 클라이언트가 HTTP 요청에 `Upgrade: websocket` 헤더를 포함하여 보내면, 서버가 `101 Switching Protocols` 로 응답하여 **프로토콜이 전환** 됩니다. 이 과정을 Opening Handshake 라 하며, 이후에는 WebSocket 프로토콜로 통신합니다.

- **Q. WebSocket 과 Socket.IO 의 차이는?**
  - WebSocket 은 **표준 프로토콜 (RFC 6455)** 이고, Socket.IO 는 WebSocket 을 기반으로 한 **라이브러리** 입니다. Socket.IO 는 자동 재연결, Room/Namespace, Fallback (Long Polling) 등의 추가 기능을 제공하지만, 순수 WebSocket 과 호환되지 않는 자체 프로토콜 계층을 가지고 있습니다.

- **Q. SSE 와 WebSocket 중 어떤 것을 선택해야 하나요?**
  - **서버에서 클라이언트로의 단방향 통신** 만 필요하면 (알림, 피드 업데이트 등) SSE 가 적합합니다. HTTP 기반이므로 인프라 호환성이 좋고, 자동 재연결도 지원합니다. **양방향 통신** 이 필요하거나 바이너리 데이터를 다뤄야 하면 (채팅, 게임 등) WebSocket 을 사용해야 합니다.

- **Q. WebSocket 의 보안 문제는?**
  - `wss://` (TLS) 를 사용해 데이터를 암호화해야 합니다. 또한 **Origin 검증** 으로 허가되지 않은 도메인의 연결을 거부하고, 인증 토큰을 Handshake 단계에서 검증해야 합니다. CSRF 와 유사한 **Cross-Site WebSocket Hijacking (CSWSH)** 공격에도 주의가 필요합니다.
