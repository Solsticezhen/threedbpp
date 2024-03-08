
class CLayout:
    def __init__(self, stack_s, p, x, y, r):
        self.stacks = stack_s
        self.p = p
        self.x = x
        self.y = y
        self.r = r

    def __eq__(self, other):
        if self.stacks == other.stacks and self.p == other.p and \
                self.x == other.x and self.y == other.y and self.r == other.r:
            return True
        return False
