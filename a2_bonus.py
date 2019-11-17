import itertools
import sys

class Board():

    ##########################################
    ####   Constructor
    ##########################################
    def __init__(self):

        #initialize all of the variables
        self.n2 = 9
        self.n = 3
        self.spaces = 0
        self.board = {}
        self.unsolved = set(itertools.product(range(self.n2), range(self.n2)))

    # makes a move, records it in its row, col, and box, and removes the space from unsolved
    def placeValue(self, space, val):
        self.board[space] = int(val)
        self.unsolved.remove(space)


##### Citations ####
# http://www.csc.kth.se/utbildning/kth/kurser/DD143X/dkand13/Group1Vahid/report/henrik-viksten.viktor-mattsson-kex.pdf
# This paper found that a dancing links/exact cover solution scales the best, so I'm going to be attemping to implement that
# https://arxiv.org/pdf/cs/0011047.pdf
# Donald Knuth's original paper on Dancing Links to solve Exact Cover problems. 
# https://www.ocf.berkeley.edu/~jchu/publicportal/sudoku/sudoku.paper.html
# This paper describes Dr. Donald Knuth's Dancing Link (DLX) algorithm to solve Exact Cover problems, as well as its relevancy to Sudoku
# While this page contains very short Java snippets, describing the core principles behind Knuth's DLX algorithm, 
# it does not contain a full source code, nor specifics on how to convert Sudoku to an Exact Cover problem
# https://www.geeksforgeeks.org/exact-cover-problem-algorithm-x-set-1/
# This page contains Psuedo code and helpful visuals for understanding DLX
# https://www.kth.se/social/files/58861771f276547fe1dbf8d1/HLaestanderMHarrysson_dkand14.pdf
# This paper describes the process of converting a Sudoku puzzle into an exact Cover problem 
# Specifically, a reduction method that doesn't use an intermediate matrix for the conversion, saving significant time *reportedly*


# DLX Data Structures:

class Node():

    def __init__(self, row, col, val):
        self.row = row
        self.col = col
        self.val = val
        self.leftNode = self
        self.upNode = self
        self.rightNode = self
        self.downNode = self

    def setColumnNode(self, columnNode): ## Don't forget to set these
        self.columnNode = columnNode


class ColumnNode(Node):

    def __init__(self):
        Node.__init__(self, -1, -1, -1)
        self.size = 0

    def cover(self):
        #Unlink our node from the list, while maintaining pointers to where we were in the list for easy re-insertion/backtracking
        self.rightNode.leftNode = self.leftNode
        self.leftNode.rightNode = self.rightNode

        #Now we unlink all of the nodes that share a row with nodes in our current column from the Matrix, while maintaining the original relationships for re-insertion
        verticalTraverseNode = self.downNode
        while (verticalTraverseNode is not self):
            horizontalTraverseNode = verticalTraverseNode.rightNode
            while(horizontalTraverseNode is not verticalTraverseNode):
                #Pull this node from our matrix, and update its ColumnNode so we can filter by the "shortest" column later
                horizontalTraverseNode.downNode.upNode = horizontalTraverseNode.upNode
                horizontalTraverseNode.upNode.downNode = horizontalTraverseNode.downNode
                horizontalTraverseNode.columnNode.size-=1
                
                horizontalTraverseNode = horizontalTraverseNode.rightNode
            verticalTraverseNode = verticalTraverseNode.downNode

    def uncover(self):
        #This is where our doubly linked list magic comes into play, and we re-insert a covered ColumnNode back into the Matrix, efficiently backtracking in ~O(1)
        verticalTraverseNode = self.upNode
        while (verticalTraverseNode is not self):
            horizontalTraverseNode = verticalTraverseNode.leftNode
            while(horizontalTraverseNode is not verticalTraverseNode):
                #Re-inserting the node into our Matrix, and undoing the adjustments to its ColumnNode size
                horizontalTraverseNode.upNode.downNode = horizontalTraverseNode
                horizontalTraverseNode.downNode.upNode = horizontalTraverseNode
                horizontalTraverseNode.columnNode.size+=1

                horizontalTraverseNode = horizontalTraverseNode.leftNode
            verticalTraverseNode = verticalTraverseNode.upNode
        self.rightNode.leftNode = self
        self.leftNode.rightNode = self







class Solver:
    ##########################################
    ####   Constructor
    ##########################################
    def __init__(self):
        self.definiteRows = []
        sys.setrecursionlimit(3000)
        pass

    ##########################################
    ####   Solver
    ##########################################

    #According to Knuth, it is faster at scale to use the shortest column first when branching
    def findShortestColumn(self, h):
        shortestColumn = h.rightNode
        column = shortestColumn
        while(column is not h):
            if(column.size == 1): #This is a significant 10-20% improvement on average for our test cases
                return column     
            if(column.size < shortestColumn.size):
                shortestColumn = column
            column = column.rightNode
        return shortestColumn

    def updateBoard(self, board, solutionRows):
        for n in solutionRows:
            if((n.col-1, n.row-1) in self.board.unsolved):
                self.board.placeValue((n.col-1, n.row-1), n.val)

    #Dancing Links "Algorithm X" as described by Knuth
    def DLXSearch(self, h, board, solutionRows):
        if(h.rightNode is h):
            self.updateBoard(board, solutionRows)
            return True
        column = self.findShortestColumn(h)
        column.cover()

        verticalTraverseNode = column.downNode
        while(verticalTraverseNode is not column):
            solutionRows.append(verticalTraverseNode)

            horizontalTraverseNode = verticalTraverseNode.rightNode
            while(horizontalTraverseNode is not verticalTraverseNode):
                horizontalTraverseNode.columnNode.cover()
                horizontalTraverseNode = horizontalTraverseNode.rightNode 

            if(self.DLXSearch(h, board, solutionRows)):
                return True

            solutionRows.pop()
            column = verticalTraverseNode.columnNode

            horizontalTraverseNode = verticalTraverseNode.leftNode
            while(horizontalTraverseNode is not verticalTraverseNode):
                horizontalTraverseNode.columnNode.uncover()
                horizontalTraverseNode = horizontalTraverseNode.leftNode

            verticalTraverseNode = verticalTraverseNode.downNode
        column.uncover()
        return False

    #This function generates 4 nodes, doubly linked in a circle, with a given rowNumber
    #For use in our Exact Cover constraint table (Every square/number value constrains 4 things)
    #1. That square itself from having another value
    #2. Its column from sharing a value
    #3. Its row from sharing a value
    #4. Its box from sharing a value
    def makeConstraintNodes(self, row, col, value):
        nodes = [None for _ in range(0, 4)]
        nodes[0] = Node(row, col, value)
        nodes[1] = Node(row, col, value)
        nodes[2] = Node(row, col, value)
        nodes[3] = Node(row, col, value)

        nodes[0].rightNode = nodes[1]
        nodes[1].rightNode = nodes[2]
        nodes[2].rightNode = nodes[3]
        nodes[3].rightNode = nodes[0]

        nodes[0].leftNode = nodes[3]
        nodes[1].leftNode = nodes[0]
        nodes[2].leftNode = nodes[1]
        nodes[3].leftNode = nodes[2]
        return nodes

    #This function generates 4 numbers representing the constraints columns given to the row in the DLX matrix
    def getConstraintValues(self, value, column, row, n):
        n2 = n * n
        constraints = [None for _ in range(0, 4)]
        
        constraints[0] = int(column + int(row * n2) ) #Constrain our solution to have one value per box
        constraints[1] = int(value + int(row * n2) ) + (n2*n2) #Constrain our solution to have one of each value per row
        constraints[2] = int(value + int(column * n2) ) + (n2*n2)*2 #Constrain our solution to have one of each value per column
        boxNumber = int(column / n) + int(int(row / n) * n)
        # 0 | 1 | 2
        # 3 | 4 | 5
        # 6 | 7 | 8
        
        constraints[3] = int(value + int(boxNumber*n2)) + (n2*n2)*3 #Constrain our solution to have one of each value per box
        return constraints
        


    #This will convert our sudoku board into an Exact Cover problem (more specifically, directly into a DLX problem, saving us some time in the reduction step)
    #This function comes from the verbal description of the reduction algorithm in "Solving Sudoku efficiently with Dancing Links" 
    def sudokuToExactCover(self, board):
        headerNode = ColumnNode()

        columnNodes = [ColumnNode() for _ in range(0, 4 * (self.board.n2*self.board.n2))]

        headerNode.rightNode = columnNodes[0]
        columnNodes[0].leftNode = headerNode

        
        for x in range(1, len(columnNodes)):
            columnNodes[x-1].rightNode = columnNodes[x]
            columnNodes[x].leftNode = columnNodes[x-1]
        columnNodes[len(columnNodes)-1].rightNode = headerNode
        headerNode.leftNode = columnNodes[len(columnNodes) - 1]


        for space in board.unsolved:
             sudokuCol = space[0]
             sudokuRow = space[1]
             for value in range(1, self.board.n2 + 1):     
                if(value in self.board.valuesInBoxes[board.spaceToBox(sudokuCol,sudokuRow)]):
                    continue
                if(value in self.board.valuesInRows[sudokuCol]): 
                    continue
                if(value in self.board.valuesInCols[sudokuRow]):
                    continue
                nodes = self.makeConstraintNodes(sudokuRow+1, sudokuCol+1, value)
                constraintValues = self.getConstraintValues(value-1, sudokuCol, sudokuRow, board.n)

                #Insert our nodes into our DLX matrix
                for x in range(0, 4):
                    nodes[x].downNode = columnNodes[constraintValues[x]].downNode
                    nodes[x].downNode.upNode = nodes[x]
                    nodes[x].upNode = columnNodes[constraintValues[x]]
                    columnNodes[constraintValues[x]].downNode = nodes[x]

                    #Don't forget these lines, it'll let us search by "shortest" column later!
                    nodes[x].setColumnNode(columnNodes[constraintValues[x]])
                    nodes[x].columnNode.size += 1
        for space in board.board:
            sudokuCol = space[0]
            sudokuRow = space[1]
            #This space is already populated, making this step easy for us
            #This is also an efficiency gain in the DLX algorithm execution
            #We're reducing the number of rows by n2-1 every time we have a pre-filled space
            value = board.board[(sudokuCol,sudokuRow)]
            nodes = self.makeConstraintNodes(sudokuRow+1, sudokuCol+1, value)
            constraintValues = self.getConstraintValues(value-1, sudokuCol, sudokuRow, board.n)
            
            #Insert our nodes into our DLX matrix
            for x in range(0, 4):
                nodes[x].downNode = columnNodes[constraintValues[x]].downNode
                nodes[x].downNode.upNode = nodes[x]
                nodes[x].upNode = columnNodes[constraintValues[x]]
                columnNodes[constraintValues[x]].downNode = nodes[x]

                #Don't forget these lines, it'll let us search by "shortest" column later!
                nodes[x].setColumnNode(columnNodes[constraintValues[x]])
                nodes[x].columnNode.size -= 1000 #I made this a huge number, because we want to target these columns with solved spaces in them first.
        return headerNode

    # returns True if a solution exists and False if one does not
    def solve(self, board):
        # We first must convert the sudoku puzzle into an Exact Cover problem
        self.board = board
        if (len(self.board.unsolved) == 0):
            return True
        exactCover = self.sudokuToExactCover(board)

        return self.DLXSearch(exactCover, board, [])
