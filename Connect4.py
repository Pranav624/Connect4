import random
import math
import pickle

class Node:
    def __init__(self, state, player, parent=None):
        self.state = state
        self.player = player
        self.children = []
        self.visits = 0
        self.score = 0
        self.parent = parent

    def select_child(self):
        total_visits = sum(child.visits for child in self.children)
        log_exploration_value = math.log(total_visits + 1e-8) if total_visits else 0

        def ucb_score(node):
            return node.score / (node.visits + 1e-8) + math.sqrt(log_exploration_value / (node.visits + 1e-8))

        return max(self.children, key=ucb_score)

    def expand(self):
        possible_moves = self.state.get_possible_moves()
        for move in possible_moves:
            new_state = self.state.make_move(move, self.player)
            new_player = 'O' if self.player == 'X' else 'X'
            child = Node(new_state, new_player, parent=self)
            self.children.append(child)
        return self.children

    def simulate(self):
        state = self.state.copy()
        player = self.player
        while not state.is_terminal():
            possible_moves = state.get_possible_moves()
            move = random.choice(possible_moves)
            state = state.make_move(move, player)
            player = 'O' if player == 'X' else 'X'
        return state.evaluate()

    def backpropagate(self, score):
        self.visits += 1
        self.score += score
        if self.parent:
            self.parent.backpropagate(-score)

class Connect4:
    def __init__(self):
        self.board = [[' ' for _ in range(7)] for _ in range(6)]
        self.player = 'X'

    def copy(self):
        new_board = Connect4()
        new_board.board = [row[:] for row in self.board]
        new_board.player = self.player
        return new_board

    def get_possible_moves(self):
        return [col for col in range(7) if self.board[0][col] == ' ']

    def make_move(self, col, player):
        new_board = self.copy()
        for row in range(5, -1, -1):
            if new_board.board[row][col] == ' ':
                new_board.board[row][col] = player
                break
        new_board.player = 'O' if player == 'X' else 'X'
        return new_board

    def is_terminal(self):
        # Check for horizontal wins
        for row in range(6):
            for col in range(4):
                if self.board[row][col] != ' ' and all(self.board[row][col+i] == self.board[row][col] for i in range(4)):
                    return True

        # Check for vertical wins
        for row in range(3):
            for col in range(7):
                if self.board[row][col] != ' ' and all(self.board[row+i][col] == self.board[row][col] for i in range(4)):
                    return True

        # Check for diagonal wins (positive slope)
        for row in range(3):
            for col in range(4):
                if self.board[row][col] != ' ' and all(self.board[row+i][col+i] == self.board[row][col] for i in range(4)):
                    return True

        # Check for diagonal wins (negative slope)
        for row in range(3):
            for col in range(3, 7):
                if self.board[row][col] != ' ' and all(self.board[row+i][col-i] == self.board[row][col] for i in range(4)):
                    return True

        # Check for a tie
        if all(self.board[0][col] != ' ' for col in range(7)):
            return True

        return False

    def evaluate(self):
        # Check for horizontal wins
        for row in range(6):
            for col in range(4):
                if self.board[row][col] != ' ' and all(self.board[row][col+i] == self.board[row][col] for i in range(4)):
                    return 1 if self.board[row][col] == 'X' else -1

        # Check for vertical wins
        for row in range(3):
            for col in range(7):
                if self.board[row][col] != ' ' and all(self.board[row+i][col] == self.board[row][col] for i in range(4)):
                    return 1 if self.board[row][col] == 'X' else -1

        # Check for diagonal wins (positive slope)
        for row in range(3):
            for col in range(4):
                if self.board[row][col] != ' ' and all(self.board[row+i][col+i] == self.board[row][col] for i in range(4)):
                    return 1 if self.board[row][col] == 'X' else -1

        # Check for diagonal wins (negative slope)
        for row in range(3):
            for col in range(3, 7):
                if self.board[row][col] != ' ' and all(self.board[row+i][col-i] == self.board[row][col] for i in range(4)):
                    return 1 if self.board[row][col] == 'X' else -1

        return 0

def mcts(root, iterations):
    for _ in range(iterations):
        node = root
        while node.children and not node.state.is_terminal():
            node = node.select_child()
        if not node.state.is_terminal():
            node = node.expand()[0]
        score = node.simulate()
        node.backpropagate(score)
    return max(root.children, key=lambda node: node.visits)

def load_or_create_tree():
    try:
        with open('game_tree.pkl', 'rb') as f:
            root = pickle.load(f)
    except (FileNotFoundError, EOFError):
        root = Node(Connect4(), 'X')
    return root

def reset_tree():
    root = Node(Connect4(), 'X')
    save_tree(root)
    return root

def save_tree(root):
    with open('game_tree.pkl', 'wb') as f:
        pickle.dump(root, f)

def play_game():
    root = load_or_create_tree()
    game = root.state
    while not game.is_terminal():
        best_child = mcts(root, 1000)
        game = best_child.state
        root = best_child
        print('\n'.join([''.join(row) for row in game.board]))
        print()
    score = game.evaluate()
    print("Game over. Result:", "Draw" if score == 0 else "X wins" if score == 1 else "O wins")
    root.backpropagate(score)
    save_tree(root)

if __name__ == "__main__":
    root = reset_tree()
    play_game()