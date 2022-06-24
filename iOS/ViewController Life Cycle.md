# 🏠   [Go Main](https://github.com/Raccoon97/Swift/blob/main/README.md)   🏠
- []()


<br><br><br>

# ViewController Life Cycle
- 기기에 표시되는 화면의 Life Cycle 이다.

![image](https://user-images.githubusercontent.com/101554627/175507245-2834c849-e25c-4327-bac2-86f4c33c084f.png)

<br>

## loadView
- ViewController 가 View 를 만들고 메모리에 올리는 역할을 한다.
- View 와 ViewController 를 만들기 위해서 Interface Builder 를 사용했다면 이 메소드를 override 하지 말아야 한다. ??

<br>

## viewDidLoad
- View 의 Controller 가 메모리에 로드된 상태
- ViewController Life Cycle 에서 한번만 호출된다.
- 일반적으로 리소스를 초기화하거나 초기 화면을 구성하는 용도로 사용한다.
- 화면전환 시 viewDidLoad 가 아닌 viewWillAppear 가 호출된다.
```swift
override func viewDidLoad() {
  super.viewDidLoad()
  // Do any additional setup after loading the view, typically from a nib.
}
```

<br>

## viewWillAppear
- View 가 화면에 나타나기 직전에 호출된다.
- 화면전환 시 처리하는 용도로 사용된다.

![image](https://user-images.githubusercontent.com/101554627/175509360-236fcc37-7257-46cb-a0bc-63cdbace729b.png)


<br>

## viewDidAppear
- View 가 화면에 나타난 후 호출된다.
- 화면에 적용될 애니메이션을 그려준다.

<br>

## viewWillDisappear
- 화면전환 전이나 ViewController 가 사라지기 전 호출된다.

<br>

## viewDidDisappear
- View 가 사라진 후 호출된다.

<br><br><br>

# 참조
- [TONO님](https://tono18.tistory.com/11)
- [Zedd님](https://zeddios.tistory.com/43)
