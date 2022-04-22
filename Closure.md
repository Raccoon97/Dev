🏠   [Go Main](https://github.com/Raccoon97/Swift/blob/main/README.md)   🏠

- [Closure](https://github.com/Raccoon97/Swift/edit/main/Closure.md#closure)
- [Closure의 표현식](https://github.com/Raccoon97/Swift/edit/main/Closure.md#closure%EC%9D%98-%ED%91%9C%ED%98%84%EC%8B%9D)
- [1급 객체로서의 Closure](https://github.com/Raccoon97/Swift/edit/main/Closure.md#1%EA%B8%89-%EA%B0%9D%EC%B2%B4%EB%A1%9C%EC%84%9C%EC%9D%98-closure)
- [Closure 실행하기](https://github.com/Raccoon97/Swift/edit/main/Closure.md#closure-%EC%8B%A4%ED%96%89%ED%95%98%EA%B8%B0)
- [Closure 의 경량화](https://github.com/Raccoon97/Swift/blob/main/Closure.md#closure-%EC%9D%98-%EA%B2%BD%EB%9F%89%ED%99%94)
- [Closure의 경량 문법](https://github.com/Raccoon97/Swift/blob/main/Closure.md#closure%EC%9D%98-%EA%B2%BD%EB%9F%89-%EB%AC%B8%EB%B2%95)
- [@autoclosure](https://github.com/Raccoon97/Swift/blob/main/Closure.md#autoclosure)
- [@escaping](https://github.com/Raccoon97/Swift/blob/main/Closure.md#escaping)
- [Closure 의 Capture](https://github.com/Raccoon97/Swift/blob/main/Closure.md#closure-%EC%9D%98-capture)
- [Closure 의 Capture List](https://github.com/Raccoon97/Swift/blob/main/Closure.md#closure-%EC%9D%98-capture-list)
- [Closure 와 ARC( Automatic Reference Counting )](https://github.com/Raccoon97/Swift/blob/main/Closure.md#closure-%EC%99%80-arc-automatic-reference-counting-)
- [Named Closure](https://github.com/Raccoon97/Swift/blob/main/Closure.md#named-closure)

# Closure
- Named Closure
        - 평소에 일반적으로 사용하는 함수는 Named Closure 이다.
```swift
func doSomething() {
   print("Somaker")
}
```
- Unnamed Closure
        - 이름을 붙이지 않고 사용하는 함수를 Unnamed Closure 라고 한다.  
```swift
let closure = { print("Somaker") }
```
- 보통 Closure 하면 Unamed Closure 를 의미하지만 사실 Named Closure 와 Unamed Closure 둘 다 Closure 이다.
- Closure 는 함수라서 " 1급 객체 함수 " 의 특성을 다 갖고 있다.
- Closure 는 대입, 반환이 가능하기에 자료형을 갖고 있다.
<br><br><br>
# Closure의 표현식

```swift
 {
     (Parameter) -> Return Type in         // Closure Head
     실행 구문                               // Closure Body
 }
```
- 주로 Closure 를 언급할 땐 익명함수( Unamed Closure ) 이므로 func 키워드는 사용하지 않는다.
- Closure는 Closure Head 와 Closure Body로 이루어져 있는데, 그 둘을 구분짓는 것이 in 키워드 이다.
- Parameter 와 Return Type 이 없는 Closure
```swift
let closure = { () -> () in
   print("Closure")
}
```
>- Closure 는 익명함수이긴 하지만 함수이다, 따라서 Swift 에서 1급 객체 함수이기 때문에, 상수에 대입이 가능하다.
- Parameter 와 Return Type 이 있는 Closure
```swift
let closure = { (name: String) -> String in
    return "Hello, \(name)"
}
```
>- 여기서 Parameter Name 은 Argument Name 이 아니다. Closure 는 Argument Name 을 사용하지 않는다.
- Ex
```swift
let closure = { (name: String) -> String in
    return "Hello, \(name)"
}

closure("Raccoon")
closure(name: "Raccoon")  //error!
```
<br><br><br>
# 1급 객체로서의 Closure
- Closure 를 변수나 상수에 대입할 수 있다.
```swift
let closure = { () -> () in
    print("Closure")
}
```
>- 대입과 동시에 Closure 를 작성할 수 있다.
```swift
let closure2 = closure
```
>- 기존에 Closure 를 대입한 변수나 상수를 새로운 변수나 상수에 대입할 수 있다.
- 함수의 파라미터 타입으로 Closure 를 전달할 수 있다.
```swift
func doSomething(closure: () -> ()) {
    closure()
}

doSomething(closure: { () -> () in
    print("Hello!")
})
```
>- 이처럼 함수를 파라미터로 전달받는 함수가 있다, 하지만 파라미터를 Closure 로 넘겨줘도 된다.
- 함수의 반환 타입으로 Closure 를 전달할 수 있다.
```swift
func doSomething() -> () -> () {
    return { () -> () in
        print("Hello!")
    }
}
```
>- 실제 Return을 할 때 함수가 아닌 Closure 를 Return할 수 있다.
```swfit
let closure = doSomething()
closure()
```
>- 또한 상수에 함수의 Return 값( Closure )을 대입해서 위와 같이 실행할 수 있다.

<br><br><br>
# Closure 실행하기
- Closure 가 대입된 변수나 상수로 호출하기
```swift
let closure = { () -> String in
    return "Hello!"
}

closure()
```
>- 이처럼 클로저가 대입된 closure 상수를 호출 구문인 () 를 이용해서 실행할 수 있다.
- Closure 를 직접 호출하기
```swift
({ () -> () in
    print("Hello!")
})()
```
>- 일회성, 클로저를 소괄호로 감싸고 끝에 호출 구문인 () 를 이용해서 실행할 수 있다.

<br><br><br>
# Closure 의 경량화
- Trailling Closure
>- 함수의 마지막 Parameter가 Closure 일 때, 이를 Parameter 형식이 아닌 함수 뒤에 붙여 사용하는 문법, 이 때, Argument Label 은 생략된다.
>>- Trailling Closure 를 사용하기 위한 조건 --> 마지막 Parameter 가 Closure 일 경우
- Parameter 가 Closure 하나인 함수
```swift
func doSomething(closure: () -> ()) {
    closure()
}
// 위 함수는 아래와 같이 호출된다.

doSomething(closure: { () -> () in
    print("Hello!")
})
```
>- 이렇게 Closure 가 Parameter 형식으로 함수의 호출 구문 안에 있는 것을 Inline Closure 라고 부른다.
>- 함수 해석이 쉽지만은 않은 모양의 함수이므로 이 때 함수의 가장 마지막에 꼬리처럼 붙여 사용할 수 있는 Trailling Closure 를 사용한다.
```swift
// Trailling Closure
doSomething () { () -> () in
    print("Hello!")
}
```
>- Parameter 가 Closure 하나인 경우에는 더 경량화 시킬 수 있다.( 함수 호출 구문인 () 를 생략 가능 )
```swift
doSomething () { () -> () in
    print("Hello!")
}
// 기존 Trailling Closure 를 사용했을 때 모습

doSomething { () -> () in
    print("Hello!")
}
// Parameter 가 Closure 하나인 경우 더 경량화 된 모습
```
- Parameter 가 여러 개인 함수
```swift
func fetchData(success: () -> (), fail: () -> ()) {
    //do something...
}
// 이런 함수가 있을 때 

fetchData(success: { () -> () in
    print("Success!")
}, fail: { () -> () in
    print("Fail!")
})
// Inline Closure 의 경우


fetchData(success:  { () -> () in
    print("Success!")
}) { () -> () in
    print("Fail!")
}
// Trailling Closure 를 적용한 모습, 마지막 Parameter 가 Closure 이기에 Trailling Closure 를 사용하여 표현함
// 마지막 Parameter 만 Argument Label 을 생략할 수 있다.
```

<br><br><br>

# Closure의 경량 문법
- 문법을 최적화하여 Closure 를 간단하게 쓸 수 있는 것
```swift
func doSomething(closure: (Int, Int, Int) -> Int) {
    closure(1, 2, 3)
}
```
>- 경량화 할 함수 예시

```swift
doSomething(closure: { (a: Int, b: Int, c: Int) -> Int in
    return a + b + c
})
```
>- Inline Closure 작성
- Parameter 형식과 Return 형식을 생략할 수 있다.
```swift
doSomething(closure: { (a, b, c ) in
    return a + b + c
})
```
>- Parameter 생략, Return 생략
- Parameter Name 은 Shortand Argument Names 로 대체하고 이 경우 Parameter Name 과 in 키워드를 생략한다.
>- Shortand Argument Names 란 a, b, c 라는 Parameter Name 대신에 $0, $1, $2 와 같이 $ 과 index 를 이용해서 Parameter 에 순서대로 접근하는 것
```swift
doSomething(closure: {  
    return $0 + $1 + $2
})
```
>- Shortand Argument Names 로 Parameter 를 대체하여 경량화된 Closure 
- 단일 Return 문만 남을 경우 Return 도 생략할 수 있다, 단일 Return 문이 아닌 경우엔 Error가 발생한다.
>- 단일 Return 문이란, Closure 내부에 return 구문 하나만 남은 상태 
```swift
doSomething(closure: {  
    $0 + $1 + $2
})
```
- Closure Parameter 가 마지막 Parameter 라면 Trailling Closure 로 작성한다.
```swift
doSomething() {  
     $0 + $1 + $2
}
```
>- Trailling Closure 로 작성하여 Closure 를 함수의 끝 부분으로 뺀 모습
- 함수 호출부에 별다른 Argument 가 없다면 ()를 생략할 수 있다.
```swift
doSomething { $0 + $1 + $2 }
```
>- Closure를 최종적으로 경량화 시킨 모습

<br><br><br>
# @autoclosure
- 파라미터로 전달된 일반 구문 또는 함수를 클로저로 래핑( Wrapping ) 하는 것
```swift
func doSomething(closure: @autoclosure () -> ()) {
}
```
>- 이렇게 autoclosure 를 사용하게 되면 실제로 Closure 를 전달받지는 않지만, Closure 처럼 사용이 가능하다.
>- 실제 Closure 와 다른 점은 실제로 전달하는 것이 아니기 때문에 파라미터로 값을 넘기는 것 처럼 ()를 통해 넘겨줄 수 있다.
```swift
func doSomething(closure: @autoclosure () -> ()) {
closure()
}

doSomething(closure: 1 > 2)
```
>- 1 > 2는 Closure 가 아닌 일반 구문이지만 실제 함수 내에서는 일반 구문을 Closure 처럼 사용할 수 있다.
>- 하지만 autoclosure 를 사용할 경우, 파라미터가 반드시 없어야 한다. 리턴 타입은 상관 없다.
- @autoclosure 특징 : 지연된 실행( Delayed Evaluation )
>- 원래 일반 구문이라면 작성되자마자 실행되어야 하지만 autoclosure 로 작성한 구문은 함수가 실행될 시점에 구문을 Closure 로 만들어 줌으로 함수 내에서 클로저를 실행할 때 까지 구문이 실행되지 않는다.
```swift
var names = ["Kim", "Park", "Lee"]

func doSomething(@autoclosure closure: () -> String) {
  closure()
}

names
// ["Kim", "Park", "Lee"]

doSomething(names.removeFirst())

names
// ["Park", "Lee"]
```
>- 지연된 실행은 autoclosure 가 아닌 일반 Closure 를 사용했을 때도 적용된다.
```swift
var names = ["Kim", "Park", "Lee"]

let closure = {
  names.removeFirst()
}

names
// ["Kim", "Park", "Lee"]

closure()

names
// ["Park", "Lee"]
```
>- 위와 같이 Closure 를 호출하기 전까지는 선언 단계에서 작성된 구문이 실행되지 않는다.
>- 일반 구문을 autoclosure 로 래핑한 구문에서 지연된 실행이 발생하는 이유이다.
>- autoclosure 속성은 기본적으로 @noescape 속성을 부여한다. 그 속성을 없애기 위해서는 (escaping) 을 이용한다.
```swift
func doSomething(@autoclosure(escaping) closure: () -> String) {
  closure()
}
```
<br><br><br>
# @escaping
- 지금까지의 Closure 는 모두 non-escaping Closure 이다, @escaping 키워드가 없는 Closure 는 모두 non-escaping Closure 이다.
- non-escaping Closure 는 함수 내부에서만 쓰이기 때문에 메모리 관리가 용이해 성능이 향상되며 함수가 종료됨과 동시에 Closure 도 사용이 끝난다.
- escaping 의 경우, 함수가 종료되더라도 실제 Closure 가 사용되지 않을 때 까지 메모리를 추적해줘야 한다.
>- 함수 내부에서 직접 실행하기 위해서만 사용한다.
>- Parameter로 받은 Closure 를 변수나 상수에 대입할 수 없다.
>>- 실제로 변수나 상수에 Closure 를 대입하면, "Using non-escaping parameter 'closure' in a context expecting an @escaping closure" 과 같은 에러가 발생한다.
>- 중첩 함수에서 Closure 를 사용할 경우, 중첩 함수를 리턴할 수 없다.
>- 함수의 실행 흐름 밖으로 나갈 수 없으므로, 함수가 종료되기 전에 무조건 실행 되어야 한다.
>>- 함수가 종료되고 나서 클로저가 실행될 수 없다.
```swift
func doSomething(closure: () -> ()) {
    let f: () -> () = closure // Using non-escaping parameter 'closure' in a context expecting an @escaping closure
}
// 함수가 종료되고 나서 클로저가 실행될 수 없다는 에러가 발생함.
```

```swift
func doSomething(closure: () -> ()) {
    print("function start")
    
    DispatchQueue.main.asyncAfter(deadline: .now() + 10) { // Escaping closure captures non-escaping parameter 'closure'
        closure()
    }
    print("function end")
}
// 함수가 끝나고 클로저가 실행되기 때문에 에러가 발생함.
```

```swift
func outer(closure: () -> ()) -> () -> () {
    func inner() {
        closure()
    }
    return inner // Escaping local function captures non-escaping parameter 'closure'
}
// 중첩 함수 내부에서 매개 변수로 받은 클로저를 사용할 경우 중첩 함수를 리턴할 수 없기 때문에 에러가 발생함.
```
>- 위 에러의 원인은 non-escaping closure 의 주변 값 capture 방식에 있다.
- 함수 실행을 벗어나서 함수가 끝난 후에도 Closure 를 실행하거나, 중첩 함수에서 실행 후 중첩 함수를 리턴하고 싶거나, 변수나 상수에 대입하고 싶은 경우에 @escaping 키워드를 사용한다.
```swift
func doSomething(closure: @escaping () -> ()) {
}
// Closure Parameter 타입 앞에 @escaping 을 붙여주면 된다.
```
- @escaping 키워드를 사용할 경우
>- 변수나 상수에 Parameter 로 받은 Closure 를 대입할 수 있다.
>- 함수가 종료된 후에도 Closure 가 실행될 수 있다.
>- 중첩 함수에서 실행 후 중첩 함수를 리턴할 수 있다.

<br><br><br>
# Closure 의 Capture
- Closure 란 내부 함수와 내부 함수에 영향을 미치는 주변 환경을 모두 포함한 객체이다.
```swift
func doSomething() {
    var message = "Hi i am sodeul!"
 
    //클로저 범위 시작
    
    var num = 10
    let closure = { print(num) }
 
    //클로저 범위 끝
    
    print(message)
}
// closure 라는 익명 함수는, Closure 내부에서 외부 변수인 num 이라는 변수를 사용하기 때문에 num 의 값을 Closure 내부적으로 저장하고 있다.
// 이것을 Closure 에 의해 num의 값이 Capture 되었다 라고 한다.
// message 변수는 Closure 내부에서 사용하지 않기 때문에 Closure 에 의해 값이 Capture 되지 않는다.
```
- Closure 의 값 Capture 방식
>- Closure 는 값을 Capture 할 때, Value/Reference 타입에 관계 없이 Reference Capture 한다.
>- 위 예시에서 살펴보면 num 은 Int 타입의 구조체 이고 이는 Value 타입이기 때문에, 값을 복사해서 저장해야 한다. 하지만 Closure 는 타입에 관계 없이 Capture 하는 값들을 Reference Capture 한다.

```swift
func doSomething() {
    var num: Int = 0
    print("num check #1 = \(num)")
    
    let closure = {
        print("num check #3 = \(num)")
    }
    
    num = 20
    print("num check #2 = \(num)")
    closure()
}
// --> num check #1 = 0
// --> num check #2 = 20
// --> num check #3 = 20

// Closure 는 num 이라는 외부 변수를 Closure 내부에서 사용하기에 num 을 Capture 할 것이다.
// Closure 를 실행하기 전에 num 의 값을 외부에서 변경하면 Closure 내부에서 사용하는 num 의 값 또한 변경된다.


func doSomething() {
    var num: Int = 0
    print("num check #1 = \(num)")
    
    let closure = {
        num = 20
        print("num check #3 = \(num)")
    }
    
    closure()
    print("num check #2 = \(num)")
}
// --> num check #1 = 0
// --> num check #3 = 20
// --> num check #2 = 20

// Closure 내부에서 num 값을 변경하면 Closure 외부에 있는 num 의 값도 변경된다.
```

<br><br><br>
# Closure 의 Capture List
- Closure 의 시작인 { 옆에 [ ] 를 이용하여 Capture 할 멤버를 나열한다. in 키워드도 함께 작성한다.
```swift
let closure = { [num, num2] in ...
```
- Capture List 를 사용하면 Value 타입의 경우 Value Capture 가 가능하게 된다.
```swift
func doSomething() {
    var num: Int = 0
    print("num check #1 = \(num)")
    
    let closure = { [num] in
        print("num check #3 = \(num)")
    }
    
    num = 20
    print("num check #2 = \(num)")
    closure()
}
// --> num check #1 = 0
// --> num check #2 = 20
// --> num check #3 = 0
```
>- Value 타입으로 Capture 한 경우, Closure 를 선언할 당시의 num 의 값을 Const Value Type( 상수 ) 으로 Capture 한다.
>- 따라서 Closure 내부에서 Value Capture 된 값을 변경할 수 없다.
```swift
let closure = { [num, num2] in
    num = 2 // Cannot assign to value: 'num' is an immutable capture
```
>- Closure 는 기본적으로 Value 타입도 Reference Capture 를 하지만, Closure Capture List 를 이용하면 Value Capture 도 가능하다.
>- Reference 타입의 값은 Closure Capture List 에 작성한다 해도 Value Capture 가 되지 않고 Reference Capture 가 이루어진다.
<br><br><br>
# Closure 와 ARC( Automatic Reference Counting )
- ARC
>- WWDC2021 에서 ARC세션 - https://developer.apple.com/videos/play/wwdc2021/10216/
>- 인스턴스의 Reference Count 를 자동으로 계산하여 메모리를 관리하는 방법.
>- ARC 는 객체에 대한 Reference Count 를 관리하고 0이 되면 자동으로 메모리 해제한다.
>- Run Time 에 계속 실행되는 게 아니라 Compile Time 에 실행된다.
>- Retain Cycle 에는 유의해야 한다.
>>- Retain Cycle --> 메모리를 차지하고 있는 Reference 인스턴스는 아주 강하게 연결되어 있다.
>>- 인스턴스들 끼리 강하게 연결되어 있다가 nil 이 되면 그 아래 프로퍼티끼리 연결된 것들은 해제되지 않고 남아있게 되며 메모리 릭을 발생시킨다.
>>- 이런 메모리 릭을 방지하고자 연결상태를 Strong, Weak, Unowned 으로 상황에 따라서 결정하는 것이 Retain Cycle 이다.
>- Obj-C 에서는 MRC( Manual Reference Counting ), 수동으로 메모리를 관리 했다.
```obj-c
- (void)setName:(NSString *)newName {
  [newName retain];
  [name release];
  name = newName;
}
// retain : retain count( Reference Count ) 증가를 통해 현재 Scope 에서 객체가 유지되는 것을 보장
// release : retain count( Reference Count ) 를 감소시킨다, retain 후 필요없어질 때 release 한다.
```
>- 수동적인 MRC 와는 다르게 ARC 는 Compile Time 에 자동으로 retain, release 를 적절한 위치에 삽입하는 방식이다.
>>- 동적 할당으로 object 가 생성되면 해당 정보는 HeapObject 라는 struct 로 관리된다.
>>- HeapObject 안에는 Reference Count 도 포함된다.
>>- Class 에 대한 HeapObject 를 통해 Reference Count 를 관리할 수 있다.
```swift
class Human {
    var name = ""
    lazy var getName: () -> String = {
        return self.name
    }
    
    init(name: String) {
        self.name = name
    }
 
    deinit {
        print("Human Deinit!")
    }
}
// Closure 를 호출 시에만 초기화 되게끔 lazy 키워드를 사용했다.

var name: Human? = .init(name: "Hong-Gildong")
print(name!.getName())
// name 이라는 인스턴스를 만들고 Closure 로 작성되어 있는 getName 이란 지연 저장 프로퍼티를 호출했다.
// --> Hong-Gildong

name = nil

// name 인스턴스가 필요 없어서 nil을 할당을 했으니, 인스턴스의 Reference Count 가 0이 되어 deinit 이 호출되어야 한다.
// deinit 함수가 호출되지 않았다.
```
- Closure 의 강한 순환 참조
>- Closure 는 Reference 타입으로 Heap 에 존재한다.
>- 위 코드에서 생성한 human 이라는 인스턴스는 getName 을 호출하는 순간 그 Closure 가 Heap 에 할당되며, 이 Closure 를 참조하게 된다.
>- lazy 키워드를 사용하여 인스턴스 생성 직후가 아닌, 호출되순 순간에 Heap 에 할당된다.
>- getName 이라는 Closure 는 self 를 통해 Human 인스턴스의 프로퍼티에 접근하고 있으며, Closure 는 값을 Capture 할 때, Strong Capture를 하게 된다.
>- 따라서 이 때 Human 인스턴스의 Reference Count 가 증가한다.
>- * Human 인스턴스는 Closure 를 참조하고, Closure 는 Human 인스턴스의 변수를 참조하기 때문에 둘 다 메모리에서 헤제되지 않는 강한 순환 참조가 발생한다.
>- 강한 순환 참조는 weak, unowned 를 통해 해결할 수 있다.
- Closure 의 강한 순환 참조 해결법
>- Closure 가 Property 에 접근할 때 self 를 참조하면서 문제가 발생했기 때문에 self 에 대한 참조를 Closure Capture List 를 이용해 weak, unowned 로 Capture 한다.
```swift

class Human {
    lazy var getName: () -> String? = { [weak self] in
        return self?.name
    }
    
    init(name: String) {
        self.name = name
    }
 
    deinit {
        print("Human Deinit!")
    }
}
// weak 를 사용해서 Capture한 self 

class Human {
    lazy var getName: () -> String = { [unowned self] in
        return self.name
    }
    
    init(name: String) {
        self.name = name
    }
 
    deinit {
        print("Human Deinit!")
    }
}
// unowned 를 사용해서 Capture한 self 
```
>- 이렇게 하면 인스턴스의 Reference Count 가 0이 되면서 deinit 이 정상적으로 출력된다.
>- weak 의 경우 nil 을 할당받을 가능성이 있기에 Optional Type 으로 처리해줘야 하지만 unowned 의 경우엔 Non-Optional Type 으로 사용할 수 있다.
>- Closure 를 Lazy Initialization 으로 선언하여 강한 순환 참조가 일어난 경우, 인스턴스가 존재해야만 초기화가 가능하고, 이 때는 self 에 값이 있다고 가정하기 때문에 unowned 를 Optional Binding 을 하지 않고 사용할 수 있다.
>>- Swift 5.0 부터는 unowned 도 Optional Type 이 되지만, Capture List 로 동작할 땐 Non-Optional Type 이 되는 듯 하다.

<br><br><br>

# Named Closure
- Named Closure 는 전역 함수, 중첩 함수 를 뜻한다.
>- 전역 함수는 주변의 어떠한 값도 Capture 하지 않는다.
>- 중첩 함수는 자신을 포함하고 있는 함수의 값을 Capture 한다.
```swift
func outer() {
    var num: Int = 0
    
    func inner() {
        print(num)
    }
}
```
>- 위 코드에서 inner() 라는 중첩 함수는 outer() 함수의 num 값을 Reference Capture 하게 된다.



<br><br><br><br><br><br>

- 참조
>- [소들님](https://babbab2.tistory.com/81?category=828998)
>- [수진님](https://sujinnaljin.medium.com/ios-arc-%EB%BF%8C%EC%8B%9C%EA%B8%B0-9b3e5dc23814)
>- [Fomagran님](https://fomaios.tistory.com/entry/iOS-%EB%A9%B4%EC%A0%91%EC%A7%88%EB%AC%B8-Retain-Cycle%EC%9D%B4%EB%9E%80?category=890971)
