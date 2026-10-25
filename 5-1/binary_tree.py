from linear_structures import Queue

class TreeNode:
    def __init__(self,value):
        self.value = value
        self.left = None
        self.right = None

def preorder(node: TreeNode, result: list =None) -> list:
    if result is None:
        result = []
    if node:
        result.append(node.value)
        preorder(node.left, result)
        preorder(node.right, result)
    return result

def inorder(node: TreeNode, result:list =None) ->list:
    if result is None:
        result = []
    if node:
        inorder(node.left, result)
        result.append(node.value)
        inorder(node.right, result)
    return result

def postorder(node: TreeNode, result: list = None) ->list:
    if result is None:
        result = []
    if node:
        postorder(node.left, result)
        postorder(node.right, result)
        result.append(node.value)
    return result

def levelorder(root: TreeNode)->list:
    if not root:
        return []
    result = []
    q= Queue()
    q.enqueue(root)

    while not q.is_empty():
        current_node = q.dequeue()
        result.append(current_node.value)

        if current_node.left:
            q.enqueue(current_node.left)
        if current_node.right:
            q.enqueue(current_node.right)

    return result

        

if __name__ =="__main__":
    root = TreeNode(1)
    root.left = TreeNode(2)
    root.right = TreeNode(3)
    root.left.left = TreeNode(4)
    root.left.right = TreeNode(5)

    print(f"1.전위 순회(preorder) {preorder(root)}")
    print(f"2.중위 순회(inorder) {inorder(root)}")
    print(f"3.후위 순회(postorder) {postorder(root)}")
    print(f"4.레벨 순회(levelorder) {levelorder(root)}")
