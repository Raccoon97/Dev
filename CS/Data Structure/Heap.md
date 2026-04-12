# 🏠   [Go Main](../../README.md)   🏠
- [Heap 이란?](#heap-이란)
- [Heap 의 구조](#heap-의-구조)
- [배열로 구현하는 Heap](#배열로-구현하는-heap)
- [Heap 의 연산](#heap-의-연산)
- [시간 복잡도](#시간-복잡도)
- [Heap 의 활용](#heap-의-활용)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# Heap 이란?
- **완전 이진 트리 (Complete Binary Tree)** 기반의 자료구조이다.
- **Max Heap** : 부모 노드가 자식 노드보다 항상 **크거나 같음**
- **Min Heap** : 부모 노드가 자식 노드보다 항상 **작거나 같음**
- **Priority Queue** 의 가장 효율적인 구현체로 사용된다.
- Heap 은 **정렬된 구조가 아니다.** 단지 부모 ↔ 자식 관계만 유지된다.

<br><br><br>

# Heap 의 구조

```
         [10]
        /    \
      [8]    [9]
      / \    / \
    [5] [6] [7] [4]
```

- 위 예시는 Max Heap 이다.
- Root 에는 항상 최댓값 (Max Heap) 또는 최솟값 (Min Heap) 이 존재한다.
- 완전 이진 트리이므로 왼쪽부터 노드가 채워진다.

<br><br><br>

# 배열로 구현하는 Heap
- Heap 은 완전 이진 트리이므로 **배열** 로 효율적으로 구현할 수 있다.
- 일반적으로 **1 번 Index 부터** 사용하면 계산이 간편하다.

### 인덱스 규칙 (1-based)
- 부모 : `i / 2`
- 왼쪽 자식 : `i * 2`
- 오른쪽 자식 : `i * 2 + 1`

### 인덱스 규칙 (0-based, Swift 기본)
- 부모 : `(i - 1) / 2`
- 왼쪽 자식 : `i * 2 + 1`
- 오른쪽 자식 : `i * 2 + 2`

```swift
struct MaxHeap {
    private var heap: [Int] = []
    
    var peek: Int? { heap.first }
    var count: Int { heap.count }
    
    mutating func insert(_ value: Int) {
        heap.append(value)
        siftUp(from: heap.count - 1)
    }
    
    mutating func pop() -> Int? {
        guard !heap.isEmpty else { return nil }
        heap.swapAt(0, heap.count - 1)
        let value = heap.removeLast()
        siftDown(from: 0)
        return value
    }
    
    private mutating func siftUp(from index: Int) {
        var child = index
        var parent = (child - 1) / 2
        while child > 0 && heap[child] > heap[parent] {
            heap.swapAt(child, parent)
            child = parent
            parent = (child - 1) / 2
        }
    }
    
    private mutating func siftDown(from index: Int) {
        var parent = index
        while true {
            let left = parent * 2 + 1
            let right = parent * 2 + 2
            var candidate = parent
            if left < heap.count && heap[left] > heap[candidate] { candidate = left }
            if right < heap.count && heap[right] > heap[candidate] { candidate = right }
            if candidate == parent { return }
            heap.swapAt(parent, candidate)
            parent = candidate
        }
    }
}
```

<br><br><br>

# Heap 의 연산

### 1. 삽입 (Insert / Push)
1. 배열의 맨 끝에 새 노드를 추가한다.
2. 부모 노드와 비교하며 Heap 속성이 만족될 때까지 위로 이동 (**Sift Up / Bubble Up**).

### 2. 삭제 (Extract / Pop)
1. Root 노드 값을 꺼낸다 (Max Heap 의 경우 최댓값).
2. 배열의 마지막 원소를 Root 로 옮긴다.
3. 자식 노드와 비교하며 Heap 속성이 만족될 때까지 아래로 이동 (**Sift Down / Bubble Down**).

### 3. Heapify
- 주어진 배열을 Heap 구조로 만드는 연산.
- 배열의 중간 `N/2` 부터 시작해 Sift Down 을 수행하면 `O(N)` 에 Heap 을 구성할 수 있다.

<br><br><br>

# 시간 복잡도

| 연산 | 시간 복잡도 |
|---|---|
| 최댓값/최솟값 조회 (peek) | O(1) |
| 삽입 (insert) | O(log N) |
| 삭제 (pop) | O(log N) |
| Heapify (배열 → Heap) | O(N) |
| 검색 (특정 값 찾기) | O(N) |

<br><br><br>

# Heap 의 활용

### 1. Priority Queue
- 우선순위가 높은 원소를 먼저 꺼내야 하는 경우.
- OS 의 작업 스케줄링, 프린터 작업 큐 등.

### 2. Heap Sort
- Heap 을 이용한 정렬 알고리즘.
- 시간 복잡도 `O(N log N)`, 공간 `O(1)`.

### 3. 다익스트라 (Dijkstra) 알고리즘
- 최단 경로 탐색 시 방문할 노드를 효율적으로 선택하기 위해 Min Heap 을 사용한다.

### 4. K 번째 최대/최솟값 찾기
- 크기 K 의 Heap 을 유지해 `O(N log K)` 에 K 번째 원소를 찾을 수 있다.

### 5. 중앙값 (Median) 찾기
- Max Heap 과 Min Heap 두 개를 활용해 스트림 데이터의 중앙값을 `O(log N)` 에 구할 수 있다.

<br><br><br>

# 면접 예상 질문
- **Q. Heap 과 이진 탐색 트리(BST) 의 차이는?**
  - BST 는 **전체적으로 정렬** 된 구조 (좌 < 부모 < 우) 로 탐색이 `O(log N)` 입니다. Heap 은 **부모-자식 관계** 만 유지하고 형제 간에는 순서가 없으며, 최댓값/최솟값 접근이 `O(1)` 이지만 특정 값 탐색은 `O(N)` 입니다.

- **Q. Priority Queue 를 Heap 이 아닌 다른 자료구조로 구현하면?**
  - 정렬된 배열이나 Linked List 로 구현할 수도 있지만, 삽입이 `O(N)` 이라 비효율적입니다. Heap 으로 구현하면 삽입/삭제 모두 `O(log N)` 이어서 가장 효율적입니다.

- **Q. Heap 은 왜 배열로 구현하나요?**
  - **완전 이진 트리** 이므로 중간에 빈 공간이 없어 배열로 구현하면 메모리 효율적이고, 포인터 대신 **인덱스 연산** 으로 부모/자식에 접근할 수 있어 **캐시 지역성** 도 좋습니다.

- **Q. Heapify 가 O(N) 인 이유는?**
  - 상위 레벨의 노드는 아래로 내려가는 깊이가 짧고, 하위 레벨의 노드 개수는 많습니다. 각 레벨의 노드 수와 이동 깊이를 모두 곱해서 합산하면 `O(N)` 이 됩니다. 반면 `N` 개를 하나씩 insert 하면 `O(N log N)` 이 됩니다.

- **Q. Heap 에서 특정 값을 빠르게 찾을 수 있나요?**
  - 아니요. Heap 은 정렬된 구조가 아니므로 특정 값 검색은 `O(N)` 이 필요합니다. 이것이 필요하면 BST 나 Hash Table 을 사용해야 합니다.
