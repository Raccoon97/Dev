# 🏠   [Go Main](https://github.com/Raccoon97/Swift/blob/main/README.md)   🏠
- [Extension](https://github.com/Raccoon97/Swift/blob/main/Extension.md#extension)
- [Extension 구문](https://github.com/Raccoon97/Swift/blob/main/Extension.md#extension-%EA%B5%AC%EB%AC%B8)
- [연산 프로퍼티](https://github.com/Raccoon97/Swift/blob/main/Extension.md#%EC%97%B0%EC%82%B0-%ED%94%84%EB%A1%9C%ED%8D%BC%ED%8B%B0)
- [이니셜라이저](https://github.com/Raccoon97/Swift/blob/main/Extension.md#%EC%9D%B4%EB%8B%88%EC%85%9C%EB%9D%BC%EC%9D%B4%EC%A0%80)
>- [클래스에서의 이니셜라이저, 디이니셜라이저](https://github.com/Raccoon97/Swift/edit/main/Extension.md#%ED%81%B4%EB%9E%98%EC%8A%A4%EC%97%90%EC%84%9C%EC%9D%98-%EC%9D%B4%EB%8B%88%EC%85%9C%EB%9D%BC%EC%9D%B4%EC%A0%80-%EB%94%94%EC%9D%B4%EB%8B%88%EC%85%9C%EB%9D%BC%EC%9D%B4%EC%A0%80-extension)
>- [구조체에서의 이니셜라이저](https://github.com/Raccoon97/Swift/edit/main/Extension.md#%EA%B5%AC%EC%A1%B0%EC%B2%B4%EC%97%90%EC%84%9C%EC%9D%98-%EC%9D%B4%EB%8B%88%EC%85%9C%EB%9D%BC%EC%9D%B4%EC%A0%80)
- [Method](https://github.com/Raccoon97/Swift/blob/main/Extension.md#method)
- [Mutating 인스턴스 Method](https://github.com/Raccoon97/Swift/blob/main/Extension.md#mutating-%EC%9D%B8%EC%8A%A4%ED%84%B4%EC%8A%A4-method)
- [서브스크립트](https://github.com/Raccoon97/Swift/blob/main/Extension.md#%EC%84%9C%EB%B8%8C%EC%8A%A4%ED%81%AC%EB%A6%BD%ED%8A%B8)
- [중첩 타입](https://github.com/Raccoon97/Swift/blob/main/Extension.md#%EC%A4%91%EC%B2%A9-%ED%83%80%EC%9E%85)


<br><br><br>

# Extension
- Extension 은 기존 Class, Struct, Enum, Protocol 에 새로운 기능( Property, Method, Initializer, Deinitializer ) 을 추가한다.
- 원본 소스에 접근하지 못하는 타입들도 새로운 기능을 만들 수 있다. ( 원본 소스는 그대로 두고 원하는 기능만 추가 )
- Extension 은 Obj-C 의 Category 와 유사하다. ( 익명 Category )
- 새 기능을 추가할 수 있지만 오버라이드는 할 수 없다.

<br><br><br>

# Extension 구문
```swift
extension SomeType {
  // new functionality to add to SomeType goes here
}
```
- Extension 은 하나 이상의 Protocol 을 적용할 수 있다. 
- Protocol 을 추가하려면 Class 또는 Struct 에서 다른 Class 또는 Struct 를 참조할 때 처럼 사용하면 된다.

```swift
extension SomeType: SomeProtocol, AnotherProtocol {
  // implementation of protocol requirements goes here
}
```
- 새로 Extension 을 정의하면, 거기에 포함된 새 기능들은 Extension 을 정의하기 전에 생성한 인스턴스라고 해도 해당 유형의 모든 인스턴스에서 사용할 수 있다.

<br><br><br>

# 연산 프로퍼티
- Extension 은 기존 유형에 Computed Property 를 추가할 수 있다.
```swift
// 아래 예시는 거리 단위 작업에 대한 5개의 Computed Property 을 Swfit 의 Double 클래스에 Extension 한다.
// 여기서 Double 1.0 은 1m 를 나타내는 것으로 간주된다.
extension Double {
  var km: Double { return self * 1_000.0 }
  var m: Double { return self }
  var cm: Double { return self / 100.0 }
  var mm: Double { return self / 1_000.0 }
  var ft: Double { return self / 3.28084 }
}

let oneInch = 25.4.mm
 print(" One inch is \(oneInch) meters ") // "One inch is 0.0254 meters"
 
 let threeFeet = 3.ft
 print(" Three feet is \(threeFeet) meters ") // "Three feet is 0.914399970739201 meters "
```
- 이러한 Computed Property 는 Double 값이 특정 길이 단위로 간주되어야 함을 나타낸다.
- 반환 값은 Double 유형이며 Double 로 가능한 수학적 계산에서 사용할 수 있다.
```swift
let aMarathon = 42.km + 195.m
print(" A marathon is \(aMaraton) meters long ") // "A marathon is 42195.0 meters long"
```
- Extension 은 새로운 Computed Property 를 추가할 수 있지만 Stored Property 를 추가할 수 없으며 Property Observer 또한 추가될 수 없다.
```swift
extension Int {
  var ten: Int = 10 // Extensions must not contain stored properties
}
```

<br><br><br>

# 이니셜라이저
### 클래스에서의 이니셜라이저, 디이니셜라이저
-  Designated initializer, deinitializer 는 추가할 수 없다.
-  Convenience initializer 는 추가할 수 있다. ( Convenience 는 init 에만 사용할 수 있음 )
-  Convenience initializer 는 최종적으로 Designated initializer 를 호출해야 한다.
```swift

// Designated
      // 클래스의 init Extension
      extension NSString {
        init { print("init") } 
      } // Error
        // Designated initializer cannot be declared in an extension of 'NSString'; did you mean this to be a convenience initializer?

      // 클래스의 deinit Extension
      extension NSString {
        deinit { print("deinit") } 
      } // Error
        // Deinitializers may only be declared within a class

// Convenience
    // 클래스의 convenience init Extension
    extension NSString {
      convenience init(name: NSString) {
        self.init()
    } // PASS

    // 클래스의 convenience deinit Extension
    extension NSString {
      convenience deinit(name: NSString) {
        self.deinit()
    } // Error
      // 'convenience' may only be used on 'init' declarations
      // Deinitalizers may only be declared within a class
```
### 구조체에서의 이니셜라이저
- Extension 으로 이니셜라이저를 추가할 경우 Memberwise Initalizer( 기본 생성자 ) 를 유지한 채 새로운 이니셜라이저를 추가할 수 있다.
- 구조체는 클래스와 달리 이니셜라이저를 따로 구현하지 않았을 경우에 Memberwise 라는 이니셜라이저를 자동으로 제공한다.
- 직접 구조체에 이니셜라이저를 구현하면 Memberwise Initializer 는 제공되지 않는다.
- 구조체에서는 Convenience 키워드를 사용할 수 없다.
- 구조체에서는 디이니셜라이저를 사용할 수 없다.
```swift
struct test { }

  // 구조체의 init Extension
  extension test {
    init(value: Int { self.x = value } 
  } // PASS
```

<br><br><br>

# Method
- Extension 은 새로운 Method 를 추가할 수 있다.
- 아래 코드는 새 Method 를 추가하는 예시이다.
```swift
// 이 Method 는 매개변수가 없고 값을 반환하지 않는 함수이다.
extension Int {
  func repetitions( task: () -> Void ) {
    for _ in 0..<self {
      task()
    }
  }
}

3.repetitions {
  print("Hello!")
}
// Hello!
// Hello!
// Hello!
```

<br><br><br>

# Mutating 인스턴스 Method
- Extension 으로 추가된 Method 는 인스턴스 자체를 수정할 수도 있다.
- self는 Immutating 이므로 self 를 변경해야하는 Method 는 mutating 을 사용해야 한다.
- 아래 코드는 원래 값을 제곱하는 새로운 Method 를 추가하는 예시이다.
```swift
extension Int {
  mutating func square() {
    self = self * self
  }
}
var someInt = 3
someInt.square() // 9
```

<br><br><br>

# 서브스크립트
- Extension 을 이용해 존재하는 타입에 새로운 Subscripts 를 추가할 수 있다.
```swift
// subscript[n] 은 숫자의 오른쪽에서부터 n번째 위치하는 정수를 반환한다.
extension Int {
    subscript(digitIndex: Int) -> Int {
        var decimalBase = 1
        for _ in 0..<digitIndex {
            decimalBase *= 10
        }
        return (self / decimalBase) % 10
    }
}
746381295[0] // 5
746381295[1] // 9
746381295[2] // 2
746381295[8] // 7

746381295[9] // 0, as if you had requested: 0746381295[9]
```

<br><br><br>

# 중첩 타입
- Extension 을 이용해 Class, Strucr, Enum 에 중첩 타입을 추가할 수 있다.
- 아래 코드는 Int 에 중첩형 Enum 을 추가하는 예시이다.
```swift
// Kind 라는 Enum 은, Int 를 음수, 0, 양수로 표현한다.
extension Int {
    enum Kind {
        case negative, zero, positive
    }
    var kind: Kind {
        switch self {
        case 0:
            return .zero
        case let x where x > 0:
            return .positive
        default:
            return .negative
        }
    }
}

// Kind 프로퍼티를 이용해 특정 수가 음수, 0 양수 인지 나타낸다.
func printIntegerKinds(_ numbers: [Int]) {
    for number in numbers {
        switch number.kind {
        case .negative:
            print("- ", terminator: "")
        case .zero:
            print("0 ", terminator: "")
        case .positive:
            print("+ ", terminator: "")
        }
    }
    print("")
}
printIntegerKinds([3, 19, -27, 0, -6, 0, 7]) // "+ + - 0 - 0 + "
```


<br><br><br>

참조
- [Swift Document](https://docs.swift.org/swift-book/LanguageGuide/Extensions.html)
