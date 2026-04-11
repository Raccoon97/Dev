# 🏠   [Go Main](../../README.md)   🏠
- [Graph](#graph)
- [Graph 의 종류](#graph-의-종류)
- [Graph 표현 방식](#graph-표현-방식)
- [Graph 탐색](#graph-탐색)
- [Tree 와 Graph 의 차이](#tree-와-graph-의-차이)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# Graph
- **정점(Vertex, Node)** 과 **간선(Edge)** 의 집합으로 이루어진 자료구조이다.
- `G = (V, E)` 로 표현한다.
- 현실 세계의 다양한 관계를 모델링할 수 있는 강력한 자료구조이다.
- 활용 예 : 소셜 네트워크, 지도/내비게이션, 추천 시스템, 네트워크 라우팅 등

<br><br><br>

# Graph 의 종류

### 방향성 여부
- **무방향 그래프 (Undirected Graph)** : 간선에 방향이 없는 그래프. `(A, B) == (B, A)`
- **방향 그래프 (Directed Graph, Digraph)** : 간선에 방향이 있는 그래프.

### 가중치 여부
- **가중치 그래프 (Weighted Graph)** : 각 간선에 비용 또는 거리 등의 가중치가 있는 그래프.
- **비가중치 그래프 (Unweighted Graph)** : 간선에 가중치가 없는 그래프.

### 사이클 여부
- **사이클 그래프 (Cyclic Graph)** : 사이클이 존재하는 그래프.
- **비순환 그래프 (Acyclic Graph)** : 사이클이 존재하지 않는 그래프.
- **DAG (Directed Acyclic Graph)** : 사이클이 없는 방향 그래프. 작업 스케줄링, Git 커밋 그래프 등에 활용된다.

### 연결 여부
- **연결 그래프 (Connected Graph)** : 임의의 두 정점 사이에 경로가 존재하는 그래프.
- **비연결 그래프 (Disconnected Graph)** : 연결되지 않은 정점이 존재하는 그래프.

<br><br><br>

# Graph 표현 방식

### Adjacency Matrix (인접 행렬)
- 2 차원 배열로 그래프를 표현한다. `matrix[i][j]` 가 1 이면 i 와 j 사이에 간선이 있다.
- 장점
  - 두 정점 사이의 간선 존재 여부를 `O(1)` 에 확인 가능
  - 구현이 간단
- 단점
  - 공간복잡도가 `O(V²)` 로 정점이 많을 때 메모리 낭비가 심함
  - 모든 간선을 탐색하는 데 `O(V²)` 이 걸림

```
    A B C D
  A 0 1 1 0
  B 1 0 0 1
  C 1 0 0 1
  D 0 1 1 0
```

### Adjacency List (인접 리스트)
- 각 정점마다 연결된 정점들의 리스트를 갖는 방식이다.
- 장점
  - 공간복잡도가 `O(V + E)` 로 효율적
  - 실제로 연결된 간선만 순회 가능
- 단점
  - 두 정점 사이의 간선 존재 여부 확인에 `O(V)` 소요

```
A: [B, C]
B: [A, D]
C: [A, D]
D: [B, C]
```

<br><br><br>

# Graph 탐색

### DFS (Depth First Search, 깊이 우선 탐색)
- 한 방향으로 갈 수 있는 만큼 깊게 탐색 후, 더 이상 갈 곳이 없으면 되돌아와 다른 방향으로 탐색한다.
- **Stack** 또는 **재귀** 로 구현한다.
- 모든 경로를 방문해야 하는 경우에 유용하다.

```swift
func dfs(_ graph: [Int: [Int]], start: Int) {
    var visited: Set<Int> = []
    var stack: [Int] = [start]

    while let current = stack.popLast() {
        if visited.contains(current) { continue }
        visited.insert(current)
        print(current)
        for next in (graph[current] ?? []).reversed() {
            if !visited.contains(next) { stack.append(next) }
        }
    }
}
```

### BFS (Breadth First Search, 너비 우선 탐색)
- 현재 정점과 가까운 정점부터 탐색한다.
- **Queue** 로 구현한다.
- 최단 경로를 구할 때 유용하다. (가중치가 없는 그래프)

```swift
func bfs(_ graph: [Int: [Int]], start: Int) {
    var visited: Set<Int> = [start]
    var queue: [Int] = [start]
    var head = 0

    while head < queue.count {
        let current = queue[head]
        head += 1
        print(current)
        for next in graph[current] ?? [] where !visited.contains(next) {
            visited.insert(next)
            queue.append(next)
        }
    }
}
```

<br><br><br>

# Tree 와 Graph 의 차이

| 구분 | Tree | Graph |
|---|---|---|
| 방향성 | 부모 → 자식 (대개 방향성 있음) | 방향 / 무방향 가능 |
| 사이클 | 없음 | 있을 수도 없을 수도 있음 |
| 루트 노드 | 있음 | 없음 |
| 간선 수 | `V - 1` 개 | 제한 없음 |
| 모델 | 계층적 | 네트워크 |

> Tree 는 사이클이 없는 연결 그래프 라고도 표현할 수 있다.

<br><br><br>

# 면접 예상 질문
- **Q. DFS 와 BFS 는 언제 사용하나요?**
  - 모든 경로를 찾거나 특정 정점까지의 경로가 존재하는지 확인할 때는 DFS 를, 가중치 없는 그래프에서 최단 경로를 구할 때는 BFS 를 사용합니다.

- **Q. 인접 행렬과 인접 리스트 중 언제 어떤 것을 사용하나요?**
  - 정점이 적고 간선이 많은 **조밀한 그래프** 는 인접 행렬이 유리하고, 정점이 많고 간선이 적은 **희소한 그래프** 는 인접 리스트가 유리합니다.

- **Q. 가중치가 있는 그래프에서 최단 경로는 어떻게 구하나요?**
  - 음수 가중치가 없다면 **Dijkstra 알고리즘** 을, 음수 가중치가 있다면 **Bellman-Ford 알고리즘** 을 사용합니다. 모든 정점 쌍에 대해 구한다면 **Floyd-Warshall 알고리즘** 을 사용합니다.

- **Q. DAG 의 활용 예를 들어 주세요.**
  - 작업 스케줄링 (Topological Sort), Git 의 커밋 히스토리, 빌드 시스템의 의존성 그래프 등에 사용됩니다.
