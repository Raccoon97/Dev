# 🏠   [Go Main](https://github.com/Raccoon97/Swift/blob/main/README.md)   🏠
- [Scene Delegate](https://github.com/Raccoon97/Swift/blob/main/iOS/Scene%20Delegate.md#scene-delegate)
- [iOS12 까지의 App Delegate](https://github.com/Raccoon97/Swift/blob/main/iOS/Scene%20Delegate.md#ios12-%EA%B9%8C%EC%A7%80%EC%9D%98-app-delegate)
- [iOS13 이후로 바뀐 App Delegate](https://github.com/Raccoon97/Swift/blob/main/iOS/Scene%20Delegate.md#ios13-%EC%9D%B4%ED%9B%84%EB%A1%9C-%EB%B0%94%EB%80%90-app-delegate)
- [Scene 이란?](https://github.com/Raccoon97/Swift/blob/main/iOS/Scene%20Delegate.md#scene-%EC%9D%B4%EB%9E%80)
- [Scene Delegate 의 메소드 호출](https://github.com/Raccoon97/Swift/blob/main/iOS/Scene%20Delegate.md#scene-delegate-%EC%9D%98-%EB%A9%94%EC%86%8C%EB%93%9C-%ED%98%B8%EC%B6%9C)
- [심화 - iOS 에서의 Scene](https://github.com/Raccoon97/Swift/blob/main/iOS/Scene%20Delegate.md#%EC%8B%AC%ED%99%94---ios-%EC%97%90%EC%84%9C%EC%9D%98-scene)
  - [SceneDelegate 의 출현 배경]()
  - [명제 확인]()
  - ㅑㅖ
  - [명제 확인]I

<br><br><br>

# Scene Delegate
- 화면에 무엇( Window/ Scene )을 보여줄지 관리하는 역할을 한다.

<br>

## iOS12 까지의 App Delegate
- 하나의 App 에 하나의 Window 이다.

<br>

![image](https://user-images.githubusercontent.com/101554627/175017828-1a18ddab-1c1c-4804-9baf-72127715745c.png)

## iOS13 이후로 바뀐 App Delegate
- Window 의 개념이 Scene 으로 대체되고 하나의 App 에서 여러 개의 Scene 을 가질 수 있게 되었다.

<br>

![image](https://user-images.githubusercontent.com/101554627/175017838-36ca3dfc-e158-4248-a4d6-9dcc902e2181.png)
- 아래 예시와 같이 하나의 메모장 App 에서 2개의 Scene 을 동시에 띄울 수 있다.

<br>

![image](https://user-images.githubusercontent.com/101554627/175018913-8ba00d8a-0d21-41aa-bf81-b6bec1437e1f.png)

- AppDelegate 의 역할 중 UI 의 상태를 알 수 있는 UILifeCycle 에 대한 부분을 SceneDelegate 가 하게 되었다.

<br>

![image](https://user-images.githubusercontent.com/101554627/175018354-c886ccf0-f66c-438a-be3f-81b08f3e8472.png)
- AppDelegate 에 Session LifeCycle 에 대한 역할이 추가되었다.
- Scene Session 이 생성되거나 삭제될 때 AppDelegate 에 알리는 두 메소드가 추가되었으며 App 에서 생성한 모든 Scene 의 정보를 관리한다.
<br>

![image](https://user-images.githubusercontent.com/101554627/175018791-74f86477-1706-4dd0-a055-17ff4bfed4dd.png)


## Scene 이란?
- UIKit 는 UIWindowScene 객체를 사용하는 App UI 의 각 인스턴스를 관리한다.
- Scene 에는 UI 의 하나의 인스턴스를 나타내는 Windows 와 ViewControllers 가 들어있다.
- 각 Scene 에 해당하는 UIWindowSceneDelegate 객체를 가지고 있으며 이 객체는 UIKit 과 App 간의 상호 작용을 조정하는 데 사용된다.
- Scene 들은 같은 메모리와 App 프로세스 공간을 공유하면서 서로 동시에 실행된다.
- 하나의 App 은 여러 Scene 과 SceneDelegate 객체를 동시에 활성화할 수 있다.

<br>

## Scene Delegate 의 메소드 호출

<br>

### scene(_ : willConnectTo: options: )
```swift
func scene(_ scene: UIScene, 
           willConnectTo session: UISceneSession, 
           options connectionOptions: UIScene.ConnectionOptions) {
  guard let _ = (scene as? UIWindowScene) else { return }
}
// 제일 처음으로 호출되는 메소드로 첫 Content View, 새로운 UIWindow 를 생성하고 Window 의 RootViewController 를 설정한다.
// 이 때의 Window 는 사용자가 보는 Window 가 아닌 App 이 동작하는 ViewPort 이다.
// 첫 View 를 만들 때 쓰이지만 과거에 Disconnected 된 UI 를 되돌릴 때 사용하기도 한다.
```

<br>

### sceneWillEnterForeground(_ :)
```swift
func sceneWillEnterForeground(_ scene: UIScene) {
}
// 첫 View 가 생성되면 sceneWillEnterForeground 가 호출된다.
// Background -> Foreground 인 경우와 최초 Active 상태가 되었을 때 호출된다.
```

<br>

### sceneDidBecomeActive(_ :)
```swift
func sceneDidBecomeActive(_ scene: UIScene) {
}
// Scene 이 설정되고 화면에 보여지면서 사용 준비가 끝난 상태이다.
// Inactive -> Active 상태에서 호출된다.
```

<br>

### sceneWillResignActive(_ :)
```swift
func sceneWillResignActive(_ scene: UIScene) {
}
// Active 한 상태에서 Inactive 상태로 빠질 때 호출된다.
// App 사용 중 전화가 오는 것 처럼 임시 Interruption 때문에 호출될 수 있다.
```

<br>

### sceneDidEnterBackground(_ :)
```swift
func sceneDidEnterBackground(_ scene: UIScene) {
}
// Scene 이 Foreground 에서 Background 로 전환될 때 호출된다.
// 다시 Foreground 로 돌아올 때 복원될 수 있게 상태 정보를 저장하거나, 데이터를 저장, 공유 자원을 반환하는 일을 한다.
```

<br>

### sceneDidDisconnect(_ :)
```swift
func sceneDidDisconnect(_ scene: UIScene) {
}
// Scene 이 Background 가 되었을 때 시스템이 자원을 확보하기 위해 Disconnect 할 수 있다 --> Suspended
// Scene 이 해당 메소드로 전달되면 Session 이 끊어지게되며, Disconnect 는 App 의 종료와는 다르다
```

<br>

<br>

# 심화 - iOS 에서의 Scene
- SceneDelegate 는 왜 생겼는지 알아보자.
- 과연 iPhone 을 사용할 때에도 위의 명제가 참인지 확인해보도록 하자.
- 하나의 프로젝트를 사용해서 iPad Pro 3rd, iPhone 12 Pro 두 가지 기기에 대해서 테스트를 진행해보았다.

<br>

## SceneDelegate 의 출현 배경
- iOS 12 까지는 AppDelegate 가 App 에 이벤트를 알리거나 UI 상태를 알리는 역할을 한다.
  - App 들이 하나의 프로세스와 하나의 UI 인스턴스를 갖고 있기 때문에 AppDelegate 하나로 충분하다.
- iOS 13 부터는 하나의 프로세스가 여러 UI 인스턴스를 가질 수 있다.
  - 프로세스 이벤트와 Lift Cycle 에 경우 그대로 AppDelegate 가 담당한다.
- _1:1 인 AppDelegate 말고 1:N 이 되는, UI LifeCycle 관리가 필요하기 때문에 SceneDelegate 가 출현하게 되었다._

<br>
<br>

## 
- Info.plist 의 Enable Multiple Windows 를 YES 로 변경시킨다.
- AppDelegate 에서 multipleScene 여부와 기기 정보를 확인한다.
- SceneDelegate 에서 Scene 을 생성할 때 마다 출력되게 한다.

<br>

## iPad
- 확인 결과 
  - supportsMultipleScene = true
  - Enable Multiple Windows = YES
  - Scene 을 새로 만들 때 마다 SceneDelegate 에서 출력이 된다.

![스크린샷 2022-07-01 오후 8 02 42](https://user-images.githubusercontent.com/101554627/176884985-d323acf4-d20c-43e8-aa18-e20efd92a6cc.png)


<br><br>

## iPhone
- 확인 결과 
  - supportsMultipleScene = false
  - Enable Multiple Windows = YES
  - Scene 을 하나 이상 만들 수 없다.

![스크린샷 2022-07-01 오후 8 05 09](https://user-images.githubusercontent.com/101554627/176884995-35fb4f49-02b8-4cbd-ae80-8098f45a8389.png)

<br><br>

## 결과
- 프로젝트 설정 상에서 Enable Multiple Windows 는 활성화가 가능하며 iPhone, iPad 둘 다 적용된다.
- 하지만 실제 App 구동 시 AppDelegate 에서 supportsMultipleScene 은 iPhone = false, iPad = true 로 갈리게 된다.
- iOS 13 이후로 하나의 앱이 여러 개의 Scene 을 갖을 수 있다고 했지만, 실제로 iPadOS 만 가능하다.
- 현재 출시된 iPhone 용 Split View App 들은 Web Browser 기반으로 하나의 페이지를 나누어 각각 App 을 사용할 수 있게 해준다.
  - 실제 기기에서 구동되는 App 이 아니며, Web 으로 접근이 가능한 App 들만 가능하다.


<br>

<br>

<br>

# 참조
- [Jake님](https://ios-development.tistory.com/53)
- [Sueaty님](https://sueaty.tistory.com/134)
- [Lena님](https://velog.io/@dev-lena/iOS-AppDelegate%EC%99%80-SceneDelegate)
- [iPadOS Tutorial](https://www.raywenderlich.com/5814609-adopting-scenes-in-ipados)
