# General code
from abc import ABC, abstractmethod

class Game(ABC):
	@staticmethod
	@abstractmethod
	def init_state():
		return None
	
	@staticmethod
	@abstractmethod
	def legal_moves(state):
		return []
	
	@staticmethod
	@abstractmethod
	def make_move(state, move):
		return state
	
	@staticmethod
	@abstractmethod
	def who_winner(state):
		return None


# Particular implementation
from enum import Enum

class Player(Enum):
	ONE = 1
	TWO = 2
	
	@property
	def next(self):
		return Player((self.value + 1) % 2)

class TicTacToe(Game):
	def init_state():
		return ([[None for j in range(3)] for i in range(3)], Player.ONE)
	
	def legal_moves(state):
		brd = state[0]
		moves = []
		for i in range(3):
			for j in range(3):
				if brd[i][j] is None:
					moves.append((i, j))
		return moves
	
	def make_move(state, (i, j)):
		state[0][i][j] = state[1]
		state[1] = state[1].next
		return state
	
	def who_winner(state):
		brd = state[0]
		
		# Check rows
		for i in range(3):
			pl = brd[i][0]
			if pl is None:
				continue
			
			iswin = True
			for j in range(1, 3):
				if pl != brd[i][j]:
					iswin = False
					break
			
			if iswin:
			 	return pl
		
		# Check columns
		for j in range(3):
			pl = brd[0][j]
			if pl is None:
				continue
			
			iswin = True
			for i in range(1, 3):
				if pl != brd[i][j]:
					iswin = False
					break
			
			if iswin:
			 	return pl
		
		# Check diagonals
		if brd[0][0] is not None and brd[0][0] == brd[1][1] and brd[1][1] == brd[2][2]:
			return brd[0][0]
		
		if brd[0][2] is not None and brd[0][2] == brd[1][1] and brd[1][1] == brd[2][0]:
			return brd[0][2]
		
		return None
