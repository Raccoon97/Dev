

# Dispatch Queue
- Dispatch Queue 는 작업 항목의 실행을 관리하는 클래스이다.

<br><br><br>

# Serial
- 이전 작업이 끝나면 다음 작업을 순차적으로 실행하는 직렬 형태의 Queue
- 하나의 작업을 실행하고 끝날 때까지 대기열에 있는 다른 작업을 잠시 미룬 뒤 그 작업이 끝나면 실행된다.

<br><br><br>

# Concurrent
- 이전 작업이 끝날 때까지 기다리지 않고 병렬 형태로 동시에 실행되는 Queue
- 대기열에 있는 작업을 동시에 별도의 Thread 를 사용하여 실행한다.

<br><br><br>

# QoS( Quality of Service )
- Dispatch Queue 에서 수행 할 작업을 분류하기 위해 사용한다.
- QoS 를 지정해서 중요도를 표시하고, 시스템이 우선순위를 정해 이에 따라 스케쥴링을 한다.

```swift
// Main Queue
DispatchQueue.global(pos: .userInteractive) {}

// 유저가 시작한 작업, 유저가 응답을 기다림
DispatchQueue.global(pos: .userInitiated) {}

// userInitiated 와 utility 의 중간
DispatchQueue.global(pos: .default) {}

// 시간이 걸리며 즉각적인 응답이 필요하지 않은 경우
DispatchQueue.global(pos: .utility) {}

// 눈에 보이지 않는 부분의 작업, 완료되는 시간이 중요하지 않을 경우
DispatchQueue.global(pos: .background) {}

// QoS 가 지정되지 않는 경우
DispatchQueue.global(pos: .unspecified) {}
```

<br><br><br>

# 참조
