# 🏠   [Go Main](https://github.com/Raccoon97/Swift/blob/main/README.md)   🏠
- [GCD( Grand Central Dispatch )](https://github.com/Raccoon97/Swift/blob/main/GCD.md#gcd-grand-central-dispatch-)
- [GCD 의 구조](https://github.com/Raccoon97/Swift/blob/main/GCD.md#gcd-%EC%9D%98-%EA%B5%AC%EC%A1%B0)
  - [Dispatch Queue](https://github.com/Raccoon97/Swift/blob/main/GCD.md#dispatch-queue)
  - [Dispatch Group](https://github.com/Raccoon97/Swift/blob/main/GCD.md#dispatch-groups)
  - [Dispatch Semaphores](https://github.com/Raccoon97/Swift/blob/main/GCD.md#dispatch-semaphores)
  - [Dispatch WorkItem](https://github.com/Raccoon97/Swift/blob/main/GCD.md#dispatch-work-item)
  - [Dispatch Sources](https://github.com/Raccoon97/Swift/blob/main/GCD.md#dispatch-sources)
- [GCD 의 사용](https://github.com/Raccoon97/Swift/blob/main/GCD.md#gcd-%EC%9D%98-%EC%82%AC%EC%9A%A9)
  - [Dispatch Queue](https://github.com/Raccoon97/Swift/blob/main/GCD.md#dispatch-queue-1)
  - [Dispatch WorkItem](https://github.com/Raccoon97/Swift/blob/main/GCD.md#dispatch-workitem)
  - [Dispatch Group](https://github.com/Raccoon97/Swift/blob/main/GCD.md#dispatch-group)
  - [Dispatch Semaphores](https://github.com/Raccoon97/Swift/blob/main/GCD.md#dispatch-semaphores-1)
- [GCD 의 장/단점](https://github.com/Raccoon97/Swift/blob/main/GCD.md#gcd-%EC%9D%98-%EC%9E%A5%EB%8B%A8%EC%A0%90)
- [주의](https://github.com/Raccoon97/Swift/blob/main/GCD.md#%EC%A3%BC%EC%9D%98)
<br><br><br>

# GCD( Grand Central Dispatch )
- 직접적으로 Thread 를 관리하지 않고 작업을 Queue 로 보내 분산처리 하는 방법
- iOS SDK 에는 비동기 처리를 위한 NSOperation 및 NSOpercisionQueue 클래스가 있었고 애플은 또 다른 방법으로 GCD 를 발표했다.
- GCD 는 멀티코어 시스템에서 동시성 실행을 제공하는 프레임워크이다.
- 기존 GCD 는 C 라이브러리 처럼 저수준의 API로 제공되어서 쉽게 사용하기 어려웠다.
- iOS 10 이후 Dispatch FrameWork 가 GCD 의 모든 내용을 캡슐화 해서 사용하기 쉽게 사용이 가능하다.

<br><br><br>

# GCD 의 구조
### Dispatch Queue
- 비동기 적으로 Task 를 수행시킬 수 있는 Queue 이다.
- Task 를 관리하는 Queue 이기 때문에, FIFO 데이터 구조이다. ( First In, First Out )
- Dispatch Queue 에는 Serial Dispatch Queue 와 Concurrent Dispatch Queue, Main Dispatch Queue 가 있다.
  - Serial Disaptch Queue - Queue 에 쌓인 Task 들을 순차적으로 1개씩 시작하며 이전 Task 가 종료되면 다음 Task 를 실행한다. ( 1번에 1개 )
  - Concurrent Disaptch Queue - Queue 에 쌓인 Task 들을 순서대로 시작하며, 이전 Task 가 종료되는 것을 기다리지 않고 다음 Task 를 실행한다. ( FIFO 구조로 계속 Task 를 실행 )
  - Main Dispatch Queue - Application 의 MainThread 에서 RunLoop 를 통해 관리되는 Queue 이며, Serial 하게 수행된다.
- Block Coding 을 기반으로 이해하기 쉽다.
- 사용하기 쉬운 인터페이스를 제공한다.
- OS 에서 자동으로 Thread 풀 관리를 수행한다.

<br>

### Dispatch Groups
- Dispatch Queue들의 Task 들을 모니터링 하는 그룹이다.
- 모든 큐들이 동작을 완료했을 때, 다음 Task를 진행시킬 수 있다.

<br>

### Dispatch Semaphores
- MultiThread 환경에서 Thread Safe를 지키기 위하여 객체나 변수에 대한 접근을 lock 하는 기존의 semaphore와 유사한 개념이다.

<br> 

### Dispatch Work Item
- Dispatch Queue 들을 캡슐화 하여 사용할 수 있게 한 것, 중간에 취소가 가능하다.

<br>

### Dispatch Sources
- 프로세스의 Notification,Signal 등 이벤트를 모니터링 할 수 있고, 이벤트가 발생하면 Dispatch Queue의 Task를 Submit 한다.

<br><br><br>

# GCD 의 사용

### Dispatch Queue
- 아래와 같이 새 Dispatch Queue 를 쉽게 만들 수 있다.
- Debugging 할 때 Thread 목록에 My Dispatch Queue 라는 레이블이 나타난다.
```swift
let dq = DispatchQueue(label: "my dispatch queue")
dq.async {
    print ("hello")
}
```
- 여러 개의 루프를 동시에 실행할 수 있다.
```swift
// 두 개의 동시 루프
DispatchQueue.global().async {
    for i in 1...5 {
        print("global async \(i)")
    }
}

DispatchQueue.global().async {
    for i in 1...5 {
        print("global async 2 \(i)")
    }
}
```
- .global() 메서드는 Default global queue 를 반환한다.
- Async 메서드는 Serial 하지 않다. -> 동시성
- Serial 하기를 원하면 sync() 메서드를 사용해야 한다. -> 비동시성
- sync 및 async 는 모두 다른 매개변수를 사용하며 가장 일반적인 매개변수는 블록을 전달하는 것이다.
- 서로 다른 QoS 대기열에서 블록을 실행할 수 있다.
```swift
DispatchQueue.global(qos: .background).async {
    for i in 1...5 {
        print("global async \(i)")
    }
}

DispatchQueue.global(qos: .userInteractive).async {
    for i in 1...5 {
        print("global async 2 \(i)")
    }
}
```
- QoS 는 우선 순위를 결정하고 시스템이 성능을 최적화 할 수 있도록 지원한다.
  - User Interactive - 메인 헤드에 해당하는 클래스이다.
  - User Initiated - 사용자가 트리거한 작업은 기본 Thred 에서 실행할 필요가 없다. DISPATCH_QUEUE_PRIORITY_HIGH 와 동일하다.
  - Default - 기본 QoS 이다. DISPATCH_QUE_PRIORITY_DEFAULT 와 동일하다.
  - Utility - 파일 및 네트워크 I/O 와 같은 시스템 리소스에 의존하는 Dispatch 항목에 사용된다. DISPATCH_QUE_PRIORITY_LOW 와 동일하다.
  - Background - 우선 순위가 낮은 작업에 사용된다. DISPATCH_QUE_PRIORITY_BACKGROUND 와 동일하다. 
- Main Dispatch Queue 를 통해 아래 예시처럼 Main Thread 에 작업을 제출할 수 있다.
```swift
DispatchQueue.main.async {
    for i in 1...5 {
        print("main async \(i)")
    }
}
```
- Main Queue 에서 동기적으로 작업을 실행하면 DeadLock 이 걸린다.
- Dispatch Queue 를 사용하면 concurrentPerform 메서드를 사용해 동시 루프를 간단히 수행할 수 있다.
```swift
DispatchQueue.concurrentPerform(iterations: 5) { (i) in
    print(i)
}
```

<br>

### Dispatch WorkItem
- 작업 항목의 개념을 캡슐화 한 것
- 블록을 사용하여 인스턴스를 초기화 한 후 현재 Thread 에서 실행하거나 Dispatch Queue 에 제출할 수 있다.
```swift
let dispatchWorkItem = DispatchWorkItem {
    for i in 1...5 {
        print("DispatchWorkItem \(i)")
    }
}
// Thread 실행
dispatchWorkItem.perform()

// Dispatch Queue 에 제출
DispatchQueue.global().async(execute: dispatchWorkItem)
```
- 취소 플래그가 있으며 Thread 에서 실행하기 전에 취소되면 Dispatch Queue 에서 실행하지 않고 건너뛴다.
- 실행 중에 취소되면 취소 프로퍼티가 True 를 반환한다. 이 경우 실행이 중단된다.

```swift
// dispatch work item 생성
var dispatchWorkItem: DispatchWorkItem? = DispatchWorkItem {
    for i in 1...5 {
        if (dispatchWorkItem?.isCancelled)!{
            break
        }
        sleep(1)
        print("DispatchWorkItem : \(i)")
    }
}
//global queue 에 제출
DispatchQueue.global().async(execute: dispatchWorkItem!)

//3초 뒤에 작업 취소
DispatchQueue.global().async{
    sleep(3)
    dispatchWorkItem?.cancel()
}
```

<br>

### Dispatch Group
- Dispatch Group 을 사용하면 다른 대기열에서 실행되는 경우에도 다른 작업을 확인할 수 있다.
```swift
let dispatchWorkItem = DispatchWorkItem{
    print("work item start")
    sleep(1)
    print("work item end")
}

let dg = DispatchGroup()

// Work Items 를 Group 에 넣기
let dispatchQueue = DispatchQueue(label: "custom dq")
dispatchQueue.async(group: dg) {
    print("block start")
    sleep(2)
    print("block end")
}
DispatchQueue.global().async(group: dg, execute: dispatchWorkItem)

// 모든 Group 이 끝나면 메시지 출력하기
dg.notify(queue: DispatchQueue.global()) {
    print("dispatch group over")
}
```

<br>

### Dispatch Semaphores
- Semaphores 를 사용하여 실행 흐름을 제어할 수 있다.
```swift
let semaphore = DispatchSemaphore(value: 0)
DispatchQueue.global().async {
    print("waiting for at least one signal")
    
    // 신호 대기
    semaphore.wait()
    print("At least one signal has been received")
}

DispatchQueue.global().async {
    sleep(2)
    print("calling signal")
    
    // 신호 전송
    semaphore.signal()
}
```
- wait 메서드를 사용해 시간 초과를 지정할 수 있다.
```swift
let sem = DispatchSemaphore(value: 0)
DispatchQueue.global().async {
    print("waiting for at least one signal for 1 second")
    
    // 신호 대기
    let res = sem.wait(timeout: DispatchTime.now() + 1)
    if(res == .timedOut){
        print("wait timed out")
    }else{
        print("At least one signal has been received")
    }
}

DispatchQueue.global().async {
    sleep(3)
    print("calling signal")
    
    // 신호 전송
    sem.signal()
}
```

<br><br><br>

# GCD 의 장/단점
### 장점
- Thread 의 관리를 개발자가 아닌 OS 가 해주기 때문에 신경쓸 일이 적다.
- Block 코딩 방식으로 쉬운 개발이 가능하다.

<br>

### 단점
- Queue 에 있는 Task 들의 취소가 까다롭다. ( DispatchWorkItem 을 이용하면 가능하다. )
- Block Coding 시 순환참조에 주의해야 한다.
- DeadLock 에 주의해야 한다. ( MainQueue 에서의 Sync 는 DeadLock 을 야기한다. )
- Obj-C 와 Swift 의 Block/Closure 에서 참조하는 외부 변수가 Reference Type 인지 Value Type 인지 고려해야 한다.
  - Obj-C Block 내 변수는 Value Type 이며 Swift Closuer 내 변수는 Reference Type 이다.
  - Ojb-C Block 의 경우는 _block 키워드를 선언하여 Reference Type 으로 사용할 수 있다.
  - Swift Clouser 의 경우는 Capture List 를 선언하여 Value Type 으로 사용할 수 있다.

<br><br><br>

# 주의
- 어떤 작업이 완료되고 나서 UI 를 갱신시키는 경우, Application 의 Main Thread 에서 처리되도록 해야 한다.
- MainQueue 는 Serial 하기 때문에, UI 갱신이 아닌 API 호출이나 Download 같은 작업을 MainQueue 에서 할 경우 Freezing 현상이 일어나며 Application 의 효율이 떨어지게 된다.
- tableView 혹은 collectionView 를 이용한 List 를 보여주는 동작에서 Image 에 대한 다운로드를 MainQueue 에서 모두 수행할 경우 버벅임이 일어난다.
- Image DownLoad 는 globalQueue( Concurrent Queue ) 에서 수행시키고 Download 완료 시 UI 갱신만 MainQueue 에서 호출해야 한다.
- UI 갱신이 필요하지 않고, 수행시간이 길거나, 수행에 소비되는 리소스가 큰 경우 Councurrent Queue 를 이용하면 좋다.

<br><br><br>

# 참조
- [Aske님](https://burzum17.tistory.com/8)
- [Yassine Benabbas님](https://medium.com/@yostane/swift-sweet-bits-the-dispatch-framework-ios-10-e34451d59a86)
