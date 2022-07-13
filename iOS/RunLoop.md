# 🏠   [Go Main](https://github.com/Raccoon97/Swift/blob/main/README.md)   🏠
- [RunLoop](https://github.com/Raccoon97/Swift/blob/main/iOS/RunLoop.md#runloop)
  - [RunLoop 를 사용하는 경우](https://github.com/Raccoon97/Swift/blob/main/iOS/RunLoop.md#runloop-%EB%A5%BC-%EC%82%AC%EC%9A%A9%ED%95%98%EB%8A%94-%EA%B2%BD%EC%9A%B0)
- [RunLoop 에서 수신하는 Event Source 와 구조](https://github.com/Raccoon97/Swift/blob/main/iOS/RunLoop.md#runloop-%EC%97%90%EC%84%9C-%EC%88%98%EC%8B%A0%ED%95%98%EB%8A%94-event-source-%EC%99%80-%EA%B5%AC%EC%A1%B0)
- [RunLoop 를 실행시키는 방법](https://github.com/Raccoon97/Swift/blob/main/iOS/RunLoop.md#runloop-%EB%A5%BC-%EC%8B%A4%ED%96%89%EC%8B%9C%ED%82%A4%EB%8A%94-%EB%B0%A9%EB%B2%95)
  - [RunLoop 의 모드](https://github.com/Raccoon97/Swift/blob/main/iOS/RunLoop.md#runloop-%EC%9D%98-%EB%AA%A8%EB%93%9C)


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

<br><br><br>

# RunLoop 에서 수신하는 Event Source 와 구조
- Input Source
  - 다른 Thread 나 Application 에서 온 비동기 이벤트
  - 핸들러에 비동기 이벤트를 전달하고 runUtilDate 메소드가 종료된다.
- Timer
  - 예약된 시간 또는 반복 간격으로 발생하는 동기 이벤트
  - 핸들러에 이벤트를 전달하지만 RunLoop 를 종료하지는 않는다.

- RunLoop 는 동작에 대해 노티피케이션을 생성한다.
- 등록된 RunLoop 옵저버를 통해 알림을 수신하고 추가 처리를 위해 Thread 에 구현하는 것이 가능하다.

<p align="center">
  <img width="569" alt="img1" src="https://user-images.githubusercontent.com/101554627/178672201-ecca75bd-237e-4665-95e7-3373a4052b46.png">
</p>

<br><br><br>

# RunLoop 를 실행시키는 방법
- run()
  - run 메소드를 실행하기 전 정의해 놓았던 Input Source, Timer 는 영구적으로 처리한다.
  - run 메소드 전의 Timer 와 후의 Timer 를 실행한 모습 

<p align="center">
  <img width="569" alt="img1" src="https://user-images.githubusercontent.com/101554627/178679960-a60b02f0-7fd7-4b49-84c7-433f04e4c3c8.gif">
</p>

<br>

- run(mode: before:)
  - Loop 를 한 번 실행하는데, 해당 모드로 지정된 기간까지 Input 을 막는다. 
<br>

- run(until: )
  - 메소드를 실행하기 전 정의해 놓았던 Input Source, Timer 를 지정된 기간까지 처리한다.
  - Loop 의 실행 시간을 지정할 수 있다.

<p align="center">
  <img width="569" alt="img1" src="https://user-images.githubusercontent.com/101554627/178682892-b64a3880-b72b-4730-babe-c707cfb38111.gif">
</p>

<br>

- acceptInput(fotMode: before:)
  - Loop 를 한 번 실행하는데, 해당 모드 또는 지정된 날짜까지만 입력을 허용한다.

<br><br>

## RunLoop 의 모드

|모드|이름|설명|
|------|---|---|
|Default|RunLoop.Mode.default(Cocoa)<br/><br/>kCFRunLoopDefaultMode(Core Foundtaion)|대부분 연산에 대한 기본 모드이다.|
|Modal|RunLoop.Mode.modalPanel(Cocoa)|Modal Panel 에서 발생한 이벤트만 처리한다.<br/><br/>macOS 에서만 사용 가능하다.|
|Event Tracking|RunLoop.Mode.EventTracking(Cocoa)|특정 이벤트 루프 중에 다른 이벤트 발생을 막아야 할 때 사용한다.( 마우스 드래깅 이벤트 등 )<br/><br/>macOS 에서만 사용 가능하다.|
|Tracking|RunLoop.Mode.tracking(Cocoa)|컨트롤을 추적하고 있는 상황에서 사용한다.<br/><br/>iOS, tvOS 에서 사용 가능하다.|
|Common modes|RunLoop.Mode.common(Cocoa)<br/><br/>kCFRunLoopCommonModes(Core Foundation)|여러 Mode 의 집합이다.<br/><br/>이 옵션으로 추가된 이벤트 소스나 옵저버는 common 모드에 속한 모든 모드에 속하게 된다.<br/><br/>기본 값으로 Cocoa 는 default, modal, eventTracking/ tracking 모드가 속하게 되고, Core Foundation 은 default 모드만 속해있다.<br/><br/>여기에 새로운 모드를 추가하려면 CFRunLoopAddCommonMode(::) 메소드를 사용하면 된다. (제거 기능은 없다. )|

<br><br><br>


# 참조
- [라이노님](https://jcsoohwancho.github.io/2019-09-01-%EC%8A%A4%EB%A0%88%EB%93%9C-%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%98%EB%B0%8D(2)-RunLoop/)
- [엠아이노님](https://minosaekki.tistory.com/54)
- [소들님](https://babbab2.tistory.com/68)
