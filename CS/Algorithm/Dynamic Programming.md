# 🏠   [Go Main](../../README.md)   🏠
- [Dynamic Programming 이란?](#dynamic-programming-이란)
- [DP 의 조건](#dp-의-조건)
- [Top-Down vs Bottom-Up](#top-down-vs-bottom-up)
- [Memoization vs Tabulation](#memoization-vs-tabulation)
- [대표 예제](#대표-예제)
- [DP vs 분할 정복](#dp-vs-분할-정복)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# Dynamic Programming 이란?
- **DP (동적 계획법)** 는 복잡한 문제를 **작은 하위 문제** 로 나누어 해결하고, 중복되는 하위 문제의 결과를 **저장** 해 재사용하는 방식이다.
- **Richard Bellman** 이 1950 년대에 제안한 방법.
- 하위 문제를 반복적으로 계산하지 않아 **시간 복잡도를 크게 줄일 수 있다.**

<br><br><br>

# DP 의 조건
- 어떤 문제가 DP 로 해결 가능하려면 다음 두 조건을 만족해야 한다.

### 1. Optimal Substructure (최적 부분 구조)
- 문제의 **최적 해** 가 하위 문제들의 **최적 해** 로부터 구성될 수 있어야 한다.
- 예 : 피보나치 `fib(n) = fib(n-1) + fib(n-2)`

### 2. Overlapping Subproblems (중복 부분 문제)
- 같은 하위 문제가 **반복적으로** 등장해야 한다.
- 한 번 계산한 결과를 저장해두면 재사용할 수 있다.

> Divide & Conquer 와 달리, DP 는 하위 문제들이 **독립적이지 않고 중복** 된다.

<br><br><br>

# Top-Down vs Bottom-Up

### Top-Down (Memoization)
- **재귀** 로 큰 문제부터 시작해 작은 문제로 내려간다.
- 이미 계산한 결과는 배열이나 딕셔너리에 **저장** 해둔다.
- 구현이 직관적이지만 재귀 호출 오버헤드가 있다.

```swift
var memo: [Int: Int] = [:]

func fib(_ n: Int) -> Int {
    if n < 2 { return n }
    if let cached = memo[n] { return cached }
    let result = fib(n - 1) + fib(n - 2)
    memo[n] = result
    return result
}
```

### Bottom-Up (Tabulation)
- **반복문** 으로 작은 문제부터 해결해 올라간다.
- **표 (Table)** 를 채워가는 방식.
- 재귀 오버헤드가 없고 일반적으로 더 빠르다.

```swift
func fib(_ n: Int) -> Int {
    if n < 2 { return n }
    var dp = [Int](repeating: 0, count: n + 1)
    dp[1] = 1
    for i in 2...n {
        dp[i] = dp[i - 1] + dp[i - 2]
    }
    return dp[n]
}
```

<br><br><br>

# Memoization vs Tabulation

| 구분 | Memoization (Top-Down) | Tabulation (Bottom-Up) |
|---|---|---|
| 접근 방식 | 재귀 | 반복문 |
| 계산 순서 | 필요한 하위 문제만 계산 | 모든 하위 문제를 계산 |
| 속도 | 재귀 오버헤드 존재 | 보통 더 빠름 |
| 공간 | Call Stack + Cache | Table |
| 구현 | 직관적 | 계산 순서 고려 필요 |

<br><br><br>

# 대표 예제

### 1. 피보나치 수열
- `fib(n) = fib(n-1) + fib(n-2)`
- 단순 재귀 : `O(2ⁿ)` → DP : `O(N)`

### 2. 동전 거스름돈 (Coin Change)
- 주어진 동전들로 특정 금액을 만드는 **최소 동전 개수** 를 구하는 문제.

```swift
func coinChange(_ coins: [Int], _ amount: Int) -> Int {
    var dp = Array(repeating: amount + 1, count: amount + 1)
    dp[0] = 0
    for i in 1...amount {
        for coin in coins where i >= coin {
            dp[i] = min(dp[i], dp[i - coin] + 1)
        }
    }
    return dp[amount] > amount ? -1 : dp[amount]
}
```

### 3. 0/1 Knapsack (배낭 문제)
- N 개의 물건이 있고 각각 무게와 가치가 있을 때, **무게 제한 W** 안에서 **최대 가치** 를 얻는 문제.
- `dp[i][w]` = i 번째 물건까지 고려했을 때 무게 w 이하에서 얻을 수 있는 최대 가치

### 4. LIS (Longest Increasing Subsequence)
- 가장 긴 증가하는 부분 수열의 길이를 구하는 문제.
- DP : `O(N²)` / 이진 탐색 활용 : `O(N log N)`

### 5. LCS (Longest Common Subsequence)
- 두 문자열의 **공통 부분 수열 중 가장 긴 것** 을 구하는 문제.

```swift
func lcs(_ a: String, _ b: String) -> Int {
    let a = Array(a), b = Array(b)
    var dp = Array(repeating: Array(repeating: 0, count: b.count + 1), count: a.count + 1)
    for i in 1...a.count {
        for j in 1...b.count {
            if a[i - 1] == b[j - 1] {
                dp[i][j] = dp[i - 1][j - 1] + 1
            } else {
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
            }
        }
    }
    return dp[a.count][b.count]
}
```

### 6. 편집 거리 (Edit Distance)
- 한 문자열을 다른 문자열로 바꾸기 위해 필요한 **최소 연산 횟수** (삽입/삭제/교체).

<br><br><br>

# DP vs 분할 정복

| 구분 | 분할 정복 | DP |
|---|---|---|
| 하위 문제 | 독립적 | 중복됨 |
| 결과 저장 | 저장하지 않음 | 저장해 재사용 |
| 예시 | Merge Sort, Quick Sort | 피보나치, LCS, Knapsack |

<br><br><br>

# 면접 예상 질문
- **Q. Dynamic Programming 이 무엇인가요?**
  - 복잡한 문제를 **작은 하위 문제** 로 나누어 해결하고, **중복되는 하위 문제** 의 결과를 저장해 재사용하는 알고리즘 기법입니다. **최적 부분 구조** 와 **중복 부분 문제** 라는 두 조건을 만족하는 문제에 적용할 수 있습니다.

- **Q. DP 와 분할 정복의 차이는?**
  - 둘 다 문제를 하위 문제로 나누어 해결하지만, **분할 정복은 하위 문제가 독립적** 이고 **DP 는 하위 문제가 중복** 됩니다. DP 는 중복 계산을 피하기 위해 결과를 저장해 재사용하는 반면, 분할 정복은 저장하지 않습니다.

- **Q. Memoization 과 Tabulation 중 어떤 것을 선호하나요?**
  - 상황에 따라 다릅니다. **Memoization** 은 재귀 기반으로 직관적이고 필요한 하위 문제만 계산하지만 재귀 오버헤드가 있습니다. **Tabulation** 은 반복문 기반으로 일반적으로 더 빠르고 메모리 효율이 좋지만 계산 순서를 고려해야 합니다. 성능이 중요하면 Tabulation, 가독성이 중요하면 Memoization 을 선호합니다.

- **Q. 피보나치를 재귀로 구현하면 왜 느린가요?**
  - `fib(n) = fib(n-1) + fib(n-2)` 를 단순 재귀로 구하면 같은 하위 문제가 **여러 번 중복 계산** 되어 시간 복잡도가 `O(2ⁿ)` 이 됩니다. DP 로 결과를 저장하면 각 하위 문제를 한 번만 계산해 `O(N)` 으로 줄일 수 있습니다.

- **Q. DP 문제를 해결하는 순서를 설명해주세요.**
  - 1) **점화식(Recurrence Relation) 정의** : 하위 문제들의 관계를 수식으로 표현합니다. 2) **Base Case 정의** : 가장 작은 하위 문제의 답을 정합니다. 3) **DP 테이블 초기화** 및 채우는 순서 결정 (Top-Down 또는 Bottom-Up). 4) **최종 답 추출**. 특히 점화식 정의가 DP 문제에서 가장 어려운 부분입니다.
