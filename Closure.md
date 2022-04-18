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

# 클로저의 경량화
