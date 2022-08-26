# 🏠   [Go Main](https://github.com/Raccoon97/Swift/blob/main/README.md)   🏠
- [SnapKit 사용하기](https://github.com/Raccoon97/Swift/blob/main/Etc/SnapKit%20%EC%82%AC%EC%9A%A9.md#snapkit-%EC%82%AC%EC%9A%A9%ED%95%98%EA%B8%B0)
  - [SnapKit 가져오기](https://github.com/Raccoon97/Swift/blob/main/Etc/SnapKit%20%EC%82%AC%EC%9A%A9.md#snapkit-%EA%B0%80%EC%A0%B8%EC%98%A4%EA%B8%B0)

<br><br><br>

# SnapKit 사용하기
- 짧은 코드로 AutoLayout 을 표현하기 위해 사용하는 프레임워크

<br><br>

## SnapKit 가져오기
- brew 또는 gem 을 이용해 cocoapods 를 설치한다.
```zsh
$ brew install cocoapods

          or

$ gem install cocoapods
```

<br>

- cocoapods 이 설치되었는지 확인한다.
- 정상적으로 설치되었다면 아래 그림처럼 출력된다.
```zsh
$ pod env
```

<img width="941" alt="스크린샷 2022-08-26 오후 7 09 55" src="https://user-images.githubusercontent.com/101554627/186881555-20a1df5d-0142-45ea-bb93-d65a640ae5eb.png">

<br>

- SnapKit 을 사용하려는 프로젝트의 경로에 아래 명령어를 입력한다.
- 프로젝트경로에 새로 생성된 PodFile 을 확인할 수 있다.

```zsh
$ cd <Your Target Name>
$ pod init
```

<img width="941" alt="스크린샷 2022-08-26 오후 7 10 52" src="https://user-images.githubusercontent.com/101554627/186881738-9a6d25ba-e003-4ed7-91bf-5a09d6ad25ec.png">

<br>

- 이제 새로 생성된 PodFile 을 텍스트 편집기 혹은 vi 편집기로 열어서 수정해준다.

```cocoapods
target '<Your Target Name>' do
    pod 'SnapKit'
end
```

<br>

- PodFile 을 수정했다면 해당 PodFile 이 있는 경로에 아래 명령어를 입력한다.
- 아래 그림과 같은 결과가 나왔다면 정상적으로 프레임워크를 사용할 수 있다.
```zsh
pod install
```

<img width="941" alt="스크린샷 2022-08-26 오후 7 15 38" src="https://user-images.githubusercontent.com/101554627/186882513-93683085-ff99-45b1-9e3a-1522b21ed06f.png">

>- SnapKit Git 에서는 Swift 4. 버전은 SnapKit 4. 버전으로, Swift 5. 버전은 SnapKit 5. 버전으로 사용하는 것을 추천한다.
>- 플랫폼을 따로 지정하지 않아 자동으로 iOS 13. 으로 지정되었다. https://guides.cocoapods.org/syntax/podfile.html#platform 을 참고해서 플랫폼을 지정하자.
>- 마스터 사양 보고서는 추후에..

## SnapKit 사용하기
- 프로젝트 폴더를 보면 아래 이미지와 같이 xcworkspace 파일이 새로 추가되었을텐데, 그걸 실행해준다.
<img width="779" alt="스크린샷 2022-08-26 오후 7 22 44" src="https://user-images.githubusercontent.com/101554627/186883738-cc659a03-602a-4331-a65e-c88a3efdecf3.png">

<br>

- UIKit import 하듯이 SnapKit 도 import 해준다. 이제 사용이 가능하다.
<img width="1226" alt="스크린샷 2022-08-26 오후 7 24 48" src="https://user-images.githubusercontent.com/101554627/186884114-d17d6523-a7c1-4457-adee-39ae0a16fa81.png">

- 아래는 SnapKit Git 에 나와있는 예제 코드와 실행 결과이다.
<img width="1226" alt="스크린샷 2022-08-26 오후 7 26 41" src="https://user-images.githubusercontent.com/101554627/186884440-5f81222e-e405-4917-a757-0a1980e87da9.png">

<img width="482" alt="스크린샷 2022-08-26 오후 7 27 11" src="https://user-images.githubusercontent.com/101554627/186884514-c59e93d4-6a84-4679-abb0-8a72964f8654.png">


<br><br><br>

# 참조
- [SnapKit Git](https://github.com/SnapKit/SnapKit)
