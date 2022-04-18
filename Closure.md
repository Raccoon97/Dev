클로저
   - Named Closure
        - 일반적으로 함수라고 부르는 이것은 Named Closure 이다.

        func doSomething() {
            print("Somaker")
        }


   - Unnamed Closure
        - 이름을 붙이지 않고 사용하는 함수를 Unnamed Closure 라고 한다.
        
        let closure = { print("Somaker") }


    - 보통 Closure 하면 Unamed Closure 를 의미하지만 사실 Named Closure 와 Unamed Closure 둘 다 Closure 이다.
    - Closure 는 함수라서 " 1급 객체 함수 " 의 특성을 다 갖고 있다.
    - Closure 는 대입, 반환자이 가능하기에 자료형을 갖고 있다.

Closure의 표현식

    {
        (Parameter) -> Return Type in         // Closure Head
        실행 구문                               // Closure Body
    }

    - 익명함수 이므로 func 키워드는 사용하지 않는다.
    - Closure는 Closure Head 와 Closure Body로 이루어져 있는데, 그 둘을 구분짓는 것이 in 키워드 이다.

    - Parameter 와 Return Type 이 없는 클로저
        
        let closure = { () -> () in
            print("Closure")
        }
