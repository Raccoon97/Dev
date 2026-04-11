# 🏠   [Go Main](../../README.md)   🏠
- [SOLID 원칙이란?](#solid-원칙이란)
- [S - Single Responsibility Principle](#s---single-responsibility-principle)
- [O - Open/Closed Principle](#o---openclosed-principle)
- [L - Liskov Substitution Principle](#l---liskov-substitution-principle)
- [I - Interface Segregation Principle](#i---interface-segregation-principle)
- [D - Dependency Inversion Principle](#d---dependency-inversion-principle)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# SOLID 원칙이란?
- 객체지향 프로그래밍과 설계의 **5 가지 기본 원칙** 이다.
- Robert C. Martin (Uncle Bob) 이 정리했다.
- **유연하고 유지보수 가능한 소프트웨어** 를 만들기 위한 가이드라인이다.

<br><br><br>

# S - Single Responsibility Principle
- **단일 책임 원칙**
- 하나의 클래스는 **하나의 책임만** 가져야 한다.
- 클래스를 변경해야 하는 이유는 오직 하나여야 한다.

### 나쁜 예 ❌

```swift
class UserManager {
    func saveUserToDB(_ user: User) { ... }
    func sendEmailToUser(_ user: User) { ... }  // 이메일 전송은 다른 책임
    func generateUserReport(_ user: User) { ... }  // 리포트 생성은 또 다른 책임
}
```

### 좋은 예 ✅

```swift
class UserRepository {
    func saveUser(_ user: User) { ... }
}

class EmailService {
    func sendEmail(to user: User) { ... }
}

class ReportGenerator {
    func generateReport(for user: User) { ... }
}
```

<br><br><br>

# O - Open/Closed Principle
- **개방-폐쇄 원칙**
- 소프트웨어는 **확장에는 열려** 있고, **수정에는 닫혀** 있어야 한다.
- 새로운 기능을 추가할 때 기존 코드를 수정하지 않고 확장할 수 있어야 한다.

### 나쁜 예 ❌

```swift
class DiscountCalculator {
    func calculate(type: String, price: Double) -> Double {
        if type == "VIP" { return price * 0.7 }
        else if type == "Regular" { return price * 0.9 }
        // 새로운 타입이 추가되면 이 함수를 수정해야 함
        return price
    }
}
```

### 좋은 예 ✅

```swift
protocol DiscountPolicy {
    func calculate(_ price: Double) -> Double
}

struct VIPDiscount: DiscountPolicy {
    func calculate(_ price: Double) -> Double { price * 0.7 }
}

struct RegularDiscount: DiscountPolicy {
    func calculate(_ price: Double) -> Double { price * 0.9 }
}

// 새 할인 정책은 기존 코드를 수정하지 않고 새 타입만 추가하면 됨
```

<br><br><br>

# L - Liskov Substitution Principle
- **리스코프 치환 원칙**
- 자식 클래스는 언제나 **부모 클래스를 대체** 할 수 있어야 한다.
- 즉, 부모 타입으로 선언된 변수에 자식 객체를 넣어도 프로그램이 정상 작동해야 한다.

### 나쁜 예 ❌
- 정사각형(Square) 이 직사각형(Rectangle) 을 상속하면, `width` 와 `height` 를 독립적으로 변경할 수 없어 LSP 를 위반한다.

### 좋은 예 ✅
- 공통된 행위만 부모에 두거나, 상속 대신 protocol 이나 composition 을 사용한다.

<br><br><br>

# I - Interface Segregation Principle
- **인터페이스 분리 원칙**
- 클라이언트는 **자신이 사용하지 않는** 메서드에 의존해서는 안 된다.
- 하나의 큰 interface 보다 여러 개의 작은 interface 로 분리해야 한다.

### 나쁜 예 ❌

```swift
protocol Worker {
    func work()
    func eat()
}

class Robot: Worker {
    func work() { ... }
    func eat() { }  // 로봇은 먹지 않지만 강제로 구현해야 함
}
```

### 좋은 예 ✅

```swift
protocol Workable {
    func work()
}

protocol Eatable {
    func eat()
}

class Human: Workable, Eatable {
    func work() { ... }
    func eat() { ... }
}

class Robot: Workable {
    func work() { ... }
}
```

<br><br><br>

# D - Dependency Inversion Principle
- **의존성 역전 원칙**
- 고수준 모듈은 **저수준 모듈에 의존해서는 안 되며**, 둘 다 **추상화에 의존** 해야 한다.
- **구체 타입** 이 아닌 **프로토콜(인터페이스)** 에 의존하게 설계한다.

### 나쁜 예 ❌

```swift
class UserService {
    let database = MySQLDatabase()  // 구체 타입에 의존
}
```

### 좋은 예 ✅

```swift
protocol Database {
    func save(_ user: User)
}

class MySQLDatabase: Database { ... }
class MongoDatabase: Database { ... }

class UserService {
    let database: Database  // 추상화에 의존
    
    init(database: Database) {
        self.database = database
    }
}
```

- 이를 **의존성 주입 (Dependency Injection, DI)** 이라고 한다.

<br><br><br>

# 면접 예상 질문
- **Q. SOLID 원칙이 무엇인가요?**
  - 객체지향 설계의 5 가지 원칙으로, 단일 책임(S), 개방-폐쇄(O), 리스코프 치환(L), 인터페이스 분리(I), 의존성 역전(D) 원칙을 말합니다. 유지보수성과 확장성이 높은 소프트웨어를 만들기 위한 가이드라인입니다.

- **Q. SRP 를 지키면 어떤 이점이 있나요?**
  - 하나의 클래스가 하나의 책임만 가지면 변경의 이유가 하나로 줄어, 수정에 따른 파급 효과가 작아집니다. 또 코드를 이해하고 테스트하기 쉬워지며, 재사용성도 높아집니다.

- **Q. OCP 는 어떻게 구현하나요?**
  - Swift 에서는 **protocol** 과 **다형성** 을 활용해 구현합니다. 동작을 protocol 로 추상화하고, 구현체를 추가하는 방식으로 기능을 확장하면 기존 코드를 수정하지 않고도 확장이 가능합니다.

- **Q. DIP 와 DI 의 차이는?**
  - DIP (의존성 역전 원칙) 는 **설계 원칙** 으로 "추상화에 의존해야 한다" 는 방향성을 제시합니다. DI (의존성 주입) 는 이를 **구현하는 기법** 으로, 의존 객체를 외부에서 주입받는 방식입니다. DI 는 DIP 를 실현하는 대표적인 수단입니다.

- **Q. SOLID 원칙을 실무에서 모두 지키나요?**
  - 현실적으로 모든 원칙을 엄격히 지키는 것은 어렵고, 과하게 적용하면 오히려 복잡해질 수 있습니다. 프로젝트의 규모, 변경 가능성, 팀 컨벤션에 맞춰 **균형 있게** 적용하는 것이 중요합니다. 특히 SRP 와 DIP 는 자주 의식적으로 지키려 노력합니다.
