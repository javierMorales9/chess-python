import re


class Position:
    def __init__(self, row, col):
        if row < 0 or row > 7 or col < 0 or col > 7:
            raise Exception("Invalid position: out of bounds")

        self.row = row
        self.col = col

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

    def isForward(self, origin, distance, turn):
        if turn.isBlack():
            return origin.row - self.row == distance and self.col == origin.col
        else:
            return self.row - origin.row == distance and self.col == origin.col

    def isInDiagonalForward(self, origin, distance, turn):
        if turn.isBlack():
            return (
                origin.row - self.row == distance
                and abs(self.col - origin.col) == distance
            )
        else:
            return (
                self.row - origin.row == distance
                and abs(self.col - origin.col) == distance
            )


pawnRules = [
    {
        "description": "Pawn moves two cells forwars as first move",
        "precons": [
            {
                "description": "Pawn is in its first position",
                "fn": lambda move, board, originalPosition, turn: move.origin
                == originalPosition,
            },
            {
                "description": "Pawn is not blocked",
                "fn": lambda move, board, originalPosition, turn: not board.isPieceInPosition(
                    move.dest
                ),
            },
            {
                "description": "Pawn moves two cells forward",
                "fn": lambda move, board, originalPosition, turn: move.dest.isForward(
                    move.origin, 2, turn
                ),
            },
        ],
        "postcon": lambda move, board: [
            (move.origin, None),
            (move.dest, board.pieceInPosition(move.origin)),
        ],
    },
    {
        "description": "Pawn moves one cells forward",
        "precons": [
            {
                "description": "Pawn is not blocked",
                "fn": lambda move, board, originalPosition, turn: not board.isPieceInPosition(
                    move.dest
                ),
            },
            {
                "description": "Pawn moves one cell forward",
                "fn": lambda move, board, originalPosition, turn: move.dest.isForward(
                    move.origin, 1, turn
                ),
            },
        ],
        "postcon": lambda move, board: [
            (move.origin, None),
            (move.dest, board.pieceInPosition(move.origin)),
        ],
    },
    {
        "description": "Pawn takes an enemy piece",
        "precons": [
            {
                "description": "Destination Piece belongs to enemy",
                "fn": lambda move, board, originalPosition, turn: board.pieceInPosition(
                    move.dest
                )
                and not turn.doesPieceBelongToTurn(board.pieceInPosition(move.dest)),
            },
            {
                "description": "Enemy piece in 1 diagonal forward position",
                "fn": lambda move, board, originalPosition, turn: move.dest.isInDiagonalForward(
                    move.origin, 1, turn
                ),
            },
        ],
        "postcon": lambda move, board: [
            (move.origin, None),
            (move.dest, board.pieceInPosition(move.origin)),
        ],
    },
]

towerRules = [
    {
        "description": "Castling",
        "precons": [
            {
                "description": "The piece is in its original position",
                "fn": lambda move, board, originalPosition, turn: move.origin
                == originalPosition,
            },
            {
                "description": "King is in its original position",
                "fn": lambda move, board, originalPosition, turn: board.isKingInOriginalPosition(
                    turn
                ),
            },
            {
                "description": "Destination is right next to the king",
                "fn": lambda move, board, originalPosition, turn: move.dest.col == 3
                or move.dest.col == 5,
            },
            {
                "description": "There are no pieces in the way",
                "fn": lambda move, board, originalPosition, turn: len(
                    board.piecesInLine(move.origin, move.dest)
                )
                == 0,
            },
        ],
        "postcon": lambda move, board: [
            (move.origin, None),
            (move.dest, board.pieceInPosition(move.origin)),
            (
                Position(move.dest.row, 2 if move.dest.col == 3 else 6),
                board.pieceInPosition(Position(move.dest.row, 4)),
            ),
            (Position(move.dest.row, 4), None),
        ],
    },
    {
        "description": "Tower moves in a straight line",
        "precons": [
            {
                "description": "There is a straight line between origin and destination",
                "fn": lambda move, board, originalPosition, turn: move.origin.row
                == move.dest.row
                or move.origin.col == move.dest.col,
            },
            {
                "description": "The destination is not an ally",
                "fn": lambda move, board, originalPosition, turn: not turn.doesPieceBelongToTurn(
                    board.pieceInPosition(move.dest)
                ),
            },
            {
                "description": "There are no pieces in the way",
                "fn": lambda move, board, originalPosition, turn: len(
                    board.piecesInLine(move.origin, move.dest)
                )
                == 0,
            },
        ],
        "postcon": lambda move, board: [
            (move.origin, None),
            (move.dest, board.pieceInPosition(move.origin)),
        ],
    },
]

kingRules = [
    {
        "description": "King moves one cell in any direction",
        "precons": [
            {
                "description": "There is a straight line between origin and destination",
                "fn": lambda move, board, originalPosition, turn: abs(
                    move.origin.row - move.dest.row
                )
                <= 1
                and abs(move.origin.col - move.dest.col) <= 1,
            },
        ],
        "postcon": lambda move, board: [
            (move.origin, None),
            (move.dest, board.pieceInPosition(move.origin)),
        ],
    },
    {
        "description": "Castling",
        "precons": [
            {
                "description": "The piece is in its original position",
                "fn": lambda move, board, originalPosition, turn: move.origin
                == originalPosition,
            },
            {
                "description": "The destination is correct",
                "fn": lambda move, board, originalPosition, turn: move.dest.col == 2
                or move.dest.col == 6,
            },
            {
                "description": "The corresponding tower is in its original position",
                "fn": lambda move, board, originalPosition, turn: board.isTower(
                    Position(move.origin.row, 0 if move.dest.col == 2 else 7), turn
                ),
            },
            {
                "description": "There are no pieces in the way",
                "fn": lambda move, board, originalPosition, turn: len(
                    board.piecesInLine(move.origin, move.dest)
                )
                == 0,
            },
        ],
        "postcon": lambda move, board: [
            (move.origin, None),
            (move.dest, board.pieceInPosition(move.origin)),
            (
                Position(move.dest.row, 3 if move.dest.col == 2 else 5),
                board.pieceInPosition(
                    Position(move.dest.row, 0 if move.dest.col == 2 else 7)
                ),
            ),
            (Position(move.dest.row, 0 if move.dest.col == 2 else 7), None),
        ],
    },
]

whitePawnNames = ["PW1", "PW2", "PW3", "PW4", "PW5", "PW6", "PW7", "PW8"]
blackPawnNames = ["PB1", "PB2", "PB3", "PB4", "PB5", "PB6", "PB7", "PB8"]

whiteRightTowerName = "TWR"
whiteLeftTowerName = "TWL"
blackRightTowerName = "TBR"
blackLeftTowerName = "TBL"

whiteKingName = "RWW"
blackKingName = "RBB"

pieces = {}
for name in whitePawnNames:
    pieces[name] = {
        "originalPosition": Position(1, whitePawnNames.index(name)),
        "rules": pawnRules,
    }

for name in blackPawnNames:
    pieces[name] = {
        "originalPosition": Position(6, blackPawnNames.index(name)),
        "rules": pawnRules,
    }

pieces[whiteLeftTowerName] = {
    "originalPosition": Position(0, 0),
    "rules": towerRules,
}

pieces[whiteRightTowerName] = {
    "originalPosition": Position(0, 7),
    "rules": towerRules,
}

pieces[blackLeftTowerName] = {
    "originalPosition": Position(7, 0),
    "rules": towerRules,
}

pieces[blackRightTowerName] = {
    "originalPosition": Position(7, 7),
    "rules": towerRules,
}

pieces[whiteKingName] = {
    "originalPosition": Position(0, 4),
    "rules": kingRules,
}

pieces[blackKingName] = {
    "originalPosition": Position(7, 4),
    "rules": kingRules,
}


class Cell:
    def __init__(self, position, piece):
        self.position = position
        self.piece = piece

    def setPiece(self, piece):
        self.piece = piece

    def removePiece(self):
        self.piece = None

    def hasPiece(self):
        return self.piece is not None


class Move:
    def __init__(self, moveStr: str):
        match = re.search("([A-H])([1-8]) - ([A-H])([1-8])", moveStr)

        if match is not None:
            data = match.groups(0)
            origin = Position(int(data[1]) - 1, ord(str(data[0])) - ord("A"))
            destination = Position(int(data[3]) - 1, ord(str(data[2])) - ord("A"))

            if origin == destination:
                raise Exception("Invalid move: origin and destination are the same")

            self.origin = origin
            self.dest = destination
        else:
            raise Exception("Invalid move: bad format")


class Board:
    def __init__(self):
        self.board = [[Cell(Position(y, x), None) for x in range(8)] for y in range(8)]

        for piece in pieces:
            pos = pieces[piece]["originalPosition"]
            cell = self.board[pos.row][pos.col]
            cell.setPiece(piece)

    def getCell(self, pos):
        return self.board[pos.row][pos.col]

    def columnNumber(self):
        return len(self.board)

    def rowNumber(self):
        return len(self.board[0])

    def setPiece(self, pos, piece):
        cell = self.getCell(pos)
        cell.setPiece(piece)

    def isPieceInPosition(self, pos):
        return self.getCell(pos).hasPiece()

    def pieceInPosition(self, pos):
        return self.getCell(pos).piece

    def piecesInLine(self, origin, dest):
        if origin.row == dest.row:
            return self.piecesInRow(origin, dest)
        elif origin.col == dest.col:
            return self.piecesInColumn(origin, dest)
        else:
            raise Exception(
                "Invalid move: origin and destination are not in the same line"
            )

    def piecesInRow(self, origin, dest):
        if origin.col > dest.col:
            origin, dest = dest, origin

        pieces = []
        for col in range(origin.col + 1, dest.col):
            cell = self.getCell(Position(origin.row, col))
            if cell.hasPiece():
                pieces.append(cell.piece)

        return pieces

    def piecesInColumn(self, origin, dest):
        if origin.row > dest.row:
            origin, dest = dest, origin

        pieces = []
        for row in range(origin.row + 1, dest.row):
            cell = self.getCell(Position(row, origin.col))
            if cell.hasPiece():
                pieces.append(cell.piece)

        return pieces

    def isKingInOriginalPosition(self, turn):
        if turn.isBlack():
            return (
                self.pieceInPosition(pieces[blackKingName]["originalPosition"])
                == blackKingName
            )
        else:
            return (
                self.pieceInPosition(pieces[whiteKingName]["originalPosition"])
                == whiteKingName
            )

    def isTower(self, pos, turn):
        piece = self.pieceInPosition(pos)
        if turn.isBlack():
            return piece == blackRightTowerName or piece == blackLeftTowerName
        else:
            return piece == whiteRightTowerName or piece == whiteLeftTowerName


class Turn:
    def __init__(self):
        self.turn = "W"

    def doesPieceBelongToTurn(self, piece):
        if piece is None:
            return False

        return piece[1] == self.turn

    def toggle(self):
        if self.turn == "W":
            self.turn = "B"
        else:
            self.turn = "W"

    def isBlack(self):
        return self.turn == "B"


class Game:
    def __init__(self, painter):
        self.board = Board()
        self.turn = Turn()
        self.painter = painter

    def nextTurn(self):
        self.turn.toggle()

    def paint(self):
        self.painter.paint(self.board)

    def executeMove(self, move):
        self.move = move

        pieceName = self.getPieceNameFromBoard()
        self.checkIfPieceBelongsToTurn(pieceName)
        self.pieceData = pieces[pieceName]

        rule = self.getFirstValidRule()

        if not rule:
            raise Exception("Invalid move: The move contradicts the rules of the piece")

        self.applyRule(rule)

    def getPieceNameFromBoard(self):
        pieceName = self.board.pieceInPosition(self.move.origin)

        if pieceName is None:
            raise Exception("Invalid move: there is no piece in the origin position")

        return pieceName

    def checkIfPieceBelongsToTurn(self, pieceName):
        if not self.turn.doesPieceBelongToTurn(pieceName):
            raise Exception("Invalid move: piece does not belong to current player")

    def getFirstValidRule(self):
        rules = self.pieceData["rules"]

        for rule in rules:
            if self.validPrecons(rule["precons"]):
                return rule

        return None

    def validPrecons(self, precons):
        move = self.move
        board = self.board
        originalPosition = self.pieceData["originalPosition"]
        turn = self.turn

        for precon in precons:
            if not precon["fn"](move, board, originalPosition, turn):
                return False

        return True

    def applyRule(self, rule):
        postcon = rule["postcon"]
        move = self.move
        board = self.board

        for cellState in postcon(move, board):
            print(cellState[0].row, cellState[0].col, cellState[1])
            board.setPiece(cellState[0], cellState[1])

    def hasWon(self):
        return False


class BoardPainter:
    def paint(self, board):
        for row in reversed(range(board.rowNumber())):
            print(row + 1, end="  ")
            for col in range(board.columnNumber()):
                piece = board.pieceInPosition(Position(row, col))
                if not piece:
                    print("", end="    ")
                else:
                    print(piece, end=" ")
            print()
        print("    A   B   C   D   E   F   G   H")


painter = BoardPainter()
game = Game(painter)
while True:
    game.paint()
    moveStr = input("Enter move in the format A1 - B2: ")

    try:
        move = Move(moveStr)
        game.executeMove(move)

        if game.hasWon():
            print("Player " + game.turn.turn + " wins!")
            break

        game.nextTurn()
    except Exception as e:
        print(e)
