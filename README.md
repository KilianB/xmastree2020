# Animation

Original youtube video: https://www.youtube.com/watch?v=TvlpIojusBE

<p align="center">
<img src="/resources/LEDDistribution.png?raw=true"/>
</p>

The following code is not tested on any real hardware.

## Singing christmas tree


Create a simple equalizer visualization and display it on the tree

1. The gain of different frequenices of a music file are extracted by applying a fast fourier transform
2. The frequencies between 20 Hz and 20 KHz are normalized to range [0-1] and are equidistantly grouped into n buckets.
3. The leds are sorted into n buckets based on a line drawn from the to the middle of the tree.
4. The precomputed values are played back in real time.

### Not normalized spectogram

<p align="center">
<img src="/resources/compact.gif?raw=true" alt="Not normalized spectogram"/>
</p>

### LED bucket index

<p align="center">
<img src="/resources/ChristmasSong.png?raw=true" alt="LED bucket index"/>
</p>

Required:

- Use a sound file which is at least 30 seconds long

``` sh

    pip install cffi
    pip install numpy
    pip install pysoundfile

    #For linux
    sudo apt-get install libsndfile1

    # If using conda use 
    conda install -c conda-forge pysoundfile
```


## Game of live

Run a Game of Live simulation on the tree

k = 8 
1. A k-nearest neighbour graph is constructed based on the euclidiean distance of each led 
    - the nearesth neighour peroperty isn't symmetric, therefore the simulation might behave wonky at times
    - The board is constrained on the edges and does not wrap around 
2. Random pixels are initialized at the beginning and the simulations starts

## Drop.py

Work in progress? Randomly select individual Leds which light up and propagate it's color value each iteration to close by neighbour leds. Each step the led looses a little bit of brightness. 
