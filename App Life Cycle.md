# 🏠   [Go Main]()   🏠
- []()

<br><br><br>

# App Life Cycle
- App 의 실행/ 종료 및 App 이 Foreground/ Background 상태에 있을 때, 시스템이 발생시키는 Event 에 의해 App 의 상태가 전환되는 일련의 과정.
  - Background 상태 - App 이 화면에 보이지 않지만 실행되고 있는 상태
  - Foreground 상태 - App 이 화면에 보이면서 실행되고 있는 상태

<br><br>

## App State
- App 상태는 총 5가지로 구분된다.
<img width="569" alt="스크린샷 2022-06-22 오후 12 56 05" src="https://user-images.githubusercontent.com/101554627/174940201-6a6831e1-ad13-4be3-813b-1628254d8c98.png">

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
