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

# UINavigationController 의 사용

<br>

## StoryBoard 구현
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

- Navigation Controller 를 적용해서 Root ViewController 와 Child ViewController 를 표시하는 결과

<p align="center">
<img width="300" alt="ezgif-2-0dad8dc71a" src="https://user-images.githubusercontent.com/101554627/176648998-6e19f16a-b0de-4127-8ce6-37a85892149e.gif">
</p>


<br><br>

## Code 구현

```swift
import UIKit


// 버튼의 3가지 위치를 미리 지정.
let statBtnRect = CGRect(x: 50, y: 100, width: 300, height: 52)
let commonBtnRect = CGRect(x: 100, y: 100, width: 200, height: 52)
let dimissBtnRect = CGRect(x: 100, y: 162, width: 200, height: 52)

// 버튼을 만들고 View 에 띄우는 함수
// 3 개의 뷰컨트롤러에 겹치는 부분이 많아 코드가 길어져서 상단으로 빼놓았다.
func makeButton(
                _ viewSelf: UIViewController ,  // viewSelf - 각 ViewController 인스턴스를 사용하기 위함
                _ view_: UIView,                // view     - 각 ViewController 의 View 를 사용하기 위함
                _ btn: UIButton,                // btn      - 버튼의 위치와 모양을 지정해서 View 에 띄우기 위함
                _ title: String,                // title    - 버튼의 Title 을 다양하게 사용하기 위함
                _ function: Selector,           // function - 코드로 구현함에 따라 objc 함수를 작성하고 사용하기 위함
                _ rect: CGRect                  // rect     - 버튼의 위치를 다양하게 지정하기 위함
                ) {
    
    // 버튼의 Title 을 지정한다.
    btn.setTitle(title, for: .normal)
    
    // 버튼을 View 에 추가한다.
    view_.addSubview(btn)
    
    // 버튼의 배경색을 지정한다.
    btn.backgroundColor = .clear
    
    // 버튼의 Title 색깔을 지정한다.
    btn.setTitleColor(.systemBlue, for: .normal)
    
    // 버튼의 위치를 지정한다.
    btn.frame = rect
    
    // 버튼이 호출되는 곳과 어떤 작업을, 어떤 이벤트가 발생되었을 때 하게 되는지 지정한다.
    btn.addTarget(viewSelf, action: function, for: .touchUpInside)
}


// @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

// View 시작지점, 버튼을 눌러 네비게이션 컨트롤러를 사용한다.
class ViewController: UIViewController {
    
    // 탭하면 네비게이션 컨트롤러를 사용하게되는 버튼
    private let button = UIButton()
    
    override func viewDidLoad() {
        super.viewDidLoad()

        // 버튼을 만들어 View 에 띄워준다.
        makeButton(self, view, button, "네비게이션 컨트롤러 사용하기", #selector(didTapButton_ToNav), statBtnRect)
    }
        
    // 버튼을 눌렀을 때 실행되는 함수
    @objc private func didTapButton_ToNav() {
        
        // Root 뷰컨트롤러는 RootViewController 이다.
        let rootVC = RootViewController()
        
        // 지정한 rootVC 를 갖고 UINavigationController 를 선언해준다.
        let navVC = UINavigationController(rootViewController: rootVC)
        
        // FullScreen 스타일로 Modal 하겠다고 미리 설정해준다.
        navVC.modalPresentationStyle = .fullScreen
        
        // UINavigationController 를 갖는 Root 뷰컨트롤러를 보여준다.
        present(navVC, animated: true)
    }
    

}


// @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

// Root 뷰컨트롤러, 네비게이션 컨트롤러의 최상위 뷰
class RootViewController: UIViewController {
    
    // 다음 뷰컨트롤러를 Push 할 버튼과 네비게이션 컨트롤러를 끝내는 버튼
    private let button_PushView = UIButton()
    private let button_Dimiss = UIButton()
    
    override func viewDidLoad() {
        super.viewDidLoad()

        // 배경이 없을 경우 View 가 올라오지 않음, Title 은 상관 없음
        view.backgroundColor = .white
        title = "네비게이션 컨트롤러"
        
        // 버튼 2개를 만들어 View 에 띄워준다. Push, Dismiss
        makeButton(self, view, button_PushView, "다른 뷰컨트롤러 Push 하기", #selector(didTapButton_PushView), commonBtnRect)
        makeButton(self, view, button_Dimiss, "돌아가기", #selector(didTapButton_Dismiss), dimissBtnRect)
    }
    
    // 다른 뷰컨트롤러를 Push 하는 함수
    @objc private func didTapButton_PushView() {
        let vc = SecondViewController()
        navigationController?.pushViewController(vc, animated: true)
    }
    
    // 네비게이션 컨트롤러 시작 전으로 돌아가는 함수
    @objc private func didTapButton_Dismiss(){
        dismiss(animated: true)
    }
    
}


// @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

// 두 번째 뷰컨트롤러
class SecondViewController: UIViewController {
    
    // 현재 뷰컨트롤러를 Pop 할 버튼
    private let button = UIButton()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // 배경이 없을 경우 View 가 올라오지 않음, Title 은 상관 없음
        view.backgroundColor = .white
        title = "2번째 장"
        
        // 버튼을 만들어 View 에 띄워준다. Pop
        makeButton(self, view, button, "현재 뷰컨트롤러 Pop하기", #selector(didTapButton_PopView), commonBtnRect)
    }
    
    // 현재 뷰컨트롤러를 Pop 하는 함수
    @objc private func didTapButton_PopView() {
        navigationController?.popViewController(animated: true)
    }
}


```

- 위 코드를 실행하게 되면 아래와 같은 결과를 얻을 수 있다.
- 불필요한 코드를 제외하기 위해 필요한 버튼과 라벨만 넣어서 초라하다..

<p align="center">
<img width="300" alt="코드구현gif" src="https://user-images.githubusercontent.com/101554627/176740506-da22913e-5311-45a0-896d-c4f675846e95.gif">
</p>


<br><br><br>


# 참조
- [Apple Developer Documentation](https://developer.apple.com/documentation/uikit/uinavigationcontroller)
- [iseeu95님](https://velog.io/@iseeu95/UINavigationController-%EC%97%90-%EB%8C%80%ED%95%B4)
- [통스님](https://tong94.tistory.com/26)
