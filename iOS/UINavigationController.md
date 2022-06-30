# 🏠   [Go Main](https://github.com/Raccoon97/Swift/blob/main/README.md)   🏠
- []()


<br><br><br>

# UINavigationController
```swift
@MainActor class UINavigationController : UIViewController
```

- Navigation 인터페이스에서 1개 이상의 하위 View Controller 를 관리하는 Container View Controller 이다.
- Stack 기반이며, 한 번에 하나의 View Controller 만 보여지고 Push/ Pop 을 통해 보여질 View Controller 를 결정한다.
- 첫 번째 View Controller 는 Root View Controller 이며 Stack 의 맨 아래 항목을 나타낸다.
- 마지막 View Controller 는 Stack 의 맨 위 항목이며, 현재 표시된 View Controller 이다.

<br>

![image](https://user-images.githubusercontent.com/101554627/176487930-094feaca-9a90-45d7-a556-b8659c49073e.png)

<img width="960" alt="프레젠테이션1" src="https://user-images.githubusercontent.com/101554627/176492414-bd3bc7ca-fc33-473a-a7bf-6a92cc8f4aa8.png">

<br><br>

## UINavigationViewController 에서 관리하는 개체

![image](https://user-images.githubusercontent.com/101554627/176494081-c5fdcaaf-fe17-4e39-a964-cf394613209b.png)

<br>

- ViewControllers
  - UINavigationController 는 여러 개의 View Controller 를 관리할 수 있는 Contrainer View Controller 이다.
  - Navigation Stack 에 쌓인 View Controller 들을 배열 형태로 갖으며, 해당 배열은 push, pop 형태로 관리된다.

<br>

- navigationBar < UINavigationBar >
  - 앱을 사용함에 있어 상단에 타이틀, 뒤로가기, 설정 등 UI 요소들의 영역을 Navigation Bar 라고 한다.
  - UINavigationController 를 사용하면 따로 UI 를 추가할 필요 없이 사용할 수 있다.

<br>

- toolbar < UIToolbar >
  - 주로 앱 하단에 위치한 여러 도구의 모음이다.
  - 기본적으로 UINavigationController 에서는 숨김처리( isToolbarHidden = True ) 되어있지만, 숨김을 해제하고 해당 영역 설정이 가능하다.

<br>

- delegate < Custom Delegate Object >
  - UITableViewDelegate 처럼 UINavigationController 에도 특정 Event 에서 사용할 수 있는 delegate 가 선언되어 있다.
  - 특정 ViewController 를 보여주고 사라지게 하거나, 커스텀 애니메이션을 제공한다. 
  - UINavigationControllerDelegate 프로토콜을 준수해야 한다.

<br><br>

## UINavigationController 의 사용
- StoryBoard 에 Root ViewController 와 Child ViewController 가 있다고 가정한다.
- Root ViewController 의 Go Child 버튼을 탭하면 Child ViewController 가 보이게 된다.
  - 이 때, Go Child 버튼의 Segue 는 Push 로 해준다.

<br>

<p align="center">
<img width="600" alt="스크린샷 2022-06-30 오후 6 41 14" src="https://user-images.githubusercontent.com/101554627/176646159-d9f44469-0ada-49d3-bd40-7cef0814252f.png">
</p>

<br>

- Root ViewController 를 선택한 뒤 Editor -> Embed In -> Navigation Controller 를 선택한다.

<br>

<p align="center">
<img width="600" alt="스크린샷 2022-06-30 오후 6 43 35" src="https://user-images.githubusercontent.com/101554627/176646347-2eed793c-cfab-4ca1-997e-2fba5f104cbb.png">
</p>

<br>

- 정상적으로 Navigation Controller 가 추가되었고 Child ViewController 에서는 < back 표시를 확인할 수 있다.

<br>

<p align="center">
<img width="946" alt="스크린샷 2022-06-30 오후 6 47 40" src="https://user-images.githubusercontent.com/101554627/176647578-5df3ede1-348b-48ed-9b8f-e9124a2454c0.png">
</p>

<br>



## Sub





# 참조
- [Apple Developer Documentation](https://developer.apple.com/documentation/uikit/uinavigationcontroller)
- []()
