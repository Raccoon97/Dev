# 🏠   [Go Main](../../README.md)   🏠
- [CPU 스케줄링이란?](#cpu-스케줄링이란)
- [스케줄링의 목표](#스케줄링의-목표)
- [선점형 vs 비선점형](#선점형-vs-비선점형)
- [스케줄링 알고리즘](#스케줄링-알고리즘)
- [Process 상태](#process-상태)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# CPU 스케줄링이란?
- 다수의 프로세스가 존재할 때, 어떤 프로세스에게 CPU 를 할당할지 결정하는 정책이다.
- OS 의 **스케줄러 (Scheduler)** 가 담당하며, CPU 자원을 효율적으로 분배하는 것이 목표이다.

<br><br><br>

# 스케줄링의 목표
- **CPU 사용률 (CPU Utilization) 극대화** : CPU 가 놀지 않도록 한다.
- **처리량 (Throughput) 극대화** : 단위 시간당 완료되는 프로세스 수를 증가시킨다.
- **응답 시간 (Response Time) 최소화** : 요청에 대한 첫 응답까지의 시간을 줄인다.
- **대기 시간 (Waiting Time) 최소화** : Ready Queue 에서 대기하는 시간을 줄인다.
- **공정성 (Fairness)** : 모든 프로세스가 공평하게 CPU 를 할당받도록 한다.

> 이 목표들은 **Trade-off** 관계가 있으므로 상황에 따라 적절히 조절해야 한다.

<br><br><br>

# 선점형 vs 비선점형

### 선점형 (Preemptive)
- 실행 중인 프로세스가 있어도 OS 가 강제로 CPU 를 빼앗아 다른 프로세스에게 할당할 수 있다.
- 응답성이 좋고 대화형 시스템에 적합하다.
- Context Switching 오버헤드가 크고, 공유 자원에 대한 동기화 문제가 발생할 수 있다.
- 예 : Round Robin, SRT, Multilevel Queue

### 비선점형 (Non-Preemptive)
- 프로세스가 CPU 를 자발적으로 반납할 때까지 다른 프로세스는 기다려야 한다.
- Context Switching 오버헤드가 적고 구현이 단순하다.
- 응답성이 떨어지고, 긴 작업이 먼저 시작되면 짧은 작업이 오래 기다려야 한다.
- 예 : FCFS, SJF, HRRN, Priority

<br><br><br>

# 스케줄링 알고리즘

### 1. FCFS (First Come First Served)
- 먼저 온 프로세스부터 순서대로 처리하는 방식. (비선점형)
- 장점 : 구현이 간단하다.
- 단점 : **Convoy Effect** - 긴 작업이 먼저 오면 짧은 작업들이 오래 대기해야 한다.

### 2. SJF (Shortest Job First)
- CPU Burst Time 이 가장 짧은 프로세스를 먼저 처리하는 방식. (비선점형)
- 장점 : 평균 대기 시간이 최소가 되는 이상적인 알고리즘이다.
- 단점 : Burst Time 을 미리 알기 어렵고, 짧은 작업이 계속 들어오면 긴 작업이 **Starvation** 에 빠질 수 있다.

### 3. SRT (Shortest Remaining Time)
- SJF 의 선점형 버전. 남은 실행 시간이 가장 짧은 프로세스에게 CPU 를 할당한다.
- 단점 : 새로운 프로세스가 들어올 때마다 남은 시간을 비교해야 하므로 오버헤드가 크다.

### 4. Priority Scheduling
- 우선순위가 높은 프로세스부터 실행한다.
- 선점형/비선점형 모두 가능하다.
- 단점 : 우선순위가 낮은 프로세스가 Starvation 에 빠질 수 있다.
- 해결 : **Aging** (대기 시간이 길수록 우선순위를 높여줌)

### 5. Round Robin (RR)
- 각 프로세스에게 **Time Quantum (Time Slice)** 만큼 CPU 를 할당하고, 시간이 지나면 다음 프로세스로 넘긴다. (선점형)
- 장점 : 응답 시간이 짧고 공정하다.
- 단점 : Time Quantum 설정이 중요하다. 너무 짧으면 Context Switching 오버헤드가 크고, 너무 길면 FCFS 와 비슷해진다.

### 6. Multilevel Queue
- Ready Queue 를 여러 개로 나누고, 각 Queue 에 서로 다른 스케줄링 알고리즘을 적용한다.
- 예 : 시스템 프로세스, 대화형 프로세스, 배치 프로세스로 구분

### 7. Multilevel Feedback Queue
- Multilevel Queue 의 확장형으로, 프로세스가 Queue 사이를 이동할 수 있다.
- CPU Burst 시간이 긴 프로세스는 우선순위가 낮은 Queue 로, CPU 를 적게 사용하는 프로세스는 우선순위가 높은 Queue 로 이동시킨다.
- 가장 일반적으로 사용되는 알고리즘이다.

<br><br><br>

# Process 상태

```
  New → Ready → Running → Terminated
           ↑      ↓
        Waiting ←─
```

- **New** : 프로세스가 생성 중인 상태
- **Ready** : CPU 를 할당받을 준비가 된 상태 (Ready Queue 에서 대기)
- **Running** : CPU 를 할당받아 실행 중인 상태
- **Waiting (Blocked)** : I/O 등의 이벤트를 기다리며 대기 중인 상태
- **Terminated** : 실행이 완료된 상태

<br><br><br>

# 면접 예상 질문
- **Q. 선점형 스케줄링과 비선점형 스케줄링의 차이는?**
  - 선점형은 OS 가 실행 중인 프로세스로부터 CPU 를 강제로 빼앗을 수 있는 방식이고, 비선점형은 프로세스가 자발적으로 반납할 때까지 CPU 를 계속 사용하는 방식입니다. 선점형은 응답성이 좋지만 Context Switching 오버헤드가 크고, 비선점형은 오버헤드가 적지만 응답성이 떨어집니다.

- **Q. Round Robin 스케줄링의 Time Quantum 을 결정할 때 고려할 점은?**
  - Time Quantum 이 너무 짧으면 Context Switching 이 자주 발생해 오버헤드가 크고, 너무 길면 FCFS 와 동일해져 응답 시간이 길어집니다. 일반적으로 대부분의 CPU Burst 가 Time Quantum 내에 끝날 정도로 설정하는 것이 좋습니다.

- **Q. SJF 의 문제점은?**
  - CPU Burst 시간을 미리 알기 어렵다는 점과, 짧은 작업이 계속 들어올 경우 긴 작업이 Starvation 에 빠질 수 있다는 점입니다. 이를 해결하기 위해 Aging 기법을 사용합니다.

- **Q. iOS 의 QoS 와 관련이 있나요?**
  - 네, iOS 의 QoS (Quality of Service) 도 우선순위 기반 스케줄링의 일종입니다. userInteractive, userInitiated, default, utility, background 등으로 작업의 우선순위를 구분하고, 시스템은 이에 따라 CPU 자원을 분배합니다.
