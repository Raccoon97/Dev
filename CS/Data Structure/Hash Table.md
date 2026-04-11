# 🏠   [Go Main](../../README.md)   🏠
- [Hash Table](#hash-table)
- [Hash Function](#hash-function)
- [Hash Collision](#hash-collision)
- [Resizing](#resizing)
- [Swift 의 Dictionary 와 Hashable](#swift-의-dictionary-와-hashable)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# Hash Table
- Key 와 Value 의 쌍으로 데이터를 저장하는 자료구조이다.
- **Hash Function** 을 통해 Key 를 해시값으로 변환하고, 이를 배열의 인덱스로 사용해 데이터에 접근한다.
- 평균적으로 **삽입, 삭제, 탐색 연산 모두 `O(1)`** 의 시간복잡도를 가진다.
- 단, Hash Collision 이 많이 발생하면 최악의 경우 `O(n)` 까지 느려질 수 있다.

```
Key → Hash Function → Hash → Index → Value
```

<br><br><br>

# Hash Function
- 임의의 길이의 데이터를 고정된 길이의 데이터로 매핑하는 함수이다.
- 좋은 해시 함수의 조건
  - **균등 분포 (Uniform Distribution)** : 해시값이 골고루 분포되어야 Collision 을 줄일 수 있다.
  - **결정적 (Deterministic)** : 동일한 입력에 대해 항상 동일한 해시값을 반환해야 한다.
  - **빠른 계산** : 해시 계산이 빨라야 한다.
- 대표적인 해시 함수
  - Division Method : `h(k) = k mod m`
  - Multiplication Method : `h(k) = ⌊m * (k * A mod 1)⌋`
  - Universal Hashing

<br><br><br>

# Hash Collision
- 서로 다른 Key 가 동일한 Hash 값을 갖는 현상을 말한다.
- 비둘기집 원리에 의해 완벽한 해싱은 불가능하므로, Collision 해결 방법이 반드시 필요하다.

### 해결 방법 1. Chaining (Separate Chaining)
- 해시 충돌이 발생한 경우 해당 인덱스에 LinkedList 등으로 데이터를 연결해 저장한다.
- 장점 : 구현이 간단하고, 메모리를 효율적으로 사용할 수 있다.
- 단점 : LinkedList 탐색에 `O(n)` 이 소요될 수 있으며, 메모리 할당 오버헤드가 존재한다.

### 해결 방법 2. Open Addressing
- 해시 충돌이 발생한 경우 다른 빈 슬롯을 찾아 저장하는 방식이다.
- 종류
  - **Linear Probing (선형 탐사)** : 다음 인덱스를 순차적으로 탐색한다. 특정 영역에 데이터가 몰리는 **Clustering** 현상이 발생할 수 있다.
  - **Quadratic Probing (제곱 탐사)** : `1, 4, 9, 16 ...` 씩 건너뛰며 탐색해 Clustering 을 완화한다.
  - **Double Hashing (이중 해싱)** : 또 다른 해시 함수를 이용해 간격을 결정한다. Clustering 이 거의 없으나 계산 비용이 높다.

<br><br><br>

# Resizing
- Hash Table 의 원소 개수가 일정 비율 이상 차게 되면 (보통 **Load Factor ≥ 0.75**) Hash Table 의 크기를 늘리고 기존 원소들을 재배치해야 한다.
- 이를 통해 Collision 빈도를 줄이고 평균 `O(1)` 성능을 유지할 수 있다.
- Resizing 자체는 `O(n)` 이 소요되지만, 자주 발생하지 않으므로 amortized 시간은 `O(1)` 이다.

<br><br><br>

# Swift 의 Dictionary 와 Hashable
- Swift 의 `Dictionary` 와 `Set` 은 내부적으로 Hash Table 로 구현되어 있다.
- Key 로 사용되는 타입은 반드시 `Hashable` 프로토콜을 준수해야 한다.
- Swift 의 기본 타입 (`Int`, `String`, `Double` 등) 은 이미 `Hashable` 을 준수하고 있으며, 사용자 정의 타입의 경우 모든 저장 프로퍼티가 `Hashable` 이라면 자동으로 `Hashable` 을 준수하도록 컴파일러가 합성해준다.

```swift
struct User: Hashable {
    let id: Int
    let name: String
}

var map: [User: Int] = [:]
map[User(id: 1, name: "Raccoon")] = 100
```

- Swift 는 **Hash Flooding 공격** 을 방지하기 위해 프로세스마다 다른 Seed 를 사용한다. 따라서 동일한 값이라도 프로세스마다 해시값이 다를 수 있다.

<br><br><br>

# 면접 예상 질문
- **Q. Hash Table 의 평균 시간복잡도는 왜 `O(1)` 인가요?**
  - 좋은 해시 함수를 사용하면 Key 가 해시값으로 균등하게 분포되고, 해시값을 인덱스로 사용하므로 배열의 Random Access 와 동일하게 `O(1)` 에 데이터에 접근할 수 있기 때문입니다. 다만 Collision 이 많이 발생하면 최악 `O(n)` 까지 느려질 수 있습니다.

- **Q. Chaining 과 Open Addressing 중 어떤 것이 더 좋은가요?**
  - 상황에 따라 다릅니다. 데이터 양이 많고 Load Factor 가 높을 때는 Chaining 이 유리하고, 캐시 친화성이 중요한 작은 크기의 데이터셋에는 Open Addressing 이 유리합니다.

- **Q. Dictionary 의 Key 로 사용되는 타입은 어떤 조건을 만족해야 하나요?**
  - Swift 에서는 `Hashable` 프로토콜을 준수해야 하며, 이는 `Equatable` 도 함께 요구합니다. 두 객체가 같다면 (`==` 가 true) 해시값도 동일해야 한다는 규약을 지켜야 합니다.

- **Q. Hash Table 의 Load Factor 는 무엇인가요?**
  - `(저장된 원소의 수) / (Hash Table 의 크기)` 로, 이 값이 높아질수록 Collision 확률이 증가합니다. 일반적으로 0.75 를 임계값으로 두고 이를 넘으면 Resizing 을 수행합니다.
