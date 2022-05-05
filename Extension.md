

# Extension
- Extension 은 기존 Class, Struct, Enum, Protocol 에 새로운 기능을 추가한다.
- 원본 소스에 접근하지 못하는 타입들도 새로운 기능을 만들 수 있다.
>- 원본 소스는 그대로 두고 원하는 기능만 추가하는 것
- Extension 은 Obj-C 의 Category 와 유사하다.

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
- Extension 은 새로운 이니셜라이저를 추가할 수 있다.
- 기존에 지정되어있던 이니셜라이저, 디이니셜라이저를 추가할 수는 없다.
- Extension 을 사용하여 다른 모듈에서 선언된 구조에 이니셜라이저를 추가하는 경우, 추가된 이니셜라이저는 정의된 모듈에서 기존 이니셜라이저가 호출되기 전까지 엑세스할 수 없다.
- ⭐️⭐️⭐️⭐️⭐️ 도와주세요 이 부분은 잘 이해가 가지 않아요. ⭐️⭐️⭐️⭐️⭐️
>- 다른 타입이 사용자 타입의 이니셜라이저 인자로 받거나 타입의 기본 구현의 부분에 포함되지 않는 추가적인 초기화 옵션을 제공하도록 확장이 가능하다.
>- 모든 저장 속성에 기본 값을 주고 사용자 이니셜라이저를 정의하지 않는 값 타입에 이니셜라이저를 추가하기 위해 확장을 사용한다면, 확장 이니셜라이저 안으로부터 값 타입을 위한 기본 이니셜라이저와 멤버 이니셜라이저를 호출한다.
- ⭐️⭐️⭐️⭐️⭐️ 도와주세요 이 부분은 잘 이해가 가지 않아요. ⭐️⭐️⭐️⭐️⭐️
