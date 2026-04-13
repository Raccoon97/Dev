# 🏠   [Go Main](../../README.md)   🏠
- [Trie 란?](#trie-란)
- [Trie 의 구조](#trie-의-구조)
- [Swift 구현](#swift-구현)
- [시간 복잡도](#시간-복잡도)
- [Trie vs 다른 자료구조](#trie-vs-다른-자료구조)
- [활용 사례](#활용-사례)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# Trie 란?
- **Trie (트라이)** 는 문자열 집합을 효율적으로 저장하고 탐색하기 위한 **트리 기반** 자료구조이다.
- **Retrieval** 에서 이름이 유래했으며, "트라이" 또는 "프리픽스 트리 (Prefix Tree)" 라고도 부른다.
- 각 노드가 **문자 하나** 를 저장하며, 루트에서 특정 노드까지의 경로가 하나의 문자열 (또는 접두사) 을 나타낸다.
- 문자열 검색, 자동완성, 사전 구현 등에 널리 사용된다.

<br><br><br>

# Trie 의 구조
- **루트 노드** 는 빈 문자를 나타낸다.
- 각 노드는 **자식 노드에 대한 링크** (보통 Dictionary 또는 배열) 와 **해당 노드가 문자열의 끝인지** 를 나타내는 플래그를 가진다.

### 예시
- `["apple", "app", "bat", "bad"]` 를 저장한 Trie :

```
        (root)
       /      \
      a         b
      |         |
      p         a
      |        / \
      p       t   d
     / \
    l    [end: "app"]
    |
    e
   [end: "apple"]
```

- `"app"` 은 `"apple"` 의 **접두사 (Prefix)** 이면서 독립적인 단어이기도 하다.
- 공통 접두사를 공유하므로 **메모리를 절약** 할 수 있다.

<br><br><br>

# Swift 구현

### TrieNode
```swift
class TrieNode {
    var children: [Character: TrieNode] = [:]
    var isEndOfWord: Bool = false
}
```

### Trie
```swift
class Trie {
    private let root = TrieNode()
    
    // 단어 삽입 - O(M), M = 단어 길이
    func insert(_ word: String) {
        var current = root
        for char in word {
            if current.children[char] == nil {
                current.children[char] = TrieNode()
            }
            current = current.children[char]!
        }
        current.isEndOfWord = true
    }
    
    // 단어 검색 - O(M)
    func search(_ word: String) -> Bool {
        guard let node = findNode(word) else { return false }
        return node.isEndOfWord
    }
    
    // 접두사 검색 - O(M)
    func startsWith(_ prefix: String) -> Bool {
        return findNode(prefix) != nil
    }
    
    // 단어 삭제 - O(M)
    func delete(_ word: String) {
        delete(root, word, 0)
    }
    
    // 주어진 접두사로 시작하는 모든 단어 반환
    func wordsWithPrefix(_ prefix: String) -> [String] {
        guard let node = findNode(prefix) else { return [] }
        var results: [String] = []
        collectWords(node, prefix, &results)
        return results
    }
    
    // MARK: - Private
    
    private func findNode(_ str: String) -> TrieNode? {
        var current = root
        for char in str {
            guard let next = current.children[char] else { return nil }
            current = next
        }
        return current
    }
    
    @discardableResult
    private func delete(_ node: TrieNode, _ word: String, _ depth: Int) -> Bool {
        let chars = Array(word)
        
        if depth == chars.count {
            if !node.isEndOfWord { return false }
            node.isEndOfWord = false
            return node.children.isEmpty
        }
        
        let char = chars[depth]
        guard let child = node.children[char] else { return false }
        
        let shouldDeleteChild = delete(child, word, depth + 1)
        if shouldDeleteChild {
            node.children[char] = nil
            return !node.isEndOfWord && node.children.isEmpty
        }
        return false
    }
    
    private func collectWords(_ node: TrieNode, _ prefix: String, _ results: inout [String]) {
        if node.isEndOfWord {
            results.append(prefix)
        }
        for (char, child) in node.children {
            collectWords(child, prefix + String(char), &results)
        }
    }
}
```

### 사용 예시
```swift
let trie = Trie()
trie.insert("apple")
trie.insert("app")
trie.insert("application")

trie.search("app")          // true
trie.search("apple")        // true
trie.search("ap")           // false (접두사이지만 완전한 단어가 아님)
trie.startsWith("ap")       // true

trie.wordsWithPrefix("app") // ["app", "apple", "application"]

trie.delete("app")
trie.search("app")          // false
trie.search("apple")        // true (삭제되지 않음)
```

<br><br><br>

# 시간 복잡도

| 연산 | 시간 복잡도 | 설명 |
|---|---|---|
| **Insert** | O(M) | M = 삽입할 단어의 길이 |
| **Search** | O(M) | M = 검색할 단어의 길이 |
| **StartsWith** | O(M) | M = 접두사의 길이 |
| **Delete** | O(M) | M = 삭제할 단어의 길이 |

- Hash Table 의 문자열 검색도 `O(M)` 이지만, Trie 는 **접두사 기반 검색** 에서 훨씬 효율적이다.
- 공간 복잡도는 최악의 경우 `O(N × M × C)` (N = 단어 수, M = 평균 길이, C = 문자 집합 크기) 이지만, 공통 접두사를 공유하므로 실제로는 훨씬 적다.

<br><br><br>

# Trie vs 다른 자료구조

| 구분 | Trie | Hash Table | BST |
|---|---|---|---|
| **정확한 검색** | O(M) | O(M) 평균 | O(M log N) |
| **접두사 검색** | O(M) | 불가 | O(M log N) |
| **자동완성** | 효율적 | 비효율적 | 비효율적 |
| **정렬된 순회** | 알파벳 순 가능 | 불가 | 가능 |
| **공간 효율** | 접두사 공유 | 각 단어 독립 저장 | 각 단어 독립 저장 |
| **최악 검색** | O(M) | O(N × M) 해시 충돌 | O(N × M) 편향 |

<br><br><br>

# 활용 사례
- **자동완성 (Autocomplete)** : 검색 엔진, IDE 의 코드 자동완성 등에서 사용자가 입력한 접두사로 시작하는 후보 목록을 빠르게 제공한다.
- **사전 (Dictionary)** : 단어 존재 여부를 빠르게 확인하고, 유사 단어를 검색한다.
- **맞춤법 검사 (Spell Checker)** : 입력한 단어가 사전에 존재하는지 확인하고, 유사한 단어를 제안한다.
- **IP 라우팅 (Longest Prefix Match)** : 라우터에서 IP 주소의 가장 긴 접두사 일치를 찾아 패킷을 라우팅한다.
- **전화번호부** : 전화번호의 접두사를 기반으로 검색한다.
- **문자열 관련 알고리즘 문제** : 코딩 테스트에서 접두사, 단어 검색, 와일드카드 매칭 등의 문제에 활용된다.

<br><br><br>

# 면접 예상 질문
- **Q. Trie 란 무엇인가요?**
  - 문자열 집합을 효율적으로 저장하고 검색하기 위한 **트리 기반 자료구조** 입니다. 각 노드가 문자 하나를 나타내며, 루트에서 특정 노드까지의 경로가 문자열의 접두사를 나타냅니다. 공통 접두사를 공유하므로 메모리 효율적이며, **삽입/검색이 단어 길이 M 에 대해 O(M)** 으로 동작합니다.

- **Q. Trie 와 Hash Table 의 차이는?**
  - 정확한 검색은 둘 다 `O(M)` 이지만, **접두사 기반 검색** 에서 Trie 가 압도적으로 유리합니다. Hash Table 은 "app" 으로 시작하는 모든 단어를 찾으려면 전체를 순회해야 하지만, Trie 는 "app" 노드까지 이동한 뒤 하위 트리만 탐색하면 됩니다. 반면 Hash Table 은 구현이 더 간단하고, 접두사 검색이 불필요한 경우 공간 효율이 더 좋을 수 있습니다.

- **Q. Trie 의 공간 복잡도를 줄이는 방법은?**
  - **Compressed Trie (Patricia Trie / Radix Tree)** 를 사용하면 자식이 하나뿐인 노드들을 하나로 합쳐 공간을 절약할 수 있습니다. 예를 들어 "application" 에서 "ication" 부분은 하나의 노드로 압축됩니다. 또한 알파벳 배열 대신 **Dictionary (HashMap)** 을 사용하면 사용하지 않는 문자에 대한 공간 낭비를 줄일 수 있습니다.

- **Q. 자동완성 기능을 Trie 로 어떻게 구현하나요?**
  - 사용자가 입력한 접두사로 Trie 를 탐색해 해당 노드에 도달한 뒤, 그 **하위 트리를 DFS 로 순회** 하며 `isEndOfWord` 가 true 인 경로의 문자열들을 수집합니다. 결과가 많을 경우 **빈도수** 나 **최근 사용 순** 으로 정렬해 상위 N 개만 반환하는 방식으로 최적화합니다.

- **Q. Trie 를 사용하는 실제 사례는?**
  - 검색 엔진의 **자동완성**, IDE 의 **코드 자동완성**, **맞춤법 검사기**, IP 라우터의 **Longest Prefix Match**, 전화번호부 검색 등에 사용됩니다. 특히 네트워크 라우팅에서는 비트 단위 Trie 를 사용해 IP 주소를 빠르게 매칭합니다.
