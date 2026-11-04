class BSTNode:
    def __init__(self,key):
        self.key = key
        self.left= None
        self.right = None

class BinarySearchTree:
    def __init__(self):
        self.root = None

    def search(self, key) ->bool :
        curr = self.root
        while curr:
            if key == curr.key:
                return True
            elif key < curr.key:
                curr = curr.left
            else :
                curr = curr.right
        return False

    def insert(self,key) ->None:
        self.root = self._insert(self.root,key) 

    def _insert(self, node: BSTNode, key):
        if node is None:
            return BSTNode(key)

        if key < node.key:
            node.left = self._insert(node.left,key)
        elif key > node.key:
            node.right = self._insert(node.right,key)
        return node
    def delete(self,key)->None:
        self.root = self._delete(self.root,key)

    def _delete(self, node:BSTNode,key):
        if node is None:
            return None

        if key < node.key:
            node.left = self._delete(node.left,key)
        elif key> node.key:
            node.right= self._delete(node.right,key)
        else:
            if node.left is None :
                return node.right
            elif node.right is None:
                return node.left

            successor = self._get_min_node(node.right)
            node.key = successor.key
            node.right=self._delete(node.right,successor.key)
        return node

    def _get_min_node(self,node:BSTNode) ->BSTNode:
        curr = node
        while curr.left:
            curr = curr.left
        return curr

    def inorder_sort(self) -> list:
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node:BSTNode,result:list) -> None:
        if node:
            self._inorder(node.left, result)
            result.append(node.key)
            self._inorder(node.right,result)

if __name__ == "__main__":
    bst = BinarySearchTree()
    dates = [50,30,70,20,40,60,80]
    for d in dates:
        bst.insert(d)

    print("BST검증")
    print(f"삽입된 원래 순서: {dates}")
    print(f"중위 순서 결과(자동정렬): {bst.inorder_sort()}")

    print("\n탐색테스트")
    print(f"40 존재 여부: {bst.search(40)}")
    print(f"99 존재 여부: {bst.search(99)}")

    print("\n 삭제 테스트")
    print("로트노드(50) 삭제 실행..")
    bst.delete(50)
    print(f"50삭제 후 정렬 결과 : {bst.inorder_sort()}")