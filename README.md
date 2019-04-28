micromanager-samples
====================

*Python code samples for [Micro-manager](http://www.micro-manager.org) image acquisition system*

Micromanager project provides broad opportunity for constructing sophisticated image acquisition protocols (e.g. in microscopy). So it becomes possible to overreach vendor software limitation and realize your inherent researcher's freedom as far as possible.

Unfortunately, micromanager documentation lacks for detailed examples. It is not easy to understand the hardware capabilities and API logic. I hope those samples will be helpful in your journey, especially for live video acquisition.

### Available samples

[Numpy](http://www.scipy.org/index.html), [opencv](http://opencv.org) are used here.

* Getting list of available properties and their allowed values
* Video grabbing with opencv highgui
* Efficient frame conversion with numpy (rgb32 to rgb, bgr)


## Setup

### Windows 

Install Micromanager from official site and add `C:\Program Files\Micro-Manager-1.4` to PYTHONPATH system variable. After that you can simple import micromanager's core:

    import MMCorePy

### Linux

I made [Archlinux PKGBUILD](https://aur.archlinux.org/packages/micromanager-git/). Only MMCore and python 2 interface available.

See test snippet at the end of PKGBUILD.


## Issues

### Memory requirements not adequate

    2014-02-11T14:36:41.328125 p:612 t:2300 [LOG] Error occurred. Device BaumerOptronic. Failed to initialize circular buffer - memory requirements not adequate.
    Traceback (most recent call last):[Decode error - output not utf-8]
        mmc.startContinuousSequenceAcquisition(1)
      File "C:\Program Files\Micro-Manager-1.4\MMCorePy.py", line 4956, in startContinuousSequenceAcquisition
        return _MMCorePy.CMMCore_startContinuousSequenceAcquisition(self, *args)
    MMCorePy.CMMError: Failed to initialize circular buffer - memory requirements not adequate.

**Solution**: Just increase circular buffer (60 megabytes works fine for me). According with mailing list 600-800-1200 MB for circular buffer is normal.

    mmc.setCircularBufferMemoryFootprint(60)


### Circular buffer is empty

`mmc.popNextImage()` and `mmc.getLastImage()` both raises an exception while circular buffer is empty.

**Solution**: Check buffer for image count. (See the samples.)

    if mmc.getRemainingImageCount() > 0:
        rgb32 = mmc.popNextImage()


## Snippets

    def rgb32asrgb(rgb32):
        """View RGB32 as RGB array (no copy).

        low memory address    ---->      high memory address
        | pixel | pixel | pixel | pixel | pixel | pixel |...
        |-------|-------|-------|-------|-------|-------|...
        |B|G|R|A|B|G|R|A|B|G|R|A|B|G|R|A|B|G|R|A|B|G|R|A|...
        http://avisynth.nl/index.php/RGB32
        """
        return rgb32.view(dtype=np.uint8).reshape(
            rgb32.shape[0], rgb32.shape[1], 4)[...,2::-1]
