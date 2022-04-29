# 🏠   [Go Main](https://github.com/Raccoon97/Swift/blob/main/README.md)   🏠

<br><br><br>
# ARC( Automatic Reference Counting )
- Swift 는 ARC 를 사용하여 앱의 메모리 사용량을 추적하고 관리한다.
- 대부분의 경우 자동으로 메모리 관리가 이루어지며, ARC 는 해당 인스턴스가 더 이상 필요하지 않을 때 메모리를 자동으로 해제한다.
>- Reference Counting 은 class 인스턴스에만 적용되며, struct 및 enum 은 Reference Type 이 아닌 Value Type 이므로 Reference 에 의해 저장 및 전달되지 않는다.
- 아래 이미지는 기존 MRC( Manual Reference Counting ) 을 사용하여 retain/ release 코드를 넣어줬을 때와 ARC 를 사용했을 때 코드 생산성의 차이를 보여준다.
<p align="center">
  <img src="https://developer.apple.com/library/archive/releasenotes/ObjectiveC/RN-TransitioningToARC/Art/ARC_Illustration.jpg" alt="center" />
</p>

<br><br><br>
# ARC 작동 방식
- 인스턴스를 생성할 때 마다 ARC 는 해당 인스턴스에 대한 정보를 저장하기 위해 Heap 영역에 메모리를 할당한다.
>- 할당된 메모리는 해당 인스턴스와 관련된 속성 값과 인스턴스에 대한 정보를 보유한다.
- 인스턴스가 더 이상 필요하지 않은 경우 ARC 는 해당 인스턴스에서 사용하는 메모리를 해제한다.
- 사용중인 인스턴스의 할당을 해제하는 경우, 더 이상 해당 인스턴스의 Property 에 엑세스 하거나 Method 를 호출할 수 없다.
- 사용중인 인스턴스가 유지되기 위해 ARC 는 현재 각 클래스 인스턴스를 참조하는 속성, 상수 및 변수의 수를 추적한다.
>- 해당 인스턴스에 대한 활성 참조가 하나 이상 존재하는 한 인스턴스를 할당 해제하지 않는다.
>- 속성, 상수 또는 변수에 인스턴스를 할당할 때마다 Strong Reference 를 만드는데, 참조가 남아 있는 한 할당 해제를 허용하지 않아 "강력한 참조" 라고 한다.

<br><br><br>
# ARC 작동 방식의 예
- 아래 예제는 Person 클래스를 메모리에 할당하고 name 프로퍼티를 사용하며, 할당된 인스턴스를 메모리에서 해제하는 방법을 보여준다.
```swift
class Person {
    let name: String
    init(name: String) {
        self.name = name
        print("\(name) is being initialized")
    }
    deinit {
        print("\(name) is being deinitialized")
    }
}
```
- Person 클래스에는 인스턴스의 생성자와, 인스턴스의 소멸자가 있다.
- 생성자와 소멸자에는 메모리 할당과 메모리 할당 해제를 가시적으로 확인할 수 있는 메시지가 출력된다.
```swift
var reference1: Person?
var reference2: Person?
var reference3: Person?
```
- Person 클래스를 참조하는 변수를 정의한다. Optional Type 이므로 내부 프로퍼티는 nil 값으로 자동 초기화 된다.
- 미리 정의해둔 변수에 Person 인스턴스를 할당한다.
```swift
reference1 = Person(name: "Raccoon97")
// Prints "Raccoon97 is being initialized"
```
- 이니셜라이저가 호출되면서 메시지를 출력했다. 초기화를 확인할 수 있다.
- Person 인스턴스가 reference1 변수에 할당되었기 때문에 reference1 변수에서 Person 인스턴스에 대한 Strong Reference 가 발생한다.
- 하나 이상의 Strong Reference 가 있기 때문에 ARC 는 해당 Person 인스턴스를 메모리에 할당하고, 해제되지 않도록 한다.
- 동일한 Person 인스턴스를 나머지 두 개의 변수에 할당하면 해당 인스턴스에 대한 두 개의 Strong Reference 가 발생한다.
```swift
reference2 = reference1
reference3 = reference1
```
- 이제 Person 이라는 단일 인스턴스에 대해 3개의 Strong Reference 가 발생했다.
```swift
reference1 = nil
reference2 = nil
```
- 두 개의 변수에 nil 을 할당하여 원래의 참조를 포함한 Strong Reference 2개를 끊게 되면 하나의 Strong Reference 가 남아있기에 Person 인스턴스가 할당 해제되지 않는다.
```swift
reference3 = nil
// Prints "John Appleseed is being deinitialized"
```
- 마지막 세 번째 변수에 nil 을 할당하여 마지막 Strong Reference 를 끊게 되면 이제 Person 인스턴스와 연결된 Strong Reference 는 하나도 없으므로 디이니셜라이저가 호출되면서 메시지가 출력된다.

<br><br><br>
# 클래스 인스턴스 간의 Strong Reference Cycle
- 두 개 이상의 클래스 인스턴스를 사용해 서로에 대한 Strong Reference 를 발생시켜 각 인스턴스가 다른 인스턴스를 계속 유지시키는 경우를 Strong Reference Cycle 이라고 하며, 인스턴스의 Strong Reference 가 없어지지 않도록 코드를 작성할 수 있다.
- 클래스 간의 관계 중 일부를 Strong Reference 가 아닌 Weak Reference, Unowned Reference 로 정의하여 Strong Reference Cycle 를 해결할 수 있다.
>- [Resolving Strong Reference Cycles Between Class Instances](https://docs.swift.org/swift-book/LanguageGuide/AutomaticReferenceCounting.html#ID52)
- 아래 예제는 어떻게 Strong Reference Cycle 이 발생하는지 보여준다.
```swift
class Person {
    let name: String
    init(name: String) { self.name = name }
    var apartment: Apartment?
    deinit { print("\(name) is being deinitialized") }
}

class Apartment {
    let unit: String
    init(unit: String) { self.unit = unit }
    var tennant: Person?
    deinit { print("Apartment \(unit) is being deinitialized") }
}
```
- Person 인스턴스에는 필수적으로 name, 선택적으로 apartment 프로퍼티를.   Apartment 인스턴스에는 필수적으로 unit, 선택적으로 tennant 프로퍼티를 가진다.
- 두 인스턴스 모두 메모리 할당 해제를 가시적으로 확인할 수 있는 메시지가 출력된다.
```swift
var john: Person?
var unit4A: Apartment?
```
- Person, Apartment 클래스를 참조하는 변수를 정의한다. Optional Type 이므로 내부 프로퍼티는 nil 값으로 자동 초기화 된다.
- 미리 정의해둔 변수에 Person, Apartment 인스턴스를 할당한다.
```swift
john = Person(name: "John Appleseed")
unit4A = Apartment(unit: "4A")
```
- 아래 이미지는 두 인스턴스를 만들고 할당한 후 각 변수에 어떠한 Strong Reference 가 있는지 보여준다.

<br>

![image](https://docs.swift.org/swift-book/_images/referenceCycle01_2x.png)
- 이제 두 인스턴스를 서로 연결할 수 있다.
```swift
john!.apartment = unit4A
unit4A!.tennant = john
```
- 아래 이미지는 두 인스턴스를 연결한 후 Strong Reference 의 변화를 보여준다.

<br>

![image](https://docs.swift.org/swift-book/_images/referenceCycle02_2x.png)
- 이렇게 되면 두 인스턴스 사이에 Strong Reference Cycle 이 발생한다. 
>- Person 인스턴스에 Apartment 인스턴스에 대한 Strong Reference 가,  Apartment 인스턴스에 Person 인스턴스에 대한 Strong Reference 가 발생하게 된다.

```swift
john = nil
unit4A = nil
```
- 두 변수를 nil 로 할당했을 때 디이니셜라이저가 호출되지 않는다. ( 메시지가 출력되지 않음 )
- Strong Reference Cycle 은 두 인스턴스가 메모리에서 할당 해제 되는 것을 방지하여 앱에서 메모리 누수를 일으킨다.
- 아래 이미지는 두 변수를 nil 로 할당했을 때 Strong Reference 가 어떻게 남아있는지 보여준다.

<br>

![image](https://docs.swift.org/swift-book/_images/referenceCycle03_2x.png)
- Person 인스턴스와 Apartment 인스턴스 간의 Strong Reference 는 유지되며 끊을 수 없다.

<br><br><br>
# 클래스 인스턴스 간의 Strong Reference Cycle 해결
- Swift 는 Strong Reference Cycle 을 해결하는 두 가지 방법을 제공한다
>- Weak Reference: 한 쪽 인스턴스의 생명 주기가 더 짧은 경우 사용한다.( 먼저 할당 해제될 가능성이 높은 인스턴스 )
>- Unowned Reference: 한 쪽 인스턴스의 생명 주기가 같거나 긴 경우 사용한다.( 더 나중에 할당 해제되거나 같이 할당 해제될 가능성이 높은 인스턴스 )
- 두 가지 방법을 사용하면 한 인스턴스가 다른 인스턴스를 Strong Reference 하지 않고도 다른 인스턴스를 참조할 수 있다.
- 즉, Strong Reference Cycle 이 발생되지 않고도 인스턴스가 서로를 참조할 수 있다.

<br><br>

## Weak Reference
- ARC 가 참조된 인스턴스를 할당 해제하는 것을 막지 않는다.
- Strong Reference Cycle 이 되는 것을 방지한다.
- 프로퍼티, 변수 선언 시 앞에 weak 키워드를 배치한다.
```swift
// 예시
weak var tennant: Person?
```
- 인스턴스를 Strong Reference 하지 않기 때문에 해당 인스턴스를 참조하는 동안 할당 해제될 수 있다.
- ARC 는 참조하는 인스턴스가 할당 해제될 때 Weak Reference 를 nil 로 할당한다.
- Weak Reference 는 런타임에 값을 nil 로 변경할 수 있도록 해야 하므로 항상 상수가 아닌 Optional Type 의 var 형식으로 선언된다.
- ARC 가 Weak Reference 에 nil 을 할당할 때 Property Observer 는 호출되지 않는다. 
>- Property Observer 는 무엇인가.. [Zedd님 블로그](https://zeddios.tistory.com/247]
- 아래의 예시는 위의 예시와 같지만, Apartment 클래스의 tennant 프로퍼티가 Weak Reference 로 선언된다.
```swift
class Person {
    let name: String
    init(name: String) { self.name = name }
    var apartment: Apartment?
    deinit { print("\(name) is being deinitialized") }
}

class Apartment {
    let unit: String
    init(unit: String) { self.unit = unit }
    weak var tennant: Person?
    deinit { print("Apartment \(unit) is being deinitialized") }
}
```
- 두 변수와, 인스턴스 할당, 두 인스턴스 간의 연결은 위의 예시와 동일하다.
```swift
var john: Person?
var unit4A: Apartment?

john = Person(name: "John Appleseed")
unit4A = Apartment(unit: "4A")

john!.apartment = unit4A
unit4A!.tennant = john
```
- 아래 이미지는 두 인스턴스를 연결한 Reference 의 상태를 보여준다.

<br>

![image](https://docs.swift.org/swift-book/_images/weakReference01_2x.png)
- Person 인스턴스에는 여전히 Apartment 인스턴스에 대한 Strong Reference 가 있다.
- Apartment 인스턴스에는 Person 인스턴스에 대한 Weak Reference 가 있다.
- 즉, Person 인스턴스를 갖고 있는 john 변수를 nil 로 할당하면 더 이상 Strong Reference 가 존재하지 않게 된다.
```swift
john = nil
// Prints "John Appleseed is being deinitialized"
```
- Person 인스턴스의 디이니셜라이저가 호출되며 메시지가 출력되었고, 더 이상 Strong Reference 가 없으므로 Apartment 인스턴스의 tennant 속성이 nil 로 바뀌게 된다.
- 아래 이미지는 Person 인스턴스를 갖는 john 변수를 nil 로 할당한 뒤 Reference 의 변화를 보여준다.

<br>

![image](https://docs.swift.org/swift-book/_images/weakReference02_2x.png)
- 이제 남아있는 유일한 Strong Reference 는 Apartment 인스턴스를 갖고 있는 unit4A 변수이다.
```swift
unit4A = nil
// Prints "Apartment 4A is being deinitialized"
```
- Apartment 인스턴스의 디이니셜라이저가 호출되며 메시지가 출력되었고, 모든 Strong Reference 가 사라지게 되었다.
- 아래 이미지는 Apartment 인스턴스를 갖는 unit4A 변수를 nil 로 할당한 뒤 Reference 의 변화를 보여준다.

<br>

![image](https://docs.swift.org/swift-book/_images/weakReference03_2x.png)
- 다른 시스템에서의 Weak Reference
>- Garbage Collector 를 사용하는 시스템 에서는 weak 포인터가 간단한 캐싱 메커니즘을 수행하기 위해 사용된다. < Ex) Java, Python >
>- Garbage Collector 가 동작하면서 weak 포인터는 Strong Reference 가 없는 객체의 할당 해제를 수행하기 위해 사용된다.
- ARC를 사용하면 Strong Reference 가 제거되는 즉시 인스턴스에서 참조하는 Weak Reference 값이 할당 해제된다.
- Strong Reference Cycle 방지 목적이 아닌 Strong Reference 가 0인 값의 할당 해제를 위해 Weak Reference 를 쓰는 것은 적합하지 않다.

<br><br>

## Unowned Reference
- Weak Reference 와 마찬가지로 인스턴스를 Strong Reference 하지 않는다.
- 다른 인스턴스의 생명 주기가 같거나 더 긴 경우에 Unowned Reference 를 사용한다.
- 프로퍼티, 변수 선언 시 앞에 unowned 키워드를 배치한다.
```swift
// 예시
unowned var tennant: Person?
```
- Weak Reference 는 값이 nil 이어도 괜찮지만 Unowned Reference 는 항상 값이 있어야 한다.
- ARC 는 Unowned Reference 의 값을 nil 로 설정하지 않는다.
>- 항상 할당 해제되지 않는다고 확신하는 인스턴스에만 Unowned Reference 를 사용한다.
>- 인스턴스가 할당 해제된 후 Unowned Reference 값에 엑세스 하게 되면 런타임 오류가 발생한다.
- 아래 예시는 안전하게 Unowned Reference 를 사용하는 방법을 보여준다.
- Customer, CreditCard 라는 두 개의 클래스를 정의하는데 CreditCard 클래스는 항상 Customer 와 연결되며 CreditCard 인스턴스는 Unowned Reference 를 통해 언제든지 할당 해제될 수 있다.
- CreditCard 인스턴스는 숫자 값과 Customer 인스턴스를 이니셜라이저에 전달 해야만 생성이 가능하다.
```swift
class Customer {
    let name: String
    var card: CreditCard?
    init(name: String) {
        self.name = name
    }
    deinit { print("\(name) is being deinitialized") }
}

class CreditCard {
    let number: UInt64
    unowned let customer: Customer
    init(number: UInt64, customer: Customer) {
        self.number = number
        self.customer = customer
    }
    deinit { print("Card #\(number) is being deinitialized") }
}
```
>- CreditCard 클래스의 numer 프로퍼티는 32비트 및 64비트 시스템에서 16자리의 카드 번호를 저장할 수 있을 만큼 Int 가 아닌 UInt64 로 정의한다.
- Customer 클래스를 사용하기 위해 변수를 선언한다.
```swift
var john
```
- Customer 인스턴스를 만들고 card 프로퍼티에 CreditCard 인스턴스를 할당한다.
```swift
john = Customer(name: "John Appleseed")
john!.card = CreditCard(number: 1234_5678_9012_3456, customer: john!)
```
- 아래 이미지는 두 인스턴스를 연결했을 때 Reference 상황을 보여준다.
<br>

![image](https://docs.swift.org/swift-book/_images/unownedReference01_2x.png)
- Customer 인스턴스에 CreditCard 인스턴스에 대한 Strong Reference 가 있다.
- CreditCard 인스턴스에 Customer 인스턴스에 대한 Unowned Reference 가 있다.
- Unowned Reference 때문에 john 변수에 nil 을 할당하면 더이상 Strong Reference 가 없게 된다.

```swift
john = nil
// Prints "John Appleseed is being deinitialized"
// Prints "Card #1234567890123456 is being deinitialized"
```
- Customer 인스턴스에 더이상 Strong Reference 가 없기 때문에 할당이 해제된다.
- CreditCard 인스턴스를 이어주던 Customer 의 Strong Reference 가 없기 때문에 CreditCard 인스턴스도 할당이 해제된다.
>- Swift 는 성능상의 이유로 런타임 안전검사를 비활성화 하는 경우 Unsafe Unowned Reference 를 제공한다.
>- 사용자는 해당 Unsafe Unowned Reference 를 점검할 책임을 갖는다.
>- Unsafe Unowned Reference 를 사용하여 코드를 짰을 때, 만약 Unowned Reference 를 사용한 인스턴스가 할당이 해제된 후 엑세스하려고 하면 프로그램은 그 인스턴스가 있던 메모리 위치에 엑세스 하려고 하는데 이는 안전하지 않은 작업이다. 

<br><br>

## Unowned Optional Reference
- 클래스에 대한 Optional Reference 를 unowned 로 표시할 수 있다.
- ARC의 관점에서 Unowned Reference 와 Weak Reference 는 동일한 맥락에서 사용이 가능하다.
- 동일한 맥락에서 사용이 가능하지만 Unowned Reference 를 사용할 때는 항상 유효한 개체를 Reference 하거나 nil 인지 확인해야 한다.
- 아래 예시는 Unowned Optional Reference 의 예시이다.
```swift
class Department {
    var name: String
    var courses: [Course]
    init(name: String) {
        self.name = name
        self.courses = []
    }
}

class Course {
    var name: String
    unowned var department: Department
    unowned var nextCourse: Course?
    init(name: String, in department: Department) {
        self.name = name
        self.department = department
        self.nextCourse = nil
    }
}
```
- Department 클래스와 Course 클래스가 있으며 Course 클래스 내부에는 Unowned Reference 가 2가지 있다.
```swift
let department = Department(name: "Horticulture")

let intro = Course(name: "Survey of Plants", in: department)
let intermediate = Course(name: "Growing Common Herbs", in: department)
let advanced = Course(name: "Caring for Tropical Plants", in: department)

intro.nextCourse = intermediate
intermediate.nextCourse = advanced
department.courses = [intro, intermediate, advanced]
```
- 위의 코드는 Department 인스턴스 하나와 3개의 Course 인스턴스를 생성하게 된다.
- 각 Course 인스턴스 끼리는 Unowned Optional Reference 로, Department 인스턴스와 Course 인스턴스 끼리는 Unowned Reference 로 연결되어있다.
- 아래의 이미지는 Reference 를 시각적으로 나타낸다.
<br>

![image](https://docs.swift.org/swift-book/_images/unownedOptionalReference_2x.png)

- Unowned Optional Reference 는 Strong Reference 가 없으면 ARC가 할당을 해제하게 된다.
- ARC 에서 Unowned Reference 와 동일하게 동작한다.
>- 할당 해제되지 않은 다른 인스턴스를 항상 Reference 하도록 해야 한다. 
- Unowned Optional Reference 는 nil 이 할당될 수 있다.

<br><br>

## Unowned Reference 와 암시적으로 래핑 해제 된 Optional Properties
- 앞서 살펴본 Weak Reference 와 Unowned Reference 의 예시는 Strong Reference 가 사라져야 하는 시나리오이다.
- 시나리오 1 : Person, Apartment 예제
>- 둘 다 nil 일 수 있는 인스턴스가 서로 Strong Reference Cycle 를 유발할 가능성이 있는 상황
>>- Weak Reference 로 해결이 가능하다.
- 시나리오 2 : Customer, CreditCard 예제
>- nil 이 될 수 있는 인스턴스와 nil 이 될 수 없는 인스턴스 사이에 Strong Reference Cycle 이 발생될 가능성이 있는 상황
>>- Unowned Referece 로 해결이 가능하다.
- 시나리오 3 : 
>- 각 인스턴스의 프로퍼티는 항상 값을 가져야 하며, 초기화가 완료되면 각 인스턴스의 프로퍼티는 nil 이면 안된다.
>>- 한 클래스의 Unowned 프로퍼티를 다른 클래스의 암시적으로 래핑되지 않은 Optional 프로퍼티와 결합으로 해결이 가능하다. 두 프로퍼티 모두 Optional Wrapping 없이 직접 엑세스 할 수 있으며 Reference Cycle 이 발생하는 것일 피할 수 있다.

