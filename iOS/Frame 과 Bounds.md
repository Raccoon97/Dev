# 🏠   [Go Main](https://github.com/Raccoon97/Swift/blob/main/README.md)   🏠
- []()


<br><br><br>

# Frame
```swift
var frame: CGRect { get set }
```
- Super View 좌표계에서 View 의 위치와 크기를 나타낸다. < Super View 의 원점( 0, 0 ) 에서 얼마나 떨어져 있는지 >
  - Super View - 해당 View 의 윗 계층 View 를 말한다.
- View 의 위치나 크기를 설정할 때 사용한다.
- View 가 회전되었을 때 감쌀 수 있는 사각형이다.

<br>

<img width="1440" alt="스크린샷 2022-06-24 오후 8 47 40" src="https://user-images.githubusercontent.com/101554627/175528301-d64be4ff-c2de-4a08-9440-9e8dd7e7a8f4.png">

- View 3개를 만든 뒤 frame.origin 을 출력했을 때 다음과 같은 결과를 확인할 수 있다.
  - FirstView 는 RootView 이므로 ( 0.0, 0.0 )
  - SecondView 의 SuperView 는 FirestView 이므로 ( 53.0, 75.0 )
  - ThirdView 의 SuperView 는 SecondView 이므로 ( 34.0, 309.0 )
  
<br>

<img width="1440" alt="스크린샷 2022-06-24 오후 8 53 29" src="https://user-images.githubusercontent.com/101554627/175529061-62df48a6-f607-4385-b3f4-ed5dd3376d07.png">

- 또한 frame.size 를 출력했을 때 기 설정된 View 의 width, height 를 그대로 출력하는 것을 볼 수 있다.

<br>

<img width="1440" alt="스크린샷 2022-06-24 오후 9 00 42" src="https://user-images.githubusercontent.com/101554627/175530115-b4f81a36-6606-4ed0-a408-f3120b090b16.png">

- 하지만 View 가 회전하게 되면 origin 과 size 가 바뀌게 된다.
- frame 의 size 는 View 가 차지하는 영역을 모두 감싸는 사각형인데, 회전할 경우 차지하는 영역이 변화되기 때문이다.
- frame 의 size 가 변경되면 origin 값도 바뀔 수 있다.

>- secondeView --> secondView

<br><br><br>

# Bounds
```swift
var bounds: CGRect { get set }
```
- View 의 위치와 크기를 자신의 좌표계 안에서 나타낸다. 즉 최초 생성 시 자신의 원점을 ( 0.0, 0.0 ) 으로 초기화한다.
- View 내부에 그림을 그릴 때, transformation 후 View 의 크기를 알고싶을 때 등 내부적으로 변경하는 경우에 사용한다.

<br>

<img width="1440" alt="스크린샷 2022-06-24 오후 9 06 38" src="https://user-images.githubusercontent.com/101554627/175530917-717ff4aa-ba48-4d5a-bc52-2031e02732cc.png">

- 위와 같이 각 View 의 bounds.origin 을 출력해보았으나 모두 자기 자신의 원점을 ( 0.0, 0.0 ) 으로 초기화한다.

<br>

<img width="1440" alt="스크린샷 2022-06-24 오후 9 10 11" src="https://user-images.githubusercontent.com/101554627/175531409-f697ed13-cb25-4f10-83b6-af200641637d.png">

- bounds 의 size 또한 frame 의 size 와 동일하게 자기 자신의 width, height 를 반환한다.




