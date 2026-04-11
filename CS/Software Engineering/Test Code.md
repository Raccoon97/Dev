# 🏠   [Go Main](../../README.md)   🏠
- [Test Code 란?](#test-code-란)
- [Test 의 종류](#test-의-종류)
- [Unit Test 의 원칙 - F.I.R.S.T.](#unit-test-의-원칙---first)
- [Given - When - Then](#given---when---then)
- [Test Double](#test-double)
- [TDD (Test Driven Development)](#tdd-test-driven-development)
- [Code Coverage](#code-coverage)
- [Swift 에서의 테스트](#swift-에서의-테스트)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# Test Code 란?
- 코드가 **의도대로 동작하는지** 검증하기 위한 코드이다.
- 자동화된 테스트를 작성해 **회귀(Regression) 버그** 를 방지하고, 코드 변경에 대한 안정성을 확보한다.

### 테스트 코드의 이점
- **버그 조기 발견** : 배포 전에 문제를 찾을 수 있다.
- **리팩토링 안정성** : 기존 동작을 보장하며 구조를 개선할 수 있다.
- **명세 역할** : 테스트 자체가 코드의 사용 예시와 명세가 된다.
- **자신감** : 코드 변경 후에도 안심하고 배포할 수 있다.

<br><br><br>

# Test 의 종류

### Test Pyramid

```
         /\
        /  \
       / E2E\      ← 느리고 비쌈, 적게
      /------\
     /  통합  \
    /----------\
   /   단위     \   ← 빠르고 저렴, 많이
  /--------------\
```

### 1. Unit Test (단위 테스트)
- 함수, 메서드, 클래스 등 **가장 작은 단위** 를 테스트한다.
- 외부 의존성을 **격리** 하고 (Mock 사용) 순수 로직만 검증.
- 빠르게 실행되며 가장 많이 작성된다.

### 2. Integration Test (통합 테스트)
- 여러 모듈이 **함께 동작하는지** 테스트한다.
- DB, 네트워크, 파일 시스템 등 실제 의존성을 포함할 수 있다.

### 3. E2E Test (End-to-End)
- 사용자 관점에서 **전체 시스템** 이 정상 동작하는지 테스트한다.
- 느리고 비용이 크지만 실제 사용자 경험을 검증할 수 있다.

### 4. UI Test
- 앱의 UI 가 의도대로 동작하는지 테스트한다.
- iOS 에서는 `XCUITest` 를 사용.

### 5. Performance Test
- 성능(실행 시간, 메모리 사용량) 을 측정한다.
- iOS 에서는 `measure` 블록을 사용.

<br><br><br>

# Unit Test 의 원칙 - F.I.R.S.T.

| 원칙 | 설명 |
|---|---|
| **Fast** | 테스트는 빠르게 실행되어야 한다 |
| **Independent** | 테스트 간 의존성이 없어야 한다 |
| **Repeatable** | 어떤 환경에서도 같은 결과가 나와야 한다 |
| **Self-validating** | Pass/Fail 이 자동으로 결정되어야 한다 |
| **Timely** | 테스트는 제품 코드와 함께 작성되어야 한다 |

<br><br><br>

# Given - When - Then
- 테스트 코드를 작성할 때 자주 사용되는 구조이다.

- **Given** : 테스트를 위한 **초기 상태** 를 준비한다.
- **When** : 테스트할 **동작** 을 실행한다.
- **Then** : 결과가 **기대한 대로** 인지 검증한다.

```swift
func test_sum_twoPositiveNumbers_returnsSum() {
    // Given
    let calculator = Calculator()
    
    // When
    let result = calculator.sum(2, 3)
    
    // Then
    XCTAssertEqual(result, 5)
}
```

### 테스트 이름 규칙
- 보통 `test_<대상>_<상황>_<기대결과>` 의 형태로 작성.
- 예 : `test_login_withWrongPassword_returnsError`

<br><br><br>

# Test Double
- 실제 객체를 대체해 테스트에 사용하는 **가짜 객체** 들을 통칭한다.
- 외부 의존성을 격리하고 테스트를 안정적으로 만든다.

### 1. Dummy
- 단순히 **자리만 채우는** 객체. 실제로는 사용되지 않는다.

### 2. Stub
- **미리 정해진 값** 을 반환한다. 상태 검증에 사용.

```swift
class StubNetworkClient: NetworkClient {
    func fetch() -> Data { return "stubbed data".data(using: .utf8)! }
}
```

### 3. Mock
- **호출되었는지, 몇 번 호출되었는지** 를 검증한다. 행위 검증에 사용.

```swift
class MockAnalytics: Analytics {
    var logCalled = false
    func log(_ event: String) { logCalled = true }
}
```

### 4. Fake
- 실제와 동작은 같지만 **단순화된** 구현체. 예 : In-Memory DB.

### 5. Spy
- 실제 객체의 동작을 수행하면서 **호출 정보를 기록** 한다.

<br><br><br>

# TDD (Test Driven Development)
- **테스트 주도 개발** 로, 테스트 코드를 **먼저** 작성하고 이를 통과시키는 제품 코드를 작성하는 개발 방식이다.

### Red - Green - Refactor

```
 1. Red      : 실패하는 테스트를 작성한다 (아직 기능이 없음)
 2. Green    : 테스트를 통과할 최소한의 코드를 작성한다
 3. Refactor : 통과한 상태에서 코드를 리팩토링한다
```

### TDD 의 장점
- 요구사항을 **명확히** 이해하게 된다.
- 불필요한 코드를 작성하지 않게 된다.
- **테스트 가능한 설계** 가 자연스럽게 만들어진다.
- **높은 Coverage** 를 확보할 수 있다.

### TDD 의 단점
- 초기 개발 속도가 **느려질 수 있다.**
- 학습 곡선이 있다.
- 모든 상황에서 적합하지는 않다 (탐색적 개발 등).

<br><br><br>

# Code Coverage
- 테스트가 **얼마나 많은 코드** 를 실행하는지 나타내는 지표이다.
- 100% 가 항상 좋은 것은 아니며, **의미 있는 테스트** 를 작성하는 것이 중요하다.

### 종류
- **Statement Coverage** : 실행된 문장의 비율
- **Branch Coverage** : 실행된 분기(if-else) 의 비율
- **Function Coverage** : 실행된 함수의 비율

<br><br><br>

# Swift 에서의 테스트

### XCTest
- Apple 이 제공하는 기본 테스트 프레임워크.

```swift
import XCTest
@testable import MyApp

class CalculatorTests: XCTestCase {
    var sut: Calculator!  // SUT : System Under Test
    
    override func setUp() {
        super.setUp()
        sut = Calculator()
    }
    
    override func tearDown() {
        sut = nil
        super.tearDown()
    }
    
    func test_sum_twoNumbers_returnsSum() {
        XCTAssertEqual(sut.sum(2, 3), 5)
    }
}
```

### 주요 Assert 메서드
- `XCTAssertEqual`, `XCTAssertNotEqual`
- `XCTAssertTrue`, `XCTAssertFalse`
- `XCTAssertNil`, `XCTAssertNotNil`
- `XCTAssertThrowsError`
- `XCTAssertGreaterThan`, `XCTAssertLessThan`

### Swift Testing (Swift 6)
- 새로운 테스트 프레임워크로 매크로 기반의 더 간결한 API 를 제공한다.

```swift
import Testing

@Test func sumTwoNumbers() {
    let result = Calculator().sum(2, 3)
    #expect(result == 5)
}
```

<br><br><br>

# 면접 예상 질문
- **Q. 테스트 코드가 왜 필요한가요?**
  - 코드가 의도대로 동작하는지 자동으로 검증해 **버그를 조기에 발견** 하고, 리팩토링 시에도 기존 동작이 유지됨을 보장합니다. 또한 테스트 자체가 코드의 **사용 예시와 명세** 역할을 하며, 팀원 간 신뢰할 수 있는 변경을 가능하게 합니다.

- **Q. TDD 란 무엇이고 어떤 장점이 있나요?**
  - **Test Driven Development** 는 실패하는 테스트를 먼저 작성한 뒤, 이를 통과시키는 최소한의 코드를 작성하고 리팩토링하는 Red-Green-Refactor 사이클로 개발하는 방식입니다. 요구사항을 명확히 이해하게 되고, 자연스럽게 **테스트 가능한 설계** 가 만들어지며, 회귀 버그를 방지할 수 있습니다.

- **Q. Mock 과 Stub 의 차이는?**
  - **Stub** 은 미리 정해진 값을 반환해 **상태를 검증** 할 때 사용하고, **Mock** 은 함수가 **호출되었는지, 몇 번 호출되었는지** 등 **행위를 검증** 할 때 사용합니다. Stub 은 "무엇을 반환하는가", Mock 은 "어떻게 호출되는가" 에 초점을 둡니다.

- **Q. Unit Test 와 Integration Test 의 차이는?**
  - Unit Test 는 **가장 작은 단위(함수/클래스)** 를 외부 의존성 없이 **격리해서** 테스트합니다. Integration Test 는 여러 모듈이 **함께 동작하는지** 검증하며, DB 나 네트워크 같은 실제 의존성을 포함할 수 있습니다. Unit 은 빠르고 많이, Integration 은 느리고 적게 작성하는 것이 일반적입니다.

- **Q. Code Coverage 100% 를 달성하면 좋은 코드인가요?**
  - 아닙니다. Coverage 는 코드가 **실행되었는지** 를 나타낼 뿐 **의미 있는 검증** 을 보장하지 않습니다. 단순히 함수를 호출만 해도 Coverage 는 올라가지만 Assert 가 없으면 버그를 잡을 수 없습니다. **의미 있는 엣지 케이스** 를 검증하는 테스트가 더 중요합니다.
