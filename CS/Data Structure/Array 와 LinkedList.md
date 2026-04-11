# 🏠   [Go Main](../../README.md)   🏠
- [Array](#array)
- [LinkedList](#linkedlist)
- [Array 와 LinkedList 의 차이점](#array-와-linkedlist-의-차이점)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# Array
- 가장 기본적인 자료구조로, 논리적 저장 순서와 물리적 저장 순서가 일치한다.
- 메모리 상에 연속적으로 데이터가 저장되며, **인덱스(Index)** 를 통해 원소에 접근할 수 있다.
- 인덱스를 통한 접근이 가능하므로 찾고자 하는 원소의 인덱스 값을 안다면 `O(1)` 에 해당 원소로 접근할 수 있다. ( Random Access )
- 삭제 또는 삽입의 경우 해당 원소에 접근 후 `O(1)` 시간 안에 처리가 가능하지만, 그 뒤에 위치한 원소들을 한 칸씩 옮겨야 하므로 최악의 경우 `O(n)` 의 시간이 소요된다.
- 즉 Array 는 **Search 에 강하고, Insertion / Deletion 에 약하다.**

```swift
// Swift Array 예시
var numbers: [Int] = [1, 2, 3, 4, 5]
let third = numbers[2]        // O(1) 접근
numbers.append(6)             // 뒤에 추가는 amortized O(1)
numbers.insert(0, at: 0)      // 앞에 삽입은 O(n)
```

<br><br><br>

# LinkedList
- 각각의 원소가 자기 자신 다음에 오는 원소에 대한 주소(참조) 를 가지고 있는 자료구조이다.
- 원하는 원소의 위치를 찾기 위해선 Head 노드부터 순차적으로 따라가야 하므로 **탐색에 `O(n)`** 의 시간이 걸린다.
- 삽입 / 삭제 자체는 포인터만 바꿔주면 되므로 `O(1)` 에 수행할 수 있으나, 해당 노드를 찾는 시간까지 포함하면 `O(n)` 이 된다.
- Tree 자료구조의 근간이 되는 구조이기도 하다.

```swift
// Swift 로 구현한 단일 연결 리스트
final class Node<T> {
    var value: T
    var next: Node<T>?
    init(value: T) { self.value = value }
}

final class LinkedList<T> {
    var head: Node<T>?

    func append(_ value: T) {
        let newNode = Node(value: value)
        guard let head = head else {
            self.head = newNode
            return
        }
        var current = head
        while let next = current.next { current = next }
        current.next = newNode
    }
}
```

- 종류
  - **Singly Linked List** : 단방향 연결 리스트
  - **Doubly Linked List** : 양방향 연결 리스트, 이전 노드에 대한 포인터도 함께 가진다.
  - **Circular Linked List** : 마지막 노드가 다시 Head 를 가리키는 원형 연결 리스트

<br><br><br>

# Array 와 LinkedList 의 차이점

| 구분 | Array | LinkedList |
|---|---|---|
| 메모리 할당 | 연속적 (Static) | 비연속적 (Dynamic) |
| 접근 시간 | `O(1)` Random Access | `O(n)` Sequential Access |
| 삽입/삭제 | `O(n)` | `O(1)` ( 위치를 알고 있는 경우 ) |
| 메모리 사용 | 데이터 크기만큼 | 데이터 + 포인터(참조) |
| 캐시 친화성 | 높음 | 낮음 |

<br><br><br>

# 면접 예상 질문
- **Q. Array 와 LinkedList 의 장단점은 무엇인가요?**
  - Array 는 인덱스 기반 Random Access 가 가능해 조회가 빠르지만, 중간 삽입/삭제 시 원소 이동이 필요해 비효율적입니다. LinkedList 는 삽입/삭제는 빠르지만 특정 위치의 원소에 접근하기 위해서는 Head 부터 순차 탐색해야 하므로 조회가 느립니다.

- **Q. 왜 Array 의 삽입/삭제가 `O(n)` 인가요?**
  - 배열은 메모리 상에 연속적으로 저장되므로, 중간에 원소를 삽입하거나 삭제하면 그 뒤의 모든 원소를 한 칸씩 이동시켜야 하기 때문입니다.

- **Q. LinkedList 의 탐색이 `O(n)` 인데, 어떻게 개선할 수 있나요?**
  - Skip List 나 Hash Table 등을 함께 사용해 특정 노드에 `O(1)` 또는 `O(log n)` 으로 접근할 수 있도록 개선할 수 있습니다.

- **Q. Swift 의 Array 는 내부적으로 어떻게 구현되어 있나요?**
  - Swift 의 Array 는 Value Type(Struct) 이지만 내부적으로 Reference Type 인 버퍼(ContiguousArrayBuffer) 를 가지며 **Copy-on-Write (COW)** 방식으로 동작합니다. 따라서 단순 대입 시에는 참조만 공유되고, 수정이 일어나는 순간 실제 복사가 이루어집니다.
