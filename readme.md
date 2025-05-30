# CS4480 Network Management Assignment - Part 2

## Setup Instructions

1. Clone the repository & set up Docker:

  get ./dockersetup in cs4480-2025-s/pa3/part1/
  afterwards put sh-command folder and python folder in part1/
  move the Dockerfile from the sh_command folder into part1 folder. 
  modify the docker-compose.yaml in /part1/ to be the one downloaded
  
    afterwards call "chmod +x part1/*.sh" and 
                    "chmod +x part2/Dom_Johansen_u1304418.py"

  call ./Dom_Johansen_u1304418.py --setup-all to set up everything,
  if errors occur do it mainly in order. Afterwards

now after its running you can define what route to take by either calling
./Dom_Johansen_u1304418.py --north or ./Dom_Johansen_u1304418.py --south to change routes

## Demo Video Info

The demo video shows the following:

Initially you see all the commands hostname, geni-get user_urn etc. on the left side from top down is HostA, R1, R4, and HostB. 
Ive cut the time inbetween changing from north to south just so it wouldnt go over 60 seconds on the video. you can see me type 
./orch.py --north and ./orch.py --south (the python file name isn't correct but its code is the same as the submission python file)
you see i start pinging HostB from hostA, i change the path so its north -> south -> north, afterwards i Ctrl-C hostA ping, and you see 
that there is no packet loss during changing paths. 

**Quick clarifications for Demo Video**
1. cuts are used since it was taking a long time for the shell script to move from north to south (it was monday (4/21/2025) and people were saying powder was giving slow connectivity problems) so to have it within the wanted time frame I just paused the recording until the script finished.
2. the file is not called "Dom_Johansen_u1304418.py" but called "orch.py", it is the same python code just renamed.