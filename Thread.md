# 🏠   [Go Main](https://github.com/Raccoon97/Swift/blob/main/README.md)   🏠
- [Thread](https://github.com/Raccoon97/Swift/blob/main/Thread.md#thread)
- [Thread Safe](https://github.com/Raccoon97/Swift/blob/main/Thread.md#thread-safe)
- [atomic](https://github.com/Raccoon97/Swift/blob/main/Thread.md#atomic)
- [non-atomic](https://github.com/Raccoon97/Swift/blob/main/Thread.md#non-atomic)
- [Thread Safe 를 위한 방법](https://github.com/Raccoon97/Swift/blob/main/Thread.md#thread-safe-%EB%A5%BC-%EC%9C%84%ED%95%9C-%EB%B0%A9%EB%B2%95)

<br><br><br>

# Thread
- Thread 란 Process 내에서 실제로 작업을 수행하는 주체를 의미한다.
- 모든 Process 에는 한 개 이상의 Thread 가 존재하여 작업을 수행한다.
- 두 개 이상의 Thread 를 가지는 Process 를 Multi-Threaded Process 라고 한다.

<br>
  
![image](https://user-images.githubusercontent.com/101554627/170500892-a2cbc9c9-3707-402c-9f17-c80422cfbb16.png)

<br><br><br>

# Thread Safe
- Thread Safe 란 Multi-Threaded 프로그래밍에서 어떤 함수나 변수, 객체가 어떤 Thread 로 부터 동시에 접근이 이루어져도 문제가 생기지 않는다는 것을 의미한다.
- iOS 에서는 Multi-Threaded 방식을 사용한다.
- Multi-Threaded 의 경우 Stack 을 제외한 Heap, Data 영역 등을 공유하고 있기 때문에 한 Thread 에서 사용중인 곳에 다른 Thread 가 접근하면 문제가 생길 수 있다.
- Multi-Process 에서는 공유하는 자원공간이 없기 때문에 문제가 생기지 않는다.

<br>

## atomic
- 프로그래밍에서 데이터의 변경이 동시에 일어난 것처럼 보이게 하는 것
- atomic 한 데이터를 변경하는 동안에는 lock 을 걸어서 다른 Thread 의 접근이 이루어지지 않게 한다.
- Property 가 atomic 하다는 것은 Multi-Threaded 환경에서 데이터가 수정되는 순간에는 접근할 수 없다는 것이다.
- atomic Property 는 항상 Concurrent 가 아닌 serial 하게 접근된다.
- Swift 는 Thread Safe 를 고려한 언어가 아니기 때문에 모든 Property 는 non-atomic 이므로 별도로 atomic 을 지정하는 것이 불가하다.
- 위와 같은 이유로 GCD( Grand Central Dispatch ) 를 통해 데이터를 다뤄야 한다.

<br>

## non-atomic
- 반환된 값에 대해 보장하지 않는다. 정확한 값이거나 쓰레기 값이다.

<br>

## Thread Safe 를 위한 방법
- Mutual Exclusion - Thread 에 lock 이나 semaphore 를 걸어서 공유자원에는 하나의 Thread 만 접근 가능하게 한다.
- Thread Local Storage - 특정 Thread 에만 접근 가능한 저장소를 만든다.
- ReEntrancy - Thread 에서 동작하는 코드가 동일 Thread 에서 재수행되거나, 다른 Thread 에서 해당 코드를 동시에 수행해도 동일한 결과를 얻을 수 있도록 작성한다.
- Atomic Operation - 데이터 변경 시 atomic 하게 데이터에 접근하도록 만든다.
- Immutable Object - 객체 생성 이후에 값을 변경할 수 없도록 만든다.

<br><br><br>

# 참조
- [ginjo님](https://ginjo.tistory.com/17)
- [엠아이노님](https://minosaekki.tistory.com/50)
