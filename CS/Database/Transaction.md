# 🏠   [Go Main](../../README.md)   🏠
- [Transaction 이란?](#transaction-이란)
- [ACID 특성](#acid-특성)
- [Transaction 상태](#transaction-상태)
- [격리 수준 (Isolation Level)](#격리-수준-isolation-level)
- [동시성 이슈](#동시성-이슈)
- [Lock](#lock)
- [면접 예상 질문](#면접-예상-질문)

<br><br><br>

# Transaction 이란?
- 데이터베이스의 상태를 변화시키는 **하나의 논리적 작업 단위** 이다.
- 여러 개의 쿼리를 하나의 단위로 묶어, 모두 성공하거나 모두 실패해야 한다.
- 대표적인 예 : 계좌 이체 (A 의 돈 차감 + B 의 돈 증가 가 모두 성공해야 함)

```sql
BEGIN;                                      -- 트랜잭션 시작
UPDATE accounts SET balance = balance - 1000 WHERE id = 1;  -- A 계좌 차감
UPDATE accounts SET balance = balance + 1000 WHERE id = 2;  -- B 계좌 증가
COMMIT;                                     -- 트랜잭션 커밋 (영구 반영)

-- 오류 발생 시
ROLLBACK;                                   -- 트랜잭션 취소
```

<br><br><br>

# ACID 특성
- Transaction 이 보장해야 하는 4 가지 특성이다.

### 1. Atomicity (원자성)
- Transaction 의 연산은 **모두 실행** 되거나 **모두 실행되지 않아야** 한다.
- 중간에 실패하면 모든 변경 사항을 Rollback 해야 한다.

### 2. Consistency (일관성)
- Transaction 완료 후에도 데이터베이스의 **무결성 제약 조건** 을 만족해야 한다.
- Transaction 실행 전과 후의 데이터베이스는 항상 일관된 상태여야 한다.

### 3. Isolation (격리성)
- 동시에 실행되는 Transaction 들은 **서로 영향을 미치지 않아야** 한다.
- 한 Transaction 이 다른 Transaction 의 중간 상태를 볼 수 없어야 한다.

### 4. Durability (지속성)
- 성공적으로 완료된 Transaction 의 결과는 **영구히 반영** 되어야 한다.
- 시스템 장애가 발생해도 Commit 된 데이터는 유지되어야 한다.

<br><br><br>

# Transaction 상태

```
    활동 (Active)
       ↓
  부분 완료 (Partially Committed)
    ↓          ↓
완료(Committed)  실패(Failed)
                  ↓
              철회(Aborted)
```

- **Active** : Transaction 이 실행 중인 상태
- **Partially Committed** : 마지막 연산이 실행된 직후, 아직 Commit 되지 않은 상태
- **Committed** : 모든 연산이 성공적으로 완료된 상태
- **Failed** : 정상 실행이 더 이상 불가능한 상태
- **Aborted** : Rollback 되어 실행 전 상태로 복귀

<br><br><br>

# 격리 수준 (Isolation Level)

| Level | Dirty Read | Non-Repeatable Read | Phantom Read |
|---|---|---|---|
| **Read Uncommitted** | O | O | O |
| **Read Committed** | X | O | O |
| **Repeatable Read** | X | X | O |
| **Serializable** | X | X | X |

### 1. Read Uncommitted
- 다른 Transaction 의 **Commit 되지 않은** 데이터도 읽을 수 있다.
- 가장 낮은 격리 수준, 성능은 좋지만 데이터 정합성 문제가 심각하다.

### 2. Read Committed
- **Commit 된 데이터만** 읽을 수 있다.
- 대부분의 RDBMS 의 기본 격리 수준 (PostgreSQL, Oracle).

### 3. Repeatable Read
- Transaction 내에서 **같은 쿼리는 항상 같은 결과** 를 반환한다.
- MySQL (InnoDB) 의 기본 격리 수준.

### 4. Serializable
- Transaction 들을 **순차적으로** 실행하는 것처럼 보이게 한다.
- 가장 높은 격리 수준, 데이터 정합성은 완벽하지만 성능이 저하된다.

<br><br><br>

# 동시성 이슈

### Dirty Read
- 다른 Transaction 이 변경 후 **아직 Commit 하지 않은** 데이터를 읽는 현상.

### Non-Repeatable Read
- 같은 Transaction 내에서 같은 쿼리를 실행했을 때 **결과가 달라지는** 현상.
- 중간에 다른 Transaction 이 Update/Delete 해 Commit 했기 때문.

### Phantom Read
- 같은 Transaction 내에서 같은 쿼리를 실행했을 때 **없던 행이 생기거나 사라지는** 현상.
- 중간에 다른 Transaction 이 Insert/Delete 했기 때문.

<br><br><br>

# Lock

### 공유 Lock (Shared Lock, S-Lock)
- **읽기** 작업에 사용된다.
- 여러 Transaction 이 동시에 공유 Lock 을 걸 수 있다.
- 공유 Lock 이 걸린 데이터에는 배타 Lock 을 걸 수 없다.

### 배타 Lock (Exclusive Lock, X-Lock)
- **쓰기** 작업에 사용된다.
- 하나의 Transaction 만 걸 수 있다.
- 배타 Lock 이 걸린 데이터에는 다른 어떤 Lock 도 걸 수 없다.

### 낙관적 Lock vs 비관적 Lock
- **낙관적 Lock (Optimistic)** : 충돌이 드물다고 가정하고, Commit 시점에 충돌을 검증한다. Version 컬럼을 활용한다.
- **비관적 Lock (Pessimistic)** : 충돌이 자주 일어난다고 가정하고, 데이터 조회 시점부터 Lock 을 건다. `SELECT ... FOR UPDATE`.

<br><br><br>

# 면접 예상 질문
- **Q. Transaction 이 필요한 이유는?**
  - 여러 쿼리를 하나의 논리적 작업 단위로 묶어 데이터의 무결성을 보장하기 위함입니다. 예를 들어 계좌 이체처럼 두 개 이상의 쿼리가 모두 성공하거나 모두 실패해야 하는 상황에서 Transaction 이 필요합니다.

- **Q. ACID 에 대해 설명해주세요.**
  - Atomicity (원자성) 는 Transaction 의 연산이 모두 성공하거나 모두 실패해야 한다는 것이고, Consistency (일관성) 는 Transaction 완료 후에도 DB 의 무결성이 유지되어야 한다는 것입니다. Isolation (격리성) 은 동시에 실행되는 Transaction 이 서로 영향을 주지 않아야 한다는 것이고, Durability (지속성) 는 완료된 Transaction 의 결과가 영구적으로 유지되어야 한다는 것입니다.

- **Q. 격리 수준이 높아지면 어떤 문제가 생기나요?**
  - 격리 수준이 높아질수록 데이터 정합성은 좋아지지만, Lock 경합이 심해져 **동시성과 성능** 이 저하됩니다. 따라서 서비스의 특성에 맞는 적절한 격리 수준을 선택해야 합니다.

- **Q. Dirty Read 와 Non-Repeatable Read 의 차이는?**
  - Dirty Read 는 **아직 Commit 되지 않은** 다른 Transaction 의 변경사항을 읽는 것이고, Non-Repeatable Read 는 같은 Transaction 내에서 같은 데이터를 두 번 읽을 때 **Commit 된 변경사항** 때문에 다른 결과를 얻는 것입니다.

- **Q. 낙관적 Lock 과 비관적 Lock 중 어떤 것을 사용해야 하나요?**
  - 충돌이 드문 환경에서는 낙관적 Lock (Version 관리) 이 성능상 유리하고, 충돌이 빈번한 환경에서는 비관적 Lock 이 데이터 정합성 면에서 유리합니다. 일반적으로 읽기가 많은 서비스는 낙관적 Lock 을, 금융처럼 정합성이 중요한 서비스는 비관적 Lock 을 사용합니다.
