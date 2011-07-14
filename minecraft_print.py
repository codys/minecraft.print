import pymclevel.mclevel as mclevel
import sys
import os
from pymclevel.box import BoundingBox
import numpy
from numpy import zeros, bincount
import logging
import itertools
import traceback
import shlex
import operator
import codecs

from math import floor
try:
    import readline
except:
    pass

class UsageError(RuntimeError): pass
class BlockMatchError(RuntimeError): pass
class PlayerNotFound(RuntimeError): pass

class MinecraftPrint:

    def __init__(self, level, output):
        self.level_name = level
        self.output_name = output + '.stl'

        #The list of goodness and markers
        #Format: [[chunk_x, chunk_z, block_x, block_z, block_y]]
        self.markers = []

        self.chunk_positions = []
        self.num_chunks = 0
        self.chunk_counter = 0

        self.diamond_check = []
        self.object_array = []
		
        #Data value for each block type
        self.diamond = 57
        self.gold = 41
        self.iron = 42

    def generate(self):
        self.find_marked_area()
        self.copy_marked_area()
        self.generate_stl()
    
    def find_marked_area(self):
        self.world = mclevel.loadWorld(self.level_name)

    	#Load chunks and determine minimize indexes
    	self.chunk_positions = list(self.world.allChunks)
    	self.num_chunks = len(self.chunk_positions)

    	#Just a little user feedback on the progress
    	print "Processing level: " + self.level_name
    	print "Scanning level for markers..."
    	self.chunk_counter = 1
        
        self.find_markers()
        
        print '100%'
        
    def find_markers(self):
        #Iterate through chunks, looking for block combination
    	for x_pos, z_pos in self.chunk_positions:
    		#User feedback
    		if self.chunk_counter % 10 == 0:
    			print str(self.chunk_counter/float(self.num_chunks)*100) + "%"
    		self.chunk_counter += 1

    		chunk = self.world.getChunk(x_pos, z_pos)
    		#Does this chunk have a diamond block?

    		diamond_check = numpy.where(chunk.Blocks == self.diamond)
    		if len(diamond_check[0]) > 0:
    			for dx, dz, dy in zip(diamond_check[0], diamond_check[1], diamond_check[2]):

    				#We found diamond, but is it a marker (diamond, gold, and iron in asc or desc vertical order)
    				#If so, define the diamond block coordinates as the marker and remove the marker from the map
    				if dy > 1 and chunk.Blocks[dx, dz, dy - 1] == self.gold and chunk.Blocks[dx, dz, dy - 2] == self.iron:
    					self.markers.append([x_pos, z_pos, dx, dz, dy])
    					chunk.Blocks[dx, dz, dy] = 0
    					chunk.Blocks[dx, dz, dy - 1] = 0
    					chunk.Blocks[dx, dz, dy - 2] = 0
    				elif dy < 126 and chunk.Blocks[dx, dz, dy + 1] == self.gold and chunk.Blocks[dx, dz, dy + 2] == self.iron:
    					self.markers.append([x_pos, z_pos, dx, dz, dy])
    					chunk.Blocks[dx, dz, dy] = 0
    					chunk.Blocks[dx, dz, dy + 1] = 0
    					chunk.Blocks[dx, dz, dy + 2] = 0
    
    def copy_marked_area(self):
        #Now we have the markers. Time to get serious 
    	if len(self.markers) == 2:
    		print "Congrats, looks like we have two markers"
    		print "..."
    		print "Capturing marked area... this may take a minute..."

    		#Calculate x_min and x_max
    		if self.markers[0][0] < self.markers[1][0]:
    			x_min = [self.markers[0][0], self.markers[0][2]]
    			x_max = [self.markers[1][0], self.markers[1][2]]
    		elif self.markers[0][0] > self.markers[1][0]:
    			x_min = [self.markers[1][0], self.markers[1][2]]
    			x_max = [self.markers[0][0], self.markers[0][2]]
    		else:
    			x_min = [self.markers[0][0], min(self.markers[0][2], self.markers[1][2])]
    			x_max = [self.markers[0][0], max(self.markers[0][2], self.markers[1][2])]

    		#Calculate z_min and z_max
    		if self.markers[0][1] < self.markers[1][1]:
    			z_min = [self.markers[0][1], self.markers[0][3]]
    			z_max = [self.markers[1][1], self.markers[1][3]]
    		elif self.markers[0][1] > self.markers[1][1]:
    			z_min = [self.markers[1][1], self.markers[1][3]]
    			z_max = [self.markers[0][1], self.markers[0][3]]
    		else:
    			z_min = [self.markers[0][1], min(self.markers[0][3], self.markers[1][3])]
    			z_max = [self.markers[0][1], max(self.markers[0][3], self.markers[1][3])]

    		#Calculate y_min and y_max
    		y_min = min(self.markers[0][4], self.markers[1][4])
    		y_max = max(self.markers[0][4], self.markers[1][4])

    		#Construct an array to fit the object
    		self.object_array = [[[0 for z in xrange((z_max[0] - z_min[0] + 1) * 16)] for y in xrange(y_max - y_min + 1)] for x in xrange((x_max[0] - x_min[0] + 1) * 16)]

    		#Copy marked blocks to object_array
    		for x_pos in range(x_min[0], x_max[0] + 1):
    			for z_pos in range(z_min[0], z_max[0] + 1):
    				chunk = self.world.getChunk(x_pos, z_pos)
    				for x in range(16):
    					for z in range(16):
    						for y in range(y_max - y_min + 1):
    							if (x_pos == x_min[0] and x < x_min[1]) or (x_pos == x_max[0] and x > x_max[1]):
    								block_type = 0
    							elif (z_pos == z_min[0] and z < z_min[1]) or (z_pos == z_max[0] and z > z_max[1]):
    								block_type = 0
    							else:
    								block_type = chunk.Blocks[x, z, y_min + y]
    							#print str((16 * (x_pos + offsetx)) + x) + ", " + str(y) + ", " + str((16 * (z_pos + offsetz)) + z)
    							self.object_array[(16 * (x_pos -x_min[0])) + x][y][(16 * (z_pos - z_min[0])) + z] = block_type

    	else:
    		print "Freak out! There are somehow more or less than 2 markers!"
    		
    def generate_stl(self):
        """Generate STL file"""
    	filename = self.output_name

    	width = len(self.object_array)
    	height = len(self.object_array[0])
    	depth = len(self.object_array[0][0])	

    	str_o = "solid Minecraft\n";
    	str_e = "    endloop\n  endfacet\n"
    	str_s = "  facet normal %d %d %d\n    outer loop\n"
    	str_v = "      vertex %d %d %d\n"	

    	print "start"

    	f=open(filename, 'w')
    	f.write(str_o)
    	for x in range(width):
    		print str(x/float(width)*100) + "%"
    		for y in range(height):
    			for z in range(depth):
    				if self.object_array[x][y][z] > 0:
    					if x==0 or self.object_array[x-1][y][z]<=0:
    						f.write("".join([str_s%(-1,0,0),str_v%(x,z+1,y), str_v%(x,z,y+1),str_v%(x,z+1,y+1),str_e]))
    						f.write("".join([str_s%(-1,0,0),str_v%(x,z+1,y), str_v%(x,z,y),str_v%(x,z,y+1),str_e]))
    					if x==width-1 or self.object_array[x+1][y][z]<=0:
    						f.write("".join([str_s%(1,0,0),str_v%(x+1,z+1,y), str_v%(x+1,z+1,y+1),str_v%(x+1,z,y+1),str_e]))
    						f.write("".join([str_s%(1,0,0),str_v%(x+1,z+1,y), str_v%(x+1,z,y+1),str_v%(x+1,z,y),str_e]))
    					if (z==0) or self.object_array[x][y][z-1]<=0:
    						f.write("".join([str_s%(0,0,-1),str_v%(x,z,y), str_v%(x+1,z,y+1),str_v%(x,z,y+1),str_e]))
    						f.write("".join([str_s%(0,0,-1),str_v%(x,z,y), str_v%(x+1,z,y),str_v%(x+1,z,y+1),str_e]))
    					if (z==depth-1) or self.object_array[x][y][z+1]<=0:
    						f.write("".join([str_s%(0,0,1),str_v%(x,z+1,y), str_v%(x,z+1,y+1),str_v%(x+1,z+1,y+1),str_e]))
    						f.write("".join([str_s%(0,0,1),str_v%(x,z+1,y), str_v%(x+1,z+1,y+1),str_v%(x+1,z+1,y),str_e]))
    					if (y==0) or self.object_array[x][y-1][z]<=0:
    						f.write("".join([str_s%(0,-1,0),str_v%(x+1,z,y), str_v%(x,z+1,y),str_v%(x+1,z+1,y),str_e]))
    						f.write("".join([str_s%(0,-1,0),str_v%(x+1,z,y), str_v%(x,z,y),str_v%(x,z+1,y),str_e]))
    					if (y==height-1) or self.object_array[x][y+1][z]<=0:
    						f.write("".join([str_s%(0,1,0),str_v%(x+1,z,y+1), str_v%(x+1,z+1,y+1),str_v%(x,z+1,y+1),str_e]))
    						f.write("".join([str_s%(0,1,0),str_v%(x+1,z,y+1), str_v%(x,z+1,y+1),str_v%(x,z,y+1),str_e]))

    	f.write("endsolid Minecraft\n")
    	print "100%"
    	f.close()

    	print "Done!"