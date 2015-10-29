# standard library
import sys
import os
import re
try:
    from subprocess import Popen, PIPE
    bsubprocess = True
except:
    bsubprocess = False
# local library
import inkex
import simplepath
import cubicsuperpath

inkex.localize()

# third party
try:
    from numpy import *
    from numpy.linalg import *
except:
    inkex.errormsg(_("Failed to import the numpy or numpy.linalg modules. These modules are required by this extension. Please install them and try again.  On a Debian-like system this can be done with the command, sudo apt-get install python-numpy."))
    exit()

class Realscale(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option("--length",
                        action="store", type="float", 
                        dest="length", default="100.0",
                        help="Length of scaling path in real-world units")
        self.OptionParser.add_option("--unit",
                        action="store", type="string", 
                        dest="unit", default="cm",
                        help="Real-world unit")

    def effect(self):
        if len(self.options.ids) != 2:
            inkex.errormsg(_("This extension requires two selected objects."))
            exit()            

        #drawing that will be scaled is selected second
        scalepath = self.selected[self.options.ids[0]]
        drawing = self.selected[self.options.ids[1]]

        if scalepath.tag != inkex.addNS('path','svg'):
            inkex.errormsg(_("The first selected object is not a path.\nPlease select a straight line instead."))
            exit()

        path = cubicsuperpath.parsePath(scalepath.get('d'))
        if len(path) < 1 or len(path[0]) < 2:
            inkex.errormsg(_("This extension requires that the second selected path be two nodes long."))
            exit()

        #calculate path length
        p1_x = path[0][0][1][0]
        p1_y = path[0][0][1][1]
        p2_x = path[0][1][1][0]
        p2_y = path[0][1][1][1]

        p_length = self.unittouu(str(distance((p1_x, p1_y),(p2_x, p2_y))) + self.getDocumentUnit())

        #calculate scaling factor
        target_length = self.unittouu(str(self.options.length) + self.options.unit)
        factor = target_length / p_length

        # Get drawing and current transformations
        for obj in (scalepath, drawing):
            transform = obj.get('transform')
            # Scale both objects as desired
            if transform:
                transform += ' scale(%f)' % (factor)
            else:
                transform = 'scale(%f)' % (factor)
            inkex.debug(transform)
            obj.set('transform', transform)

# Helper function
def distance( (x0,y0),(x1,y1)):
    return sqrt( (x0-x1)*(x0-x1) + (y0-y1)*(y0-y1) )

if __name__ == '__main__':
    e = Realscale()
    e.affect()
