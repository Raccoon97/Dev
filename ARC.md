# 🏠   [Go Main](https://github.com/Raccoon97/Swift/blob/main/README.md)   🏠
<br><br><br>
# ARC( Automatic Reference Counting )
- Swift 는 ARC 를 사용하여 앱의 메모리 사용량을 추적하고 관리한다.
- 대부분의 경우 자동으로 메모리 관리가 이루어지며, ARC 는 해당 인스턴스가 더 이상 필요하지 않을 때 메모리를 자동으로 해제한다.
>- Reference Counting 은 class 인스턴스에만 적용되며, struct 및 enum 은 Reference Type 이 아닌 Value Type 이므로 Reference 에 의해 저장 및 전달되지 않는다.

<br><br><br>

# ARC 작동 방식
- 인스턴스를 생성할 때 마다 ARC 는 해당 인스턴스에 대한 정보를 저장하기 위해 Heap 영역에 메모리를 할당한다.
>- 할당된 메모리는 해당 인스턴스와 관련된 속성 값과 인스턴스에 대한 정보를 보유한다.
- 인스턴스가 더 이상 필요하지 않은 경우 ARC 는 해당 인스턴스에서 사용하는 메모리를 해제한다.
- 사용중인 인스턴스의 할당을 해제하는 경우, 더 이상 해당 인스턴스의 Property 에 엑세스 하거나 Method 를 호출할 수 없다.
- 사용중인 인스턴스가 유지되기 위해 ARC 는 현재 각 클래스 인스턴스를 참조하는 속성, 상수 및 변수의 수를 추적한다.
>- 해당 인스턴스에 대한 활성 참조가 하나 이상 존재하는 한 인스턴스를 할당 해제하지 않는다.
>- 속성, 상수 또는 변수에 인스턴스를 할당할 때마다 강력한 참조를 만드는데, 참조가 남아 있는 한 할당 해제를 허용하지 않아 "강력한 참조" 라고 한다.

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
```swift
var reference1: Person?
var reference2: Person?
var reference3: Person?
```
- 다음 코드는 Person 클래스를 참조하는 변수를 정의한다. Optional Type 이므로 클래스 내부 프로퍼티는 nil 값으로 자동 초기화 된다.
- 미리 정의해둔 변수에 Person 인스턴스를 할당한다.
```swift
reference1 = Person(name: "Raccoon97")
// Prints "Raccoon97 is being initialized"
```
- 이니셜라이저가 호출되면서 메시지를 출력했다. 초기화를 확인할 수 있다.
- Person 인스턴스가 reference1 변수에 할당되었기 때문에 reference1 변수에서 Person 인스턴스에 대한 강력한 참조가 발생한다.
- 하나 이상의 강력한 참조가 있기 때문에 ARC 는 해당 Person 인스턴스를 메모리에 할당하고, 해제되지 않도록 한다.
- 동일한 Person 인스턴스를 나머지 두 개의 변수에 할당하면 해당 인스턴스에 대한 두 개의 강력한 참조가 발생한다.
```swift
reference2 = reference1
reference3 = reference1
```
- 이제 Person 이라는 단일 인스턴스에 대해 3개의 강력한 참조가 발생했다.
```swift
reference1 = nil
reference2 = nil
```
- 두 개의 변수에 nil 을 할당하여 원래의 참조를 포함한 강력한 참조 2개를 끊게 되면 하나의 강력한 참조가 남아있기에 Person 인스턴스가 할당 해제되지 않는다.
```swift
reference3 = nil
// Prints "John Appleseed is being deinitialized"
```
- 마지막 세 번째 변수에 nil 을 할당하여 마지막 강력한 참조를 끊게 되면 이제 Person 인스턴스와 연결된 강력한 참조는 하나도 없으므로 디이니셜라이저가 호출되면서 메시지가 출력된다.
