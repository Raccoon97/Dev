# MVVM Pattern
- 소프트웨어 디자인 패턴 중 하나이다.
- Application 을 3 개의 영역으로 분할하고 각 영역에 고유한 역할을 부여하는 방식이다.
>- MVC Pattern 에서는 다양한 로직을 Controller 가 처리하기 때문에 Massive 해지는 문제가 있는데, MVVM Pattern 에서는 View 에 업데이트할 데이터를 View Model 에서 처리함으로써 Controller 가 복잡해지는 것을 줄여준다.

- MVVM 에서는 View 가 ViewModel 을 소유하고, ViewModel 이 Model 을 소유하는 방식이다.
- MVVM 의 핵심은 Data Binding 이다. 
>- Data Binding 은 데이터를 제공측과 그 데이터를 사용측을 연결시켜 동기화하는 방식이다.
- MVC 기반의 UIKit 과 달리 SwiftUI 는 MVVM 패턴을 기반으로 한다. 
- SwiftUI 는 Reactive Programming 패러다임을 취하고 있다.
>- 변화에 따라 데이터를 전달하고, 그에 반응해 적절한 이벤트를 실행하는 반응형 프로그래밍

<br>

<p align="center">
  <img src="https://user-images.githubusercontent.com/101554627/167997945-40ba5e86-b4f2-4a15-ae18-ab11b2897cb6.png" alt="center" />
</p>

<br><br><br>

# M - Model
- Model 은 ViewModel 이 소유하고 있고 View 나 ViewModel 이 Medel 에 대해 접근할 수 없다.
- Application 의 데이터와 비즈니스 로직을 관리한다.
>- 네트워크 코드
>- 파싱 코드
>- 관리자 및 추상화 계층/클래스
>- 데이터 소스 및 delegates
>- 상수

# V - View
- 사용자 이벤트를 수신하고, 데이터를 시각적으로 표현한다.
- View 와 Model 사이에 연결이 없고 ViewModel 에 의해 연결된다.

# VM - ViewModel
