# Energy-consumption-of-a-GPS
The Internet of Things(IoT) is rapidly growing as one the most important technologies in the industry. IoT designers is facing an energy challenge, as more of the devices are designed for a substantially longer operation time. One of the most used and energy demanding technologies in IoT is the GPS. It’s therefore necessary to have an energy model of the GPS receiver that can be used for controlling it optimally.

In this project we purpose a simple energy model that can predict the energy cost of getting a positional ﬁx with a GPS receiver. In the ﬁrst step to make an energy model, we build a measurement platform for measuring the energy consumption of the GPS receiver. In the next step we measure the energy consumption of the GPS receiver during speciﬁc tests. The next step in making a model is to relate the measurements with the theory. We emphasize on two important phases of the GPS receiver’s operation, to derive to our energy model. The two phases are the acquisition phase and the tracking phase. We relate the data to the two phases by using an approach that uses a trigger mechanism for signaling during the measurements. In the next step, we build a state diagram and an energy model. The model is given by:

E_total = E_(Updateperiod) ∗t/(Updateperiod)

The results shows that an application can use the model to control a GPS receiver optimally in terms of energy consumption.
