# 🏠   [Go Main]()   🏠
- []()

<br><br><br>

# App Life Cycle
- App 의 실행/ 종료 사이에 발생하는 일련의 이벤트로 구성된다.

<br>

## 기기 부팅부터 App 실행까지의 단계
 1. 기기가 부팅되면 OS 에 속한 App 을 제외하고 실행 중인 App 이 없다.
 2. 사용자가 App 아이콘을 탭하면 SpringBoard 가 App 을 실행한다. ( SpringBoard 는 iOS 의 홈 화면을 관리하는 표준 응용 프로그램이다. )
 3. SpringBoard 가 App 의 LaunchScreen 을 보여주는 동안 App 과 필요한 라이브러리가 메모리에 로드된다.
 4. UIKit 에서 UIApplicationMain 함수를 실행해 UIApplication 객체가 생성된다.
 5. @UIApplicationMain 또는 @Main 어노테이션이 있는 클래스를 찾아 AppDelegate 객체를 생성한다.
 6. Main Event Loop 를 실행한다( 사용자의 액션을 받는 루프 )
<!-- - App 이 실행을 시작하고 Application Delegate 가 알림을 받는다.
- UIApplicationDelegate 프로토콜을 이용해서 App 의 실행, Back/Foreground 로 전환, App 종료, 푸시 알림 등 같은 사용자 이벤트에 대한 알림을 받는다.
- UIResponder 클래스를 이용해 사용자 이벤트에 응답할 수 있도록 한다. -->

<br>

## Main Run Loop
- UIApplication 객체는 App 이 실행될 때 Main Run Loop 를 실행한다.
- 모든 사용자 관련 이벤트를 처리한다.
- AppDelegate 는 App 실행 시 기본 실행 루프를 설정하여 이벤트를 처리하고 뷰 기반 인터페이스에 대한 업데이트를 처리한다.
- 이 루프는 App 의 Main Thread 에서 실행된다.
- Main Thread 는 Serial 하며, 사용자 관련 이벤트가 수신된 순서대로 Serial 하게 처리된다.

![image](https://user-images.githubusercontent.com/101554627/174982484-ce415d9e-84b0-4d80-b943-a88fb05e9535.png)

<br>

### 위 그림에 대한 설명
- 이벤트가 발생한다.
- UIKit 프레임워크를 통해 생성된 port 로 이벤트가 앱에게 전달된다.
- 이벤트는 Queue 의 형태로 정리되어 Event Queue 에 쌓여서 Main Run Loop 에 하나씩 매핑된다.
- UIApplication 객체는 매핑된 것을 바탕으로 어떤 것을 실행할지 결정한다.

<br>

## App State
- App 상태는 총 5가지로 구분된다.

<br>

- Not Running
  - App 이 실행되지 않았거나, 완전히 종료되어 동작하지 않는 상태

<br>

- Inactive( Foreground )
  - App 이 실행되면서 Foreground 에 진입하나 어떠한 이벤트도 받지 않는 상태, 앱의 상태 전환 과정에서 잠깐 머무는 단계

<br>

- Active( Foreground )
  - App 이 실행중이며, Foreground 에 있고, 이벤트를 받고 있는 상태

<br>

- Background
  - App 이 Background 에 있으며, 다른 앱으로 전환되었거나 홈버튼을 눌러 밖으로 나갔을 때의 상태, 일정 시간이 지나 앱은 Suspended 상태로 바뀌게 된다.
  - Ex) 음악 App 을 켜놓고 다른 App 을 사용해도 음악이 계속 들리는 경우

<br>

- Suspended
  - App 이 Background 상태에 있지만, 아무 작업도 실행되지 않은 상태( Background 에서 특별한 작업이 없을 경우 Suspended 상태가 된다 )
  - 이 상태에서 App 은 메모리상에 올라가있지만 아무 작업도 하지 않기에 배터리를 사용하지 않는다.
  - OS 에 의해 메모리 부족현상이 발생하면 이 상태의 App 은 메모리에서 없어질 수 있으며 따로 알림이 나타나지 않는다.

<br>

<p align="center">
  <img width="569" alt="스크린샷 2022-06-22 오후 12 56 05" src="https://user-images.githubusercontent.com/101554627/174940201-6a6831e1-ad13-4be3-813b-1628254d8c98.png">
 </p>
 
 # AppDelegate 객체의 메소드 호출
 </p>
