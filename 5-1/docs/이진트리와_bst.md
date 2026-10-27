# 이진 트리(Binary Tree) 및 이진 탐색 트리(BST) 핵심 정리

본 문서는 필기노트와 소스 코드 분석을 바탕으로, **포인터 기반 이진 트리의 노드 구조**, **4대 순회(전위·중위·후위·레벨 순회) 알고리즘의 원리와 BFS 큐 연동**, **이진 탐색 트리(BST)의 불변 규칙과 $O(\log N)$ 동작 원리**, **노드 삭제의 3가지 케이스(자식 0개, 1개, 2개-후계자 치환) 상세 트레이싱**, 그리고 **Redis Sorted Set(ZSET: ZADD, ZRANGE)으로의 확장 연계**를 총정리한 학습 문서입니다.

---

## 1. 이진 트리(Binary Tree)의 기본 개념 (`binary_tree.py`)

### 1) 노드 구조 (`TreeNode`)
일반적인 선형 자료구조(연결 리스트)가 `prev`, `next`라는 수평적 포인터를 갖는 것과 달리, 이진 트리는 하향식 계층 관계를 나타내는 두 개의 자식 포인터를 가집니다.

```python
class TreeNode:
    def __init__(self, value):
        self.value = value   # 노드가 담고 있는 실제 데이터
        self.left = None     # 왼쪽 자식 노드를 가리키는 포인터
        self.right = None    # 오른쪽 자식 노드를 가리키는 포인터
```

- **이진 트리(Binary Tree)**: 모든 노드가 **최대 2개의 자식(왼쪽, 오른쪽)**만을 가질 수 있는 트리 구조입니다.

---

### 2) 트리를 방문하는 4가지 순회(Traversal) 방식

트리는 선형 배열과 달리 갈림길이 존재하므로, 전체 노드를 빠짐없이 방문하기 위한 기준이 필요합니다.  
순회 방식을 구분하는 핵심 기준은 **"부모(루트/나)를 언제 방문하는가?"**입니다.

```text
               [ 부모 (Root) ]
                 /        \
         [ 왼쪽 (L) ]    [ 오른쪽 (R) ]
```

#### [필기 노트 순회 비교표 복원]

| 순회 방식 | 방문 순서 | 핵심 기억법 | 주로 쓰이는 곳 (실무 및 시스템 활용) |
| :--- | :--- | :--- | :--- |
| **1. 전위 순회 (Pre-order)** | **부모** $\rightarrow$ 왼 $\rightarrow$ 오 | **부모가 맨 앞 (Pre)** | 트리 구조 전체를 파일로 직렬화(Serialize)하여 저장하거나 복사할 때 |
| **2. 중위 순회 (In-order)** | 왼 $\rightarrow$ **부모** $\rightarrow$ 오 | **가운데 (In)** | **이진 탐색 트리(BST)에서 데이터를 오름차순 정렬할 때** |
| **3. 후위 순회 (Post-order)** | 왼 $\rightarrow$ 오 $\rightarrow$ **부모** | **맨 뒤 (Post)** | 하위 폴더 용량을 다 더한 뒤 상위 폴더 계산할 때, 트리 전체 메모리 삭제(해제) |
| **4. 레벨 순회 (Level-order)** | 층순서대로, 왼 $\rightarrow$ 오 | **아파트 1층부터 층순서대로** | 최단 경로 탐색(BFS). **이때 방문 대기열로 `linear_structures.py`의 `Queue` 사용** |

---

### 3) 4대 순회 알고리즘 상세 및 레벨 순회(BFS) 큐 연동

#### ① 전위 순회 (`preorder`): 재귀 기반 DFS
```python
def preorder(node: TreeNode, result: list = None) -> list:
    if result is None:
        result = []
    if node:
        result.append(node.value)        # 1. 부모(나)를 먼저 기록
        preorder(node.left, result)      # 2. 왼쪽 서브트리 탐색
        preorder(node.right, result)     # 3. 오른쪽 서브트리 탐색
    return result
```

#### ② 중위 순회 (`inorder`): 재귀 기반 DFS
```python
def inorder(node: TreeNode, result: list = None) -> list:
    if result is None:
        result = []
    if node:
        inorder(node.left, result)       # 1. 왼쪽 끝까지 내려감
        result.append(node.value)        # 2. 부모(나)를 기록
        inorder(node.right, result)      # 3. 오른쪽 서브트리 탐색
    return result
```

#### ③ 후위 순회 (`postorder`): 재귀 기반 DFS
```python
def postorder(node: TreeNode, result: list = None) -> list:
    if result is None:
        result = []
    if node:
        postorder(node.left, result)     # 1. 왼쪽 자식 처리
        postorder(node.right, result)    # 2. 오른쪽 자식 처리
        result.append(node.value)        # 3. 마지막에 부모(나) 기록
    return result
```

#### ④ 레벨 순회 (`levelorder`): 큐(`Queue`) 기반 BFS
재귀 호출(함수 호출 스택 - LIFO)을 쓰면 한쪽 깊은 곳으로 파고드는 DFS가 됩니다.  
따라서 층별(너비 우선)로 방문하기 위해 **`linear_structures.py`에서 구현한 FIFO `Queue`**를 방문 대기열로 사용합니다.

```python
from linear_structures import Queue

def levelorder(root: TreeNode) -> list:
    if not root:
        return []
    result = []
    q = Queue()          # 직접 구현한 선입선출 Queue 객체
    q.enqueue(root)      # 루트 노드를 대기열에 진입

    while not q.is_empty():
        current_node = q.dequeue()         # 1. 대기열 맨 앞 노드 꺼내기 (방문)
        result.append(current_node.value)  # 2. 값 기록

        # 3. 자식 노드가 있다면 큐의 뒤에 차례로 줄 세우기 (다음 층 방문 예약)
        if current_node.left:
            q.enqueue(current_node.left)
        if current_node.right:
            q.enqueue(current_node.right)

    return result
```

---

## 2. 이진 탐색 트리(Binary Search Tree, BST) (`binary_search_tree.py`)

### 1) What? (BST의 정의와 불변 규칙)
일반 이진 트리는 데이터의 위치에 규칙이 없어 값을 찾으려면 전체를 순회($O(N)$)해야 합니다.  
반면 **이진 탐색 트리(BST)**는 모든 노드에 대해 다음 규칙을 만족합니다.

$$\text{왼쪽 서브트리 노드들의 값} < \text{현재 부모 노드의 값} < \text{오른쪽 서브트리 노드들의 값}$$

```text
                  [ 50 (부모) ]
                  /          \
   (작은 값은 왼쪽 복도)      (큰 값은 오른쪽 복도)
               /                \
            [ 30 ]            [ 70 ]
```

- **장점**: 찾으려는 값이 현재 노드보다 작으면 오른쪽 절반을 버리고 왼쪽으로만 갑니다. 매 단계마다 탐색 범위가 절반씩 줄어들므로 평균 **$O(\log N)$**의 속도로 탐색, 삽입, 삭제가 완료됩니다.
- **특징**: **중위 순회(In-order)를 돌리면 데이터가 자동으로 오름차순 정렬**되어 출력됩니다.

---

### 2) 노드 및 클래스 설계
실제 구현 코드에서는 단일 `key`를 기준으로 트리를 구성합니다.

```python
class BSTNode:
    def __init__(self, key):
        self.key = key       # 노드가 보관할 데이터 값
        self.left = None     # 나보다 작은 값이 연결될 왼쪽 링크
        self.right = None    # 나보다 큰 값이 연결될 오른쪽 링크

class BinarySearchTree:
    def __init__(self):
        self.root = None     # 트리의 뿌리 노드
        self.size = 0        # 전체 노드 개수
```

---

### 3) 탐색: `search(key)` (반복문 방식)
```python
def search(self, key) -> bool:
    curr = self.root
    while curr:
        if key == curr.key:
            return True               # 값 발견
        elif key < curr.key:
            curr = curr.left          # 목표가 작으므로 왼쪽으로 하강
        else:
            curr = curr.right         # 목표가 크므로 오른쪽으로 하강
    return False                      # 바닥(None)까지 뒤졌으나 없음
```

> **포인트: 왜 `search`는 재귀가 아닌 `while` 반복문으로 짰을까?**  
> 재귀 호출은 호출 스택 메모리를 소모하며 트리가 깊어지면 스택 오버플로우가 날 수 있습니다. 반면 단순 탐색은 포인터 이동만 반복하므로 `while` 루프로 구현하면 추가 메모리를 전혀 쓰지 않는 **공간 복잡도 $O(1)$**을 달성하며 속도도 훨씬 빠릅니다.

---

### 4) 삽입: `insert(key)` (재귀 포인터 재연결 기법)
```python
def insert(self, key) -> None:
    self.root = self._insert(self.root, key)
    self.size += 1

def _insert(self, node: BSTNode, key):
    if node is None:
        return BSTNode(key)           # 1. 빈자리를 찾으면 새 노드를 생성하여 반환

    if key < node.key:
        node.left = self._insert(node.left, key)    # 2. 작은 값은 왼쪽 자식 링크에 연결
    elif key > node.key:
        node.right = self._insert(node.right, key)  # 3. 큰 값은 오른쪽 자식 링크에 연결
    # 중복 키(key == node.key)는 추가하지 않고 통과

    return node                       # 연결이 완료된 자기 자신을 부모에게 반환
```

- **`node.left = self._insert(node.left, key)` 구조의 의미**:  
  재귀를 타고 끝(None)에 도달했을 때 생성된 새 노드를 부모 노드가 받아 자신의 손(`node.left` 또는 `node.right`)에 쥐어주는 **"포인터 재연결 기법(Link by Assignment)"**입니다.

---

## 3. BST 노드 삭제: `delete(key)` (핵심 메커니즘)

트리에서 노드를 삭제할 때는 **"왼쪽 < 부모 < 오른쪽"**이라는 BST 정렬 규칙이 깨지지 않도록 자식의 개수에 따라 3가지 케이스로 분기합니다.

```python
def delete(self, key) -> None:
    self.root = self._delete(self.root, key)

def _delete(self, node: BSTNode, key):
    if node is None:
        return None

    # 1. 삭제할 대상을 찾는 과정
    if key < node.key:
        node.left = self._delete(node.left, key)
    elif key > node.key:
        node.right = self._delete(node.right, key)
    else:
        # [삭제할 대상 노드를 찾음! (key == node.key)]

        # Case 1 & Case 2: 자식이 없거나 1개만 있는 경우
        if node.left is None:
            return node.right         # 오른쪽 자식(또는 None)을 내 자리에 승계
        elif node.right is None:
            return node.left          # 왼쪽 자식을 내 자리에 승계

        # Case 3: 자식이 둘 다(좌/우 모두) 있는 경우 (핵심!)
        successor = self._get_min_node(node.right)     # 오른쪽 서브트리의 최솟값(후계자) 탐색
        node.key = successor.key                       # 후계자의 값만 내 자리에 덮어쓰기
        node.right = self._delete(node.right, successor.key) # 원래 후계자 노드 실제 삭제

    return node

def _get_min_node(self, node: BSTNode) -> BSTNode:
    curr = node
    while curr.left:                  # 왼쪽 끝까지 내려가면 가장 작은 값!
        curr = curr.left
    return curr
```

---

###  노드 삭제의 3가지 경우의 수 

#### Case 1: 자식이 없는 리프(Leaf) 노드 삭제
- **원리**: 부모 노드와의 연결 손만 끊고 조용히 사라집니다.
- **코드 동작**: `node.left is None` 조건에 걸려 `return node.right` (즉, `None`)이 반환되어 부모의 자식 링크가 `None`으로 갱신됩니다.

#### Case 2: 자식이 1개만 있는 노드 삭제
- **원리**: 자신이 사라지면서, 하나뿐인 자식을 자신의 부모 노드에 그대로 입양(승계)시킵니다.
- **코드 동작**: `node.left`가 없으면 `node.right`를 부모에게 돌려주고, `node.right`가 없으면 `node.left`를 부모에게 돌려줍니다.

#### Case 3: 자식이 둘 다 있는 노드 삭제 
자식이 둘 다 있는데 내가 빠져버리면 자식 둘이 갈 곳을 잃고 트리 정렬 규칙이 무너집니다.

```text
                [ 50 (삭제 대상) ]
                   /          \
                [ 30 ]      [ 70 ]
                            /    \
                  (후계자) [ 55 ]  [ 80 ]
```

1. **후계자(Successor) 탐색**:  
   내가 빠진 자리에 들어올 가장 완벽한 대체자는 **"나보다 큰 무리(오른쪽 서브트리) 중에서 가장 작은 노드"**입니다. (`_get_min_node(node.right)`)
2. **값 복사 (얼굴 성형)**:  
   후계자 노드(`[55]`)의 `key`를 삭제할 노드(`node.key`)에 덮어씌웁니다.  
   이 순간 트리에 `55`라는 값이 내 자리와 원래 후계자 자리 2군데에 중복으로 존재하게 됩니다.
3. **원래 후계자 노드 실제 삭제**:  
   `node.right = self._delete(node.right, successor.key)`  
   내 오른쪽 동네(`node.right`)로 들어가서, 방금 값만 복사해주고 껍데기만 남은 원래 `55` 노드를 실제로 삭제하고 정리된 서브트리를 다시 내 오른쪽 손(`node.right`)에 쥐어줍니다.

---

###  스스로 리뷰 시 자주 헷갈리는 코드

**Q1. `_delete()`에서 어디가 기준점이고 무엇을 비교하나요?**
> - **`key`**: 사용자가 "이거 지워줘!" 하고 던진 **'삭제 목표 번호' (고정된 타깃)**
> - **`node.key`**: 지금 컴퓨터가 서 있는 **'현재 방 번호' (매번 바뀌는 기준점)**
> - 즉, `key < node.key`이면 목표가 현재 방보다 작으므로 왼쪽 복도로 내려가고, 반대면 오른쪽 복도로 내려가는 것입니다.

**Q2. 메서드를 왜 공개용 `delete()`와 내부용 `_delete()`로 쪼갰나요?**
> 1. **사용자 편의성**: 사용자는 `tree.delete(50)`처럼 깔끔하게 호출하고 싶지, 내부 시작점인 `tree.delete(tree.root, 50)`을 알고 싶어 하지 않습니다 (캡슐화).
> 2. **루트 갱신**: 맨 꼭대기 루트 노드가 삭제될 때 `self.root = self._delete(...)`를 통해 트리의 새 머리를 안전하게 교체하기 위함입니다.

**Q3. `node.right = self._delete(node.right, successor.key)`에서 `node.right`가 후계자 노드인가요?**
> **아닙니다!** `node.right`는 후계자 개인이 아니라 **"현재 노드의 오른쪽 서브트리 전체로 가는 연결 손"**입니다. 후계자(`successor`)는 그 오른쪽 동네의 왼쪽 끝자락에 숨어 있습니다.  
> 따라서 "오른쪽 동네로 들어가서 원래 후계자를 제거하고 오너라" 하고 심부름을 보낸 뒤, 정리되어 돌아온 오른쪽 동네를 다시 내 손(`node.right`)에 잡는 것입니다.

---

## 4. 중위 순회 정렬: `inorder_sort()`

```python
def inorder_sort(self) -> list:
    result = []
    self._inorder(self.root, result)
    return result

def _inorder(self, node: BSTNode, result: list) -> None:
    if node:
        self._inorder(node.left, result)     # 1. 나보다 작은 값들 먼저 수집
        result.append(node.key)              # 2. 내 값 수집
        self._inorder(node.right, result)    # 3. 나보다 큰 값들 수집
```

- **정렬 원리**: 중위 순회는 **"왼쪽 $\rightarrow$ 나 $\rightarrow$ 오른쪽"** 순서로 방문합니다.  
  BST는 왼쪽에는 작은 값, 오른쪽에는 큰 값만 있으므로, 이 순서대로 방문하기만 하면 **별도의 정렬 알고리즘(`sort()`) 없이도 결과 리스트가 완벽한 오름차순(작은 수 $\rightarrow$ 큰 수)으로 자동 정렬**됩니다.

---

## 5. Redis Sorted Set (ZSET)으로의 확장

**Where 연결? $\implies$ 미래의 확장 토대** 내용입니다.

- **해시맵(`hash_map.py`)의 한계**:  
  해시맵은 Key-Value를 $O(1)$로 빠르게 찾지만 데이터가 해시 인덱스에 무작위로 분산되므로, "점수가 80점 이상 100점 이하인 사람을 순서대로 뽑아줘" 같은 **범위 검색(Range Query)과 정렬이 불가능**합니다.
- **BST 기반 ZSET 구현**:  
  실제 Redis의 정렬 집합인 **ZSET(`ZADD`, `ZRANGE`)**을 밑바닥부터 구현할 때 BST가 핵심 엔진으로 활용됩니다.
  - `ZADD score member`: 점수(`score`)를 `key`로 삼아 BST에 삽입 ($O(\log N)$).
  - `ZRANGE`: BST의 중위 순회(`inorder_sort`)를 실행하여 점수 오름차순으로 정렬된 멤버 목록을 즉시 추출.

---

## 6. 성능 한계와 트레이드오프: 편향 트리 (Skewed Tree)

BST의 유일한 약점은 데이터가 들어오는 순서에 따라 트리의 균형이 깨질 수 있다는 점입니다.

```text
[균형 잡힌 BST: O(log N)]              [편향된 BST: O(N) 최악]
         [ 30 ]                                  [ 10 ]
        /      \                                    \
     [ 20 ]   [ 40 ]                                [ 20 ]
     /    \   /    \                                   \
   [10]  [25][35]  [50]                                [ 30 ]
                                                          \
                                                          [ 40 ]
```

- **편향 트리 발생**: `1, 2, 3, 4, 5`처럼 이미 오름차순으로 정렬된 데이터가 순서대로 삽입되면 오른쪽으로만 계속 뻗어나가 사실상 **단일 연결 리스트**와 동일해집니다.
- **성능 퇴화**: 탐색, 삽입, 삭제 시간 복잡도가 $O(\log N)$에서 **$O(N)$**으로 추락합니다.
- **실제 시스템의 극복 방안**:  
  - Java `TreeMap`/`HashMap` 등은 스스로 회전하여 높이 균형을 맞추는 **레드-블랙 트리(Red-Black Tree)**나 **AVL 트리**를 사용하여 최악에도 $O(\log N)$을 보장합니다.
  - 실제 Redis의 Sorted Set은 구현의 단순성과 범위 검색 성능을 위해 트리 대신 **스킵 리스트(SkipList)**를 사용합니다.

