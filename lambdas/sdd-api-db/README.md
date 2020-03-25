# Social Distancing Dashboard Database API
This folder contains all apis required to access data from database.

## prerequisited
You need to have the following tools installed
* aws (amazon commandline interface)
* sam (amazon tool for deploying lambdas)
* docker (needed to start an amazon-linux docker build that is able to build alls dependencies locally. This is quite complicated... but thats the future they say. Ask Parzival for help)
* 
## deployment
* Meet prerequistes
* run ./build-helper 
  * This script contains neccessary steps. Dont ask why. It won't work if you dont do exactly these steps.

## create new api
* copy existing api
* modify names in template.yaml
* modify first two line in build-helper.sh
* update requirements.txt
* deploy
* ask Parzi for help ;-)

## change api
* contact author
* test locally 
* update requirements.txt if you added packages
* upload with build-helper as described before