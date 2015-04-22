README.md

Will Add More/better Documentation Later.

Requires Most Recent version of Anaconda Python

eventlet concurrent processing library required for Spectra List Reader.

     pip install eventlet

To Run Software: 

	run "python Plotting_Interface_5.py"
	
	If asked to build matches.rep, type 'y'
	

![alt tag](http://i.imgur.com/IZtURxg.png)	

##Interface
=======

###Plot
------
	The center of the main window shows two plots.  The top plot will always show all of the rest frame spectra that has been downloaded for an object.  The bottom plot may show transformations of these spectra which can be set in the "Transform Data" tool.  The x-axis is locked between the two plots, but the y-axis is free in each plot.  Each time the "Next" or "Previous" buttons are pressed, the plot will update with the spectra for the next object in the current set.

####Plot Tools
	These tools are imported from matplotlib.  Hover the mouse over each tool for a brief description.

###Information Bar (Left Panel)
------

####Quick Information (TOP)
	Displays angle of right ascension, declination, redshift, and a Group ID number.  

####Tags (LEFT)
	Objects can be marked with tags.  These tags will add these objects to custom made subsets.  These subsets can be viewed through the "Tags" option in the "View" menu.


