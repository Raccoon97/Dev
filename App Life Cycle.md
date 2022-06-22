# 🏠   [Go Main]()   🏠
- [App Life Cycle]()
 - [기기 부팅부터 App 실행까지의 단계]()
 - [Main Run Loop]()
- [App State]()
- [AppDelegate 객체의 메소드 호출]()
 - [Not Running]()
 - [Inactive]()
 - [Active]()
 - [Background]()
- [Foreground]()
- [Suspended]()
- []()
- []()
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

- In-active( Foreground )
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
- App 의 Life Cycle 상태에 따라서 AppDelegate 객체의 SceneDelegate 에서 특정 메소드를 호출하게 된다.

## Not Running 
```swift
application(_ :willFinishLaunchingWithOptions)
// App 을 실행할 때 최초로 실행할 코드를 작성하면 좋다.
// 필요한 주요 객체들을 생성하고 앱 실행 준비가 끝나기 직전에 호출된다.

applicationDidFinishLaunching(_ :)
// App 실행을 위한 모든 준비가 끝난 후 화면이 사용자에게 보여지기 전에 호출된다.
// 주로 초기화 코드를 이 곳에 작성한다.

applicationWillTerminate(_ :)
// App 이 종료되기 직전에 호출된다.
```

## In-active 
```swift
sceneWillEnterForeground(_ :)
// App 이 Background 나 Not Running 에서 Foreground 로 들어가기 직전에 호출된다.
// 비활성화 상태를 거쳐 활성화 상태가 된다.

sceneWillResignActive(_ :)
// App Switcher 모드 ( 홈 바 쓸어올렷을 경우, 홈 버튼 두 번 눌렀을 경우
```

## Active
```swift
sceneDidBecomeActive(_ :)
// App 이 비활성화 상태에서 활성 상태로 진입하고 난 직후 호출된다.
// App 이 실제로 사용되기 전에, 마지막으로 준비할 수 있는 코드를 작성할 수 있다.
```

## Background
```swift
sceneDidEnterBackground(_ :)
// App 이 Background 상태로 들어갔을 때 호출된다.
// Suspended 상태가 되기 전 중요한 데이터를 저장하는 등 종료하기 전 필요한 작업을 한다.
```

## Suspended
```swift
// 따로 호출되는 메소는 없으며 Background 상태에서 특별한 작업이 없을 때 Suspended 상태가 된다.
```

<br><br><br>

# iOS12 까지와 iOS13 이후의 차이점
## iOS12 까지
- SceneDelegate 없음
- Scene 을 지원하지 않는다. 이 경우 모든 Life Cycle 관련 이벤트들은 AppDelegate 에 전달된다.
- 각각의 상태에 접근하기 위해 사용되는 파일이 AppDelegate.swift 이다.
```swift
// AppDelegate.swift
import UIKit

@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {
 var window: UIWindow?
 
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        return true
    }
    
    func applciationWillResignActive(_ application: UIApplication) {
    }
    
    func applciationDidEnterBackground(_ application: UIApplication) {
    }
    
    func applciationWillEnterForeground(_ application: UIApplication) {
    }
    
    func applciationDidBecomeActive(_ application: UIApplication) {
    }
    
    func applciationWillTerminate(_ application: UIApplication) {
    }
```
- 위 코드를 보면 AppDelegate 객체는 UIResponder 와 UIApplicationDelegate 를 상속 및 참조하고 있다.
- UIResponder 는 App 에서 발생하는 이벤트들을 담고 잇는 추상형 인터페이슥 객체로 View 와 사용자 이벤트간의 연결을 관리하는 역할을 한다.
- UIApplicationDelegate 는 UIApplication 객체의 작업에 개발자가 접근할 수 있도록 하는 메소드 들을 담고 있다.

<br>

## iOS13 이후
- SceneDelegate 있음
- SceneDelegate 는 UI Life Cycle 을 관리하는 클래스이다.
- iOS12 까지는 하나의 앱이 하나의 Window 만 가지기 때문에 AppDelegate 클래스가 UI Life Cycle 관리 까지 했다.
- iOS13 부터 하나의 앱에 여러 개의 Window 를 동시에 사용할 수 있게 되어서 SceneDelegate 클래스가 추가되었다.
- Scene 을 지원하는 경우 Scene 별로 별도의 Life Cycle 을 가지게 된다.
- Scene 하나는 디바이스에서 돌아가는 App 의 UI 인스턴스 하나를 나타낸다.
- 하나의 App 은 여러개의 Scene 을 가질 수 있으며, 이를 개별적으로 띄우거나 숨길 수 있다.


<br><br><br>

# 참조
- [마나사님](https://manasaprema04.medium.com/application-life-cycle-in-ios-f7365d8c1636)
- [쿠로미님](https://blog.naver.com/PostView.naver?blogId=soojin_2604&logNo=222423840595&parentCategoryNo=&categoryNo=&viewDate=&isShowPopularPosts=false&from=postView)
