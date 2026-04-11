# 🏠   [Go Main](../../README.md)   🏠
- [Deadlock 이란?](#deadlock-이란)
- [Deadlock 발생 조건](#deadlock-발생-조건)
- [Deadlock 해결 방법](#deadlock-해결-방법)
- [Starvation (기아 상태)](#starvation-기아-상태)
- [iOS 에서의 Deadlock 예시](#ios-에서의-deadlock-예시)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# Deadlock 이란?
- 두 개 이상의 프로세스(또는 스레드) 가 서로가 가지고 있는 자원을 무한정 기다리면서 아무도 진행할 수 없는 상태를 의미한다.
- 프로세스가 원하는 자원을 획득하지 못해 다음 실행으로 넘어가지 못하는 상태이다.

```
Thread A : Lock(X) 획득 → Lock(Y) 대기
Thread B : Lock(Y) 획득 → Lock(X) 대기
→ 서로 상대방이 가진 자원을 기다리며 Deadlock 발생
```

<br><br><br>

# Deadlock 발생 조건
- Deadlock 은 **아래 4 가지 조건이 모두 동시에 충족** 되어야 발생한다. (Coffman 조건)

### 1. 상호 배제 (Mutual Exclusion)
- 한 자원은 한 번에 하나의 프로세스만 사용할 수 있다.
- 다른 프로세스가 해당 자원을 사용하려면 이전 프로세스가 자원을 반납할 때까지 기다려야 한다.

### 2. 점유 대기 (Hold and Wait)
- 하나 이상의 자원을 점유한 프로세스가 다른 프로세스가 점유한 자원을 추가로 얻기 위해 대기하는 상태이다.

### 3. 비선점 (No Preemption)
- 자원을 강제로 빼앗을 수 없다.
- 다른 프로세스가 사용 중인 자원을 빼앗을 수 없고, 자발적으로 반납할 때까지 기다려야 한다.

### 4. 순환 대기 (Circular Wait)
- 프로세스들이 순환 형태로 자원을 대기하고 있다.
- `P1 → P2 → P3 → ... → P1` 형태로 서로 대기한다.

<br><br><br>

# Deadlock 해결 방법

### 1. Deadlock 예방 (Prevention)
- 발생 조건 4 가지 중 하나 이상을 원천적으로 차단한다.
- **상호 배제 부정** : 공유 가능한 자원으로 만들기 (현실적으로 어려움)
- **점유 대기 부정** : 프로세스 시작 시 모든 자원을 한 번에 요청
- **비선점 부정** : 자원을 강제로 빼앗을 수 있게 함
- **순환 대기 부정** : 자원에 순서를 부여해 항상 그 순서대로만 요청

### 2. Deadlock 회피 (Avoidance)
- 자원 할당 시 Deadlock 가능성을 판단해 회피한다.
- 대표적으로 **Banker's Algorithm** 이 있다.
  - 자원을 할당해도 **Safe State** 가 유지되는지 확인 후 할당한다.

### 3. Deadlock 탐지 및 복구 (Detection & Recovery)
- Deadlock 발생을 허용하되, 주기적으로 탐지하고 복구한다.
- 자원 할당 그래프를 이용해 사이클을 탐지한다.
- 복구 방법 : 프로세스 종료, 자원 선점 등

### 4. Deadlock 무시 (Ignorance)
- Deadlock 발생 확률이 낮고, 처리 비용이 크다면 그냥 무시하기도 한다. (타조 알고리즘)
- UNIX, Windows 등 일부 OS 에서 채택하는 방식이다.

<br><br><br>

# Starvation (기아 상태)
- 특정 프로세스가 자원을 계속해서 할당받지 못하고 무한정 대기하는 현상이다.
- Deadlock 과 달리 시스템 전체가 멈추는 것은 아니다.
- 해결 방법 : **Aging** (대기 시간이 길수록 우선순위를 높여주는 방식)

<br><br><br>

# iOS 에서의 Deadlock 예시
- Main Queue 에서 `sync` 호출 시 Deadlock 이 발생한다.

```swift
// ❌ Deadlock 발생!
DispatchQueue.main.sync {
    print("This never runs")
}
```

- 메인 스레드는 이미 실행 중인데, 같은 스레드(Main Queue) 에 동기적(sync) 으로 작업을 제출하고 그 결과를 기다리기 때문에 서로를 기다리는 상황이 된다.
- Serial Queue 에서 자기 자신에게 `sync` 호출 시에도 동일한 문제가 발생한다.

```swift
let serialQueue = DispatchQueue(label: "com.example.serial")
serialQueue.async {
    serialQueue.sync { // ❌ Deadlock
        print("This never runs")
    }
}
```

<br><br><br>

# 면접 예상 질문
- **Q. Deadlock 이 무엇인가요?**
  - 두 개 이상의 프로세스가 서로 상대방이 가진 자원을 무한정 기다리며 진행하지 못하는 상태입니다. 상호 배제, 점유 대기, 비선점, 순환 대기 네 가지 조건이 동시에 충족될 때 발생합니다.

- **Q. Deadlock 과 Starvation 의 차이는?**
  - Deadlock 은 여러 프로세스가 서로를 기다리며 진행하지 못하는 상태이고, Starvation 은 특정 프로세스가 자원을 계속 할당받지 못해 무한 대기하는 상태입니다. Deadlock 은 시스템 전체가 멈추지만 Starvation 은 특정 프로세스만 영향을 받습니다.

- **Q. Deadlock 을 예방하는 방법은?**
  - 발생 조건 4 가지 중 하나 이상을 제거하면 됩니다. 예를 들어 자원에 순서를 부여해 항상 그 순서대로만 요청하도록 하면 순환 대기를 제거할 수 있습니다.

- **Q. iOS 에서 Deadlock 이 발생할 수 있는 상황은?**
  - 메인 큐에서 `DispatchQueue.main.sync` 를 호출하면 메인 스레드가 자기 자신을 기다리는 상태가 되어 Deadlock 이 발생합니다. 같은 Serial Queue 에 `sync` 를 호출할 때도 동일한 문제가 발생합니다.

- **Q. Banker's Algorithm 이 무엇인가요?**
  - Dijkstra 가 고안한 Deadlock 회피 알고리즘으로, 자원을 할당하기 전에 **Safe State** (모든 프로세스가 안전하게 종료될 수 있는 순서가 존재하는 상태) 가 유지되는지 미리 확인한 뒤 할당 여부를 결정합니다.
