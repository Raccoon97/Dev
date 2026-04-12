# 🏠   [Go Main](../../README.md)   🏠
- [Cache 란?](#cache-란)
- [Cache 의 계층](#cache-의-계층)
- [Cache 전략 (Caching Strategy)](#cache-전략-caching-strategy)
- [Cache 교체 알고리즘](#cache-교체-알고리즘)
- [Cache 관련 문제](#cache-관련-문제)
- [Redis](#redis)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# Cache 란?
- **자주 사용되는 데이터** 를 빠르게 접근할 수 있는 저장 공간에 임시로 저장해두는 기법이다.
- **지역성 (Locality)** 에 기반한다.
  - **시간 지역성 (Temporal Locality)** : 최근 접근한 데이터는 또 접근할 확률이 높다.
  - **공간 지역성 (Spatial Locality)** : 인접한 데이터도 곧 접근할 확률이 높다.
- 목적 : **응답 속도 향상**, **부하 감소**, **네트워크 비용 절감**

<br><br><br>

# Cache 의 계층

```
[CPU Register]  ← 가장 빠름
     ↓
[L1 / L2 / L3 Cache]
     ↓
[Main Memory (RAM)]
     ↓
[Disk (SSD / HDD)]
     ↓
[Network / Remote Storage]  ← 가장 느림
```

### 웹 서비스의 캐시 계층
- **Browser Cache** : 클라이언트 브라우저 내부
- **CDN Cache** : Edge Server 캐시
- **Web Server Cache** : Nginx, Varnish 등
- **Application Cache** : Redis, Memcached
- **Database Cache** : Query Cache, Buffer Pool

<br><br><br>

# Cache 전략 (Caching Strategy)

### 1. Cache-Aside (Lazy Loading)
- 애플리케이션이 직접 캐시를 관리한다.
- 캐시에 데이터가 있으면 사용하고, 없으면 DB 에서 조회해 캐시에 저장.
- **가장 일반적인** 전략.

```
1. Client → App : 데이터 요청
2. App → Cache : 조회
3-a. Cache Hit : 바로 반환
3-b. Cache Miss : DB 에서 조회 → Cache 에 저장 → 반환
```

- 장점 : 필요한 데이터만 캐시에 저장
- 단점 : 첫 요청은 느림 (Cache Miss)

### 2. Read-Through
- 애플리케이션은 캐시만 바라본다.
- Cache Miss 시 캐시가 직접 DB 에서 데이터를 가져와 저장.
- 애플리케이션 코드가 단순해진다.

### 3. Write-Through
- 데이터 쓰기 시 **캐시와 DB 를 동시에** 업데이트한다.
- 데이터 정합성이 높지만 쓰기 성능이 저하된다.

### 4. Write-Behind (Write-Back)
- 캐시에 먼저 쓰고, 일정 시간 후 DB 에 **비동기로** 반영한다.
- 쓰기 성능이 높지만 캐시 장애 시 데이터 유실 위험.

### 5. Write-Around
- 쓰기는 DB 에 직접 하고, 캐시는 거치지 않는다.
- 자주 읽지 않는 데이터에 적합.

<br><br><br>

# Cache 교체 알고리즘

### 1. LRU (Least Recently Used)
- **가장 오랫동안 사용되지 않은** 데이터를 제거한다.
- 가장 널리 사용되는 알고리즘.

### 2. LFU (Least Frequently Used)
- **참조 빈도가 가장 낮은** 데이터를 제거한다.
- 자주 사용되는 데이터는 유지되지만, 초기 참조가 많은 데이터가 계속 남을 수 있다.

### 3. FIFO (First In First Out)
- **가장 먼저 들어온** 데이터를 제거한다. 단순하지만 효율이 낮다.

### 4. Random
- 무작위로 선택해 제거.

<br><br><br>

# Cache 관련 문제

### 1. Cache Stampede
- 캐시가 동시에 만료되어 많은 요청이 한꺼번에 DB 로 몰리는 현상.
- 해결 : **PER 알고리즘**, **Randomized TTL**, **Lock** 사용.

### 2. Thundering Herd
- 인기 데이터의 캐시가 만료되는 순간 대량의 요청이 발생하는 현상.
- 해결 : 캐시 만료 직전에 미리 갱신 (**Pre-fetching**).

### 3. Cache Invalidation
- **"컴퓨터 과학의 가장 어려운 두 가지 : 캐시 무효화와 네이밍"** — Phil Karlton
- 데이터가 변경되었을 때 관련 캐시를 **어떻게 무효화** 할지 결정하는 것이 매우 어렵다.

### 4. Hot Key Problem
- 특정 Key 에 요청이 집중되어 캐시 서버에 부하가 몰리는 현상.
- 해결 : 복제 (Replication), 분산, 클라이언트 레벨 캐싱.

<br><br><br>

# Redis
- **Remote Dictionary Server** 의 약자이다.
- **In-Memory Key-Value Store** 로 가장 많이 사용되는 캐시 시스템.
- 단순 Key-Value 뿐 아니라 **List, Set, Hash, Sorted Set, Stream** 등 다양한 자료구조를 지원한다.

### 주요 특징
- **매우 빠름** (`O(1)` 에 가까운 성능)
- **영속성 (Persistence)** 지원 (RDB Snapshot, AOF)
- **Pub/Sub** 지원
- **Replication, Sentinel, Cluster** 로 고가용성 및 확장성 제공
- **Lua Script** 로 원자적 연산 가능

### 사용 예
- 세션 저장 (Session Store)
- 랭킹 / 리더보드 (Sorted Set)
- Rate Limiting (API 호출 제한)
- 분산 Lock
- Pub/Sub 메시징

<br><br><br>

# 면접 예상 질문
- **Q. Cache 를 사용하면 어떤 이점이 있나요?**
  - 자주 접근되는 데이터를 빠르게 제공해 **응답 속도를 향상** 시키고, **백엔드 (DB) 부하를 줄일** 수 있습니다. 또한 네트워크 비용을 절감하고 전체 시스템의 확장성을 높이는 효과가 있습니다.

- **Q. Cache Aside 와 Write Through 의 차이는?**
  - Cache Aside 는 애플리케이션이 캐시를 직접 관리하며 **Lazy Loading** 방식으로 필요한 데이터만 캐시합니다. Write Through 는 쓰기 시 캐시와 DB 를 동시에 업데이트해 정합성이 높지만 쓰기 성능이 떨어집니다. 일반적으로 읽기 중심의 서비스는 Cache Aside 를, 정합성이 중요한 경우 Write Through 를 사용합니다.

- **Q. 캐시 무효화는 왜 어려운가요?**
  - 데이터 변경이 여러 곳에서 일어날 수 있고, 어떤 캐시가 그 데이터에 의존하는지 추적하기 어렵기 때문입니다. 또한 분산 환경에서는 여러 서버의 캐시를 모두 무효화해야 해 타이밍 이슈와 일관성 문제가 발생할 수 있습니다.

- **Q. LRU 는 어떻게 구현하나요?**
  - **Doubly Linked List + Hash Map** 조합으로 `O(1)` 에 구현할 수 있습니다. Hash Map 으로 Key 를 Linked List 의 노드에 매핑하고, 접근할 때마다 해당 노드를 List 의 맨 앞으로 옮깁니다. 캐시가 가득 차면 List 의 맨 뒤 노드를 제거합니다.

- **Q. Redis 와 Memcached 의 차이는?**
  - Redis 는 **다양한 자료구조** (List, Set, Hash, Sorted Set 등) 를 지원하고 **영속성, Replication, Pub/Sub** 등을 제공합니다. Memcached 는 단순 Key-Value 만 지원하고 영속성이 없지만 더 가볍고 멀티스레드를 활용해 단순 캐싱에서는 더 빠를 수 있습니다. 실무에서는 기능이 풍부한 Redis 를 더 많이 사용합니다.
