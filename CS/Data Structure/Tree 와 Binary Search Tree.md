# 🏠   [Go Main](../../README.md)   🏠
- [Tree](#tree)
- [Tree 관련 용어](#tree-관련-용어)
- [Binary Tree](#binary-tree)
- [Binary Search Tree (BST)](#binary-search-tree-bst)
- [Balanced Binary Search Tree](#balanced-binary-search-tree)
- [Tree 순회](#tree-순회)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# Tree
- 노드(Node) 와 간선(Edge) 으로 이루어진 계층적인 자료구조이다.
- 사이클이 없는 연결 그래프(Acyclic Connected Graph) 의 일종이다.
- 대표적인 활용 예 : 파일 시스템, DOM, HTML 문서 구조, DB 인덱스 등

<br><br><br>

# Tree 관련 용어
- **Root Node** : 최상위에 위치한 노드
- **Leaf Node** : 자식이 없는 노드
- **Parent / Child Node** : 부모/자식 관계에 있는 노드
- **Sibling** : 같은 부모를 가진 노드
- **Depth** : Root 로부터 해당 노드까지의 거리
- **Height** : 해당 노드로부터 가장 먼 Leaf 까지의 거리
- **Level** : 특정 Depth 에 위치한 노드들의 집합
- **Degree** : 해당 노드의 자식 수

<br><br><br>

# Binary Tree
- 모든 노드가 **최대 2개의 자식 노드** (left, right) 를 갖는 트리이다.
- 종류
  - **Full Binary Tree** : 모든 노드가 0 개 또는 2 개의 자식을 가진 트리
  - **Complete Binary Tree** : 마지막 레벨을 제외한 모든 레벨이 완전히 채워져 있고, 마지막 레벨은 왼쪽부터 채워져 있는 트리
  - **Perfect Binary Tree** : 모든 내부 노드가 2개의 자식을 가지며, 모든 Leaf 가 같은 Level 에 있는 트리
  - **Skewed Binary Tree** : 한쪽으로 치우친 트리, 사실상 LinkedList 와 같다.

<br><br><br>

# Binary Search Tree (BST)
- 이진 탐색 트리는 다음 조건을 만족하는 이진 트리이다.
  - 모든 노드의 **왼쪽 서브트리** 는 해당 노드보다 **작은** 값을 가진다.
  - 모든 노드의 **오른쪽 서브트리** 는 해당 노드보다 **큰** 값을 가진다.
  - 중복된 값은 없다. (구현에 따라 다를 수 있음)
- 평균적으로 삽입, 삭제, 탐색 모두 `O(log n)` 의 시간복잡도를 가진다.
- 최악의 경우 (한 쪽으로 치우친 경우) `O(n)` 까지 느려질 수 있다.

```swift
final class BSTNode<T: Comparable> {
    var value: T
    var left: BSTNode?
    var right: BSTNode?
    init(_ value: T) { self.value = value }
}

final class BinarySearchTree<T: Comparable> {
    var root: BSTNode<T>?

    func insert(_ value: T) {
        root = insert(node: root, value: value)
    }

    private func insert(node: BSTNode<T>?, value: T) -> BSTNode<T> {
        guard let node = node else { return BSTNode(value) }
        if value < node.value {
            node.left = insert(node: node.left, value: value)
        } else if value > node.value {
            node.right = insert(node: node.right, value: value)
        }
        return node
    }

    func contains(_ value: T) -> Bool {
        var current = root
        while let node = current {
            if node.value == value { return true }
            current = value < node.value ? node.left : node.right
        }
        return false
    }
}
```

<br><br><br>

# Balanced Binary Search Tree
- BST 의 최악의 경우 `O(n)` 성능 문제를 해결하기 위해 트리의 균형을 자동으로 맞춰주는 트리이다.
- 종류
  - **AVL Tree** : 모든 노드의 좌우 서브트리 높이 차이가 1 이하가 되도록 유지하는 트리. 엄격한 균형을 유지하므로 탐색에 유리하다.
  - **Red-Black Tree** : 각 노드를 Red/Black 으로 색칠해 특정 규칙을 만족하도록 하는 트리. 삽입/삭제가 상대적으로 빠르며, C++ STL 의 `map`, `set`, Java 의 `TreeMap` 등에서 사용된다.
- 모든 연산에서 `O(log n)` 을 보장한다.

<br><br><br>

# Tree 순회
- **전위 순회 (Pre-order)** : Root → Left → Right
- **중위 순회 (In-order)** : Left → Root → Right ( BST 의 경우 **오름차순 정렬 순서** 로 방문 )
- **후위 순회 (Post-order)** : Left → Right → Root
- **레벨 순회 (Level-order, BFS)** : Queue 를 이용해 레벨 단위로 방문

```swift
func inorder<T>(_ node: BSTNode<T>?) {
    guard let node = node else { return }
    inorder(node.left)
    print(node.value)
    inorder(node.right)
}
```

<br><br><br>

# 면접 예상 질문
- **Q. BST 의 시간복잡도는 어떻게 되나요?**
  - 평균 `O(log n)`, 최악 `O(n)` 입니다. 한쪽으로 치우친 Skewed Tree 의 경우 LinkedList 와 동일해지기 때문입니다. 이를 방지하기 위해 AVL, Red-Black Tree 같은 균형 이진 탐색 트리가 사용됩니다.

- **Q. BST 에서 특정 노드를 삭제할 때는 어떻게 해야 하나요?**
  - 삭제할 노드가 Leaf 이면 그대로 삭제, 자식이 하나면 자식을 부모에 연결, 자식이 둘이면 오른쪽 서브트리의 최솟값(또는 왼쪽 서브트리의 최댓값) 과 자리를 바꾼 뒤 삭제합니다.

- **Q. AVL 과 Red-Black Tree 중 어떤 것이 더 좋은가요?**
  - 사용 목적에 따라 다릅니다. AVL 은 더 엄격한 균형을 유지하므로 탐색 빈도가 높은 경우에 유리하고, Red-Black Tree 는 삽입/삭제가 상대적으로 빠르므로 쓰기 작업이 많은 경우에 유리합니다.

- **Q. 중위 순회의 특징은 무엇인가요?**
  - BST 를 중위 순회 하면 **오름차순 정렬된 순서** 로 노드를 방문하게 됩니다. 따라서 BST 는 자연스러운 정렬된 자료구조이기도 합니다.
