# 🏠   [Go Main](../../README.md)   🏠
- [Process](#process)
- [Thread](#thread)
- [Process 와 Thread 의 차이](#process-와-thread-의-차이)
- [Context Switching](#context-switching)
- [Multi Process vs Multi Thread](#multi-process-vs-multi-thread)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# Process
- 실행 중인 프로그램을 의미한다. 즉, 디스크에 저장된 프로그램이 메모리에 적재되어 실행되고 있는 상태이다.
- 운영체제로부터 독립된 메모리 영역을 할당받아 사용한다.
- Process 는 최소 1 개 이상의 Thread 를 가지며, 기본적으로 하나의 메인 스레드를 가진다.
- Process 의 메모리 구조
  - **Code (Text)** : 실행 코드가 저장되는 영역
  - **Data** : 전역 변수, 정적(static) 변수가 저장되는 영역
  - **Heap** : 동적 할당된 메모리 영역 (런타임에 크기가 결정)
  - **Stack** : 지역 변수, 매개변수, 함수 호출 정보 등이 저장되는 영역

```
+---------------+  높은 주소
|     Stack     |  ↓ 함수 호출 시 증가
+---------------+
|       ↕       |
+---------------+
|     Heap      |  ↑ 동적 할당 시 증가
+---------------+
|     Data      |
+---------------+
|     Code      |
+---------------+  낮은 주소
```

<br><br><br>

# Thread
- Process 내에서 실행되는 작업의 흐름 단위이다.
- 하나의 Process 는 여러 개의 Thread 를 가질 수 있으며, 이러한 Process 를 **Multi-Threaded Process** 라고 한다.
- 같은 Process 내의 Thread 들은 **Code, Data, Heap 영역을 공유** 하고, **Stack 영역은 각각 별도로 할당** 받는다.
- Stack 을 공유하지 않는 이유는 함수의 호출 흐름이 서로 다르기 때문이다.

<br><br><br>

# Process 와 Thread 의 차이

| 구분 | Process | Thread |
|---|---|---|
| 메모리 공유 | 독립적인 메모리 영역 | Code, Data, Heap 공유 |
| 생성 비용 | 높음 | 낮음 |
| Context Switching 비용 | 높음 | 낮음 |
| 통신 방식 | IPC (파이프, 소켓, 메시지 큐 등) | 공유 메모리 직접 접근 |
| 안정성 | 한 Process 가 죽어도 다른 Process 에 영향 없음 | 한 Thread 가 죽으면 Process 전체에 영향 |

<br><br><br>

# Context Switching
- CPU 가 현재 실행 중인 Process(또는 Thread) 의 상태를 **PCB(Process Control Block)** 에 저장하고, 다음 실행할 Process 의 상태를 PCB 에서 불러와 CPU 레지스터에 복원하는 작업이다.
- Thread 간 Context Switching 이 Process 간 Context Switching 보다 훨씬 비용이 적다. 이는 Thread 는 메모리 주소 공간을 공유하므로 Page Table, TLB 등을 교체할 필요가 없기 때문이다.
- Context Switching 중에는 CPU 가 실질적인 작업을 수행하지 못하므로 **Overhead** 가 발생한다.

### PCB 에 저장되는 정보
- Process ID (PID)
- Process State (Ready, Running, Waiting ...)
- Program Counter
- CPU Register 값
- Memory Management 정보
- 입출력 상태 정보

<br><br><br>

# Multi Process vs Multi Thread

### Multi Process
- **장점**
  - 하나의 Process 가 죽어도 다른 Process 에 영향을 주지 않는다. (안정성)
  - 독립된 메모리 공간을 사용하므로 구현이 단순하고 동기화 문제가 적다.
- **단점**
  - 생성 및 Context Switching 비용이 크다.
  - Process 간 통신(IPC) 이 복잡하다.

### Multi Thread
- **장점**
  - Thread 생성 및 Context Switching 비용이 적다.
  - 자원을 공유하므로 통신이 간단하다.
  - 시스템 자원을 효율적으로 사용할 수 있다.
- **단점**
  - 동기화 문제 (Race Condition, Deadlock) 가 발생할 수 있다.
  - 한 Thread 가 문제를 일으키면 Process 전체에 영향을 미친다.
  - 디버깅이 어렵다.

<br><br><br>

# 면접 예상 질문
- **Q. Process 와 Thread 의 차이점은 무엇인가요?**
  - Process 는 실행 중인 프로그램으로 독립된 메모리 공간을 갖고, Thread 는 Process 내부의 실행 흐름 단위로 Code, Data, Heap 영역을 공유하지만 Stack 은 각각 독립적으로 갖습니다. Thread 는 Process 보다 생성과 Context Switching 비용이 훨씬 적습니다.

- **Q. 왜 Multi-Threading 이 필요한가요?**
  - 하나의 Process 가 여러 작업을 동시에 처리할 수 있도록 해서 시스템 자원을 효율적으로 사용하고 응답성을 높이기 위함입니다. 예를 들어 iOS 앱에서는 네트워크 요청이나 이미지 다운로드 같은 무거운 작업을 백그라운드 Thread 에서 수행하고 UI 는 메인 Thread 에서 갱신해 앱이 멈추지 않도록 합니다.

- **Q. Context Switching 이 일어나면 어떤 일이 발생하나요?**
  - 현재 실행 중인 Process 의 상태(레지스터, Program Counter 등) 를 PCB 에 저장하고, 다음 실행할 Process 의 PCB 에서 상태를 복원해 CPU 에 로드합니다. 이 과정에서 캐시 미스가 발생하고 실제 작업을 하지 않으므로 Overhead 가 발생합니다.

- **Q. Thread 간에는 왜 Stack 을 공유하지 않나요?**
  - Stack 에는 함수 호출 정보, 지역 변수, 매개변수가 저장되는데, Thread 마다 실행 흐름이 다르므로 각자 독립된 Stack 을 가져야 서로의 함수 호출 흐름을 침범하지 않습니다.

- **Q. iOS 의 GCD(Grand Central Dispatch) 와 관련 지어 설명해주세요.**
  - GCD 는 Thread Pool 을 OS 가 관리하며, 개발자는 DispatchQueue 에 작업(Closure) 만 제출하면 됩니다. Thread 를 직접 생성/관리하지 않으므로 개발 생산성이 높아지고 시스템 자원도 효율적으로 사용할 수 있습니다.
