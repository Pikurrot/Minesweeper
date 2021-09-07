import pygame
from collections import namedtuple, deque
import numpy as np
from numpy.random import randint, seed
import copy
import sys, os

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

#Initial variables

map_size = namedtuple('map_size', ('x y'))
alg_used = [[0,0],[0,0],[0,0],0,0]

#Set parameters
difficulty = 0.15
map_size.x, map_size.y = 30, 30
mine_num = max(round(map_size.x*map_size.y*difficulty), 0)
random_seed = randint(1000000) #882001#653240#189374


#Set configuration
pygame.init()
screen = pygame.display.set_mode((16*map_size.x, 16*map_size.y))
pygame.display.set_caption('Minesweeper')

#Load images
pyimg = pygame.image
mine_img,tile_img,tile0_img,tile1_img,tile2_img,tile3_img,tile4_img,tile5_img,tile6_img,tile7_img,tile8_img,flag_img,mine_boom_img, \
mine_flagged_img,no_mine_img = pyimg.load('tile_mine.png'),pyimg.load('tile.png'),pyimg.load('tile0.png'),pyimg.load('tile1.png'),\
pyimg.load('tile2.png'),pyimg.load('tile3.png'),pyimg.load('tile4.png'),pyimg.load('tile5.png'),pyimg.load('tile6.png'),pyimg.load('tile7.png'),\
pyimg.load('tile8.png'),pyimg.load('tile_flag.png'),pyimg.load('tile_mine_finded.png'),pyimg.load('tile_mine_flagged.png'),pyimg.load('tile_no_mine.png')

tiles = [tile0_img, tile1_img, tile2_img, tile3_img, tile4_img, tile5_img, tile6_img, tile7_img, tile8_img]

class Map():

	def __init__(self):
		global grid, grid_view
		self.finded_mines = deque([])
		#Set grid to default
		grid = np.full((map_size.y, map_size.x), None)
		grid_view = grid.copy()
		seed(random_seed)

		#Put mines
		mine_num_2 = copy.deepcopy(mine_num)
		while mine_num_2 > 0:
			rand_x = randint(map_size.x)
			rand_y = randint(map_size.y)
			if grid[rand_y,rand_x] == None:
				grid[rand_y,rand_x] = 'mine'
				mine_num_2 -= 1

		#Put nums
		for y_pos in range(map_size.y):
			for x_pos in range(map_size.x):
				if grid[y_pos,x_pos] != 'mine':
					grid[y_pos,x_pos] = self.count_mines(x_pos,y_pos)

		seed()

	def count_mines(self, x_pos, y_pos):
		count = 0
		n_tiles = self.neighbour_tiles(x_pos,y_pos,grid_view)
		for tile in n_tiles:
			count += grid[tile[1],tile[0]] == 'mine'
		return count	

	def neighbour_tiles(self, x_tile, y_tile, grid):
		n_tiles = []
		map_size2 = (len(grid[0]),len(grid))
		for x in range(x_tile-1, x_tile+2):
			if x>=0 and x<map_size2[0]:
				for y in range(y_tile-1, y_tile+2):
					if y>=0 and y<map_size2[1] and not (x==x_tile and y==y_tile):
						n_tiles.append((x,y))
		return n_tiles

	def hidden_tiles(self, x_tile, y_tile, grid):
		hidden_tiles = []
		for tile in self.neighbour_tiles(x_tile, y_tile,grid):
			if grid[tile[1],tile[0]] == None:
				hidden_tiles.append(tile)
		return hidden_tiles

	def flag_tiles(self, x_tile, y_tile, grid):
		flag_tiles = []
		for tile in self.neighbour_tiles(x_tile, y_tile,grid):
			if grid[tile[1],tile[0]] == 'flag':
				flag_tiles.append(tile)
		return flag_tiles

	def possible_tiles(self, x_tile, y_tile, grid):
		#tiles that are nums and num-flagsnum==1
		possible_tiles = []
		if grid[y_tile,x_tile] in range(9):
			if grid[y_tile,x_tile] - len(self.flag_tiles(x_tile,y_tile,grid)) == 1:
				for tile in self.hidden_tiles(x_tile, y_tile, grid):
					possible_tiles.append(tile)
		return possible_tiles

	def show_tile(self, x_tile, y_tile):
		global running, updated, hidden
		if grid[y_tile, x_tile] == 'mine':
			print('mine BOOM at',(x_tile,y_tile))
			for y_pos in range(map_size.y):
				for x_pos in range(map_size.x):
					if grid[y_pos,x_pos] == 'mine':
						if grid_view[y_pos, x_pos] == 'flag':
							grid_view[y_pos, x_pos] = 'mine_flagged'
						else:
							grid_view[y_pos, x_pos] = 'mine'
			grid_view[y_tile, x_tile] = 'boom'
			updated = True
		elif grid[y_tile, x_tile] == 0:
			zero_tiles_queue = deque([(x_tile,y_tile)])
			while len(zero_tiles_queue) > 0:
				tile = zero_tiles_queue.popleft()
				grid_view[tile[1], tile[0]] = grid[tile[1], tile[0]]
				if tile in hidden:
					hidden.remove(tile)
				n_tiles = self.neighbour_tiles(tile[0],tile[1],grid_view)
				for av_tile in n_tiles:
					if grid_view[av_tile[1],av_tile[0]] != grid[av_tile[1],av_tile[0]]:
						if grid[av_tile[1],av_tile[0]] == 0 and ((av_tile[0],av_tile[1]) not in zero_tiles_queue):
							zero_tiles_queue.append(tuple(av_tile))
						else:
							grid_view[av_tile[1],av_tile[0]] = grid[av_tile[1],av_tile[0]]
							hidden.remove(av_tile)

		else:
			grid_view[y_tile, x_tile] = grid[y_tile, x_tile]
			if (x_tile,y_tile) in hidden:
				hidden.remove((x_tile,y_tile))
			print('showed',(x_tile,y_tile))

	def search_mine(self, algorithm, map_type, grid):
		global updated,alg_used,hidden,running
		print('. algorithm',algorithm,'searching in',map_type,'map...')
		if map_type == 'possible':
			mines = deque([])
			no_mines = deque([])
		for y_tile,row in enumerate(grid):
			for x_tile,value in enumerate(row):
				hidden_tiles = self.hidden_tiles(x_tile,y_tile, grid)
				flag_tiles = self.flag_tiles(x_tile,y_tile,grid)
				if algorithm == '1 & 2' and value in range(9):
					if len(flag_tiles) == value and len(hidden_tiles) > 0:
						#algorithm 2
						if map_type == 'real':
							alg_used[1][0] += 1
							alg_used[1][1] += 1
							print('hidden tiles of',(x_tile,y_tile),':',hidden_tiles)
							for hidden_tile in hidden_tiles:
								print('showing',hidden_tile,'...')
								self.show_tile(hidden_tile[0], hidden_tile[1])
								updated = True
						else:
							alg_used[1][0] += 1
							print('hidden tiles of',(x_tile,y_tile),':',hidden_tiles)
							for hidden_tile in hidden_tiles:
								if hidden_tile not in no_mines:
									no_mines.append(hidden_tile)

					elif len(hidden_tiles) + len(flag_tiles) <= value:
						#algorithm 1
						if map_type == 'real':
							alg_used[0][0] += 1
							alg_used[0][1] += 1
							for tile in hidden_tiles:
								if tile not in self.finded_mines:
									self.finded_mines.append(tile)
									print('mine {} finded near {}; this tile has {} hidden tiles near {}, and {} flag tiles {}, with neighbours {}'\
										.format(tile, (x_tile,y_tile), len(hidden_tiles), hidden_tiles, len(flag_tiles),\
										flag_tiles, self.neighbour_tiles(tile[0],tile[1],grid)))
						else:
							alg_used[0][0] += 1
							for tile in hidden_tiles:
								if tile not in mines:
									mines.append(tile)
									print('mine {} finded near {}; this tile has {} hidden tiles near {}, and {} flag tiles {}, with neighbours {}'\
										.format(tile, (x_tile,y_tile), len(hidden_tiles), hidden_tiles, len(flag_tiles),\
										flag_tiles, self.neighbour_tiles(tile[0],tile[1],grid)))

				elif algorithm == '3':
					#algorithm 3
					alg_used[2][0] += 1
					if map_type == 'real':
						alg_used[2][1] += 1
					near_possible = set()
					possible_tiles_A = set(self.possible_tiles(x_tile,y_tile,grid))
					for possible_tile in possible_tiles_A:
						for neighbour_tile in self.neighbour_tiles(possible_tile[0],possible_tile[1],grid):
							if grid[neighbour_tile[1],neighbour_tile[0]] in range(9) and neighbour_tile != (x_tile,y_tile):
								near_possible.add(neighbour_tile)
						break
					for tile_B in near_possible:
						if grid[tile_B[1],tile_B[0]] - len(self.flag_tiles(tile_B[0],tile_B[1],grid)) == 1:
							hidden_tiles_B = set(self.hidden_tiles(tile_B[0],tile_B[1],grid))
							if possible_tiles_A.issubset(hidden_tiles_B):
								for hidden_tile in hidden_tiles_B:
									if hidden_tile not in possible_tiles_A:
										print('possible tiles of',(x_tile,y_tile),':',possible_tiles_A)
										print('near possible tiles :',near_possible)
										print('hidden tiles of',(tile_B[0],tile_B[1]),':',hidden_tiles_B)
										if map_type == 'real':
											print('showing',hidden_tile,'...')
											self.show_tile(hidden_tile[0], hidden_tile[1])
											updated = True
										else:
											no_mines.append((hidden_tile[0], hidden_tile[1]))

		if algorithm == '4':
			#algorithm 4
			alg_used[3] += 1

			#Variables
			hidden_group = []
			surrounding_nums = []
			p_to_check = deque()
			finalists = {}

			#Get hidden tiles and create new map
			hidden_list = deque([hidden[0]])
			while len(hidden_list) > 0:
				hidden_tile = hidden_list.popleft()
				for hidden_tile2 in self.hidden_tiles(hidden_tile[0],hidden_tile[1],grid):
					if hidden_tile2 not in hidden_group:
						hidden_group.append(hidden_tile2)
						hidden_list.append(hidden_tile2)
			#	x_small,y_small,x_big,_y_big
			print('hidden_group:',hidden_group)
			edges = [hidden_group[0][0],hidden_group[0][1],hidden_group[0][0],hidden_group[0][1]]
			for (x,y) in hidden_group:
			    edges[0] = min(edges[0],x)
			    edges[1] = min(edges[1],y)
			    edges[2] = max(edges[2],x)
			    edges[3] = max(edges[3],y)	

			p=2
			#	x_small, y_small, x_big, y_big
			edges = [edges[0]-min(edges[0],p),edges[1]-min(edges[1],p),edges[2]+1+min(len(grid[0])-edges[2],p),edges[3]+1+min(len(grid)-edges[3],p)]

			#	y_small : y_big, x_small : x_big
			new_grid = grid_view.copy()[edges[1] : edges[3],
										edges[0] : edges[2]]

			#Get surrounding numbers

			hidden_group = list(map(lambda t: (t[0]-edges[0],t[1]-edges[1]), hidden_group))
			print('hidden_group:',hidden_group)
			for hidden_tile in hidden_group:
				neighbours = self.neighbour_tiles(hidden_tile[0],hidden_tile[1],new_grid)
				print('len neighbours:',len(neighbours))
				surrounding_extension = [tile for tile in neighbours if new_grid[tile[1],tile[0]] in range(9) and tile not in surrounding_nums]
				surrounding_nums += surrounding_extension

			#Start the algorithm in one of the numbers
			print('surrounding_nums:',surrounding_nums)
			for tile in surrounding_nums:
				if new_grid[tile[1],tile[0]] - len(self.flag_tiles(tile[0],tile[1],new_grid)) == 1:
					possible = self.possible_tiles(tile[0],tile[1],new_grid)
					print('possible:',possible)
					possibilities = len(possible)
					relative_tile = tile
					for i in range(possibilities):
						#								   new_grid, 	     relative,   possible,	mines,	  no mines, for other possibilities
						p_to_check.append({'p.'+str(i+1):[new_grid.copy(),relative_tile,possible[i],deque([]),deque([]),{}]})
					break

			if len(p_to_check) == 0:
				surrounding_nums = set(map(lambda t: (t[0]+edges[0],t[1]+edges[1]), surrounding_nums))
				hidden_of_surrounding = set()
				for surrounding in surrounding_nums:
					for hidden_tile in self.hidden_tiles(surrounding[0],surrounding[1],grid_view):
						hidden_of_surrounding.add(hidden_tile)
				print('new_grid:',new_grid)
				return hidden_of_surrounding,0

			screen = pygame.display.set_mode((16*len(new_grid[0]), 16*len(new_grid)))
			updated2 = True
			running2 = True
			next_p = False
			pause = False
			p_end = True

			current_p = p_to_check.pop()
			_p = next(iter(current_p))
			next_p = False
			print('current p:',current_p)
			finded_mines = deque([])
			finded_no_mines = deque([])
			print('flagging',current_p[_p][2],'in',_p,'...')
			current_p[_p][0][current_p[_p][2][1],current_p[_p][2][0]] = 'flag'
			current_p[_p][3].append(current_p[_p][2])
			search = 0

			while True:
				f = [0,_p]
				#pause = True

				#Quit button
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						running2 = False
						running = False
					elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
						pause = False

				#Check all numbers match with neighbour flags
				if not pause:
					for tile in surrounding_nums:
						if len(self.hidden_tiles(tile[0],tile[1],current_p[_p][0])) == 0:
							f[0] += 1
							flag_tiles = len(self.flag_tiles(tile[0],tile[1],current_p[_p][0]))
							if current_p[_p][0][tile[1],tile[0]] != flag_tiles:
								print('tile',tile,' with num:',current_p[_p][0][tile[1],tile[0]],'not match with num of flags:',flag_tiles)
								if len(p_to_check) == 0:
									p_end = True
								else:
									next_p = True
								break
					if f[0] == len(surrounding_nums):
						finalists.update(current_p)
						print(_p, 'added at finalists')
						#print('finalists:',finalists)

				#Pass to next possibility
				if next_p and len(p_to_check) > 0 and not pause:
					current_p = p_to_check.pop()
					_p = next(iter(current_p))
					#f = [0,_p]
					next_p = False
					print('current p:',current_p)
					finded_mines = deque([])
					finded_no_mines = deque([])
					print('flagging',current_p[_p][2],'in',_p,'...')
					current_p[_p][0][current_p[_p][2][1],current_p[_p][2][0]] = 'flag'
					current_p[_p][3].append(current_p[_p][2])
					search = 0
					updated2 = True
					p_end = False

				#Search
				if not pause:
					if len(finded_mines) == 0 and len(finded_no_mines) == 0:
						finded_mines,finded_no_mines,search = self.search_mine('1 & 2','possible',current_p[_p][0])
					while len(finded_mines) > 0:
						finded_mine = finded_mines.popleft()
						print('flagging',finded_mine,'in',_p,'...')
						current_p[_p][0][finded_mine[1],finded_mine[0]] = 'flag'
						current_p[_p][3].append(finded_mine)
						if len(finded_mines) == 0:
							updated2 = True
					while len(finded_no_mines) > 0:
						finded_no_mine = finded_no_mines.popleft()
						print('marking',finded_no_mine,'in',_p,'...')
						current_p[_p][0][finded_no_mine[1],finded_no_mine[0]] = 'no_mine'
						current_p[_p][4].append(finded_no_mine)
						if len(finded_no_mines) == 0:
							updated2 = True

				if search != 'finded' and not pause:
					finded_no_mines,search = self.search_mine('3','possible',current_p[_p][0])
					if search != 'tile discarded':
						next_p = True
						for tile in surrounding_nums:
							len_hidden_tiles = len(self.hidden_tiles(tile[0],tile[1],current_p[_p][0]))
							if len_hidden_tiles > 1:
								print('-finded',len_hidden_tiles,'possibilities in tile',tile)
								if current_p[_p][0][tile[1],tile[0]] - len(self.flag_tiles(tile[0],tile[1],current_p[_p][0])) == 1:
									possible = self.possible_tiles(tile[0],tile[1],current_p[_p][0])
									possibilities = len(possible)
									relative_tile = tile
									for i in range(possibilities):
										p_to_check.append({_p+'.'+str(i+1):[current_p[_p][0].copy(),relative_tile,possible[i]\
											,current_p[_p][3].copy(),current_p[_p][4].copy(),{}]})
									#p_end = True
									break
								else:
									if current_p not in finalists.values():
										finalists.update(current_p)
										if len(p_to_check) == 0:
											p_end = True
										else:
											next_p = True

				#Stop if finish
				if len(p_to_check) == 0 and (f == [len(surrounding_nums),_p] or p_end):
					#print('finalists:',finalists)
					running2 = False
					print('Algorithm 4 END')

				#Modify screen
				if updated2:
					print('updating possible map...')
					new_grid = current_p[_p][0]
					for y_pos,row in enumerate(new_grid):
						for x_pos,value in enumerate(row):
							if new_grid[y_pos,x_pos] == None:
								screen.blit(tile_img, (x_pos*16, y_pos*16))
							elif new_grid[y_pos,x_pos] == 'mine':
								screen.blit(mine_img, (x_pos*16, y_pos*16))
							elif new_grid[y_pos,x_pos] == 'boom':
								screen.blit(mine_boom_img, (x_pos*16, y_pos*16))
							elif new_grid[y_pos,x_pos] == 'mine_flagged':
								screen.blit(mine_flagged_img, (x_pos*16, y_pos*16))
							elif new_grid[y_pos,x_pos] == 'flag':
								screen.blit(flag_img, (x_pos*16, y_pos*16))
							elif new_grid[y_pos,x_pos] == 'no_mine':
								screen.blit(no_mine_img, (x_pos*16, y_pos*16))
							else:
								screen.blit(tiles[value], (x_pos*16, y_pos*16))
					updated2 = False
					pygame.display.update()
					pygame.display.set_caption(_p)
				if not running2:
					if len(finalists) > 0:
						f_mines = []
						f_no_mines = []
						for key in finalists:
							f_mines += finalists[key][3]
							f_no_mines += finalists[key][4]
						for f_mine,f_no_mine in zip(set(f_mines),set(f_no_mines)):
							if f_mines.count(f_mine) == len(finalists):
								self.finded_mines.append((f_mine[0]+edges[0],f_mine[1]+edges[1]))
								updated = True
							if f_no_mines.count(f_no_mine) == len(finalists):
								print('f_no_mine:',f_no_mine)
								self.show_tile(f_no_mine[0]+edges[0],f_no_mine[1]+edges[1])
								print('f_no_mine:',f_no_mine)
								updated = True
					break
			screen = pygame.display.set_mode((16*map_size.x, 16*map_size.y))
			pygame.display.set_caption('Minesweeper')
			print('p to check:',p_to_check)

			surrounding_nums = set(map(lambda t: (t[0]+edges[0],t[1]+edges[1]), surrounding_nums))
			hidden_of_surrounding = set()
			for surrounding in surrounding_nums:
				for hidden_tile in self.hidden_tiles(surrounding[0],surrounding[1],grid_view):
					hidden_of_surrounding.add(hidden_tile)
			return hidden_of_surrounding,0 if updated == False else 'algorithm 4 effective'

					
		if algorithm == '1 & 2':
			if map_type == 'real':
				return 0 if len(self.finded_mines) == 0 else 'finded'
			else:
				print('returning mines:',mines,'and no_mines:',no_mines)
				return mines,no_mines,'finded' if (len(mines) > 0 or len(no_mines) > 0) else 0
		elif algorithm == '3':
			if map_type == 'real':
				return 0 if updated == False else 'tile discarded'
			else:
				print('returning no_mines:',no_mines)
				return no_mines,'tile discarded' if len(no_mines) > 0 else 0


#Game loop
blockPrint()
running = True
updated = True
print('Seed:',random_seed)
Map = Map()

spaces = [(x_pos,y_pos) for y_pos,row in enumerate(grid) for x_pos,value in enumerate(row) if value == 0]
hidden = [(x_pos,y_pos) for y_pos,row in enumerate(grid_view) for x_pos,value in enumerate(row) if value == None]

tile = spaces[randint(len(spaces))]
Map.show_tile(tile[0],tile[1])
while True:
	#Quit button
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

	print('finded mines:',Map.finded_mines)
	if len(Map.finded_mines) == 0:
		search = Map.search_mine('1 & 2','real',grid_view)
	else:
		finded_mine = Map.finded_mines.popleft()
		print('flagging',finded_mine,'...')
		grid_view[finded_mine[1],finded_mine[0]] = 'flag'
		if finded_mine not in hidden:
			print('hidden:',hidden)
			break
		hidden.remove(finded_mine)
		if len(Map.finded_mines) == 0:
			updated = True

	if search != 'finded' and len(Map.finded_mines) == 0:
		search = Map.search_mine('3','real',grid_view)

		if search != 'tile discarded':
			hidden_of_surrounding,search = Map.search_mine('4','real',grid_view)
			print('search:',search, ', hidden_of_surrounding:',hidden_of_surrounding)

			if search != 'algorithm 4 effective':
				if len(hidden_of_surrounding) > 0:
					rand_tile = list(hidden_of_surrounding)[randint(len(hidden_of_surrounding))]
				else:
					rand_tile = hidden[randint(len(hidden))]
				rand_x = rand_tile[0]
				rand_y = rand_tile[1]
				print('. Random')
				alg_used[4] += 1
				Map.show_tile(rand_x,rand_y)

	if updated:
		print('updating real map...')
		completed = True
		end = False
		for y_pos,row in enumerate(grid_view):
			for x_pos,value in enumerate(row):
				if grid_view[y_pos,x_pos] == None:
					completed = False
					screen.blit(tile_img, (x_pos*16, y_pos*16))
				elif grid_view[y_pos,x_pos] == 'mine':
					screen.blit(mine_img, (x_pos*16, y_pos*16))
				elif grid_view[y_pos,x_pos] == 'boom':
					screen.blit(mine_boom_img, (x_pos*16, y_pos*16))
					end = True
				elif grid_view[y_pos,x_pos] == 'mine_flagged':
					screen.blit(mine_flagged_img, (x_pos*16, y_pos*16))
				elif grid_view[y_pos,x_pos] == 'flag':
					screen.blit(flag_img, (x_pos*16, y_pos*16))
				else:
					screen.blit(tiles[value], (x_pos*16, y_pos*16))
		updated = False
		pygame.display.update()
		print('real map updated')
		if end or completed:
			running = False
			print('END')
	if not running:
		break

#Analysis
enablePrint()
hidden_num = map_size.x*map_size.y
flags = []
print('\nAnalysis:')
for y_pos,row in enumerate(grid_view):
	for x_pos,value in enumerate(row):
		if grid_view[y_pos,x_pos] == None or grid_view[y_pos,x_pos] == 'mine':
			hidden_num -= 1
		elif grid_view[y_pos,x_pos] == 'boom':
			hidden_num -= 1
			print('BOOM at',(x_pos,y_pos))
		elif grid_view[y_pos,x_pos] == 'flag':
			flags.append((x_pos,y_pos))
		elif grid_view[y_pos,x_pos] == 'mine_flagged':
			hidden_num -= 1
print('flags:',len(flags))
print('''Algorithm 1 used: {}, of which on real map: {}
Algorithm 2 used: {}, of which on real map: {}
Algorithm 3 used: {}, of which on real map: {}
Algorithm 4 used: {}
Random choices used: {}'''.format(alg_used[0][0],alg_used[0][1],alg_used[1][0],alg_used[1][1],alg_used[2][0],alg_used[2][1],alg_used[3],alg_used[4]))
print('Map solved:',hidden_num/(map_size.x*map_size.y)*100,'%')
print('Seed:',random_seed)

running = True
while running:
	#Quit button
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False				