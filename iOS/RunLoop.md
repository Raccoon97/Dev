# 🏠   [Go Main](https://github.com/Raccoon97/Swift/blob/main/README.md)   🏠
- []()


<br><br><br>

# RunLoop
- 소켓, 파일, 키보드, 마우스 등 이벤트 소스를 입력받아 처리한다. 또한 Timer 이벤트도 처리한다.

<br>

- 모든 Thread 는 각자의 RunLoop 를 가질 수 있으며 Thread 생성 시 자동으로 생성된다.

<br>

- MainThread 를 제외한 모든 Thread 에서 RunLoop 는 자동으로 실행되지 않는다.
  - MainThread 에서는 프레임워크 차원에서 자동으로 설정하고 실행되지만, 직접 만든 Thread 에서는 직접 관리해줘야 한다.
  ```swift
  // 현재 Thread 의 RunLoop 는 다음과 같이 접근할 수 있다.
  let runLoop = RunLoop.current
  ```

<br>

- Thread-Safe 하지 않다.
  - 다른 Thread 에서 실행중인 RunLoop 의 메소드를 호출하면 예기치 않은 결과가 발생할 수 있다.

<br>

- RunLoop 는 내부적으로 반복 실행을 하지 않는다.
  - Event Source 를 읽고 실행이 끝나면 대기한다.
  - 명시적으로 반복문을 통해 RunLoop 를 실행시켜 주어야 한다.

<br>

## RunLoop 를 사용하는 경우
- Input Source 를 통해 다른 Thread 와 통신하는 경우

<br>

- Timer 를 사용하는 경우

<br>

- Perform Selector Source 를 사용해야 하는 경우


# RunLoop 를 실행시키는 방법
- run()
  - run 메소드를 실행하기 전 정의해 놓았던 Input Source, Timer 는 영구적으로 처리한다.
  - run 메소드 전의 Timer 와 후의 Timer 를 실행한 모습 
  - Timer 1 은 실행된다. Timer 2 는 실행되지 않는다.

<p align="center">
  <img width="569" alt="img1" src="https://user-images.githubusercontent.com/101554627/178679960-a60b02f0-7fd7-4b49-84c7-433f04e4c3c8.gif">
</p>

<br>

- run(mode: before:)
  - Loop 를 한 번 실행하는데, 해당 모드로 지정된 기간까지 Input 을 막는다. 
<br>

- run(until: )
  - 지정된 기간까지 메소드를 실행하기 전 정의해 놓았던 Input Source 를 처리한다.

<br>

- acceptInput(fotMode: before:)

<br><br><br>

# RunLoop 에서 수신하는 Event Source
- Input Source
  - 다른 Thread 나 Application 에서 온 비동기 이벤트
- Timer
  - 예약된 시간 또는 반복 간격으로 발생하는 동기 이벤트


<p align="center">
  <img width="569" alt="img1" src="https://user-images.githubusercontent.com/101554627/178672201-ecca75bd-237e-4665-95e7-3373a4052b46.png">
</p>
  
  
## Sub
### TinySub





# 참조
- []()
