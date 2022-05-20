
<br><br><br>

# Singleton Pattern
- 한 개의 클래스로 만드는 인스턴스는 단 한개여야만 한다는 규칙을 갖는다.
- 특정 용도로 객체를 하나만 생성하여, 공용으로 사용하기 위한 디자인 패턴이다.
- 애플리케이션 내 특정 클래스의 인스턴스가 하나만 존재하기 때문에 객체가 불필요하게 여러 개 만들어질 필요가 없는 경우에 사용한다.
- 환경설정, 네트워크 연결처리, 데이터 관리 등에 사용된다.
- 멀티 스레드 환경에서는 동시에 싱글톤 객체를 참조할 경우 원치 않는 결과를 가져올 수 있기에 위험성을 고려해야 한다.

<br><br><br>

# Singleton Pattern 의 예시

### iOS 에서 사용중인 Singleton
```swift
// 하드웨어 기반 디스플레이와 관련된 속성을 관리하는 클래스
let screen = UIScreen.main

// Key-Value 형태로 간단한 데이터를 저장하고 관리할 수 있는 인터페이스를 제공하는 데이터베이스 클래스
let userDefault = UserDefaults.standard

// iOS 에서 실행되는 중앙제어 어플리케이션 객체
let application = UIApplication.shared

// 애플리케이션 파일 시스템을 관리하는 클래스
let fileManager = FileManager.default

// 등록된 알람의 정보를 사용할 수 있게 해주는 클래스
let notification = NotificationCenter.default

// URL 세션을 관리하는 클래스
let urlSession = URLSession.shared
```

### Singlton Class 생성 방법
- static let 으로 인스턴스를 할당해주면 끝이다.
- 인스턴스가 추가로 생성되는 것을 방지하기 위해 init() 의 접근 제어자를 private 로 선언한다.
```swift
class SingletonClass {
  static let shared = SingletonClass()
  private init() {}
}
```
### Singleton 사용 예
- Application 의 정보를 저장하고 있는 AppInfo 클래스를 Singleton 으로 작성한 코드
```swift
class AppInfo {
  static let shared = AppInfo()
	private init() {}
 
	var mainInfo: [String : Any]? {
		guard let info = Bundle.main.infoDictionary else {
			return nil
		}
		return info
	}
 
	var name: String? {
		self.mainInfo?["CFBundleName"] as? String
	}
 
	var scheme: String? {
		guard let urlTypes = self.mainInfo?["CFBundleURLTypes"] as? [AnyObject],
			let urlTypeDictionary = urlTypes.first as? [String: AnyObject],
			let urlSchemes = urlTypeDictionary["CFBundleURLSchemes"] as? [AnyObject],
			let scheme = urlSchemes.first as? String else { return nil }
		return scheme
	}
 
	var version: String? {
		self.mainInfo?["CFBundleShortVersionString"] as? String
	}
}

let appInfo = AppInfo.shared
// appInfo 변수에 AppInfo 클래스의 shared 인스턴스를 가져온다.

if let appName = appInfo.name,
	let appScheme = appInfo.scheme,
	let appVersion = appInfo.version {
		print("appName: \(appName)")
		print("appScheme: \(appScheme)")
		print("appVersion: \(appVersion)")
}
```

<br><br><br>

# Singleton Pattern 의 장/단점
### 장점
- 인스턴스를 최초 1회만 생성하므로 메모리와 성능 측면에서 효율이 좋다.
- 클래스 간 데이터 공유가 쉽다.
- 인스턴스가 1개라는 것을 보증받는다. (Thread Safe)
>- Thread Safe --> 여러 스레드에서 어떤 객체에 대해 동시에 접근이 이루어져도 프로그램의 동작에 이상이 없는 것 

### 단점
- Singleton 인스턴스가 너무 많은 일을 하거나 많은 데이터를 공유시킬 경우 다른 클래스의 인스턴스들 간에 결합도가 높아져 개방-폐쇄 원칙을 위배하게 된다.
>- 수정과 테스트가 어려워지는 결과를 낳는다.
- 멀티스레드 환경에서 인스턴스가 2개 생성될 가능성이 존재하며 그 때에는 Thread Safe 하지 않는다는 위험성이 있다.
>- Singleton 내부의 객체의 데이터를 동기적으로 처리하지 않으면 꼬여버릴 가능성도 존재한다.
- 여기저기서 쉽게 접근할 수 있기 때문에 의존성을 만들어낸다.

<br><br><br>

# 참조
- [Apple Document](https://developer.apple.com/documentation/swift/cocoa_design_patterns/managing_a_shared_resource_using_a_singleton)
