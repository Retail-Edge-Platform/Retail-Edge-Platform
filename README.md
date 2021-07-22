# Retail-Edge-Platform (REP)
REP is the beginning of an open-source platform targeted at the brick-and-mortar retail space that has been seeing a steady increase in digitization.

## Goals
### Initially REP goal was to:
 * Provide a working example of a retail end customer facing immersive and interactive portal to assist in the retail experience
 * Create a pipeline to gather streaming data about the interactive experience
 * Simulate this interactive data stream for analytics development
 * Host a data-science centric analytics development environment. (Jupyter Notebooks)
 * Provide a means to move data from the Edge -> Cloudward

### To affect the operations of the retailers and brands, Retail-Edge-Platrom needs to:
 * Continue the connection to the cloud with examples of AWS and GCP IoT integrations
 * Leverage Jupyter Notebook analytic development in the stream-based cloud framework
 * Provide extensible analytics backed dashboard for retailers
 * Provide API endpoints to these dashboard elements to allow retailers and brands the opportunity to integrate with other systems

### Delighting both retailers, brands, and end customer at the Edge means:
 * Expanding the nature of the Edge platform's presence in the physical space with display, lighting, sound, and sensors options
 * For sensors, leverage Docker containers to deliver high performance on Edge processing that will feedback to customer experience and to the cloudward datastream
 * Providing remote management of the Retail-Edge-Platform forward deployed asset. This includes installation and bring-up assistance, platform and experience calibration, and the positioning of new end-customer facing material on the Edge.
 * Creating a self-service means to create new end-customer facing material that will allow marketers, brands, and even smaller retailers to create compelling material that takes advantage of the lavish area of interactive space to educate/assist potential end customers about their purchase.


This material is much like traditional web material but because of the use of sensors can be much more interactive. Along with that theming to fit the retail or brand environment is much richer because it’s not fighting for page real-estate. 
This project uses Docker to setup data analysis pipeline.

## What is here now
### Simple Example Model
Below is a diagram of initial data analysis pipeline as built.

<img src="/assets/Overview-As Built Overview.png?raw=true" alt="drawing" width="700"/>

Example retail end customer user interface experience currently captured in the repo.

<img src="/assets/Overview-User Interface.png?raw=true" alt="drawing" width="700"/>

Data Analysis workbench using Jupyter Notebooks. Tied into the local Redis database.

<img src="/assets/Overview-DataAnalysis.png?raw=true" alt="drawing" width="700"/>

Session Generator to create fictional traffic to allow experimentation with analytics.

<img src="/assets/Overview-Session Generator.png?raw=true" alt="drawing" width="700"/>

There is 

Here is how to build it.

<img src="/assets/Overview-Build.png?raw=true" alt="drawing" width="700"/>


## Future

 * It would be easy to expand this with an OpenCV container and provide people and facial detection to start to gather real analytics.
 * Adding a IOT MQTT endpoint to AWS or GCP would be very easy. This would allow further analysis off the Edge device.
 * As to the edge device an Intel NUC would be more than enough. A USB video camera like an Intel Real Sense L515 would work nicely.
 * To keep cost down and make development easier load it with Linux, Docker or K8S. Edge management could be either AWS or other.
 * As to developing content my other project B4Time uses draw.io/diagram.net to allow computer architects to model a system.  This same plugin approach could allow a skilled graphics artist to design the user experience and deploy it without the need to involve a UI developer.
 * Retail experience could be packaged in a stylish and in expensive furniture quality shell allowing the customer to access the content through a touch screen while also accessing the physical product. 
 * The product could be a pay as you go model with sales inspired by the interface paying for the subscription.

<img src="/assets/sideboards-buffets.jpeg?raw=true" alt="sidboard" width="200"/>












