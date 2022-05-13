# MVVM Pattern
- 소프트웨어 디자인 패턴 중 하나이다.
- MVC  Pattern 에서 Controller 를 빼고 ViewModel 을 추가한 Pattern 이다.
  - <p><h6>MVC Pattern 에서는 다양한 로직을 Controller 가 처리하기 때문에 Massive 해지는 문제가 있는데, MVVM Pattern 에서는 View 에 업데이트할 데이터를 View Model 에서 처리함으로써 Controller 가 복잡해지는 것을 줄여준다.</h6></p>

- MVVM 에서는 View 가 ViewModel 을 소유하고, ViewModel 이 Model 을 소유하는 방식이다.
- MVVM 의 핵심은 Data Binding 이다. 
  - <p><h6>Data Binding 은 데이터를 제공측과 그 데이터를 사용측을 연결시켜 동기화하는 방식이다.<h6></p>
- MVC 기반의 UIKit 과 달리 SwiftUI 는 MVVM 패턴을 기반으로 한다. 
- SwiftUI 는 Reactive Programming 패러다임을 취하고 있다.
  - <p><h6>변화에 따라 데이터를 전달하고, 그에 반응해 적절한 이벤트를 실행하는 반응형 프로그래밍</h6></p>

<br>

<p align="center">
  <img src="https://user-images.githubusercontent.com/101554627/167997945-40ba5e86-b4f2-4a15-ae18-ab11b2897cb6.png" alt="center" />
</p>

<br><br><br>

# M - Model
- Model 은 ViewModel 에 의해 작동되고 Model 이 작업을 마치면 ViewModel 에게 결과를 알려준다.
- Application 의 데이터 모델, 데이터 접근 레이어, 비즈니스 로직을 관리한다.


<br><br><br>

# V - View
- 사용자 이벤트를 수신하고, 데이터를 시각적으로 표현한다.
- View 와 Model 은 상호작용이 불가하고 ViewModel 에 의해 동작된다.

<br><br><br>

# VM - ViewModel
- 주요 로직을 담당한다.
- View 에서 수신한 이벤트를 처리한 뒤 Model 을 업데이트 하고, 그 결과를 받아 View 에 다시 전달해서 UI 를 업데이트 한다.
- 객체를 쉽게 관리할 수 있는 장점이 있다.

<br><br><br>

# Data Binding
- Data Binding 은 Model 의 UI 요소 간의 싱크를 맞춰주는 것이다.
- View 와 로직이 분리되어 있어도 한 쪽이 바뀌면 다른 쪽도 업데이트가 이루어져 데이터의 일관성을 유지할 수 있다.
- iOS 에서 데이터 바인딩을 하는 방법
  - <p><h6>KVO</h6></p>
  - <p><h6>Delegation</h6></p>
  - <p><h6>Functional Reactive Programming</h6></p>
  - <p><h6>Property Observer</h6></p>

<br><br><br>

# MVVM 예시
- 기존 코드
```swift
class ViewController: UIViewController {
    //Outlets
    @IBOutlet weak var messageLabel: UILabel!
    @IBOutlet weak var userNameField: UITextField!
    @IBOutlet weak var passwordField: UITextField!
   
    var name: String
    var email: String
    var userName: String { return user.name }
    var email: String { return user.email }
    
    typealias authenticationLoginCallback = (_ status: Bool, _ message: String) -> Void //callback 
    
    var callback: authenticationLoginCallback?

    override func viewDidLoad() {
        super.viewDidLoad()
        self.messageLabel.isHidden = true
        // Do any additional setup after loading the view.
    }
    
    @objc func loginUser() {
        self.messageLabel.isHidden = true
        guard let userName = self.userNameField.text else { return }
        guard let password = self.passwordField.text else { return }
        authenticationUser(userName, password)//로그인 유효성 검사
        
      //callback에 따른 UI변환 
       loginCompletion { [weak self] status, message in
            guard let self = self else { return }
            if status {
                self.messageLabel.text = "login success"
                self.messageLabel.isHidden = false
            } else {
                self.messageLabel.text = message
                self.messageLabel.isHidden = false
            }
        }
    }
    
        //로그인 유효성 검사 
    func authenticationUser(_ email: String, _ password: String) {
        DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + 0.1) {
            if self.userName.count != 0 {
                if password.count != 0 {
                    self.verifyUser(self.userName, password)
                }else {
                    self.callback?(false, "password error")
                }
            }else {
                self.callback?(false, "user error")
            }
        }
    }
    //유저 확인 
    fileprivate func verifyUser(_ email: String, _ password: String) {
        if userName == "test" && password == "1234" {
            user = User(name: userName, email: "\(userName)@gmail.com")
            self.callback?(true, "success")
        }else {
            self.callback?(false, "Please enter valid source")
        }
    }
    
  //로그인 완료시 callback 메소드 
    func loginCompletion(callBack: @escaping authenticationLoginCallback) {
        self.callback = callBack
    }
}
```
- MVVM Pattern 으로 변경한 코드
```swift
//Model

struct User {
  var name: String
  var email: String
}
```
```swift
// View

class ViewController: UIViewController {
    //Outlets
    @IBOutlet weak var messageLabel: UILabel!
    @IBOutlet weak var userNameField: UITextField!
    @IBOutlet weak var passwordField: UITextField!
   
  var viewModel = ViewModel()//ViewModel

    override func viewDidLoad() {
        super.viewDidLoad()
        self.messageLabel.isHidden = true
        // Do any additional setup after loading the view.
    }
    
    @objc func loginUser() {
        self.messageLabel.isHidden = true
        guard let userName = self.userNameField.text else { return }
        guard let password = self.passwordField.text else { return }
        viewModel.authenticationUser(userName, password)//로그인 유효성 검사
        
      //callback에 따른 UI변환 
        viewModel.loginCompletion { [weak self] status, message in
            guard let self = self else { return }
            if status {
                self.messageLabel.text = "login success"
                self.messageLabel.isHidden = false
            } else {
                self.messageLabel.text = message
                self.messageLabel.isHidden = false
            }
        }
    }
}
```
```swift
//  ViewModel


class ViewModel: NSObject {
    var user: User! //Model 
    var userName: String { return user.name }
    var email: String { return user.email }
    
    typealias authenticationLoginCallback = (_ status: Bool, _ message: String) -> Void //callback 
    
    var callback: authenticationLoginCallback?
    
    //로그인 유효성 검사 
    func authenticationUser(_ email: String, _ password: String) {
        DispatchQueue.main.asyncAfter(deadline: DispatchTime.now() + 0.1) {
            if self.userName.count != 0 {
                if password.count != 0 {
                    self.verifyUser(self.userName, password)
                }else {
                    self.callback?(false, "password error")
                }
            }else {
                self.callback?(false, "user error")
            }
        }
    }
    //유저 확인 
    fileprivate func verifyUser(_ email: String, _ password: String) {
        if userName == "test" && password == "1234" {
            user = User(name: userName, email: "\(userName)@gmail.com")
            self.callback?(true, "success")
        }else {
            self.callback?(false, "Please enter valid source")
        }
    }
    
  //로그인 완료시 callback 메소드 
    func loginCompletion(callBack: @escaping authenticationLoginCallback) {
        self.callback = callBack
    }
    
}
```

<br><br><br>

# MVVM 의 장/단점
### 장점
- View 와 Model 이 서로 전혀 연관이 없기에 독립성을 유지할 수 있다.
- 독립성이 유지되어 효율적인 유닛테스트가 가능하다.
- ViewModel 에서는 UIKit 관련 코드가 없고 Controller 와의 의존성도 없기 때문에 유닛테스트 하기가 좋다.
- View 와 ViewModel 의 관계는 N:1 관계이다.

### 단점
- 초보자의 경우 MVVM 을 구현하기 어렵다.
- 간단한 UI 에서 MVVM 은 과하다.
- 데이터 바인딩이 필수이다.
- 복잡해질수록 Controller 처럼 ViewModel 이 Massive 해진다.
- 큰 Application 의 경우 데이터 바인딩이 복잡하므로 디버깅이 어렵다. 

<br><br><br>

# 참조
- [륳님](https://velog.io/@ryuhyewon/MVVM-%EA%B0%9C%EB%85%90%EA%B3%BC-%EC%9E%A5%EB%8B%A8%EC%A0%90)
- [GomMinjae님](https://velog.io/@gomminjae/Swift-MVVM)
- [yoonbumtae님](http://yoonbumtae.com/?p=4215)
- [sh9404님](https://lsh424.tistory.com/68)
