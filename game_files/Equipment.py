class Equipment:
    def __init__(self):
        self.eq = []
        for i in range(0, 9):
            self.eq.append([0, 0])

    def where_is_this(self, which_block):
        for i in range(len(self.eq)):
            if self.eq[i][0] == which_block:
                return i
        for i in range(len(self.eq)):
            if self.eq[i][0] == 0:
                return i
        return -1

    def add_item(self, which_block, how_many=1):
        which_block = int(which_block)
        if which_block == 1:
            which_block = 2
        where = self.where_is_this(which_block)
        if where != -1:
            self.eq[where][0] = which_block
            self.eq[where][1] += how_many

    def print_content(self):
        eq = ""
        for i in range(0, 9):
            eq += str(self.eq[i])
        return eq

    def take_item(self, position):
        if self.eq[position][1] > 1:
            self.eq[position][1] -= 1
            return self.eq[position][0]
        if self.eq[position][1] == 1:
            block_type = self.eq[position][0]
            self.eq[position][0] = 0
            self.eq[position][1] = 0
            return block_type
        return 0

