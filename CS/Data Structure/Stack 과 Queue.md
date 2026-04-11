# 🏠   [Go Main](../../README.md)   🏠
- [Stack](#stack)
- [Queue](#queue)
- [Stack 과 Queue 의 활용](#stack-과-queue-의-활용)
- [Deque (Double Ended Queue)](#deque-double-ended-queue)
- [Priority Queue](#priority-queue)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# Stack
- **LIFO (Last In First Out)** 구조를 가진 자료구조이다. 가장 마지막에 저장된 데이터가 가장 먼저 나오게 된다.
- 주요 연산
  - `push(x)` : Stack 의 top 에 원소 `x` 를 삽입한다. `O(1)`
  - `pop()` : Stack 의 top 원소를 제거하고 반환한다. `O(1)`
  - `peek()` / `top()` : Stack 의 top 원소를 확인한다. `O(1)`
- 입구와 출구가 하나인 자료구조라고 생각하면 된다.

```swift
struct Stack<T> {
    private var storage: [T] = []

    var isEmpty: Bool { storage.isEmpty }
    var count: Int { storage.count }
    var top: T? { storage.last }

    mutating func push(_ element: T) { storage.append(element) }

    @discardableResult
    mutating func pop() -> T? { storage.popLast() }
}
```

<br><br><br>

# Queue
- **FIFO (First In First Out)** 구조를 가진 자료구조이다. 가장 먼저 저장된 데이터가 가장 먼저 나오게 된다.
- 주요 연산
  - `enqueue(x)` : Queue 의 rear 에 원소 `x` 를 삽입한다.
  - `dequeue()` : Queue 의 front 에 있는 원소를 제거하고 반환한다.
  - `front()` / `peek()` : Queue 의 front 원소를 확인한다.
- 입구와 출구가 서로 다른 자료구조이다.

```swift
struct Queue<T> {
    private var storage: [T] = []
    private var head: Int = 0

    var isEmpty: Bool { head >= storage.count }

    mutating func enqueue(_ element: T) { storage.append(element) }

    @discardableResult
    mutating func dequeue() -> T? {
        guard head < storage.count else { return nil }
        let element = storage[head]
        head += 1
        // 주기적으로 head 앞쪽 메모리 회수
        if head > 50, head * 2 > storage.count {
            storage.removeFirst(head)
            head = 0
        }
        return element
    }
}
```

<br><br><br>

# Stack 과 Queue 의 활용

### Stack 활용 예
- 함수 호출 스택 (Call Stack)
- 수식의 괄호 검사
- 웹 브라우저의 뒤로가기 버튼 구현
- DFS (Depth First Search)
- 재귀 함수의 구현

### Queue 활용 예
- 프로세스/스레드 스케줄링 (Ready Queue)
- 프린터의 작업 대기열
- BFS (Breadth First Search)
- iOS 의 DispatchQueue, RunLoop Event Queue

<br><br><br>

# Deque (Double Ended Queue)
- 양쪽 끝에서 삽입과 삭제가 모두 가능한 자료구조이다.
- Stack 과 Queue 의 기능을 모두 가지고 있다.
- Swift 에서는 Swift Collections 패키지의 `Deque` 타입으로 제공된다.

<br><br><br>

# Priority Queue
- 우선순위가 가장 높은 원소가 먼저 빠져나가는 자료구조이다.
- 일반적으로 **Heap** 을 이용해 구현하며, 삽입/삭제 모두 `O(log n)` 의 시간복잡도를 가진다.
- 다익스트라 알고리즘, 허프만 코딩 등에 활용된다.

<br><br><br>

# 면접 예상 질문
- **Q. Stack 과 Queue 의 차이점은 무엇인가요?**
  - Stack 은 LIFO 구조로 마지막에 들어온 원소가 먼저 나가며, Queue 는 FIFO 구조로 먼저 들어온 원소가 먼저 나갑니다. Stack 은 입구와 출구가 같고 Queue 는 다릅니다.

- **Q. Stack 두 개로 Queue 를 구현할 수 있나요?**
  - 네, 가능합니다. 하나의 Stack(inbox) 에 enqueue 연산을 수행하고, dequeue 시에는 다른 Stack(outbox) 이 비어있으면 inbox 의 모든 원소를 outbox 로 옮긴 뒤 outbox 의 top 을 pop 합니다. Amortized 시간복잡도는 `O(1)` 입니다.

- **Q. Queue 를 배열로 구현할 때 주의할 점은?**
  - 단순히 `removeFirst()` 를 사용하면 `O(n)` 이 소요되므로 성능이 떨어집니다. Circular Queue 로 구현하거나 Head 인덱스를 따로 관리하는 방식으로 `O(1)` dequeue 를 구현해야 합니다.

- **Q. iOS 의 DispatchQueue 는 어떤 자료구조를 기반으로 하나요?**
  - 이름 그대로 Queue 자료구조를 기반으로 하며, Task 들을 FIFO 순서로 처리합니다. 다만 Concurrent Dispatch Queue 는 내부적으로 여러 스레드를 이용해 동시 실행을 수행합니다.
