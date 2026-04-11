# 🏠   [Go Main](../../README.md)   🏠
- [Load Balancing 이란?](#load-balancing-이란)
- [Load Balancer 의 종류](#load-balancer-의-종류)
- [Load Balancing 알고리즘](#load-balancing-알고리즘)
- [Scale-Up vs Scale-Out](#scale-up-vs-scale-out)
- [CDN 이란?](#cdn-이란)
- [CDN 의 동작 원리](#cdn-의-동작-원리)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# Load Balancing 이란?
- 여러 대의 서버에 트래픽을 **분산** 시켜 **성능과 가용성** 을 향상시키는 기술이다.
- 한 서버에 부하가 집중되는 것을 방지하고, 일부 서버 장애 시에도 서비스를 유지할 수 있다.

### 주요 이점
- **부하 분산** : 여러 서버로 요청을 나눠 처리
- **가용성 향상** : 한 서버가 죽어도 다른 서버가 처리
- **확장성** : 서버를 추가하면 자동으로 트래픽 분산
- **Failover** : 장애 서버 자동 제외

<br><br><br>

# Load Balancer 의 종류

### L4 Load Balancer (Transport Layer)
- **IP 주소** 와 **Port** 를 기반으로 분산한다.
- TCP / UDP 레벨에서 동작해 빠르다.
- 패킷의 내용은 확인하지 않는다.

### L7 Load Balancer (Application Layer)
- **HTTP 헤더, URL, Cookie** 등 애플리케이션 레벨 정보를 기반으로 분산한다.
- URL 별로 다른 서버로 라우팅 가능 (`/api` → API 서버, `/images` → 이미지 서버)
- SSL Termination 기능을 제공할 수 있다.
- L4 보다 느리지만 **정교한 제어** 가 가능하다.

### 대표적인 구현체
- **Software** : Nginx, HAProxy, Envoy
- **Cloud** : AWS ALB / NLB, GCP Load Balancer

<br><br><br>

# Load Balancing 알고리즘

### 1. Round Robin
- 서버에 **순차적으로** 요청을 할당한다.
- 구현이 간단하지만 서버의 성능이 다르면 비효율적.

### 2. Weighted Round Robin
- 각 서버에 가중치를 부여해 성능 좋은 서버에 더 많은 요청을 보낸다.

### 3. Least Connection
- 현재 **연결 수가 가장 적은** 서버에 할당한다.
- 요청 처리 시간이 제각각인 환경에서 효과적.

### 4. Least Response Time
- **응답 시간이 가장 빠른** 서버에 할당한다.

### 5. IP Hash
- 클라이언트 IP 를 해시해 **항상 같은 서버** 로 라우팅한다.
- Session Affinity (세션 유지) 가 필요할 때 사용.

### 6. Random
- 무작위로 서버에 할당.

<br><br><br>

# Scale-Up vs Scale-Out

| 구분 | Scale-Up (수직 확장) | Scale-Out (수평 확장) |
|---|---|---|
| 방식 | 서버의 성능(CPU/RAM) 향상 | 서버 대수 증가 |
| 비용 | 초기 비용 낮음, 한계 있음 | 분산 처리 구조 필요 |
| 확장성 | 제한적 (하드웨어 한계) | 이론상 무제한 |
| 장애 | 단일 장애점 | 장애 내성 우수 |
| 적합한 경우 | 관계형 DB, 정합성 중요 | 웹 서버, NoSQL, MSA |

- **Load Balancing 은 Scale-Out 을 가능하게 하는 핵심 기술이다.**

<br><br><br>

# CDN 이란?
- **Content Delivery Network** 의 약자이다.
- 전 세계에 분산된 **Edge Server** 에 콘텐츠를 캐시해 사용자에게 **가까운 서버에서** 콘텐츠를 제공하는 네트워크이다.
- 정적 콘텐츠 (이미지, CSS, JS, 동영상) 전송에 주로 사용된다.

### 주요 이점
- **지연 시간 (Latency) 감소** : 사용자와 가까운 서버에서 응답
- **Origin Server 부하 감소** : 대부분의 요청을 Edge 에서 처리
- **대역폭 절약**
- **DDoS 방어** : 트래픽을 여러 Edge 로 분산

### 대표 서비스
- **Cloudflare**, **AWS CloudFront**, **Akamai**, **Fastly**, **KakaoCloud CDN**

<br><br><br>

# CDN 의 동작 원리

```
[User (Seoul)] → [Edge Server (Seoul)] ← (cache miss) → [Origin Server (US)]
                     ↓ (cache hit)
                  빠른 응답
```

### 동작 과정
1. 사용자가 콘텐츠 요청 (예 : `image.png`)
2. DNS 가 사용자 위치에 가장 가까운 **Edge Server** 의 IP 를 반환 (GSLB)
3. Edge Server 가 캐시를 확인
   - **Cache Hit** : 즉시 응답
   - **Cache Miss** : Origin Server 에서 가져와 캐시 후 응답
4. 이후 동일 요청은 Edge 에서 즉시 응답

### 캐시 정책
- **Cache-Control** 헤더로 캐시 유효 시간 설정
- **ETag** / **Last-Modified** 로 변경 여부 확인
- **Purge** / **Invalidation** : 특정 콘텐츠를 캐시에서 삭제

<br><br><br>

# 면접 예상 질문
- **Q. Load Balancer 는 왜 필요한가요?**
  - 단일 서버로는 대량의 트래픽을 처리하기 어렵고, 서버 장애 시 서비스가 중단될 위험이 있습니다. Load Balancer 를 통해 여러 서버에 트래픽을 분산하면 성능과 가용성이 모두 향상되고, 무중단 배포도 가능해집니다.

- **Q. L4 와 L7 Load Balancer 의 차이는?**
  - L4 는 IP 와 Port 기반으로 동작해 빠르지만 단순합니다. L7 은 HTTP 헤더, URL, Cookie 를 기반으로 세밀한 라우팅이 가능해 URL 경로별 라우팅, SSL Termination, 콘텐츠 기반 라우팅 등 복잡한 제어가 가능합니다.

- **Q. Round Robin 방식의 단점은?**
  - 모든 서버에 순차적으로 요청을 분배하므로 서버 성능이 다르거나 요청 처리 시간이 들쭉날쭉하면 부하가 균등하지 않을 수 있습니다. 이럴 때는 **Weighted Round Robin** 이나 **Least Connection** 방식이 더 효과적입니다.

- **Q. CDN 을 사용하면 어떤 이점이 있나요?**
  - 사용자와 지리적으로 가까운 Edge Server 에서 콘텐츠를 제공하므로 **응답 속도가 빨라지고** , Origin Server 의 부하가 감소하며, 대역폭 비용이 절약됩니다. 또한 분산 특성으로 DDoS 공격에 대한 방어력도 높아집니다.

- **Q. Session 을 사용하는 서비스에서 Load Balancing 을 할 때 문제점은?**
  - 사용자의 요청이 매번 다른 서버로 갈 수 있어 Session 이 일관되지 않는 문제가 생깁니다. 해결책으로는 (1) **Sticky Session** 으로 같은 사용자를 같은 서버로 보내거나, (2) **Redis 같은 중앙 Session Store** 를 사용해 서버 간 세션을 공유하거나, (3) **JWT 같은 Stateless 인증** 으로 전환하는 방법이 있습니다.
