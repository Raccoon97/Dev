# 🏠   [Go Main](../../README.md)   🏠
- [TCP (Transmission Control Protocol)](#tcp-transmission-control-protocol)
- [UDP (User Datagram Protocol)](#udp-user-datagram-protocol)
- [TCP 와 UDP 의 차이](#tcp-와-udp-의-차이)
- [TCP 3-way Handshake](#tcp-3-way-handshake)
- [TCP 4-way Handshake](#tcp-4-way-handshake)
- [TCP 흐름 제어와 혼잡 제어](#tcp-흐름-제어와-혼잡-제어)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# TCP (Transmission Control Protocol)
- **연결 지향 (Connection-Oriented)** 프로토콜이다.
- 데이터 전송 전에 연결을 수립하고, 전송이 끝나면 연결을 해제한다.
- **신뢰성 있는** 데이터 전송을 보장한다.
  - 데이터의 순서를 보장하고, 손실된 데이터는 재전송한다.
  - Checksum 을 통해 오류를 검출한다.
  - Flow Control (흐름 제어), Congestion Control (혼잡 제어) 를 수행한다.
- 1:1 통신만 가능 (Unicast)
- 사용 예 : HTTP, HTTPS, FTP, SMTP, SSH

<br><br><br>

# UDP (User Datagram Protocol)
- **비연결 지향 (Connectionless)** 프로토콜이다.
- 연결 수립 과정 없이 데이터를 바로 전송한다.
- **신뢰성을 보장하지 않는다.**
  - 데이터의 순서를 보장하지 않고, 손실되어도 재전송하지 않는다.
  - Checksum 은 지원하지만 흐름/혼잡 제어는 없다.
- 1:1, 1:N, N:M 통신 모두 가능 (Unicast, Multicast, Broadcast)
- 헤더가 단순(8 bytes) 해서 오버헤드가 적고 전송 속도가 빠르다.
- 사용 예 : DNS, DHCP, VoIP, 실시간 스트리밍, 온라인 게임

<br><br><br>

# TCP 와 UDP 의 차이

| 구분 | TCP | UDP |
|---|---|---|
| 연결 방식 | 연결 지향 (3-way handshake) | 비연결 지향 |
| 신뢰성 | 보장 | 보장하지 않음 |
| 순서 보장 | 순서대로 전달 | 순서 무관 |
| 속도 | 상대적으로 느림 | 빠름 |
| 흐름/혼잡 제어 | 있음 | 없음 |
| 헤더 크기 | 20 ~ 60 bytes | 8 bytes |
| 통신 방식 | 1:1 (Unicast) | 1:1, 1:N, N:M |
| 전송 단위 | Stream (byte 단위) | Datagram (message 단위) |

<br><br><br>

# TCP 3-way Handshake
- TCP 연결을 수립하는 과정으로, 클라이언트와 서버가 서로 준비되었음을 확인한다.

```
Client                             Server
  |                                  |
  | ---- SYN (seq=x) ------------->  |   1. SYN
  |                                  |
  | <--- SYN+ACK (seq=y, ack=x+1) -- |   2. SYN+ACK
  |                                  |
  | ---- ACK (ack=y+1) ----------->  |   3. ACK
  |                                  |
  | ====== 연결 수립 완료 ========    |
```

1. **SYN** : 클라이언트가 서버에 연결을 요청한다. (seq=x)
2. **SYN+ACK** : 서버가 클라이언트의 요청을 수락하고 자신의 연결 요청도 함께 보낸다. (seq=y, ack=x+1)
3. **ACK** : 클라이언트가 서버의 연결 요청을 수락한다. (ack=y+1)

<br><br><br>

# TCP 4-way Handshake
- TCP 연결을 해제하는 과정이다.

```
Client                             Server
  |                                  |
  | ---- FIN --------------------->  |   1. FIN
  |                                  |
  | <--- ACK ---------------------- |   2. ACK
  |                                  |
  |        (서버가 남은 데이터 전송)      |
  |                                  |
  | <--- FIN ---------------------- |   3. FIN
  |                                  |
  | ---- ACK --------------------->  |   4. ACK
  |                                  |
  | ====== 연결 종료 ============    |
```

1. **FIN** : 클라이언트가 연결 종료를 요청한다.
2. **ACK** : 서버가 요청을 수신했음을 알린다. (남은 데이터 전송 중)
3. **FIN** : 서버가 남은 데이터를 모두 보낸 후 연결 종료를 요청한다.
4. **ACK** : 클라이언트가 서버의 요청을 수신했음을 알린다.

### TIME_WAIT 상태
- 클라이언트는 마지막 ACK 를 보낸 후 **TIME_WAIT** 상태로 일정 시간(보통 2*MSL) 대기한다.
- 이유
  1. 마지막 ACK 가 손실될 경우를 대비해 서버가 재전송한 FIN 을 받을 수 있도록 한다.
  2. 같은 포트 번호에서 새 연결이 생성될 때 이전 연결의 패킷이 섞이는 것을 방지한다.

<br><br><br>

# TCP 흐름 제어와 혼잡 제어

### Flow Control (흐름 제어)
- 송신 측이 수신 측의 처리 능력을 넘어서는 속도로 데이터를 보내지 않도록 조절한다.
- **Sliding Window** 기법을 사용한다.
- 수신 측이 Window 크기를 알려주면 송신 측은 해당 크기만큼만 한 번에 전송한다.

### Congestion Control (혼잡 제어)
- 네트워크가 혼잡할 때 송신 측이 전송 속도를 조절해 네트워크 부하를 줄인다.
- 주요 알고리즘
  - **Slow Start** : 처음에는 Window 크기를 작게 시작하고 지수적으로 증가시킨다.
  - **Congestion Avoidance** : 임계값(ssthresh) 이후에는 선형적으로 증가시킨다.
  - **Fast Retransmit** : 3 개의 중복 ACK 를 받으면 타임아웃 전에 해당 세그먼트를 재전송한다.
  - **Fast Recovery** : Fast Retransmit 후 Slow Start 가 아닌 Congestion Avoidance 부터 시작한다.

<br><br><br>

# 면접 예상 질문
- **Q. TCP 와 UDP 의 차이점은?**
  - TCP 는 연결 지향 프로토콜로 신뢰성 있는 전송을 보장하며 흐름/혼잡 제어를 수행합니다. UDP 는 비연결 지향 프로토콜로 신뢰성은 없지만 오버헤드가 적고 전송이 빠릅니다. 신뢰성이 중요한 경우 TCP 를, 속도와 실시간성이 중요한 경우 UDP 를 사용합니다.

- **Q. 왜 3-way handshake 는 3 번이고 4-way handshake 는 4 번인가요?**
  - 연결 수립 시에는 서버가 클라이언트의 SYN 에 대한 ACK 와 자신의 SYN 을 함께 보낼 수 있어 3 번이면 됩니다. 하지만 연결 해제 시에는 서버가 클라이언트의 FIN 에 대한 ACK 를 먼저 보낸 뒤, 남은 데이터를 모두 전송하고 나서 자신의 FIN 을 보내야 하므로 4 번이 필요합니다.

- **Q. TIME_WAIT 상태는 왜 필요한가요?**
  - 마지막 ACK 패킷이 손실될 경우 서버가 재전송한 FIN 에 다시 응답하기 위함이고, 또 다른 이유는 같은 포트로 새로운 연결이 만들어졌을 때 이전 연결의 잔여 패킷이 섞이는 것을 방지하기 위함입니다.

- **Q. SYN Flooding 공격에 대해 아시나요?**
  - 공격자가 SYN 패킷만 대량으로 보내고 ACK 를 보내지 않아 서버의 연결 대기 큐를 가득 채워 정상 사용자의 연결을 방해하는 DDoS 공격입니다. 방어 방법으로는 SYN Cookie, 방화벽 등이 있습니다.

- **Q. UDP 인데 신뢰성이 필요한 경우 어떻게 하나요?**
  - UDP 기반으로 Application Layer 에서 신뢰성을 구현하거나, 최근에는 Google 이 만든 **QUIC** 프로토콜(HTTP/3 의 기반) 을 사용합니다. QUIC 는 UDP 위에서 동작하면서 TCP 수준의 신뢰성과 더 빠른 연결 수립을 제공합니다.
