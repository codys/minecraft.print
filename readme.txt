Minecraft.Print() is a python library for converting defined regions of Minecraft levels to a 3D Printable format.

Includes pymclevel.
Requires numpy (https://github.com/numpy/numpy).

In game: 
Before running Minecraft.Print() you will need to define the space you wish to print by placing two markers, in-game. The marker configuration is a diamond block, followed by a gold block, followed by an iron block in vertical order (ascending or descending). The coordinates of the diamond block will be used as the marker.

Running Minecraft.Print():
Run "python run.py LEVEL_NAME OUTPUT_NAME" - replacing LEVEL_NAME and and OUTPUT_NAME with the level you wish to process and the desired output file name. The script will then run and save the STL file in the same directory.

Viewing resulting file:
There are many free programs for viewing STL files. One example: http://meshlab.sourceforge.net

Printing:
If you don't have a 3D Printer of your own, to print to, there are online services that will allow you to upload an STL file and order a print. Two random ones: cloudfab.com and shapeways.com

Show off your creation:
We figure you already know how to do this.

Sharing:
So here's the deal. We want to see what awesome stuff you guys are going to print. So drop us a line at hi@minecraftprint.com and let us know how it went. Also, if you have something really awesome, consider putting the model up on thingiverse.com for others to print.