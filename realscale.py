"""
Copyright (C) 2015 Maren Hachmann, marenhachmann@yahoo.com
Copyright (C) 2010 Blair Bonnett, blair.bonnett@gmail.com (parts from multiscale extension)
Copyright (C) 2005 Aaron Spike, aaron@ekips.org (parts from perspective extension)
Copyright (C) 2015 Giacomo Mirabassi, giacomo@mirabassi.it (parts from jpeg export extension)
Copyright (C) 2016 Neon22 @github (scale ruler)
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
import simplestyle
import cubicsuperpath

inkex.localize()

### Scale Ruler
# inches = [1, 2, 4, 8, 16, 24, 32, 48, 64, 96, 128]
# metric = [1,2,5,10,20,50,100,200,250,500,1000,1250,2500]

# TODO: 
# - maybe turn dropdown for choosing scale type (metric/imperial/custom) into radio buttons?
# - scale font size
# - scale box-height better for small boxes
# - add ruler into current layer
# - add magnification e.g. 2:1 for small drawings

class Realscale(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option('--tab', action='store', type='string', dest='tab')
        self.OptionParser.add_option('--length', action='store', type='float', dest='length', default=100.0,
                                     help='Length of scaling path in real-world units')
        self.OptionParser.add_option('--unit', action='store', type='string', dest='unit', default='cm',
                                     help='Real-world unit')
        self.OptionParser.add_option('--showscale', action='store', type='string', dest='showscale', default='false',
                                     help='Show Scale Ruler')
        self.OptionParser.add_option('--choosescale', action='store', type='string', dest='choosescale', default='all',
                                     help='Choose Scale')
        self.OptionParser.add_option('--metric', action='store', type='string', dest='metric', default='1',
                                     help='Common metric scales')
        self.OptionParser.add_option('--imperial', action='store', type='string', dest='imperial', default='1',
                                     help='Common imperial scales')
        self.OptionParser.add_option('--custom_scale', action='store', type='float', dest='custom_scale', default=45,
                                     help='Custom scale')
        self.OptionParser.add_option('--unitlength', action='store', type='int', dest='unitlength', default='1',
                                     help='Length of scale ruler')

    def calc_scale_center(self, p1x, p1y, p2x, p2y):
        """ Use straight line as scaling center.
            - determine which point is center on basis of quadrant the line is in.
            - approx this by using center of line
            0,0 corresponds to UL corner of page
        """
        scale_center = (0,0) # resulting scaling point
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
                scale_center = (minx,miny) # UL
            else:
                scale_center = (minx,maxy) # LL
        else: # Right hand side
            if line_y < pagecenter_y:
                scale_center = (maxx,miny) # UR
            else:
                scale_center = (maxx,maxy) # LR
        #inkex.debug("%s  %s,%s" % (scale_center, pagecenter_x*2, pagecenter_y*2))
        return scale_center
    
    def create_ruler(self, parent, width, pos, value, drawing_scale):
        """ Draw Scale ruler
            - Position above user's straightline.
            - Ruler shows two units together. First one cut into 5
            - pos is a tuple e.g. (0,0)
            
            TODO:
            - Fix font size for large and small rulers
            - Fix line width for large and small rulers
        """
        " Ruler is always 2 units long with 5 divs in the left half "
        # Draw two boxes next to each other. Top half of right half of ruler is filled black
        line_width = self.getUnittouu('0.25 mm')
        box_height = max(width/15, self.getUnittouu('2 mm'))
        font_height = 8
        White = '#ffffff'
        Black = '#000000'
        t = 'translate' + str(pos)
        
        # create clip in order to get an exact ruler width (without the outer half of the stroke)
        path = '//svg:defs'
        defslist = self.document.getroot().xpath(path, namespaces=inkex.NSS)
        if len(defslist) > 0:
            defs = defslist[0]
        
        clipPathData = {inkex.addNS('label', 'inkscape'):'rulerClipPath', 'clipPathUnits':'userSpaceOnUse', 'id':'rulerClipPath'}
        clipPath = inkex.etree.SubElement(defs, 'clipPath', clipPathData)
        clipBox = {'x':str(-width), 'y':'0.0',
                'width':str(width*2), 'height':str(box_height),
                'style':'fill:%s; stroke:none; fill-opacity:1;' % (Black)}

        inkex.etree.SubElement(clipPath, 'rect', clipBox)

        # create groups for scale rule and ruler
        scale_group = inkex.etree.SubElement(parent, 'g', {inkex.addNS('label','inkscape'):'scale_group', 'transform':t})
        ruler_group = inkex.etree.SubElement(scale_group, 'g', {inkex.addNS('label','inkscape'):'ruler', 'clip-path':"url(#rulerClipPath)"})
        
        # box for right half of ruler
        boxR = {'x':'0.0', 'y':'0.0',
                'width':str(width), 'height':str(box_height),
                'style':'fill:%s; stroke:%s; stroke-width:%s; stroke-opacity:1; fill-opacity:1;' % (White, Black, line_width)}
        inkex.etree.SubElement(ruler_group, 'rect', boxR)
        # top half black
        boxRf = {'x':'0.0', 'y':'0.0',
                 'width':str(width), 'height':str(box_height/2),
                 'style':'fill:%s; stroke:none; fill-opacity:1;' % (Black)}
        inkex.etree.SubElement(ruler_group, 'rect', boxRf)
        # Left half of ruler
        boxL = {'x':str(-width), 'y':'0.0',
                'width':str(width), 'height':str(box_height),
                'style':'fill:%s; stroke:%s; stroke-width:%s; stroke-opacity:1; fill-opacity:1;' % (White, Black, line_width)}
        inkex.etree.SubElement(ruler_group, 'rect', boxL)
        # staggered black fills on left half
        start = -width
        for i in range(5):
            boxRf = {'x':str(start), 'y':str((i+1)%2 * box_height/2), 
                     'width':str(width/5), 'height':str(box_height/2),
                     'style':'fill:%s; stroke:none; fill-opacity:1;' % (Black)}
            inkex.etree.SubElement(ruler_group, 'rect', boxRf)
            start += width/5
        # text
        textstyle = {'font-size': str(font_height)+ " px",
                     'font-family': 'sans-serif',
                     'text-anchor': 'middle',
                     'text-align': 'center',
                     'fill': Black }
        text_atts = {'style': simplestyle.formatStyle(textstyle),
                     'x': '0', 'y': str(-font_height/2) }
        text = inkex.etree.SubElement(scale_group, 'text', text_atts)
        text.text = "0"
        text_atts = {'style': simplestyle.formatStyle(textstyle),
                     'x': str(width), 'y': str(-font_height/2) }
        text = inkex.etree.SubElement(scale_group, 'text', text_atts)
        text.text = str(value)

        text_atts = {'style':simplestyle.formatStyle(textstyle),
                     'x': str(-width), 'y': str(-font_height/2) }
        text = inkex.etree.SubElement(scale_group, 'text', text_atts)
        text.text = str(value)
        # Scale note
        text_atts = {'style':simplestyle.formatStyle(textstyle),
                     'x': '0', 'y': str(-font_height*2.5) }
        text = inkex.etree.SubElement(scale_group, 'text', text_atts)
        text.text = "Scale 1:" + str(drawing_scale) + " (" + self.options.unit + ")"


    def effect(self):
        if len(self.options.ids) != 2:
            inkex.errormsg(_("This extension requires two selected objects. The first selected object must be the straight line with two nodes."))
            exit()

        # drawing that will be scaled is selected second, must be a single object
        scalepath = self.selected[self.options.ids[0]]
        drawing = self.selected[self.options.ids[1]]

        if scalepath.tag != inkex.addNS('path','svg'):
            inkex.errormsg(_("The first selected object is not a path.\nPlease select a straight line with two nodes instead."))
            exit()

        # apply its transforms to the scaling path, so we get the correct coordinates to calculate path length
        simpletransform.fuseTransform(scalepath)
        
        path = cubicsuperpath.parsePath(scalepath.get('d'))
        if len(path) < 1 or len(path[0]) < 2:
            inkex.errormsg(_("This extension requires that the first selected path be two nodes long."))
            exit()

        # calculate path length
        p1_x = path[0][0][1][0]
        p1_y = path[0][0][1][1]
        p2_x = path[0][1][1][0]
        p2_y = path[0][1][1][1]

        p_length = self.getUnittouu(str(distance((p1_x, p1_y),(p2_x, p2_y))) + self.getDocumentUnit())
        
        # Find Drawing Scale
        if self.options.choosescale == 'metric':
            drawing_scale = int(self.options.metric)
        elif self.options.choosescale == 'imperial':
            drawing_scale = int(self.options.imperial)
        elif self.options.choosescale == 'custom':
            drawing_scale = self.options.custom_scale
        
        # calculate scaling center
        center = self.calc_scale_center(p1_x, p1_y, p2_x, p2_y)

        # calculate scaling factor
        target_length = self.getUnittouu(str(self.options.length) + self.options.unit)
        factor = (target_length / p_length) / drawing_scale
        # inkex.debug("%s, %s  %s" % (target_length, p_length, factor))
        
        # Add scale ruler
        if self.options.showscale == "true":
            dist = int(self.options.unitlength)
            
            ruler_length = self.getUnittouu(str(dist) + self.options.unit) / drawing_scale
            ruler_pos = (p1_x + (p2_x - p1_x)/2, (p1_y + (p2_y - p1_y)/2) - self.getUnittouu('4 mm'))
            
            # TODO: add into current layer instead
            self.create_ruler(self.document.getroot(), ruler_length, ruler_pos, dist, drawing_scale)

        # Get drawing and current transformations
        for obj in (scalepath, drawing):
            # Scale both objects about the center, first translate back to origin
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
