# 🏠   [Go Main](../../README.md)   🏠
- [OSI 7계층이란?](#osi-7계층이란)
- [OSI 7계층 구조](#osi-7계층-구조)
- [TCP/IP 모델과의 비교](#tcpip-모델과의-비교)
- [Encapsulation 과 Decapsulation](#encapsulation-과-decapsulation)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# OSI 7계층이란?
- **OSI (Open Systems Interconnection)** 7 계층은 국제표준화기구(ISO) 에서 정의한 네트워크 통신 모델이다.
- 네트워크 통신 과정을 7 단계로 나누어 각 계층의 역할을 명확히 하고, 표준화된 방식으로 통신이 이루어지도록 한다.
- 각 계층은 독립적이며, 특정 계층에 문제가 생기면 해당 계층만 수정하면 되므로 유지보수가 용이하다.

<br><br><br>

# OSI 7계층 구조

```
+---------------------+
| 7. Application      | ← 사용자가 직접 접하는 계층
+---------------------+
| 6. Presentation     |
+---------------------+
| 5. Session          |
+---------------------+
| 4. Transport        |
+---------------------+
| 3. Network          |
+---------------------+
| 2. Data Link        |
+---------------------+
| 1. Physical         | ← 실제 하드웨어 계층
+---------------------+
```

### 1. Physical Layer (물리 계층)
- 전기적/기계적 신호를 통해 데이터를 비트(bit) 단위로 전송한다.
- 장비 : Cable, Repeater, Hub
- 프로토콜 : RS-232, Ethernet (물리적 측면)

### 2. Data Link Layer (데이터 링크 계층)
- 물리 계층으로 송수신되는 정보의 오류와 흐름을 관리해 신뢰성 있는 전송을 보장한다.
- 데이터 단위 : **Frame**
- 주소 : **MAC Address**
- 장비 : Switch, Bridge
- 프로토콜 : Ethernet, PPP, HDLC

### 3. Network Layer (네트워크 계층)
- 네트워크상에서 데이터를 전송할 최적의 경로를 결정한다. (Routing)
- 데이터 단위 : **Packet**
- 주소 : **IP Address**
- 장비 : Router, L3 Switch
- 프로토콜 : **IP**, ICMP, ARP, RIP, OSPF

### 4. Transport Layer (전송 계층)
- 종단 간(End-to-End) 신뢰성 있는 데이터 전송을 담당한다.
- 오류 검출, 흐름 제어, 혼잡 제어 등을 수행한다.
- 데이터 단위 : **Segment**
- 주소 : **Port Number**
- 프로토콜 : **TCP, UDP**

### 5. Session Layer (세션 계층)
- 양 끝단의 응용 프로세스 간 통신 세션을 관리한다.
- 세션의 시작, 유지, 종료를 담당한다.
- 프로토콜 : NetBIOS, SSH, TLS (일부)

### 6. Presentation Layer (표현 계층)
- 데이터 형식을 변환한다. (인코딩/디코딩, 암호화/복호화, 압축/해제)
- 프로토콜 : JPEG, MPEG, ASCII, SSL/TLS

### 7. Application Layer (응용 계층)
- 사용자가 직접 접하는 응용 프로그램의 인터페이스를 제공한다.
- 프로토콜 : **HTTP, HTTPS, FTP, SMTP, DNS, DHCP**

<br><br><br>

# TCP/IP 모델과의 비교

| OSI 7 Layer | TCP/IP 4 Layer | TCP/IP 5 Layer |
|---|---|---|
| Application | Application | Application |
| Presentation | Application | Application |
| Session | Application | Application |
| Transport | Transport | Transport |
| Network | Internet | Internet |
| Data Link | Network Access | Data Link |
| Physical | Network Access | Physical |

- OSI 7 계층은 이론적인 모델이며, 실제 인터넷은 TCP/IP 모델을 기반으로 동작한다.

<br><br><br>

# Encapsulation 과 Decapsulation
- **Encapsulation (캡슐화)** : 송신 측에서 상위 계층의 데이터에 각 계층의 헤더를 붙여 하위 계층으로 전달하는 과정
- **Decapsulation (역캡슐화)** : 수신 측에서 각 계층의 헤더를 제거하며 상위 계층으로 전달하는 과정

```
송신 측 (Encapsulation)
Application Data
→ + Header (Transport) → Segment
→ + Header (Network) → Packet
→ + Header (Data Link) + Trailer → Frame
→ Bits
```

<br><br><br>

# 면접 예상 질문
- **Q. OSI 7 계층을 나눈 이유는 무엇인가요?**
  - 계층별로 역할을 분리하면 각 계층이 독립적으로 발전할 수 있고, 특정 계층에 문제가 생겨도 전체를 수정할 필요 없이 해당 계층만 수정하면 됩니다. 또한 표준화를 통해 다양한 제조사의 장비와 소프트웨어가 호환되도록 할 수 있습니다.

- **Q. 라우터와 스위치의 차이는 무엇인가요?**
  - 스위치는 Data Link Layer(2 계층) 에서 MAC 주소를 기반으로 같은 네트워크 내의 장비들 간 통신을 담당하고, 라우터는 Network Layer(3 계층) 에서 IP 주소를 기반으로 서로 다른 네트워크 간의 통신 경로를 결정합니다.

- **Q. TCP 는 몇 계층에서 동작하나요?**
  - TCP 는 Transport Layer(4 계층) 에서 동작하며, 종단 간 신뢰성 있는 데이터 전송을 담당합니다.

- **Q. HTTPS 는 어느 계층에서 암호화가 이루어지나요?**
  - HTTPS 는 SSL/TLS 를 사용하며, SSL/TLS 는 보통 Presentation Layer(6 계층) 또는 Session Layer(5 계층) 에서 동작한다고 봅니다. 실제로는 Application Layer 와 Transport Layer 사이에서 동작한다고도 설명할 수 있습니다.

- **Q. OSI 계층 중 Session Layer 와 Presentation Layer 의 실제 역할은?**
  - 이 두 계층은 현대 네트워크에서는 명확히 구분되어 동작하지 않습니다. TCP/IP 모델에서는 이들의 역할이 Application Layer 에 포함되어 있으며, SSL/TLS 와 같은 프로토콜이 이 역할을 수행합니다.
