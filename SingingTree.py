
import numpy as np
import soundfile
import numpy
import scipy
#import pylab
import time

#import gif
#import matplotlib
#matplotlib.use('tkagg')

import re
import math

#import board
#import neopixel

def timeMs():
    return time.time_ns() // 1000000 

def xmaslight():

    # NOTE THE LEDS ARE GRB COLOUR (NOT RGB)

    # IMPORT THE COORDINATES (please don't break this bit)

    coordfilename = "Python/coords.txt"

    fin = open(coordfilename, 'r')
    coords_raw = fin.readlines()

    coords_bits = [i.split(",") for i in coords_raw]

    coords = []

    for slab in coords_bits:
        new_coord = []
        for i in slab:
            new_coord.append(int(re.sub(r'[^-\d]', '', i)))
        coords.append(new_coord)

    # set up the pixels (AKA 'LEDs')
    PIXEL_COUNT = len(coords)  # this should be 500

    pixels = neopixel.NeoPixel(board.D18, PIXEL_COUNT, auto_write=False)

    # YOU CAN EDIT FROM HERE DOWN

    #       Create a frequency spectrogram of wav file and map it to
    #       the tree.
    #       The x direction specified the bucket
    #       The z height is the maximum amplitude of a frequency which falls into the bin
    #
    #             ^
    #            / \
    #           /   \
    #          /     \
    #         /       \
    #        +---------+
    #            | |
    #
    # Bins   1 2 3 4 5 6
    #

    # Settings

    # Number of bins.
    # Each bin is a section represented on the tree
    bins = 7

    # Update interval in milliseconds
    # To compute the fft a certain number of sample points is required to extract higher frequencies
    # oversampling and overlapping sliding windows could be used to circumvent this issue
    updateInterval = 150

    #: Constrain maximum frequencies to audible range of [20Hz-20kHz]
    frequencyCutoff = [20, 20000]

    # Process wav file and compute the gain for differrent frequencies
    animationData =  precomputeAnimation(frequencyCutoff,bins, updateInterval)

    #Map the existing leds to individual bins representing a group of frequencies
    ledIndex, zMax = mapLedsToBuckets(coords, bins)
    pixels = [x for x in range(PIXEL_COUNT)]

    runAnimation(animationData,ledIndex,coords, zMax, pixels,updateInterval)


def runAnimation(animationData,ledIndex,coordinates, zMax, pixels, updateInterval):
    '''

        Parameters:
        
        animationData: a list with 
        ledIndex: led index sorted into different buckets dictionary with key [0 - (bins-1)]
        coordinates: the coordinates of the leds
        zMax: the maximum Z coordinate of the leds 
        pixels: 
        updateInterval: frame duration in milliseconds


    '''

    colourOn = [0,50,50] #purple
    colourOff = [0,0,0]

    bins = len(ledIndex)

    run = True
    
    frameCount = 0

    animationStart = timeMs()

    while run:

        ## Some time fiddeling to keep the animation in sync with the music
        ## Without actual testing the hardware this is just a best effort implementation
        frameStart = timeMs()
        
        print("Run frame: ",frameCount, "Timestamp: ", frameStart)

        animationFrame = animationData[frameCount]

        #Take a look at each bucket
        for bin in range(bins):

            ##Gain between [0-1]
            gain = animationFrame[bin]

            #The z coordinate cutoff
            zCutoff = zMax * gain

            leds = ledIndex[bin]

            ##Gain now is percentage 0 
            for led in leds:
                pixels[led] = colourOn if coordinates[led][2] <= zCutoff else colourOff
            
        #pixels.show()
        
        elapsed = timeMs() - frameStart

        delay = updateInterval - elapsed
        if delay > 0:
                time.sleep(delay/1000)
                frameCount += 1
        else:
            print("Skipping frames. Consider increasing the time window",delay)
            ##Next higher frame delay
            requiredFrameIndex = math.ceil((timeMs() - animationStart) / updateInterval)
            startTimeOfNextFrame = requiredFrameIndex * updateInterval
            
            delay = timeMs() - startTimeOfNextFrame
            time.sleep(delay/1000)
            frameCount = requiredFrameIndex

        if frameCount >= len(animationData):
            run = False



def mapLedsToBuckets(coordinates, bins):

    # Maybe don't be pythonic and resolve everything in a single loop?

    minX = min(coordinate[0] for coordinate in coordinates)
    maxX = max(coordinate[0] for coordinate in coordinates)

    minZ = min(coordinate[2] for coordinate in coordinates)
    maxZ = max(coordinate[2] for coordinate in coordinates)

    midX = (minX + maxX)/2

    binWidth = (maxX - minX)/bins

    # Define the points separating buckets on the tree.
    # All buckets end at the mid top point
    highMidPoint = np.array([midX, maxZ])

    lowerBinPoints = []

    for i in range(bins):
        lowerBinPoints.append(np.array([minX + binWidth * i, minZ]))

    def isLeftOfLine(p0, p1, p):
        ''' 
            Check if a point c lays on the left or right side of a line 
            defined by the 2 points p0 and p1.

            ##Reference:  https://stackoverflow.com/a/3461533/3244464
        '''
        ## p0 and p1 are x&y based p is z based
        return ((((p1[0] - p0[0])*(p[2] - p0[1])) - ((p1[1] - p0[1])*(p[0] - p0[0]))) > 0)

    def calculateBinForPoint(ledCoodrinate):
        for i in range(len(lowerBinPoints)):

            #If points are left of the first line count it to the first bucket  regardlessly
            
            if(isLeftOfLine(
                lowerBinPoints[i],
                highMidPoint,
                ledCoodrinate
            )):
                if i < 2:
                    return 0 
                else:
                    return i-1
        
        ##If points are not left of the last border count it towards the last bucket
        return bins - 1

    buckets = [calculateBinForPoint(coord) for coord in coordinates]

    ##Sort the led index into lists containing the bucket
    ledIndex = {}

    ##Initialize empty bucket bins
    for i in range(bins):
        ledIndex[i] = []

    for i in range(len(buckets)):
        ledIndex[buckets[i]].append(i)

    return ledIndex, maxZ


def processFrame(start, end, bins,frequencyCutoff, audio_samples_in,sample_rate):

    audio_samples = audio_samples_in[start:int(end)]

    number_samples = len(audio_samples)

    freq_bins = np.arange(number_samples) * sample_rate/number_samples

    # FFT calculation
    fft_data = scipy.fft.fft(audio_samples)

    # Throw away the second half of the fft
    freq_bins = freq_bins[range(number_samples//2)]
    normalization_data = fft_data/number_samples
    magnitude_values = normalization_data[range(len(fft_data)//2)]
    magnitude_values = numpy.abs(magnitude_values)

    # Compact the bins
    compactedFrequencyBins = numpy.linspace(
        frequencyCutoff[0], frequencyCutoff[1], bins)
    compactedMagnitudeValues = numpy.empty(len(compactedFrequencyBins))

    frequencyPerBin = freq_bins[1]
    frequencyPerNewBin = compactedFrequencyBins[1]-compactedFrequencyBins[0]


    originalBins = freq_bins

    startIndex = int(frequencyCutoff[0] // frequencyPerBin)

    binsPerOldBin = int(frequencyPerNewBin // frequencyPerBin)

    compactedMagnitudeValues[0] = (
        magnitude_values[startIndex:binsPerOldBin].max())
    for i in range(1, bins):
        compactedMagnitudeValues[i] = (
            magnitude_values[binsPerOldBin * i: binsPerOldBin * (i+1)].max())
        #print("From:",binsPerOldBin * i, "To:", binsPerOldBin * (i+1),"i:",i,compactedMagnitudeValues[i])

    x_asis_data = freq_bins
    y_asis_data = magnitude_values

    # gif_frame.append(createPyPlot(compactedFrequencyBins,compactedMagnitudeValues,frequencyPerNewBin))
    # pylab.bar(compactedFrequencyBins, compactedMagnitudeValues, color='blue',width=frequencyPerNewBin) # plotting the spectrum
    #pylab.xlabel('Freq (Hz)')
    #pylab.ylabel('|Magnitude - Voltage  Gain / Loss|')
    # pylab.savefig(str(offset)+"compact.jpg")
    return compactedMagnitudeValues


def precomputeAnimation(frequencyCutoff,bins,  updateInterval):
    '''

        updateInterval chunk length in milliseconds
    '''

    file_path = 'Python/Natalie Cole - Carol of the Bells.wav'

    # Read the audio file

    # Sample rate are the data points in HZ
    audio_samples, sample_rate = soundfile.read(file_path, dtype='int16')

    samplePoints = len(audio_samples)

    # Duration of audio file in seconds
    duration = round(len(audio_samples)/sample_rate, 2)
    print("Duration of file: ", duration,"s")

    samplesPerChunk = int(sample_rate * (updateInterval/1000))

    durationChunk = round(samplesPerChunk/sample_rate, 2)

    print("Sample points per chunk: ", samplesPerChunk)
    print("Duration of chunk: ", durationChunk,"s")

    # Audio file processing needed in seconds
    #timeWindow = samplesPerChunk / sample_rate

    print("Begin preprocessing audio file")

    i = 0
    frame = []
    requiredChunks = math.ceil(samplePoints / samplesPerChunk)

    maxGain = 0

    while True:

        start = samplesPerChunk * i
        end = start + samplesPerChunk

        if start >= samplePoints:
            break

        if end >= samplePoints:
            end = samplePoints-1

        curFrame = processFrame(start, end, bins,frequencyCutoff, audio_samples,sample_rate)

        tempMaxGain = max(curFrame)
        if(tempMaxGain > maxGain):
            maxGain = tempMaxGain

        frame.append(curFrame)
        i += 1

        if i % 100 == 0 or i == requiredChunks:
            print("Progress ",i, "/", requiredChunks)
    
    #gif.save(gif_frame, "compact.gif", duration=timeWindow, unit="seconds")

    #Normalize gain to range 0 - 
    normalizedFrame = [f/maxGain for f in frame]
    return normalizedFrame

# yes, I just put this at the bottom so it auto runs
xmaslight()


#Create gif animation

#gif_frame = []
#@gif.frame
#def createPyPlot(x_asis_data, y_asis_data, width):
#    pylab.bar(x_asis_data, y_asis_data, width=width,
#              color='blue')  # plotting the spectrum
#    pylab.xlabel('Freq (Hz)')
#    pylab.ylabel('|Magnitude - Voltage  Gain / Loss|')
#    pylab.ylim((0, 1))
    # pylab.savefig(str(offset)+"original.jpg")