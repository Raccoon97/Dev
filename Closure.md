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
- 지금까지의 Closure 는 모두 non-escaping Closure 이다.
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


```swift

```
