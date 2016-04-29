# inkscape-realscale-extension
Inkscape extension for Inkscape 0.48 and 0.91 that allows for quick resizing of (architectural) drawings by indicating a line and its length in real world units and can optionally scale the drawing with a specific scale factor and draw a scale rule.

## Installation: 

Copy the files realscale.py and realscale.inx into the directory indicated in
Edit -> Preferences -> System: User extensions

If you are using Inkscape 0.48, it may happen that the extension crashes the program when you open it, due to a bug in that Inkscape version. In this case, use the file whose name ends with 0.48 and rename it to realscale.inx.

## Usage:

* Import an architectural drawing / floor plan / map /... into Inkscape or open a file containing one. Make sure it is a single object (group it, if necessary).
* Draw a straight line that connects two points in that drawing of which you know the distance in real life (for example, if you know how long a wall of your house in the drawing is, draw the line from one end of the wall to the other).
* Select the line, then add the drawing to the selection.
* Open the extension dialog: Extensions -> Scaling -> RealScale...
* Enter the length of the line you just drew, as it is in the real world (for example, if your house wall is 10.5 m long, enter 10.50.
* Select the unit you used (for your 10.50 m house, select m; for your 10 cm cardboard box, select cm)
* If you intend to print the drawing, and the original object is bigger than the sheet, consider using a scale factor.
* To do so, first select if you want to use a metric scale factor (based on mulitples of 5) or an imperial one (based on multiples of 2) or if you would like to enter your own scale factor.
* Then, in the corresponding dropdown, or in the number entry field, select or enter the scale you would like to use.
* If you would like the scale rule to be drawn on the page, check the option 'Generate Scale Rule'.
* Now choose the number of units the scale rule will comprise. Those will be doubled in the generated scale rule - e.g. it will show 10 cm to the left of the scale rule center (labelled 0) and 10 cm to its right.
* Apply!

## Screenshots

![Extension UI](https://cloud.githubusercontent.com/assets/3240233/14926074/aea5ccbc-0e4a-11e6-92c6-da40c35cf0d6.png)
![Extension Help Tab](https://cloud.githubusercontent.com/assets/3240233/14926085/b3e309ba-0e4a-11e6-8836-dde99345f1bf.png)
![Usage example](https://cloud.githubusercontent.com/assets/3240233/14926682/94823b42-0e4d-11e6-813b-8fa6d640f28f.png)
(Map: ![Copyright OpenStreetMap Contributors](http://www.openstreetmap.org/copyright))
