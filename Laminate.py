import math
import re

class Laminate:
    # the command that describes the cuts to create the laminate with
    cutCmd = {}
    # the full length of the desired laminate described in the cmd string
    lengthDesign = 0
    # the full height of the desired laminate described in the cmd string
    heightDesign = 0
    # width of the saw blade (a float value)
    widthKerf = 0
    # number of repeated design units for the design described in the cmd string
    rdus = 0
    # the width of a repeating design unit for the design described in cmd string
    #   widthRdu/2 is the width of the cut to form the current generation
    widthRdu = 0

    """
        initialize Wood Laminate object. Note that length units are a float, either metric or english, doesn't matter

        @cmd: the command string that describes the desired laminate, 45/60A/30D/etc, angles/keys are in degrees
        @lengthDesign: the length of the laminate as described in cmd to fit the space required
        @rdus: the number of repeating design units to fit in the space required
        @kerf: the saw blade kerf as a float 
    """
    def __init__(self, cmd, lengthDesign, heightDesign, rdus, kerf):
        self.lengthDesign = lengthDesign
        self.heightDesign = heightDesign
        self.rdus = rdus
        self.widthKerf = kerf
        #print kerf
        # width of rdu in the laminate described in the cmd string
        self.widthRdu = lengthDesign / rdus
        #print "widthRdu=" + str(self.widthRdu)
        self.parseCmd(cmd)
    """
        intializes cut command data structure to be empty
    """
    def setEmptyCmd(self):
        self.cutCmd = { "angle":[], "location":[], "height":[] }

    """
        parses the string cut commands for creating the symmetric/generational laminate
        
        returns empty data structure on error
    """
    def parseCmd(self, cmd):
        self.setEmptyCmd()
        if len(cmd) > 0:
            # cmd: 45/60A/30D/etc, angles/keys are in degrees, remove all whitespace and split from /'s
            listTemp = (''.join(cmd.upper().split())).split('/')
            if '' in listTemp:
                return self.cutCmd
        else:
            return self.cutCmd

        for c in listTemp:
            try:
                angle = int(c.replace("D", "").replace("A", ""))
            except:
                self.setEmptyCmd()
                return self.cutCmd
            #print angle
            # if the angles are not valid, return empty data strucuture
            if angle <= 0 or angle >= 90:
                self.setEmptyCmd()
                return self.cutCmd
            self.cutCmd["angle"].append(math.radians(angle))
            location = "Any"
            if "A" in c:
                location = "Ascending"
                # if there is an ascending or descending first angle, return empty
                if listTemp[0] == c:
                    self.setEmptyCmd()
                    return self.cutCmd
            elif "D" in c:
                location = "Descending"
                # if there is an ascending or descending first angle, return empty
                if listTemp[0] == c:
                    self.setEmptyCmd()
                    return self.cutCmd
            self.cutCmd["location"].append(location)
            self.cutCmd["height"].append(-1)
        if len(listTemp) > 0:
            self.cutCmd["height"][-1] = self.heightDesign
        return self.cutCmd

    """
        generates the math.sin angle part values multiplied together when generating the initial laminate cut width for
            a particular symmetric/multigenerational design
            0 <= index < len(# angles) in cmd
            
            returns -1 on error
    """
    def getSinAnglesMultiplier(self, indexBegin, indexEnd):
        mult = []
        result = -1
        if indexBegin >= 0 and indexEnd >= 0 and indexBegin <= indexEnd and indexEnd < len(self.cutCmd["angle"]):
            # note that when slicing cutCmd to indexEnd, indexEnd must be 1 more than index of
            #     last item in the array to use
            indexEnd+=1
            # kerf numerator multiplier takes the form 2 * sin(angle)
            for index, angle in list(enumerate(self.cutCmd["angle"][indexBegin:indexEnd])):
                mult.append(2 * math.sin(angle))
            # multiply the terms together
            result = reduce(lambda x, y: x*y, mult)

        return result
    
    """
       generates the kerf equation multiplier
       
    """
    def kerfMultiplier(self, generation):
        # for 1st and 2nd generations, the kerf multiplier is 1
        arr = [1]
        maxindex = generation - 1

        if generation > 2:
            # get the last angle, and manipulate
            for index in reversed(range(2, generation)):
                arr.append(self.getSinAnglesMultiplier(index, maxindex))
        result = sum(arr)
        return result

    """
        the following determines the base/initial laminate (generation #0) cut width based on the
            full length and # rdus of the desired generational laminate described
            in the cmd string cut commands and saw kerf (see pdf notes for derivations and equations)
            
            returns -1 on error
    """
    def getBaseCutWidth(self):
        if len(self.cutCmd["angle"]) == 0:
            return -1
        # the base laminate cut width equations are expressed in generations 1,2,3 & 4 generational 
        #   laminates described on pages 2 & 3 of EquationsNotes.pdf
        # in written book equations, widthRdu/2 is w2 for 2nd generation, w3 for 3rd generation, etc.
        numberGenerations = len(self.cutCmd["angle"])
        denominator = self.getSinAnglesMultiplier(1, (numberGenerations - 1))
        if denominator < 0:
            denominator = 1
        # define base laminate cut width
        baseWidth = ((self.widthRdu/2) + (self.widthKerf * self.kerfMultiplier(numberGenerations))) / denominator
        
        return baseWidth
    
    """
        the following calcualates the laminate cut length based off of the current generation's
            cut width and cut angle in radians (see pdf notes for derivations and equations)
            
            returns -1 on error
    """
    def getCutLength(self, cutWidth, angle):
        cutLength = -1
        if math.degrees(angle) > 0 and math.degrees(angle) < 90 and cutWidth > 0:
            # cut length equation is L(l) in the first page of EquationsNotes.pdf
            #   L(l) [cutLength] is the hypotenuse of the right triangle formed by the cutWidth
            cutLength = (cutWidth + self.widthKerf) / math.sin(angle)

        return cutLength
    
    """
        calculates the number of sections to cut in the base/initial laminate (generation #0)
        Note: the number of design units required doubles every time a mitered laminate is
            converted to the next generation 
            
            returns -1 on error
    """
    def getNumberCuts(self, generation):
        designUnits = -1
        #generation = len(self.cutCmd["angle"])
        if generation > 0:
            designUnits = self.rdus
            for i in range(0, generation):
                designUnits = math.ceil(designUnits * 2)
            # note that this method returns the number of sections to cut, which is rdus * 2
            designUnits = (designUnits * 2)
        return designUnits

    """
        Given a design's height, calculate the height of the previous generation's full laminate
        The calculations are based on the fact that each generation is cut into an approx. parallelogram
        of a certain width and height found from the geometry of right triangles (see pdf notes for
        derivations)

        note: cutLength is calculated in getCutLength()
    """
    def getPreviousGenerationHeight(self, cutLength, angle, heightDesign):
        heightLaminate = -1
        if cutLength > 0 and angle > 0 and heightDesign > 0:
            numerator = math.cos(math.radians(90) - angle) * ((heightDesign * cutLength) + math.cos(angle))
            heightLaminate = numerator / cutLength
        return heightLaminate

    """
        cycles through all of the generations of the cut commands and design dimensions, and 
        calculates the laminates height with the getPreviousGenerationHeight() method

        Note: heightLaminate [getPreviousGenerationHeight] becomes heightDesign as cycle through generations
    """
    def setHeights(self):
        cutWidth = self.widthRdu / 2.0
        baseWidth = self.getBaseCutWidth()
        # we don't want to modify the height of the last element as it has already been set from
        #     the height of the final design set in the constructor
        maxindex = len(self.cutCmd["angle"]) - 1
        #print maxindex
        for i in reversed(range(0, maxindex)):
            #print "i ===> " + str(i)
            angle = self.cutCmd["angle"][i]
            #print "angle ===> " + str(angle)
            #print "cutWidth: " + str(self.cutCmd["cutWidth"][i + 1])
            cutLength = self.getCutLength(cutWidth, angle)
            #print "cutLength ===> " + str(cutLength)
            self.cutCmd["height"][i] = self.getPreviousGenerationHeight(cutLength, angle, self.cutCmd["height"][i + 1])
            # cut width to form the previous generation laminate
            cutWidth = (baseWidth * self.getSinAnglesMultiplier(1, maxindex)) - (self.widthKerf * self.kerfMultiplier((i + 1)))
        #print self.cutCmd
 