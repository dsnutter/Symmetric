import sys
sys.path.append("..") # Adds higher directory to python modules path.

import unittest, math
from Laminate import Laminate

class LaminateTestCase(unittest.TestCase):
    """
        test cases for Laminate class
    """
    
    laminate = None

    def setUp(self):
        kerf = 5.0/64 # usu. 1/8" for most fine cut blades
        rdus = 10
        lengthDesign = 20
        heightDesign = 7
        self.laminate = Laminate('45/60A/45D', lengthDesign, heightDesign, rdus, kerf)

    def test_parseCmd(self):
        """
            tests string command parsing for Laminates
        """
        strCmd = ''
        result = self.laminate.parseCmd(strCmd)['angle']
        self.assertEqual(len(result), 0)
        
        strCmd = '-1'
        result = self.laminate.parseCmd(strCmd)['angle']
        self.assertEqual(len(result), 0)

        strCmd = '10/0A'
        result = self.laminate.parseCmd(strCmd)['angle']
        self.assertEqual(len(result), 0)

        strCmd = '90/10A'
        result = self.laminate.parseCmd(strCmd)['angle']
        self.assertEqual(len(result), 0)

        strCmd = '10A/45D'
        result = self.laminate.parseCmd(strCmd)['angle']
        self.assertEqual(len(result), 0)

        strCmd = '10D/45D'
        result = self.laminate.parseCmd(strCmd)['angle']
        self.assertEqual(len(result), 0)

        strCmd = '45/'
        result = self.laminate.parseCmd(strCmd)['angle']
        self.assertEqual(len(result), 0)
        
        strCmd = '/45'
        result = self.laminate.parseCmd(strCmd)['angle']
        self.assertEqual(len(result), 0)
        
        strCmd = '45'
        result = self.laminate.parseCmd(strCmd)['angle']
        self.assertEqual(len(result), 1)

        # ----------------------
        strCmd = '45/60D/'
        result = self.laminate.parseCmd(strCmd)['angle']
        self.assertEqual(len(result), 0)

        strCmd = '/45/60D/'
        result = self.laminate.parseCmd(strCmd)['angle']
        self.assertEqual(len(result), 0)

        strCmd = '45/60F'
        result = self.laminate.parseCmd(strCmd)['angle']
        self.assertEqual(len(result), 0)

        strCmd = '45/60A'
        result = self.laminate.parseCmd(strCmd)['angle']
        self.assertEqual(len(result), 2)

        strCmd = '45/60D'
        result = self.laminate.parseCmd(strCmd)['angle']
        self.assertEqual(len(result), 2)

        # ----------------------
        strCmd = '45/60TEST/30A'
        result = self.laminate.parseCmd(strCmd)['angle']
        self.assertEqual(len(result), 0)

        strCmd = '45/60D/30A'
        result = self.laminate.parseCmd(strCmd)
        self.assertEqual(len(result['angle']), 3)
        self.assertEqual(result['angle'][0], math.radians(45))
        self.assertEqual(result['angle'][1], math.radians(60))
        self.assertEqual(result['angle'][2], math.radians(30))
        self.assertEqual(result['location'][0], 'Any')
        self.assertEqual(result['location'][1], 'Descending')
        self.assertEqual(result['location'][2], 'Ascending')

        strCmd = '45/60D/30D'
        result = self.laminate.parseCmd(strCmd)
        self.assertEqual(len(result['angle']), 3)
        self.assertEqual(result['angle'][0], math.radians(45))
        self.assertEqual(result['angle'][1], math.radians(60))
        self.assertEqual(result['angle'][2], math.radians(30))
        self.assertEqual(result['location'][0], 'Any')
        self.assertEqual(result['location'][1], 'Descending')
        self.assertEqual(result['location'][2], 'Descending')

    def test_getSinAnglesMultiplier(self):
        # test indices
        indexBegin = -1
        indexEnd = 2
        result = self.laminate.getSinAnglesMultiplier(indexBegin, indexEnd)
        self.assertEqual(result, -1)

        indexBegin = 0
        indexEnd = -1
        result = self.laminate.getSinAnglesMultiplier(indexBegin, indexEnd)
        self.assertEqual(result, -1)

        indexBegin = 2
        indexEnd = 1
        result = self.laminate.getSinAnglesMultiplier(indexBegin, indexEnd)
        self.assertEqual(result, -1)

        indexBegin = 0
        indexEnd = 10
        result = self.laminate.getSinAnglesMultiplier(indexBegin, indexEnd)
        self.assertEqual(result, -1)

        indexBegin = 0
        indexEnd = 0
        result = self.laminate.getSinAnglesMultiplier(indexBegin, indexEnd)
        self.assertEqual(result, 1.414213562373095)

        indexBegin = 0
        indexEnd = 1
        result = self.laminate.getSinAnglesMultiplier(indexBegin, indexEnd)
        self.assertEqual(result, 2.449489742783178)

        indexBegin = 0
        indexEnd = 2
        result = self.laminate.getSinAnglesMultiplier(indexBegin, indexEnd)
        self.assertEqual(result, 3.464101615137754)

        indexBegin = 1
        indexEnd = 2
        result = self.laminate.getSinAnglesMultiplier(indexBegin, indexEnd)
        self.assertEqual(result, 2.449489742783178)
        
        indexBegin = 1
        indexEnd = 1
        result = self.laminate.getSinAnglesMultiplier(indexBegin, indexEnd)
        self.assertEqual(result, 1.7320508075688772)

    """
        test calculating cut width of original laminate from different generations
        
        rdus: 10, rdu width: 2", toFit: 20", kerf: 5/64", design pieces cut width: 1"
    """
    def test_getBaseCutWidth(self):
        # testing 3rd generation : 45/60A/45D
        result = self.laminate.getBaseCutWidth()
        self.assertEqual(result, 0.48524817793679187)

        # testing 4th generation : 45/60A/45D/30A
        self.laminate.parseCmd('45/60A/45D/30A')
        result = self.laminate.getBaseCutWidth()
        self.assertEqual(result, 0.5171425756292812)

        # testing 2nd generation : 45/60A
        self.laminate.parseCmd('45/60A')
        result = self.laminate.getBaseCutWidth()
        self.assertEqual(result, 0.6224557589700653)

        # testing 1st generation : 45
        self.laminate.parseCmd('45')
        result = self.laminate.getBaseCutWidth()
        self.assertEqual(result, 1.078125)

        # empty command string
        self.laminate.setEmptyCmd()
        result = self.laminate.getBaseCutWidth()
        self.assertEqual(result, -1)
    
    def test_getCutLength(self):
        result = self.laminate.getCutLength(0, self.laminate.cutCmd["angle"][0])
        self.assertEqual(result, -1)

        result = self.laminate.getCutLength(5, math.radians(90))
        self.assertEqual(result, -1)

        result = self.laminate.getCutLength(5, math.radians(0))
        self.assertEqual(result, -1)

        result = self.laminate.getCutLength(5, self.laminate.cutCmd["angle"][0])
        self.assertEqual(result, 7.181553246425874)

    def test_getNumberCuts(self):
        # testing 3rd generation : 45/60A/45D ; rdus: 10
        result = self.laminate.getNumberCuts(3)
        self.assertEqual(result, 160)

        # testing 2nd generation : 45/60A; rdus: 10
        result = self.laminate.getNumberCuts(2)
        self.assertEqual(result, 80)

        # testing 1st generation : 45; rdus: 10
        result = self.laminate.getNumberCuts(1)
        self.assertEqual(result, 40)

        # testing 4th generation : 45/60A/45D/30A; rdus: 10
        result = self.laminate.getNumberCuts(4)
        self.assertEqual(result, 320)

        # error generation empty cmd
        result = self.laminate.getNumberCuts(0)
        self.assertEqual(result, -1)

    def test_getPreviousGenerationHeight(self):
        cutLength = 0
        angle = 0.5
        heightDesign = 10
        result = self.laminate.getPreviousGenerationHeight(cutLength, angle, heightDesign)
        self.assertEqual(result, -1)

        cutLength = 1
        angle = 0
        heightDesign = 10
        result = self.laminate.getPreviousGenerationHeight(cutLength, angle, heightDesign)
        self.assertEqual(result, -1)

        cutLength = 1
        angle = 0.5
        heightDesign = 0
        result = self.laminate.getPreviousGenerationHeight(cutLength, angle, heightDesign)
        self.assertEqual(result, -1)

        # angle: 60 degrees, cut length = 1.24491151794013 inches, height design = 7 inches
        angle = math.radians(60)
        cutLength = self.laminate.getCutLength(1, angle)
        heightDesign = 7
        result = self.laminate.getPreviousGenerationHeight(cutLength, angle, heightDesign)
        self.assertEqual(result, 6.410003913447593)

    def test_setHeights(self):
        #print "::Test GetHeights()"
        self.laminate.setHeights()
        #print self.laminate.cutCmd["height"]
        self.assertEqual(self.laminate.cutCmd["height"], [4.830008258375506, 6.410003913447593, 7])

if __name__ == '__main__':
    unittest.main()
