# inkscape-realscale-extension
Inkscape extension for Inkscape 0.91 that allows for quick resizing of (architectural) drawings by indicating a line and its length in real world units

## Installation: 

Copy the files realscale.py and realscale.inx into the directory indicated in
Edit -> Preferences -> System: User extensions

## Usage:

* Import an architectural drawing / floor plan / map /... into Inkscape or open a file containing one. Make sure it is a single object (group it, if necessary).
* Draw a straight line that connects two points in that drawing of which you know the distance in real life (for example, if you know how long a wall of your house in the drawing is, draw the line from one end of the wall to the other).
* Select the line, then add the drawing to the selection.
* Open the extension dialog: Extensions -> Scaling -> RealScale...
* Enter the length of the line you just drew, as it is in the real world (for example, if your house wall is 10.5 m long, enter 10.5. **NOTE**: only one decimal place behind the floating point is possible - if your house is 10.54 m long, it's better to enter the value in cm for best precision)
* Select the unit you used (for your 10.5 m house, select m; for your 1054 cm house, select cm)
* If you want to print the drawing, consider using a substitute unit which will make things fit on the page (e.g. you *mean* km, but *use* cm, so you can easily print your drawing).
* Apply!

![Extension UI](https://cloud.githubusercontent.com/assets/3240233/11429285/3c02c0be-9476-11e5-839d-62be953fd062.png)

## Known issue

Scaling also moves the two items, sometimes out of the current view. I haven't fixed that yet. As a workaround, use Numpad 4 to zoom out to all items in the current drawing to find the resized items.
