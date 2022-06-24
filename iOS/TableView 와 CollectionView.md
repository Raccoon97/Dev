# 🏠   [Go Main](https://github.com/Raccoon97/Swift/blob/main/README.md)   🏠
- [TableView](https://github.com/Raccoon97/Swift/blob/main/iOS/TableView%20%EC%99%80%20CollectionView.md#tableview)
- [CollectionView](https://github.com/Raccoon97/Swift/blob/main/iOS/TableView%20%EC%99%80%20CollectionView.md#collectionview)
- [TableView 와 CollectionView 의 차이](https://github.com/Raccoon97/Swift/blob/main/iOS/TableView%20%EC%99%80%20CollectionView.md#tableview-%EC%99%80-collectionview-%EC%9D%98-%EC%B0%A8%EC%9D%B4)


<br><br><br>

# TableView
- 단일 column 에 배열된 row 를 사용해 데이터를 표시하는 뷰 이다.
- 목록을 스타일링할 때 사용되며 수직 스크롤만 가능하다.
- 테이블의 개별 항목을 구성하는 cell 은 UITableViewCell 이다.
- indexPath 값을 통해 cell 을 구분한다.
- 섹션을 이용해 row 를 시각적으로 구분할 수 있다.
- 여러 row 는 하나의 섹션 안에 구성될 수 있고, 각 섹션은 헤더와 푸터를 가질 수 있다.
- 사용하기 위해 datasource, delegate 를 구현해야 한다. < UITableVideDataSource, UITableViewDelegate >

![lickability.com](https://user-images.githubusercontent.com/101554627/175514366-945d400f-d08e-4eab-adcb-d5b46ea13c1a.png)

<br><br><br>

# CollectionView
- 여러 데이터를 관리하고 커스텀 가능한 레이아웃을 사용해서 사용자에게 보여줄 수 있는 객체이다.
- CollectionView 는 TableView 에서 할 수 있는 모든 것을 할 수 있다.
- 섹션을 가질 수 있고 indexPath 값을 통해 cell 을 구분한다.
- CollectionView 의 개별 항목을 구성하는 cell 은 UICollectionCell 이다.
- 사용하기 위해 datasource, delegate 를 구현해야 한다. < UICollectionViewDataSource, UICollectionViewDelegate >

![lickability.com](https://user-images.githubusercontent.com/101554627/175514958-95e02ce1-3332-4992-b8fc-8a9ee96956b0.png)


<br><br><br>

# TableView 와 CollectionView 의 차이

||TableView|CollectionView|
|------|---|---|
|스크롤|수직|수직/수평|
|스타일|기본 제공 있음|기본 제공 없음|
|형태|1차원|2차원|

<br>

## TableView
- 하나의 column 에 여러 row cell 을 표현하는 방식이기에, cell 의 모양은 항상 column 에 맞춰 디자인 해야 한다.
- 수직으로만 스크롤이 가능하다.
- 기본으로 제공되는 스타일이 존재한다.
- 1차원의 형태로 리스트를 보여준다.

## CollectionView
- row, column 모두 만들 수 있기 때문에 cell 의 모양을 자유롭게 디자인할 수 있다.
- 수직/수평 스크롤이 가능하다.
- 기본으로 제공되는 스타일이 존재하지 않는다.
- 2차원의 형태로 리스트를 보여준다.


<br><br><br>

# 참조
- [nareunhagae님](https://nareunhagae.tistory.com/19)
- [김주희님](http://labs.brandi.co.kr/2018/05/02/kimjh.html)
