"""
Copyright (C) 2015 Maren Hachmann, marenhachmann@yahoo.com
Copyright (C) 2010 Blair Bonnett, blair.bonnett@gmail.com (parts from multiscale extension)
Copyright (C) 2005 Aaron Spike, aaron@ekips.org (parts from perspective extension)
Copyright (C) 2015 Giacomo Mirabassi, giacomo@mirabassi.it (parts from jpeg export extension)
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# standard library
import sys
import os
import re
import math

# local library
import inkex
import simpletransform
import cubicsuperpath

inkex.localize()

class Realscale(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option("--tab", action="store", type="string", dest="tab")
        self.OptionParser.add_option("--length", action="store", type="float", dest="length", default="100.0",
                                     help="Length of scaling path in real-world units")
        self.OptionParser.add_option("--unit", action="store", type="string", dest="unit", default="cm",
                                     help="Real-world unit")
    def getUnittouu(self, param):
        try:
            return inkex.unittouu(param)
        except AttributeError:
            return self.unittouu(param)
            
    def calc_scale_center(self, p1x, p1y, p2x, p2y):
        """ Use straight line as scaling center.
            - determine which point is center on basis of quadrant the line is in.
            - approx this by using center of line
            0,0 corresponds to UL corner of page
        """
        scale_center = [0,0] # resulting scaling point
        # calc page center
        pagecenter_x = self.getUnittouu(self.document.getroot().get('width'))/2
        pagecenter_y = self.getUnittouu(self.document.getroot().get('height'))/2
        # calc minmax of straightline ref points
        minx = min(p1x, p2x)
        maxx = max(p1x, p2x)
        miny = min(p1y, p2y)
        maxy = max(p1y, p2y)
        # simplifiy calc by using center of line to determine quadrant
        line_x = p1x + (p2x - p1x)/2
        line_y = p1y + (p2y - p1y)/2
        # determine quadrant
        if line_x < pagecenter_x:
            # Left hand side
            if line_y < pagecenter_y:
                scale_center = [minx,miny] # UL
            else:
                scale_center = [minx,maxy] # LL
        else: # Right hand side
            if line_y < pagecenter_y:
                scale_center = [maxx,miny] # UR
            else:
                scale_center = [maxx,maxy] # LR
        #inkex.debug("%s  %s,%s" % (scale_center, pagecenter_x*2, pagecenter_y*2))
        return scale_center

    def effect(self):
        if len(self.options.ids) != 2:
            inkex.errormsg(_("This extension requires two selected objects. Straightline path first."))
            exit()

        #drawing that will be scaled is selected second, must be a single object
        scalepath = self.selected[self.options.ids[0]]
        drawing = self.selected[self.options.ids[1]]

        if scalepath.tag != inkex.addNS('path','svg'):
            inkex.errormsg(_("The first selected object is not a path.\nPlease select a straight line instead."))
            exit()

        #apply its transforms to the scaling path, so we get the correct coordinates to calculate path length
        simpletransform.fuseTransform(scalepath)
        
        path = cubicsuperpath.parsePath(scalepath.get('d'))
        if len(path) < 1 or len(path[0]) < 2:
            inkex.errormsg(_("This extension requires that the first selected path be two nodes long."))
            exit()

        #calculate path length
        p1_x = path[0][0][1][0]
        p1_y = path[0][0][1][1]
        p2_x = path[0][1][1][0]
        p2_y = path[0][1][1][1]

        p_length = self.getUnittouu(str(distance((p1_x, p1_y),(p2_x, p2_y))) + self.getDocumentUnit())
        
        # calculate scaling center
        center = self.calc_scale_center(p1_x, p1_y, p2_x, p2_y)

        #calculate scaling factor
        target_length = self.getUnittouu(str(self.options.length) + self.options.unit)
        factor = target_length / p_length

        # Get drawing and current transformations
        for obj in (scalepath, drawing):
            # Scale both objects about the center# first translate back to origin
            scale_matrix = [[1, 0.0, -center[0]], [0.0, 1, -center[1]]]
            simpletransform.applyTransformToNode(scale_matrix, obj)
            # Then scale
            scale_matrix = [[factor, 0.0, 0.0], [0.0, factor, 0.0]]
            simpletransform.applyTransformToNode(scale_matrix, obj)
            # Then translate back to original scale center location
            scale_matrix = [[1, 0.0, center[0]], [0.0, 1, center[1]]]
            simpletransform.applyTransformToNode(scale_matrix, obj)

    def getUnittouu(self, param):
        try:
            return inkex.unittouu(param)
        except AttributeError:
            return self.unittouu(param)

# Helper function
def distance((x0,y0),(x1,y1)):
    return math.sqrt((x0-x1)*(x0-x1) + (y0-y1)*(y0-y1))

if __name__ == '__main__':
    e = Realscale()
    e.affect()
