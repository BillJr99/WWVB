# WWVB

This program reads and decodes 1000 Hz modulated audio according to the [WWVB](https://en.wikipedia.org/wiki/WWVB) modulation standard.  WWVB is a radio station operated by the National Institute of Standards and Technology (NIST) from Fort Collins, Colorado.  It broadcasts the current time and date on a 60 kHz channel, which reaches most of the continental United States for use by clocks and watches to automatically set the time.

This low frequency uses ground propagation to reach most of the country, and although best reception can be found during the overnight hours, it works remarkably well most days on the east coast as well.  However, a properly tuned antenna would need to be some large proportion of the wavelength of the signal, and even a one-quarter wavelength antenna at this frequency would measure about 3 quarters of a mile in length!  Because the WWVB signal consists of a slow and simple modulation strategy, its signal can be heard by devices with tiny inefficient antennas (small enough to fit in a wristwatch!).  

This modulation strategy is called [Pulse-Width Modulation (PWM)](https://en.wikipedia.org/wiki/Pulse-width_modulation).  WWVB uses three kinds of data values that it sends using this modulation: a 0, a 1, and a marker bit.  Sending a single bit takes one whole second, and during that second, a weak attenuated signal is sent followed by a stronger signal.  The duration (or width) of that attenuated signal tells us what kind of bit we have.  Here are the durations of each bit sent in a one second period:

|   **Bit**  | **Attenuated Signal Width** | **Strong Signal Width** |
|:----------:|:---------------------------:|-------------------------|
|    **0**   |            200 ms           |          800 ms         |
|    **1**   |            500 ms           |          500 ms         |
| **Marker** |            800 ms           |          200 ms         |

Here is an example signal that sends a marker bit followed by two zero bits.  Notice that the first bit is quiet for almost one second (0.8 seconds), and then loud for the remainder of the second (0.2 seconds).  That's a marker.  The second and third bits reverse that trend, and a requiet for only 0.2 seconds and then loud for the remainder of the second (0.8 seconds).  These are zero bits.  This signal transmitted a marker, followed by a 0, followed by a 0.

![A marker followed by two zero bits from WWVB using PWM](marker-zero-zero.png)

Here's another example that sends a zero, a one, and a one bit.

![A zero followed by two one bits from WWVB using PWM](zero-one-one.png)

