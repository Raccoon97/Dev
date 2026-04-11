# 🏠   [Go Main](../../README.md)   🏠
- [DNS 란?](#dns-란)
- [DNS 의 구조](#dns-의-구조)
- [DNS 조회 과정](#dns-조회-과정)
- [DNS Record 종류](#dns-record-종류)
- [DNS Cache](#dns-cache)
- [DNS 관련 이슈](#dns-관련-이슈)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# DNS 란?
- **Domain Name System** 의 약자이다.
- 사람이 읽기 쉬운 **도메인 이름** (예 : `google.com`) 을 컴퓨터가 이해할 수 있는 **IP 주소** (예 : `142.250.76.46`) 로 변환해주는 시스템이다.
- 인터넷의 **전화번호부** 에 비유된다.
- 기본적으로 **UDP 53 번 포트** 를 사용한다. (응답이 크거나 Zone Transfer 시에는 TCP 사용)

<br><br><br>

# DNS 의 구조
- DNS 는 **계층적(Hierarchical)** 구조로 되어 있다.

```
            . (Root)
           /        \
         .com       .kr
        /    \        \
    google  naver    co.kr
      |       |        |
     www     www     naver
```

### 1. Root DNS Server
- DNS 의 최상위 서버. 전 세계에 **13 개** 의 논리적 루트 서버가 존재한다.
- TLD DNS Server 의 IP 주소를 알려준다.

### 2. TLD (Top-Level Domain) DNS Server
- `.com`, `.net`, `.kr` 등 최상위 도메인을 관리한다.
- Authoritative DNS Server 의 IP 주소를 알려준다.

### 3. Authoritative DNS Server
- 실제 도메인과 IP 의 매핑 정보를 가지고 있다.
- 도메인 구입 시 등록기관에 등록되는 서버이다.

### 4. Recursive DNS Resolver (로컬 DNS)
- 클라이언트의 요청을 받아 Root → TLD → Authoritative 순으로 **재귀적으로** 조회한다.
- 보통 ISP (KT, SKT, LG) 가 운영하거나 `8.8.8.8` (Google), `1.1.1.1` (Cloudflare) 를 사용할 수 있다.

<br><br><br>

# DNS 조회 과정

```
[Client] ← → [Local DNS (Resolver)]
                  ↓
             [Root DNS]
                  ↓
             [TLD DNS (.com)]
                  ↓
            [Authoritative DNS (google.com)]
```

### 순서
1. 사용자가 브라우저에 `www.google.com` 입력
2. 브라우저는 먼저 **로컬 캐시** 를 확인
3. 캐시에 없으면 **Local DNS Resolver** 에 질의
4. Resolver 는 캐시에 없으면 **Root DNS Server** 에 질의 → `.com` TLD DNS IP 반환
5. **TLD DNS Server** 에 질의 → `google.com` Authoritative DNS IP 반환
6. **Authoritative DNS Server** 에 질의 → `www.google.com` 의 IP 주소 반환
7. Resolver 는 결과를 캐시에 저장하고 클라이언트에 반환
8. 클라이언트는 받은 IP 로 HTTP 요청

### 재귀적 조회 vs 반복적 조회
- **Recursive Query** : Resolver 가 클라이언트를 대신해 최종 답을 찾아줌
- **Iterative Query** : Resolver 가 각 서버에 차례로 물어보며 답을 찾아감

<br><br><br>

# DNS Record 종류

| 타입 | 설명 |
|---|---|
| **A** | 도메인 → IPv4 주소 매핑 |
| **AAAA** | 도메인 → IPv6 주소 매핑 |
| **CNAME** | 도메인 → 다른 도메인으로 Alias |
| **MX** | 메일 서버 주소 (Mail eXchange) |
| **NS** | 해당 도메인의 Name Server 정보 |
| **TXT** | 텍스트 정보 (SPF, DKIM 등 인증에 사용) |
| **PTR** | IP → 도메인 역방향 조회 |
| **SOA** | 도메인의 권한 정보 (Start of Authority) |

<br><br><br>

# DNS Cache
- DNS 조회 결과는 여러 계층에서 캐시된다.

### 캐시 계층
1. **Browser Cache** : 브라우저 자체 캐시
2. **OS Cache** : OS 의 DNS 캐시 (`ipconfig /displaydns`, `scutil --dns`)
3. **Local DNS Resolver Cache** : ISP 나 공용 DNS
4. **Authoritative DNS Cache** : 권한 서버 자체

### TTL (Time To Live)
- 각 DNS Record 에는 TTL 값이 있어 **얼마 동안 캐시될지** 를 나타낸다.
- TTL 이 짧으면 변경이 빠르게 반영되지만, DNS 트래픽이 증가한다.

<br><br><br>

# DNS 관련 이슈

### 1. DNS Spoofing / Cache Poisoning
- 공격자가 가짜 DNS 응답을 주입해 사용자를 악성 사이트로 유도하는 공격.
- 방어 : **DNSSEC** (DNS Security Extensions)

### 2. DNS over HTTPS (DoH) / DNS over TLS (DoT)
- 기존 DNS 는 평문 통신이라 도청과 변조에 취약하다.
- DoH / DoT 는 DNS 쿼리를 암호화해 프라이버시와 보안을 향상시킨다.

### 3. GSLB (Global Server Load Balancing)
- DNS 레벨에서 사용자 위치에 따라 다른 IP 를 반환해 트래픽을 분산시키는 기법.
- CDN 이 이를 활용한다.

<br><br><br>

# 면접 예상 질문
- **Q. DNS 가 필요한 이유는?**
  - 인간이 IP 주소를 기억하기 어렵기 때문입니다. 도메인 이름은 기억하기 쉽고 의미 전달이 명확한 반면, IP 주소는 숫자의 나열이라 기억이 어렵습니다. 또한 서버의 IP 가 변경되어도 도메인 이름은 그대로 유지할 수 있어 유연성이 높아집니다.

- **Q. `www.google.com` 을 주소창에 입력하면 어떤 일이 일어나나요?**
  - 브라우저 → OS → Local DNS Resolver 순으로 캐시를 확인하고, 없으면 Resolver 가 Root → TLD → Authoritative DNS 를 거쳐 IP 주소를 가져옵니다. 그 후 TCP 3-way handshake → TLS handshake → HTTP 요청 → 응답 → 렌더링 순으로 진행됩니다.

- **Q. DNS 는 왜 UDP 를 사용하나요?**
  - DNS 쿼리와 응답은 크기가 작고 빠른 응답이 중요하기 때문입니다. TCP 의 3-way handshake 오버헤드를 피하고, 작은 데이터는 재전송 비용이 적어 UDP 가 효율적입니다. 응답이 크거나 (512 byte 초과) Zone Transfer 시에는 TCP 를 사용합니다.

- **Q. CNAME 과 A 레코드의 차이는?**
  - A 레코드는 도메인을 **IP 주소** 에 직접 매핑하고, CNAME 은 도메인을 **다른 도메인** 에 매핑합니다. 예를 들어 `blog.example.com` 을 `example.github.io` 에 CNAME 으로 연결하면, `example.github.io` 의 IP 가 바뀌어도 자동으로 따라갑니다.

- **Q. TTL 값을 짧게 설정하면 어떤 장단점이 있나요?**
  - 짧으면 도메인 변경 사항이 빠르게 전파되지만, DNS 서버 부하가 증가하고 응답 지연이 생길 수 있습니다. 길면 반대로 변경 반영이 느리지만 성능이 좋습니다. 일반적으로 안정된 서비스는 길게 설정하고, 마이그레이션 직전에는 짧게 조정합니다.
