Launching the game
==================

The simplest way is: ::

    ppython main.py

If you want to play a specific level : just pass its name as the first argument to ``main.py`` (without the ``.lvl`` extension). For example: ::

    ppython main.py level3

Playing the game
================

Your goal is to reach the exit in each level. The exit is a big white sphere. You can use "portals" to go from one point of the level to another unreachable point. Just create a portal where you want to go, create a portal near you, go into the portal and "tadam" you're on the other side.

Here are the available keys (AZERTY keyboard by default, change this in ``Gate/constants.py`` if needed):

* ``Z, Q, S, D`` : strafe and move
* ``SPACE`` : jump
* ``LMB`` : create "left" portal
* ``RMB`` : create "right" portal
* ``E`` : erase portals
* ``C`` : clear portal status (for debug purpose only)
* ``R`` : reset position
* ``P`` : print position
* ``B`` : enter pdb
