# 🏠   [Go Main](https://github.com/Raccoon97/Swift/blob/main/README.md)   🏠
- [JSON ( JavaScript Object Notation )](https://github.com/Raccoon97/Swift/blob/main/Etc/JSON%EA%B3%BC%20XML.md#json--javascript-object-notation-)
  - [JSON 문법](https://github.com/Raccoon97/Swift/blob/main/Etc/JSON%EA%B3%BC%20XML.md#json-%EB%AC%B8%EB%B2%95)
- [XML ( eXtensible Markup Language )](https://github.com/Raccoon97/Swift/blob/main/Etc/JSON%EA%B3%BC%20XML.md#xml--extensible-markup-language-)
  - [XML 문법](https://github.com/Raccoon97/Swift/blob/main/Etc/JSON%EA%B3%BC%20XML.md#xml-%EB%AC%B8%EB%B2%95)
- [JSON 과 XML 의 공통점](https://github.com/Raccoon97/Swift/blob/main/Etc/JSON%EA%B3%BC%20XML.md#json-%EA%B3%BC-xml-%EC%9D%98-%EA%B3%B5%ED%86%B5%EC%A0%90)
- [JSON 과 XML 의 차이점](https://github.com/Raccoon97/Swift/blob/main/Etc/JSON%EA%B3%BC%20XML.md#json-%EA%B3%BC-xml-%EC%9D%98-%EC%B0%A8%EC%9D%B4%EC%A0%90)


<br><br><br>

# JSON ( JavaScript Object Notation )
- 데이터를 저장하거나 전송할 때 사용되는 경량의 DATA 교환 형식이다.
- JSON 은 사람과 기계 모두 이해하기 쉽고 용량이 작다.
- 단순히 데이터를 표시하는 방법이다.
- 서버와 클라이언트 간의 교류에서 일반적으로 많이 사용된다.
- 대부분의 프로그래밍 언어에서 JSON 포맷의 데이터를 핸들링할 수 있다.

<br><br>

## JSON 문법
```json
{
  "City": [
  {
    "name": "Seoul",
    "location": "Korea"
  },
  {
    "name": "Busan",
    "location": "Korea"
  }
  ]
  
  "alphabet" : [ "Aa","Bb", "Cc", "Dd" ....]
}
```

<br><br><br>

# XML ( eXtensible Markup Language )
- 다른 목적의 마크업 언어를 만드는 데 사용되는 다목적 마크업 언어이다.
- 다른 시스템끼리 다양한 종류의 데이터를 손쉽게 교환할 수 있도록 해준다.
- 새로운 태그를 만들어 추가해도 계속 동작하므로, 확장성이 좋다.
- 데이터를 보여주지 않고, 데이터를 전달하고 저장하는 것을 목적으로 한다.
- 텍스트 데이터 형식의 언어로 유니코드 문자로만 이루어진다.

<br><br>

## XML 문법

```xml
<City>
  <name>Seoul</name>
  <location>Korea</location>
</City>
<City>
  <name>Busan</name>
  <location>Korea</location>
</City>
<alphabet>
  <Aa>Aa</Aa>
  <Bb>Bb</Bb>
  <Cc>Cc</Cc>
  <Dd>Dd</Dd>
  .....
</alphabet>
```

<br><br><br>

# JSON 과 XML 의 공통점
- 데이터를 저장하고 전달하기 위해 고안되었다.
- 기계 뿐 아니라 사람도 쉽게 읽을 수 있다.
- 계층적인 데이터 구조를 가진다.
- 대부분의 프로그래멍 언어에 의해 파싱될 수 있다.

<br><br><br>

# JSON 과 XML 의 차이점
- JSON 은 종료 태그를 사용하지 않는다.
- JSON 의 구문이 XML 의 구문보다 훨씬 짧다.
- JSON 데이터가 XML 데이터보다 더 빨리 읽고 쓸 수 있다.
- XML 은 배열을 사용할 수 없지만 JSON 은 배열을 사용할 수 있다.

<br><br><br>

# 참조
- [곰돌이님](https://helloworld-88.tistory.com/67)
- [TCPSchool](http://www.tcpschool.com/json/json_intro_xml)
