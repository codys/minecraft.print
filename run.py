import sys
import minecraft_print

if __name__ == "__main__":
	if len(sys.argv[1:]) == 2:
		mp = minecraft_print.MinecraftPrint(sys.argv[1], sys.argv[2])
		mp.generate()
	else:
		print "Try the following syntax: python run.py levelname outputname"