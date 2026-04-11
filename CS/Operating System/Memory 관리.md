# 🏠   [Go Main](../../README.md)   🏠
- [Memory 계층 구조](#memory-계층-구조)
- [가상 메모리 (Virtual Memory)](#가상-메모리-virtual-memory)
- [Paging 과 Segmentation](#paging-과-segmentation)
- [Page Fault 와 Page Replacement](#page-fault-와-page-replacement)
- [Memory 할당 방식](#memory-할당-방식)
- [iOS 의 메모리 관리](#ios-의-메모리-관리)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# Memory 계층 구조
- 빠르지만 비싼 메모리 ↔ 느리지만 싼 메모리 사이의 Trade-off 를 해결하기 위해 계층 구조로 구성한다.

```
Register         (가장 빠름, 용량 작음)
  ↓
Cache (L1/L2/L3)
  ↓
Main Memory (RAM)
  ↓
SSD / HDD        (가장 느림, 용량 큼)
```

- 지역성(Locality) 원리 덕분에 이러한 계층 구조가 잘 동작한다.
  - **Temporal Locality (시간 지역성)** : 최근에 접근한 데이터는 가까운 미래에도 접근될 가능성이 높다.
  - **Spatial Locality (공간 지역성)** : 특정 위치에 접근하면 그 근처 위치도 접근될 가능성이 높다.

<br><br><br>

# 가상 메모리 (Virtual Memory)
- 프로세스가 물리적 메모리보다 더 큰 크기의 메모리를 사용하는 것처럼 보이도록 하는 기법이다.
- 각 프로세스에는 **가상 주소 공간** 이 할당되고, MMU (Memory Management Unit) 가 이를 **물리 주소** 로 변환한다.
- 장점
  - 프로세스마다 독립된 주소 공간을 갖기 때문에 메모리 보호가 가능하다.
  - 물리 메모리보다 큰 프로그램도 실행 가능하다.
  - 실제 필요한 부분만 메모리에 적재하므로 메모리 효율이 높다.

<br><br><br>

# Paging 과 Segmentation

### Paging
- 가상 메모리를 고정된 크기의 **Page** 로, 물리 메모리를 **Frame** 으로 나누어 관리하는 기법이다.
- Page Table 을 이용해 가상 주소를 물리 주소로 매핑한다.
- **외부 단편화 (External Fragmentation)** 문제를 해결한다.
- 단점 : **내부 단편화 (Internal Fragmentation)** 가 발생할 수 있다.

### Segmentation
- 메모리를 논리적 단위(Code, Data, Stack, Heap 등) 로 나누어 관리하는 기법이다.
- Segment 마다 크기가 다를 수 있다.
- **내부 단편화** 는 없지만 **외부 단편화** 가 발생할 수 있다.

### Paged Segmentation
- Segmentation 과 Paging 을 결합한 방식으로, 각 Segment 를 다시 Page 로 나누어 관리한다.
- 현대 OS 에서 주로 사용한다.

<br><br><br>

# Page Fault 와 Page Replacement
- **Page Fault** : CPU 가 필요로 하는 Page 가 물리 메모리에 없을 때 발생하는 인터럽트. 디스크에서 해당 Page 를 읽어와 메모리에 적재해야 한다.
- 메모리가 가득 차 있을 때는 기존 Page 중 하나를 Swap-out 해야 하며, 어떤 Page 를 교체할지 결정하는 알고리즘이 **Page Replacement Algorithm** 이다.

### 주요 Page Replacement 알고리즘
- **FIFO (First In First Out)** : 가장 먼저 들어온 Page 를 교체. 구현은 간단하지만 성능이 좋지 않다. Belady's Anomaly 발생 가능.
- **Optimal** : 앞으로 가장 오랫동안 사용되지 않을 Page 를 교체. 이론상 최적이지만 미래를 알아야 하므로 실제로 구현 불가.
- **LRU (Least Recently Used)** : 가장 오랫동안 사용되지 않은 Page 를 교체. 실제로 많이 사용된다.
- **LFU (Least Frequently Used)** : 가장 적게 사용된 Page 를 교체.
- **Clock (Second Chance)** : LRU 의 근사 알고리즘. 참조 비트를 이용해 구현한다.

<br><br><br>

# Memory 할당 방식

### 정적 할당 (Static Allocation)
- 컴파일 타임에 크기가 결정된다.
- 전역 변수, 정적 변수 등이 해당된다.
- Data 영역에 저장된다.

### 동적 할당 (Dynamic Allocation)
- 런타임에 크기가 결정된다.
- `malloc`, `new` 등을 통해 Heap 에 할당한다.
- 사용 후 명시적으로 해제해야 한다. (C/C++)

### Heap 동적 할당 전략
- **First Fit** : 처음 발견한 충분한 크기의 빈 공간에 할당
- **Best Fit** : 가장 알맞은(가장 작은) 빈 공간에 할당
- **Worst Fit** : 가장 큰 빈 공간에 할당

<br><br><br>

# iOS 의 메모리 관리
- iOS 는 **ARC (Automatic Reference Counting)** 를 통해 자동으로 객체의 메모리를 관리한다.
- Garbage Collection 과 달리 ARC 는 **컴파일 타임** 에 retain/release 코드를 삽입하므로 런타임 오버헤드가 적다.
- Strong Reference Count 가 0 이 되면 객체가 자동으로 해제된다.
- **Swap 이 없다** : iOS 는 디스크 공간이 제한적이므로 Swap 영역을 사용하지 않는다. 메모리가 부족하면 `didReceiveMemoryWarning` 이 호출되고, 그래도 부족하면 앱이 강제 종료된다.
- 객체가 저장되는 영역
  - **Value Type (struct, enum)** : Stack 에 할당 (크기가 클 경우 Heap)
  - **Reference Type (class, closure)** : Heap 에 할당

<br><br><br>

# 면접 예상 질문
- **Q. 가상 메모리는 왜 필요한가요?**
  - 각 프로세스에 독립된 주소 공간을 제공해 메모리 보호를 가능하게 하고, 물리 메모리보다 큰 프로그램을 실행할 수 있게 하며, 필요한 부분만 메모리에 올려 메모리 효율을 높입니다.

- **Q. Paging 과 Segmentation 의 차이점은?**
  - Paging 은 고정 크기 단위로 메모리를 관리하므로 외부 단편화는 없지만 내부 단편화가 발생합니다. Segmentation 은 논리적 단위로 메모리를 관리해 내부 단편화는 없지만 외부 단편화가 발생합니다. 현대 OS 는 두 방식을 결합한 Paged Segmentation 을 주로 사용합니다.

- **Q. LRU 는 어떻게 구현하나요?**
  - 일반적으로 **Doubly Linked List 와 Hash Map 을 결합** 해 구현합니다. 접근 시 해당 노드를 리스트의 맨 앞으로 이동시키고, 교체 시에는 리스트의 맨 뒤 노드를 제거합니다. 모든 연산을 `O(1)` 에 수행할 수 있습니다.

- **Q. Stack 과 Heap 의 차이는 무엇인가요?**
  - Stack 은 함수 호출 시 자동으로 할당/해제되며 LIFO 구조입니다. 접근 속도가 빠르지만 크기가 제한적입니다. Heap 은 동적으로 할당되며 개발자(또는 GC/ARC) 가 해제를 관리합니다. 접근 속도는 Stack 보다 느리지만 크기 제약이 적습니다.

- **Q. iOS 는 왜 Garbage Collector 대신 ARC 를 사용하나요?**
  - GC 는 주기적으로 실행되면서 CPU 와 메모리를 점유해 성능 저하를 일으킬 수 있고, 언제 실행될지 예측하기 어려워 실시간성이 떨어집니다. ARC 는 컴파일 타임에 retain/release 코드를 자동 삽입하므로 런타임 오버헤드가 적고 예측 가능한 동작을 보장합니다.
