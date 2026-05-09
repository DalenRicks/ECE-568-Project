The files used in the presentation and report were 
```
ESP B run1.csv
ESP B run2.csv
ESP B run3.csv
ESP D run1.csv
ESP D run2.csv
ESP D run3.csv
```

The remaining files are additional test results that did not make it into the report, but provide insight to the behavior of the system.
For example, profiling the ESP32 on my laptop provided different results than profiling on my desktop. This makes sense due to the 
different clock speeds and internal crystals of the two devices adding their own skew to the "ground truth" time measurement.

One improvement of the system would be to use a more stable time source as the ground truth measurement like GPS-time, but that would require
additional hardware and a clear view of the sky to work reliably. Another option is to directly the fingerprinting device's clock skew 
using a trusted external measurement device, like a calibrated oscilloscope. Once the clock skew is known, it can simply be subtracted from the
measurements. 