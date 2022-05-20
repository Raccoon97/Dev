
<br><br><br>

# Type Casting
- 인스턴스의 타입을 확인하거나 인스턴스를 같은 계층에 있는 superclass 또는 subclass 로 취급하는 방법이다.
- Type Casting 에는 is 와 as 두 연산자를 사용한다.
- Type Casting 을 이용하면 특정 프로토콜을 따르는지 확인할 수 있다.
- Casting 은 실제 인스턴스나 값을 바꾸는 것이 아니라 지정한 타입으로 취급하는 것이다.

<br><br><br>

# Type Casting 을 위한 클래스 계층구조 선언
- Type Casting 동작을 확인하기 위한 클래스
```swift
class MediaItem {
  var name: String
  init(name: String) {
    self.name = name
  }
}
```
- 위의 MediaItem 클래스를 서브클래싱해서 두 개의 다른 서브클래스를 만들고 그 두 클래스를 아이템으로 갖는 배열을 선언
```swift
class Movie: MediaItem {
  var director: String
  init(name: String, director: String) {
    self.director = director
    super.init(name: name)
  }
}

class Song: MediaItem {
  var artist: String
  init(name: String, artist: String){
    self.artist = artist
    super.init(name: name)
  }
}

let library = [
  Movie(name: "Casablanca", director: "Michael Curtiz"),
  Song(name: "Blue Suede Shoes", artist: "Elvis Presley"),
  Movie(name: "Citizen Kane", director: "Orson Welles"),
  Song(name: "The One And Only", artist: "Chesney Hawkes"),
  Song(name: "Never Gonna Give You Up", artist: "Rick Astley")
]
```
- 위의 코드에서 library 배열이 갖고 있는 Movie, Song 인스턴스의 공통 부모는 MediaItem 이기 때문에 library 배열은 타입 추론에 의해 [MediaItem] 배열의 형을 갖게 된다.
- library 배열을 순회하면 Movie, Song 타입이 아니라 MediaItem 타입이라는 것을 확인할 수 있다.
- 타입 지정을 위해서는 downcasting 을 사용해야 한다.

<br><br><br>

# Type 확인
- is 연산자를 이용해 특정 인스턴스의 타입을 확인할 수 있다. 
- 아래 예시는 배열을 순회하고 아이템이 특정 타입일 때 마다 숫자를 증가하는 코드이다.
```swift
var movieCount = 0
var songCount = 0

for item in library {
  if item is Movie {
    movieCount += 1
  } else if item is Song {
    songCount += 1
  }
}

print("Media library contains \(movieCount) movies and \(songCount) songs")
// "Media library contains 2 movies and 3 songs"
```

<br><br><br>

# Downcasting
- 특정 클래스 타입의 상수나 변수는 특정 서브크래스의 인스턴스를 참조하고 있을 수 있다.
- as? 와 as! 연산자를 이용해 어떤 타입의 인스턴스인지 확인할 수 있다.
- as? 는 특정 타입이 맞는지 확신할 수 없을 때 사용한다.
- as! 는 특정 타입이 맞는지 확신할 수 있을 때 사용한다 단, 해당 타입이 아니라면 런타임 에러가 발생한다.
- 아래 예시는 배열의 mediaItem 이 Movie 또는 Song 인스턴스 일 수 있기 때문에 다운캐스팅을 위해 as? 를 사용한 코드이다.
```swift
for item in library {
  if let movie = item as? Movie {
    print("Movie: \(movie.name), dir. \(movie.director)")
  } else if let song = item as? Song {
    print("Song: \(song.name), by \(song.artist)")
  }
}

// Movie: Casablanca, dir. Michael Curtiz
// Song: Blue Suede Shoes, by Elvis Presley
// Movie: Citizen Kane, dir. Orson Welles
// Song: The One And Only, by Chesney Hawkes
// Song: Never Gonna Give You Up, by Rick Astley
```


<br><br><br>

# Any, AnyObject 의 Type Casting

<br><br><br>

# 참조
