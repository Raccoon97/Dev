# 🏠   [Go Main](https://github.com/Raccoon97/Swift/blob/main/README.md)   🏠
- []()


<br><br><br>

# Scene Delegate
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

## Sub
### TinySub


<p aling="center"> Image Center
</p>

# 참조
- []()
