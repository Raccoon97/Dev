

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

<br><br><br>

# Extension 을 이용해 Protocol 따르게 하기
- 이미 존재하는 타입에 Protocol 을 따르게 하기 위해 Extension 을 사용할 수 있다.
- 원래 값에 접근 권한이 없어도 Extension 을 활용해 기능을 확장할 수 있다.
>- 이미 Extension 으로 확장된 타입에 Extension 을 추가하면 그 타입에 추가된 기능을 사용할 수 있다.
```swift
protocol TextRepresentable {
  var textualDescription: String { get }
}

extension Dice: TextRepresentable {
  var textualDescription: String {
    return "A \(sides)-sided dice"
  }
}

let d12 = Dice(sides: 12, generator: LinearCongruentialGenerator())
print(d12.textualDescription) // "A 12-sided dice"
```

<br>

### 조건적으로 Protocol 을 따르기
- 특정 조건을 만족시킬 때만 Protocol 을 따르도록 제한할 수 있다.
- where 키워드를 이용해 정의한다.
- 아래 코드는 TextRepresentable을 따르는 Array중에 Array의 각 원소가 TextRepresentable인 경우에만 따르는 프로토콜을 정의한다.
```swift
extension Array: TextRepresentable where Element: TextRepresentable {
  var textualDescription: String {
    let itemsAsText = self.map { $0.textualDescription }
    return "[" + itemsAsText.joined(separator: ", ") + "]"
  }
}
let myDice = [d6, d12]
print(myDice.textualDescription) // "[A 6-sided dice, A 12-sided dice]"

// Array 의 각 원소가 TextRepresentable 을 따르기 때문에 textualDecription Property 를 사용할 수 있다.
// textualDescription는 Array의 모든 아이템을 순회하고 각각의 textualDescription를 결합해 반환하는 Method 이다.
```

### Extension 을 이용해 Protocol 사용 선언하기
- 어떤 Protocol 을 사용하는 모든 조건을 만족하지만 아직 그 Protocol 을 따른다는 선언을 하지 않았다면, 빈 Extension 으로 선언할 수 있다.
- 아래 코드는 Protocol 을 따른다는 선언은 Extension 에 하고 Protocol 을 따르기 위한 구현은 Struct 에 구현해 사용하는 예시이다.
```swift
struct Hamster {
  var name: String
  var textualDescription: String {
    return "A hamster named \(name)"
  }
}
extension Hamster: TextRepresentable { }

let simonTheHamster = Hamster(name: "Simon")
let somthingTextRepresentable: TextRepresentable = simonTheHamster
print(somethingTextRepresentable.textualDescription) // "A hamster named Simon"
```
- Protocol 의 요구사항을 기술하는 것만으로 Protocol 의 사용 조건을 충족시킬 수 없다.
- 반드시 어떤 Protocol 을 따르는지 기술해야 한다.

<br><br><br>

# Protocol 타입 콜렉션
- Protocol 을 Array, Dictionary 등 콜렉션 타입에 넣기 위한 타입으로 사용할 수 있다.
- 아래 코드는 Protocol 을 따르는 Array 의 사용 예시이다.
```swift
let things: [TextRepresentable] = [game, d12, simonTheHamster]
// 모든 객체는 TextRepresentable 을 따르므로 textualDescription Propety 를 갖는다.

for things in things {
  print(thing.textualDescription)
}
// A game of Snakes and Ladders with 25 squares
// A 12-sided dice
// A hamster named Simon
```

<br><br><br>

# Property 상속
- Class 상속처럼 Protocol 도 상속할 수 있다.
- 여러 Protocol 을 상속받는 경우 콤마(,) 로 구분한다.
```swift
protocol InheritingProtocol: SomeProtocol, AnotherProtocol {
  // protocol definition goes here
}
```
- 아래 코드는 TextRepresentable Protocol 을 상속받아 새로운 Protocol PrettyRepresentable 을 구현하여 사용하는 예시이다.
```swift
protocol PrettyTextRepresentable: TextRepresentable {
  var prettyTextualDescription: String { get }
}

extension SnakesAndLadders: PrettyTextRepresentable {
  var prettyTextualDescription: String {
    var output = textualDescription + ":\n"
    for index in 1...finalSquare {
      switch board[index] {
      case let ladder where ladder > 0:
        output += "▲ "
      case let snake where snake < 0:
        output += "▼ "
      default:
        output += "○ "
      }
    }
    return output
  }
}

print(game.prettyTextualDescription)
// A game of Snakes and Ladders with 25 squares:
// ○ ○ ▲ ○ ○ ▲ ○ ○ ▲ ▲ ○ ○ ○ ▼ ○ ○ ○ ○ ▼ ○ ○ ▼ ○ ▼ ○
```

<br><br><br>

# Protocol 합성
- 동시에 여러 Protocol 을 따르는 타입을 선언할 수 있다. 
- 아래 코드는 동시에 여러 Protocol 을 따르는 방법의 예시이다.
```swift
protocol Named {
  var name: String { get }
}
protocol Aged {
  var age: Int { get }
}

// 동시에 Named, Aged Protocol 을 따르는 Struct 이다.
struct Person: Named, Aged {
  var name: String
  var age: Int
}
func wishHappyBirthday(to celebrator: Named & Aged) {
  print("Happy birthday, \(celebrator.name), you're \(celebrator.age)!")
}
let birthdayPerson = Person(name: "Malcolm", age: 21)
wishHappyBirthday(to: birthdayPerson) //  "Happy birthday, Malcolm, you're 21!"


// Location 프로토콜과 위의Named 프로토콜을 따르는 City 클래스의 구현
class Location {
  var latitude: Double
  var longitude: Double
  init(latitude: Double, longitude: Double) {
    self.latitude = latitude
    self.longitude = longitude
  }
}
class City: Location, Named {
  var name: String
  init(name: String, latitude: Double, longitude: Double) {
    self.name = name
    super.init(latitude: latitude, longitude: longitude)
  }
}
func beginConcert(in location: Location & Named) {
  print("Hello, \(location.name)!")
}

let seattle = City(name: "Seattle", latitude: 47.6, longitude: -122.3)
beginConcert(in: seattle)
// Prints "Hello, Seattle!"
```
<br><br><br>

# Protocol Conform 확인
- 어떤 타입이 특정 Protocol 을 따르는지 다음과 같은 방법으로 확인할 수 있다.
- is 를 이용하여 어떤 타입이 특정 Protocol 을 따르는지 확인 가능하다. 따르면 true/ 따르지 않으면 false 반환
- as? 는 특정 Protocol 을 따르는 경우 그 Optional 타입의 Protocol 타입으로 다운캐스트를 하게 되고 따르지 않는 경우 nil 을 반환한다.
- as! 는 강제로 특정 Protocol 을 따르도록 정의한다. 다운캐스트에 실패하면 런타임 에러가 발생한다.
- 아래 코드는 as? 확인 방법의 예시이다.
```swift
// area 라는 값을 필요로 하는 HasArea Protocol 을 선언한다.
protocol HasArea {
    var area: Double { get }
}

// HasArea Protocol 을 따르는 Circle, Country Class 를 선언한다.
class Circle: HasArea { // Computed Property 구현
  let pi = 3.1415927
  var radius: Double
  var area: Double { return pi radius radius }
  init(radius: Double) { self.radius = radius }
}
class Country: HasArea {
  var area: Double  // Stored Property 구현
  init(area: Double) { self.area = area }
}

// HasArea Protocol 을 따르지 않는 Animal Class 를 선언한다.
class Animal {
  var legs: Int
  init(legs: Int) { self.legs = legs }
}

// Circle, Country, Animal 의 인스턴스를 objects Array 에 넣는다.
let objects: [AnyObject] = [
  Circle(radius: 2.0),
  Country(area: 243_610),
  Animal(legs: 4)
]

// Array 를 순회하며 as? HasArea 구문을 사용해 Protocol 을 따르는지 확인한 후 따르는 경우 HasArea 타입으로 다운캐스팅 한다.
  // 다운캐스팅 - 부모클래스의 타입을 자식클래스의 타입으로 다운하여 캐스팅한다 
for object in objects {
  if let objectWithArea = object as? HasArea {
      print("Area is \(objectWithArea.area)")
  } else {
      print("Something that doesn't have an area")
  }
}
// Circle, Country 인스턴스는 HasArea 를 따르기 때문에 area 값이 반환되고, Animal 인스턴스는 else 절이 실행된다.
// Area is 12.5663708
// Area is 243610.0
// Something that doesn't have an area
```

<br><br><br>

# Optional Protocol 요구조건
- Protocol 을 선언하면서 필수 구현이 아닌 Optional 구현 조건을 정의할 수 있다.
- 이 Protocol 의 정의를 위해 @objc 키워드를 Protocol 앞에 붙이고, 개별 Func, Property 에는 @objc 와 Optional 키워드를 붙인다.
- @objc Protocol 은 Class 타입에서만 사용할 수 있고, Struct, Enum 에서는 사용할 수 없다.
- 아래 코드는 두 가지 Optional 구현을 할 수 있는 Protocol 의 예시이다.
```swift
@objc protocol CounterDataSource {
    @objc optional func increment(forCount count: Int) -> Int
    @objc optional var fixedIncrement: Int { get }
}

// Counter Class 에서 CounterDataSource 를 따르는 dataSource 를 선언
class Counter {
    var count = 0
    var dataSource: CounterDataSource?
    func increment() {
        if let amount = dataSource?.increment?(forCount: count) {
            count += amount
        } else if let amount = dataSource?.fixedIncrement {
            count += amount
        }
        // increment?(forCount: count), fixedIncrement 는 Optional 이므로 구현이 안되어이 있을 수 있기 때문에 Optional Chaining 을 이용해 확인해본다.
    }
}

// CounterDataSource Protocol 을 따르는 ThreeSource Class 를 선언한다.
class ThreeSource: NSObject, CounterDataSource {
    let fixedIncrement = 3
}

// Counter 인스턴스의 dataSource 를 ThreeSource 로 부터 입력받아 값을 증가시킬 수 있다.
var counter = Counter()
counter.dataSource = ThreeSource()
for _ in 1...4 {
    counter.increment()
    print(counter.count)
}
// 3
// 6
// 9
// 12

// 복잡한 예제로 CounterDataSource 를 이용해 어떤 값을 0에 수렴하도록 만드는 클래스를 선언한다.
class TowardsZeroSource: NSObject, CounterDataSource {
    func increment(forCount count: Int) -> Int {
        if count == 0 {
            return 0
        } else if count < 0 {
            return 1
        } else {
            return -1
        }
    }
}

// -4 부터 시작하지만 TowardZeroSource 의 increment 에 의해 counter.increment() 가 호출될 때 마다 0에 가까워지면서 결국 0에 수렴한다.
counter.count = -4
counter.dataSource = TowardsZeroSource()
for _ in 1...5 {
    counter.increment()
    print(counter.count)
}
// -3
// -2
// -1
// 0
// 0
```

<br><br><br>

# Protocol Extension
- Extension 을 이용해 Protocol 을 확장할 수 있다.
- 아래 코드는 RandomNumberGenerator 에 randomBool() 을 추가하여 사용하는 예시이다.
```swift
extension RandomNumberGenerator {
  func randomBool() -> Bool {
    return random() > 0.5
  }
}

let generator = LinearCongruentialGenerator()
print("Here's a random number: \(generator.random())") // "Here's a random number: 0.3746499199817101"
print("And here's a random Boolean: \(generator.randomBool())") // "And here's a random Boolean: true"
```
