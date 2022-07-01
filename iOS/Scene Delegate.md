# 🏠   [Go Main](https://github.com/Raccoon97/Swift/blob/main/README.md)   🏠
- [Scene Delegate](https://github.com/Raccoon97/Swift/blob/main/iOS/Scene%20Delegate.md#scene-delegate)
- [iOS12 까지의 App Delegate](https://github.com/Raccoon97/Swift/blob/main/iOS/Scene%20Delegate.md#ios12-%EA%B9%8C%EC%A7%80%EC%9D%98-app-delegate)
- [iOS13 이후로 바뀐 App Delegate](https://github.com/Raccoon97/Swift/blob/main/iOS/Scene%20Delegate.md#ios13-%EC%9D%B4%ED%9B%84%EB%A1%9C-%EB%B0%94%EB%80%90-app-delegate)
- [Scene 이란?](https://github.com/Raccoon97/Swift/blob/main/iOS/Scene%20Delegate.md#scene-%EC%9D%B4%EB%9E%80)
- [Scene Delegate 의 메소드 호출](https://github.com/Raccoon97/Swift/blob/main/iOS/Scene%20Delegate.md#scene-delegate-%EC%9D%98-%EB%A9%94%EC%86%8C%EB%93%9C-%ED%98%B8%EC%B6%9C)
-[심화 - iOS 에서의 Scene](https://github.com/Raccoon97/Swift/blob/main/iOS/Scene%20Delegate.md#%EC%8B%AC%ED%99%94---ios-%EC%97%90%EC%84%9C%EC%9D%98-scene)

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
- 하나의 앱에서 여러 개의 Scene 을 가질 수 있게 되었다. 
- 과연 iPhone 을 사용할 때에도 위의 명제가 참인지 확인해보도록 하자.



<br>

<br>

<br>

# 참조
- [https://ios-development.tistory.com/53](Jake님)
- [https://sueaty.tistory.com/134](Sueaty님)
- [https://velog.io/@dev-lena/iOS-AppDelegate%EC%99%80-SceneDelegate](Lena)
