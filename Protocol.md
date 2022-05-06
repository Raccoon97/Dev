

# Protocol
- Protocol 은 특정 기능 수행에 필수적인 요소를 정의한 청사진이다.
- Protocol 을 만족시키는 타입을 Protocol 을 따른다고 한다.
- Protocol 에 기능을 추가하기 위해 Extension 하는 것이 가능하다.

<br><br><br>

# Protocol 문법
- Protocol 의 정의는 Class, Struct, Enum 등과 유사하다.
```swift
protocol SomeProtocol {
  // protocol definition goes here
}
```
- Protocol 을 따르는 타입은 아래와 같이 작성한다.
```swif
struct SomeStructure: FirstProtocol, AnotherProtocol {
  // structure definition goes here
}
```
- 서브클래싱인 경우 수퍼클래스를 맨 앞에 적어준다.
```swift
class SomeClass: SomeSuperClass, FirstProtocol, AnotherProtocol {
  // class definition goes here
}
```

<br><br><br>

# Property 요구사항
- Protocol 에서는 Property 가 Stored Property 인지 Computed Property 인지 명확하지 않다.
- Property 의 이름과 타입, Gettable, Settable 한지는 명시하며, 필수 Property 는 항상 var 키워드로 선언해야 한다.
```swift
protocol SomeProtocol {
  var mustBeSettable: Int { get set }
  var doesNotNeedToBeSettable: Int { get }
}
```
- 타입을 갖는 Property 는 static 키워드로 선언해야 한다.
```swift
protocol AnotherProtocol {
  static var someTypeProperty: Int { get set }
}
```
- 아래 코드는 하나의 Property 를 갖는 Protocol 을 선언하고 Stored Property 와 Computed Property 로 사용하는 예시이다.
```swift
protocol FullyNamed {
  var fullName: String { get }
}

// Stored Property 로 사용하기 위한 Struct
struct Person: FullyNamed {
  var fullName: String
}
let john = Person(fullName: "John Appleseed") // john.fullName == "John Appleseed"

// Computed Property 로 사용하기 위한 Class
class Starship: FullyNamed {
  var prefix: String?
  var name: String
  init(name: String, prefix: String? = nil) {
    self.name = name
    self.prefix = prefix
  }
  var fullName: String {
    return (prefix != nil ? prefix! + " " : "") + name
  }
}
var ncc1701 = Starship(name: "Enterprise", prefix: "USS") // ncc1701.fullName == "USS Enterprise"
```

<br><br><br>

# Method 요구사항
- Protocol 에서는 Method 를 명시할 수 있다.
- Method 파라미터의 기본 값은 Protocol 안에서 사용할 수 없다.
```swift
protocol SomeProtocol {
  static func someTypeMethod()
  func someInstanceMethod()
}
```
- 아래 코드는 Protocol 에서 필수 Method 를 명시하고 그 Protocol 을 따르는 클래스에서 Method 를 구현하는 예시이다.
```swift
protocol RandomNumberGenerator {
  func random() -> Double
} // 필수 Method 지정시 함수명과 반환값을 지정할 수 있고, 구현에 사용되는 괄호는 적지 않아도 된다.

class LinearCongruentialGenerator: RandomNumberGenerator {
  var lastRandom = 42.0
  let m = 139968.0
  let a = 3877.0
  let c = 29573.0
  // ------------------------- Protocol 의 Method 구현부
  func random() -> Double {
      lastRandom = ((lastRandom * a + c).truncatingRemainder(dividingBy:m))
      return lastRandom / m
  }
  // ------------------------- Protocol 의 Method 구현부
}
let generator = LinearCongruentialGenerator()
print("Here's a random number: \(generator.random())") // "Here's a random number: 0.3746499199817101"
print("And another one: \(generator.random())") // "And another one: 0.729023776863283"
```
- 아래 코드는 Protocol 에서 필수 Method 를 명시하고 그 Protocol 을 따르는 클래스에서 필수 Method 를 구현하지 않았을 때 발생하는 에러 예시이다.
```swift
protocol someProtocol {
  func yesConform() -> Double
}

class someClass: someProtocol { // Error : Type 'someClass' does not conform to protocol 'someProtocol'
  func noConform() -> Double {
    return 0.0
  }
}
```

<br><br><br>

# Mutating Method 요구사항
- mutating 키워드는 값타입 에만 사용한다.
- Protocol 에 mutating 을 명시한 경우 이 Protocol 을 따르는 Class 를 구현할 때에는 Method 에 mutating 을 명시하지 않아도 된다.
>- Struct 나 Enum 에 대해서는 mutating 을 명시해야 함.
- 아래 코드는 mutating Method 를 선언한 Protocol 의 사용 예시이다.
```swift
protocol Togglable {
  mutating func toggle()
}

enum OnOffSwitch: Togglable {
  case off, on
  mutating func toggle() {
    switch self {
    case .off:
      self = .on
    case .on:
      self = .off
    }
  }
}
```

<br><br><br>

# 이니셜라이저 요구사항
- Protocol 에서 필수로 구현해야하는 이니셜라이저를 지정할 수 있다.
```swift
protocol SomeProtocol {
  init(someParameter: Int)
}
```

<br>

### Class 에서 Protocol 필수 이니셜라이저의 구현
- Protocol 에서 특정 이니셜라이저가 필요하다고 명시했기 때문에 Protocol 을 따르는 Class 의 구현에서 해당 이니셜라이저에 required 키워드를 붙여줘야 한다.
- Class 타입에서 final 로 선언된 것에는 required 를 표시하지 않아도 된다, final 로 선언되면 서브클래싱 되지 않기 때문이다.
>- 서브클래싱 : 부모로 부터 성격을 상속받고 자기 자신 고유의 특성도 추가할 수 있다.
>- Protocol 선언부에서는 이니셜라이저 앞에 final 키워드를 사용할 수 없다.
```swift
class SomeClass: SomeProtocol {
  required init(someParemeter: Int) {
      // initializer implementation goes here
  }
    
}

final class SomeFinalClass: SomeProtocol {
  init(someParemeter: Int) {
      // initializer implementation goes here
  }
}
```
- 특정 Protocol 의 필수 이니셜라이저를 구현하고, SuperClass 의 이니셜라이저를 서브클래싱 하는 경우 이니셜라이저 앞에 required 키워드와 override 키워드를 붙여준다.
```swift
protocol SomeProtocol {
  init()
}

class SomeSuperClass {
  init() {
    // initializer implementation goes here
  }
}

class SomeSubClass: SomeSuperClass, SomeProtocol { 
  // required --> SomeProtocol Conformance, override --> SomeSuperClass SubClassing
  required override init() {
    // initializer implementation goes here
  }
}
```

<br>

### Failable 이니셜라이저 요구사항
- Protocol 에 Failable 한 이니셜라이저를 선언할 수 있다.
- Failable 이니셜라이저 : Class, Struct, Enum 에서 초기화를 하다가 실패하는 경우가 있을 수 있다면 정의하는 이니셜라이저.
>- Optional Type 처럼 init 뒤에 ? 를 붙여주면 된다.
```swift
// Failable 이니셜라이저의 예시
struct Animal { 
  let species: String 
  init?(species: String) { 
    if species.isEmpty { 
      return nil 
    } 
    self.species = species 
  } 
}
```
- Failable 이니셜라이저를 Protocol 에서 사용하는 법
```swift
protocol Something {
  init?()
}

struct Some: Something {
  init() {
  }
}
```

<br><br><br>

# 타입으로써의 Protocol
- Protocol 도 하나의 타입으로 사용되므로 다음과 같은 상황에서 Protocol 을 사용할 수 있다.
>- Func, Method, 이니셜라이저의 파라미터 타입 혹은 리턴 타입
>- let, var, Property 의 타입
>- 컨테이너인 Array, Dictionary 등의 아이템 타입
- Protocol 은 타입이기 때문에 첫 글자를 대문자로 적어준다.
- 아래 코드는 Protocol 을 타입으로 사용한 예시이다.
```swift
protocol RandomNumberGenerator {
  func random() -> Double
}

class LinearCongruentialGenerator: RandomNumberGenerator {
  var lastRandom = 42.0
  let m = 139968.0
  let a = 3877.0
  let c = 29573.0
  func random() -> Double {
    lastRandom = ((lastRandom * a + c).truncatingRemainder(dividingBy:m))
    return lastRandom / m
  }
}

class Dice {
  let sides: Int
  let generator: RandomNumberGenerator
  init(sides: Int, generator: RandomNumberGenerator) {
    self.sides = sides
    self.generator = generator
  }
  func roll() -> Int {
    return Int(generator.random() * Double(sides)) + 1
  }
}

var d6 = Dice(sides: 6, generator: LinearCongruentialGenerator())
for _ in 1...5 {
  print("Random dice roll is \(d6.roll())")
}

"""
    RandomNumberGenerator 를 generator 상수의 타입으로 그리고 이니셜라이저의 파라미터 형으로 사용했다.
    Dice를 초기화 할 때 generator 파라미터 부분에 RandomNumberGenerator Protocol 을 따르는 인스턴스를 넣습니다.
"""
```

<br><br><br>

# Delegation
- Delegation 은 Class 혹은 Strutc 인스턴스에 특정 행위에 대한 책임을 넘길 수 있게 해주는 디자인 패턴 중 하나이다.
```swift
protocol DiceGame {
  var dice: Dice { get }
  func play()
}
protocol DiceGameDelegate: AnyObject {
  func gameDidStart(_ game: DiceGame)
  func game(_ game: DiceGame, didStartNewTurnWithDiceRoll diceRoll: Int)
  func gameDidEnd(_ game: DiceGame)
}
```
- DiceGame Protocol 을 선언하고 DiceGameDelegated 에 선언해서 실제 DiceGame 의 행위와 관련된 구현을 DiceGameDelegate 를 따르는 인스턴스에 위임한다.
- DiceGameDelegate 를 AnyObject 로 선언하면 Class 만 이 Protocol 을 따를 수 있게 한다.
```swift
class SnakesAndLadders: DiceGame {
  let finalSquare = 25
  let dice = Dice(sides: 6, generator: LinearCongruentialGenerator())
  var square = 0
  var board: [Int]
  init() {
    board = Array(repeating: 0, count: finalSquare + 1)
    board[03] = +08; board[06] = +11; board[09] = +09; board[10] = +02
    board[14] = -10; board[19] = -11; board[22] = -02; board[24] = -08
  }
  weak var delegate: DiceGameDelegate?
  func play() {
    square = 0
    delegate?.gameDidStart(self)
    gameLoop: while square != finalSquare {
      let diceRoll = dice.roll()
      delegate?.game(self, didStartNewTurnWithDiceRoll: diceRoll)
      switch square + diceRoll {
      case finalSquare:
        break gameLoop
      case let newSquare where newSquare > finalSquare:
        continue gameLoop
      default:
        square += diceRoll
        square += board[square]
        }
      }
    delegate?.gameDidEnd(self)
  }
}
```
- SnakesAndLadders 는 DiceGame Protocol 을 따른다.
- DiceGameDelegate Protocol 을 따르는 Delegate 'delegate' 를 갖는다.
- 게임을 실행했을 때 delegate?.gameDidStart(self), delegate?.game(self, didStartNewTurnWithDiceRoll: diceRoll), delegate?.gameDidEnd(self)를 실행한다.
- delegate는 게임을 진행시키는데 반드시 필요한 건 아니라서 옵셔널로 정의되어 있다.
- 아래 코드는 DiceGameDelegate 를 상속하는 delegate DiceGameTracker 를 구현한 예시이다.
```swift
class DiceGameTracker: DiceGameDelegate {
  var numberOfTurns = 0
  func gameDidStart(_ game: DiceGame) {
    numberOfTurns = 0
    if game is SnakesAndLadders {
      print("Started a new game of Snakes and Ladders")
    }
    print("The game is using a \(game.dice.sides)-sided dice")
  }
  func game(_ game: DiceGame, didStartNewTurnWithDiceRoll diceRoll: Int) {
    numberOfTurns += 1
    print("Rolled a \(diceRoll)")
  }
  func gameDidEnd(_ game: DiceGame) {
    print("The game lasted for \(numberOfTurns) turns")
  }
}
```
- DiceGameTracker 를 이용해서 게임을 진행시킨다. 게임으 tracking 관련된 작업은 DiceGameTracker 가 위임 받아 그 곳에서 싫행된다.
```swift
let tracker = DiceGameTracker()
let game = SnakesAndLadders()
game.delegate = tracker
game.play()
// Started a new game of Snakes and Ladders
// The game is using a 6-sided dice
// Rolled a 3
// Rolled a 5
// Rolled a 4
// Rolled a 5
// The game lasted for 4 turns
```

# Extension 을 이용해 Protocol 따르게 하기
- 이미 
