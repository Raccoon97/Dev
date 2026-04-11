# 🏠   [Go Main](../../README.md)   🏠
- [Greedy Algorithm 이란?](#greedy-algorithm-이란)
- [Greedy 의 조건](#greedy-의-조건)
- [Greedy 의 단점](#greedy-의-단점)
- [대표 예제](#대표-예제)
- [Greedy vs DP](#greedy-vs-dp)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# Greedy Algorithm 이란?
- **탐욕 알고리즘** 으로, 각 단계에서 **지금 당장 가장 좋아 보이는** 선택을 하는 방식이다.
- **Local Optimum (지역 최적해)** 을 선택해 **Global Optimum (전역 최적해)** 에 도달하려고 한다.
- 구현이 단순하고 실행 속도가 빠르다.
- 단, **모든 문제에 적용할 수 있는 것은 아니다.**

<br><br><br>

# Greedy 의 조건
- Greedy 로 최적해를 구할 수 있으려면 다음 두 가지를 만족해야 한다.

### 1. Greedy Choice Property (탐욕적 선택 속성)
- 각 단계에서의 **지역 최적해** 가 **전역 최적해** 로 이어져야 한다.
- 이전 선택이 이후 선택에 영향을 주지 않아야 한다.

### 2. Optimal Substructure (최적 부분 구조)
- 문제의 최적 해가 하위 문제의 최적 해로 구성될 수 있어야 한다.

<br><br><br>

# Greedy 의 단점
- **항상 최적해를 보장하지는 않는다.**
- 예를 들어 동전이 `{1, 7, 10}` 이고 `14 원` 을 거슬러 줄 때
  - Greedy : `10 + 1 + 1 + 1 + 1 = 5 개`
  - 최적해 : `7 + 7 = 2 개`
- 이럴 때는 **DP** 를 사용해야 한다.
- Greedy 가 적용 가능한지 검증이 필요하다.

<br><br><br>

# 대표 예제

### 1. 동전 거스름돈 (한국 동전)
- 한국 동전 `{500, 100, 50, 10}` 은 **Greedy 로 최적해** 가 된다.
- 가장 큰 동전부터 사용하면 된다.

```swift
func coinChange(_ amount: Int) -> Int {
    let coins = [500, 100, 50, 10]
    var remain = amount
    var count = 0
    for coin in coins {
        count += remain / coin
        remain %= coin
    }
    return count
}
```

### 2. 활동 선택 문제 (Activity Selection)
- 여러 활동 중 **겹치지 않게** 가장 많은 활동을 선택하는 문제.
- 해결법 : **끝나는 시간이 빠른 순서대로** 선택한다.

```swift
func activitySelection(_ activities: [(start: Int, end: Int)]) -> Int {
    let sorted = activities.sorted { $0.end < $1.end }
    var count = 0
    var lastEnd = -1
    for activity in sorted where activity.start >= lastEnd {
        count += 1
        lastEnd = activity.end
    }
    return count
}
```

### 3. 회의실 배정
- 활동 선택 문제와 동일. 최대한 많은 회의를 한 회의실에 배정.

### 4. 배낭 문제 (Fractional Knapsack)
- 물건을 **쪼갤 수 있는** 배낭 문제는 Greedy 로 풀 수 있다.
- **가치/무게 비율** 이 높은 순으로 담는다.
- 단, **0/1 Knapsack (쪼갤 수 없음) 은 DP 로 풀어야 한다.**

### 5. 허프만 코딩 (Huffman Coding)
- 문자의 등장 빈도를 기반으로 **가변 길이 이진 코드** 를 생성해 압축하는 알고리즘.
- 가장 빈도가 낮은 두 노드를 합치는 Greedy 로 최적 코드를 만든다.

### 6. MST (Minimum Spanning Tree)
- **Kruskal** 과 **Prim** 알고리즘이 대표적인 Greedy 이다.
- Kruskal : 가장 가중치가 작은 간선부터 선택 (사이클이 생기지 않는 한)
- Prim : 현재 트리에 연결된 간선 중 가장 작은 간선을 선택

### 7. 다익스트라 (Dijkstra)
- 출발점에서 가장 가까운 노드부터 방문하며 최단 거리를 갱신.
- 매 단계에서 가장 가까운 미방문 노드를 선택하는 Greedy 접근.

<br><br><br>

# Greedy vs DP

| 구분 | Greedy | DP |
|---|---|---|
| **접근 방식** | 각 단계에서 최선 선택 | 모든 경우를 고려해 최적해 탐색 |
| **정답 보장** | 특정 조건에서만 | 항상 최적해 보장 (문제에 적용 가능할 시) |
| **속도** | 빠름 | 상대적으로 느림 |
| **메모리** | 적게 사용 | 많이 사용 (DP 테이블) |
| **구현 난이도** | 쉬움 | 어려움 (점화식) |

> Greedy 가 가능하면 Greedy, 아니면 DP 로 접근하는 것이 일반적인 전략이다.

<br><br><br>

# 면접 예상 질문
- **Q. Greedy Algorithm 이란 무엇인가요?**
  - 각 단계에서 **지금 당장 가장 좋아 보이는 선택** 을 해 전체 최적해에 도달하려는 알고리즘입니다. 구현이 간단하고 빠르지만, **Greedy Choice Property** 와 **Optimal Substructure** 를 만족하는 문제에서만 최적해를 보장합니다.

- **Q. Greedy 가 최적해를 보장하지 못하는 예시는?**
  - **0/1 Knapsack** 문제가 대표적입니다. 가치/무게 비율이 가장 높은 물건부터 담는 Greedy 전략은 물건을 쪼갤 수 없는 경우 최적해를 보장하지 못합니다. 또한 동전이 `{1, 7, 10}` 이고 14 원을 거슬러 줄 때도 Greedy 는 실패합니다.

- **Q. 한국 동전으로 거스름돈 문제를 Greedy 로 풀 수 있는 이유는?**
  - 한국 동전 `{500, 100, 50, 10}` 은 각각 **배수 관계** 에 있어, 큰 동전을 하나 사용하는 것이 항상 작은 동전 여러 개를 사용하는 것보다 낫습니다. 이처럼 **동전들이 서로 배수 관계** 일 때 Greedy 가 최적해를 보장합니다.

- **Q. Greedy 와 DP 의 차이는?**
  - Greedy 는 각 단계에서 **지역 최적해** 만을 선택해 빠르게 답을 구하고, DP 는 **모든 경우** 를 탐색한 결과를 저장해 전역 최적해를 구합니다. Greedy 가 적용 가능하면 더 빠르지만, 적용 가능 여부를 반드시 검증해야 합니다. 적용 불가능하면 DP 를 사용해야 합니다.

- **Q. 활동 선택 문제를 Greedy 로 어떻게 푸나요?**
  - **끝나는 시간이 가장 빠른 활동** 을 먼저 선택하는 것이 핵심입니다. 끝나는 시간이 빠를수록 이후에 선택할 수 있는 활동이 더 많아지기 때문입니다. 이 전략으로 정렬한 뒤 앞에서부터 겹치지 않는 활동을 선택하면 최대 개수를 얻을 수 있습니다.
