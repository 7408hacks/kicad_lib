'''
Created on 11-06-2014

@author: Masta
'''
import os

class footprint_generator(object):
    libPath=None
    
    def __init__(self,_libPath):
        self.libPath = _libPath
        if not os.path.exists(_libPath):
            os.makedirs(_libPath)
                    
    def library_generator(self, classes):         
        for c in classes:
            instance = c(self.libPath)
            instance.library()
        
class footprint():
    libPath=""
    libFile=None
    
    def __init__(self, _libPath):
        self.libPath = _libPath
    
    def footprintHeader(self, name, reference, refPos=[0,0], namePos=[0,0]):
        header = r"""(module %s (layer F.Cu)
  (fp_text reference %s (at %f %f) (layer F.SilkS)
    (effects (font (size 1 1) (thickness 0.15)))
  )
  (fp_text value %s (at %f %f) (layer F.SilkS)
    (effects (font (size 1 1) (thickness 0.15)))
  )
""" % (name, reference, refPos[0], refPos[1], name, namePos[0], namePos[1])
        self.libFile = open(self.libPath + "\\" + name + ".kicad_mod", "w")
        self.libFile.write(header)
    
    def footprintFooter(self):
        self.libFile.write(")\n")

#    def drawRect(self, x1, y1, x2, y2, width=0, fill=0):
#        # fill = 0 - none, 1 - background, 2 - foreground
#        if fill == 1:
#            fill = "f"
#        elif fill == 2:
#            fill = "F"
#        else:
#            fill = "N"
#        self.libFile.write("S %d %d %d %d 0 1 %d %s\n" % (x1, y1, x2, y2, width, fill))

    def drawLine(self, start, end, layer = "F.SilkS", width=0.15):
        self.libFile.write("(fp_line (start %f %f) (end %f %f) (layer %s) (width %f))\n" %
            (start[0], start[1], end[0], end[1], layer, width))
    
    def drawRect(self, start, end, layer = "F.SilkS", width=0.15):
        self.drawLine(start, [start[0], end[1]], layer, width)
        self.drawLine([start[0], end[1]], end, layer, width)
        self.drawLine(end, [end[0], start[1]], layer, width)
        self.drawLine([end[0], start[1]], start, layer, width)
    
    def drawPolygon(self, points, layer = "F.SilkS", width=0.15):
        for i in range(len(points)-1):
            self.drawLine(points[i], points[i+1], layer, width)
        self.drawLine(points[0], points[-1], layer, width)
        
    def drawPad(self, name, position, size, orientation = 0, shape = "rect", padType = "smd", drill = 0, layers ="F.Cu F.Paste F.Mask"):
        # type = "smd"/"thru_hole"
        # shape = "round"/"circle"
        if type(name) is int:
            name = str(name)
        if orientation == 0:
            orientationString = ""
        else:
            orientationString = " %f" % orientation
        if padType == "smd":
            drillString = ""
        else:
            drillString = " (drill %f)" % drill
        self.libFile.write("  (pad %s %s %s (at %f %f%s) (size %f %f)%s (layers %s))\n" % 
            (name, padType, shape, position[0], position[1], orientationString, size[0], size[1], drillString, layers))

class pinFootprint(footprint):
    def footprint(self, rows, cols):
        if cols == 1:
            name = "PIN%d" % (rows)
        elif cols == 2:
            name = "PIN%dx%d" % (rows, cols)
        else:
            raise Exception("Number of columns (%d) to high!" % cols)
        # header
        h = cols * 1.27
        self.footprintHeader(name, "CON", refPos=[0,h+0.75], namePos=[0,-h-0.75])
        # body
        h = cols * 1.27
        l = rows * 1.27
        self.drawRect([-l, -h], [l, h])
        self.drawPolygon([[-l+0.635, 3.81], [-l+1.905, 3.81], [-l+1.27, 2.54]])
        # pins
        self.drawPins(rows, cols)
        self.footprintFooter()
    
    def drawPins(self, rows, cols):
        for c in range(cols): # 1 or 2
            for r in range(rows):
                if (c==0 and r==0):
                    shape = "rect"
                else:
                    shape = "circle"
                self.drawPad(r*cols+c+1, [((-rows/2.0 + 0.5 +r) * 2.54), (-c+0.5*(cols-1))*2.54], [2, 2], 
                    shape = shape, drill = 1.0, padType = "thru_hole", layers ="*.Cu *.Mask F.SilkS")

    def library(self, rows=range(1,41), cols=[1,2]):
        for c in cols:
            for r in rows:
                self.footprint(r, c)

class idcFootprint(pinFootprint):
    def footprint(self, rows, cols):
        name = "IDC%d" % (rows*2)
        # header
        self.footprintHeader(name, "CON", refPos=[0,6], namePos=[0,-5])
        # body
        h = 4.2
        l = rows * 1.27 + 3.8
        self.drawRect([-l, -h], [l, h])
        self.drawRect([-1.5, h], [1.5, h+1])
        self.drawPolygon([[-l+0.635, h+1.27], [-l+1.905, h+1.27], [-l+1.27, h]])
        # pins
        self.drawPins(rows, cols)
        self.footprintFooter()

    def library(self, rows=range(3,35)):
        for r in rows:
            self.footprint(r, 2)

        
if __name__ == "__main__":
    if 1:
        gen = footprint_generator("test.pretty")
        gen.library_generator([idcFootprint, pinFootprint])
    if 1:
        pass