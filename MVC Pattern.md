# 🏠   [Go Main](https://github.com/Raccoon97/Swift/blob/main/README.md)   🏠
- [MVC Pattern](https://github.com/Raccoon97/Swift/blob/main/MVC%20Pattern.md#mvc-pattern)
- [M - Model](https://github.com/Raccoon97/Swift/blob/main/MVC%20Pattern.md#m---model)
- [V - View](https://github.com/Raccoon97/Swift/blob/main/MVC%20Pattern.md#v---view)
- [C - Controller](https://github.com/Raccoon97/Swift/blob/main/MVC%20Pattern.md#c---controller)
- [MVC Pattern 의 예시](https://github.com/Raccoon97/Swift/blob/main/MVC%20Pattern.md#mvc-pattern-%EC%9D%98-%EC%98%88%EC%8B%9C)
- [MVC Pattern 의 장/단점](https://github.com/Raccoon97/Swift/blob/main/MVC%20Pattern.md#mvc-pattern-%EC%9D%98-%EC%9E%A5%EB%8B%A8%EC%A0%90)

<br><br><br>

# MVC Pattern
- 소프트웨어 디자인 패턴 중 하나이다.
- MVC Cocoa Pattern 이다.
- Application 을 3 개의 영역으로 분할하고 각 영역에 고유한 역할을 부여하는 방식이다.
- MVC Pattern 을 도입하면 비즈니스 로직 영역과 UI 영역이 분리되므로 서로 영향을 주지 않고 유지보수가 가능하다.
>- 업무에 필요한 데이터 처리를 수행하는 로직
- UIKit 을 사용하는 앱의 구조는 MVC 디자인 패턴을 기반으로 한다.

<br>

<p align="center">
  <img src="https://user-images.githubusercontent.com/101554627/167997796-34cb28da-ded7-4f4a-9334-ce0518c884a3.png" alt="center" />
</p>

<br><br><br>

# M - Model
- View 접근 : 불가
- Controller 접근 : Notification & KVO 방식을 통해 모델의 변화를 Controller 에게 알릴 수 있다.
- Application 의 데이터와 비즈니스 로직을 관리한다.
>- 네트워크 코드
>- 파싱 코드
>- 관리자 및 추상화 계층/클래스
>- 데이터 소스 및 delegates
>- 상수

<br><br><br>

# V - View
- Model 접근 : 불가
- Controller 접근 : target - action 구조로 사용자의 행위에 따라 필요한 함수를 호출할 수 있으며, 구조적으로 미리 정해진 방식으로 행위에 대한 요청(delegate), 데이터에 대한 요청(data-source) 을 할 수 있다.
- 데이터를 시각적으로 표현한다.
- 비즈니스 로직이 포함되어있지 않기 때문에 재사용이 가능한 경우가 많다.
- View 레이어의 검사
>- Model 레이어와 상호작용 하는지?
>- 비즈니스 로직이 포함되어 있는지?
>- UI와 관련이 없는 작업을 하려고 하는지?
- 위 세가지 질문 중 하나라도 긍정이면 리펙토링을 해야한다.

<br><br><br>

# C - Controller
- Model 접근 : 가능
- View 접근 : 가능
- Delegate Pattern 을 통해 View 와 Model 사이를 중재한다.
- View 와 Model 사이에서 적절하게 데이터를 이동하며 브릿지 역할을 한다.
- Application 에서 가장 재사용이 적은 부분이다.
- 다음과 같은 상황을 결정하는 레이어이다
>- 가장 먼저 액세스 해야 하는 것?
>- 얼마나 자주 앱을 새로고쳐야 하는지?
>- 앱이 백그라운드로 이동하면 무엇을 정리해야 하는지?
>- 사용자가 셀을 탭했을 때 무엇을 해야 하는지?

<br><br><br>

# MVC Pattern 의 예시
- 기존 코드
```swift
// ViewController.swift

import UIKit

class ViewController: UIViewController {
  @IBOutlet weak var message: UILabel!
  @IBOutlet weak var emailTxtField: UITextField!
  @IBOutlet weak var passwdTxtField: UITextField!
  
  var user_Email: String
  var user_Passwd: String
  
  override func viewDidLoad() {
    super.viewDidLoad()
    message.isHidden = true
  }
  
  @IBAction func didPressLogin(_ sender: UIButton) {
    guard let email = emailTxtField.text else {return}
    guard let passwd = passwdTxtField.text else {return}
    
    user_Email = email
    user_Passwd = passwd
    
    if user_Email == "test@gmail.com" && user_Passwd == "12345" {
      message.text = "로그인 성공"
      message.text.isHidden = false
    }
  }
}
```

- MVC Pattern 으로 변경한 코드
```swift
// ViewController.swift --> View, Controller

import UIKit

// Controller
class ViewController: UIViewController {

  // View
  @IBOutlet weak var message: UILabel!
  @IBOutlet weak var emailTxtField: UITextField!
  @IBOutlet weak var passwdTxtField: UITextField!
  
  var user: User!
  
  override func viewDidLoad() {
    super.viewDidLoad()
    message.isHidden = true
  }
  
  @IBAction func didPressLogin(_ sender: UIButton) {
    guard let email = emailTxtField.text else {return}
    guard let passwd = passwdTxtField.text else {return}
    
    user = User(email: email, passwd: passwd
    
    if user.email == "test@gmail.com" && user.passwd == "12345" {
      message.text = "로그인 성공"
      message.text.isHidden = false
    }
  }
}
```
```swift
// User.swift --> Model
import Foundation

struct User {
  var email: String
  var passwd: String
}
```

<br><br><br>

# MVC Pattern 의 장/단점
### 장점
- 다른 Pattern 에 비해 코드량이 많지 않다.
- Apple 에서 기본적으로 지원하는 Pattern 이다.
- 개발 속도가 빠르기 때문에 아키텍처가 중요하지 않을 때, 규모가 작은 프로젝트에서 사용하기 좋다.

### 단점
- View 와 Controller 가 너무 밀접하게 연결되어 있다.
- Controller 가 View 의 생명주기까지 관랗기 때문에 View 와 Controller 를 분리하기 어렵다.
>- 재사용성이 떨어지고 유닛 테스트를 진행하기 어렵다.
- 대부분의 코드가 Controller 에 밀집될 수 있는데, 그런 이유로 MVC를 Massive View Controller 라고 부르기도 한다.
