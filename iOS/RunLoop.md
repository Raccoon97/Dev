# 🏠   [Go Main](https://github.com/Raccoon97/Swift/blob/main/README.md)   🏠
- []()


<br><br><br>

# RunLoop
- 소켓, 파일, 키보드, 마우스 등 이벤트 소스를 입력받아 처리한다.
- Timer 는 current() 메소드로 처리가 가능하다.
- MainThread 에서는 자동으로 설정하고 실행되지만, 직접 만든 Thread 에서는 직접 관리해줘야 한다.
- Thread-Safe 하지 않다.
  - 다른 

<br>

## RunLoop 를 사용하는 경우
- Input Source 를 통해 다른 Thread 와 통신하는 경우
- Timer 를 사용하는 경우
- Perform Selector Source 를 사용해야 하는 경우

<br><br><br>

# RunLoop 에서 수신하는 Event Source
- Input Source
  - 다른 Thread 나 Application 에서 온 비동기 이벤트
- Timer
  - 예약된 시간 또는 반복 간격으로 발생하는 동기 이벤트

- RunLoop 는 내부적으로 반복 실행을 하지 않는다.
  - Event Source 를 읽고 실행이 끝나면 대기한다.
  - 명시적으로 반복문을 통해 RunLoop 를 실행시켜 주어야 한다.

<p align="center">
  <img width="569" alt="img1" src="https://user-images.githubusercontent.com/101554627/178672201-ecca75bd-237e-4665-95e7-3373a4052b46.png">
</p>
  
  
## Sub
### TinySub





# 참조
- []()
