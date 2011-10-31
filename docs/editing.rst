Level editing
#############

Edit the ``.lvl`` files
=======================

Each level consists of a ``.lvl`` file (look at ``level1.lvl``, ``level2.lvl``... for examples).

The structure of ``.lvl`` files is :

* a JSON header that contains some settings for the level :

    * ``origin`` : player starting point
    * ``next_level`` : name of the level to load when this level is won
    * ``pointlights`` : list of coordinates for the lights

* a line containing ``-LEVEL-`` that begins the level "model"
* many "slices" of ASCII chars separated by lines containing ``-Z-``

The "slices" are ASCII representations of each Z level of the level world. For example, this is a floot with a hole in its center: ::

    #####
    #####
    ## ##
    #####
    #####

Here are the ASCII chars availables :

* Normal cubes with different textures

    * ``D`` : a "orange" texture with black curves on it
    * ``#`` : a stone texture
    * ``=`` : a wood texture

* Cubes that cannot receive portals

    * ``M`` : a metallic rusty texture

* Deadly cubes

    * ``L`` : lava

* Friendly cubes

    * ``X`` : exit

Use the ingame editor
=====================

If you don't want to edit ``.lvl`` files by hand, I'm working on an inline editor. To launch it, just start the game with the ``-e`` flag before the name of the level: ::

    ppython main.py -e mylevel

When in editor mode, here are the available keys (AZERTY keyboard by default, change this in ``Gate/constants.py`` if needed):

* ``A`` : fly up
* ``W`` : fly down
* ``Z, Q, S, D`` : strafe
* ``R`` : reset position
* ``P`` : print position
* ``B`` : enter pdb
* ``L`` : add a light at the current position
* ``F11`` : save the level

Here is what you can do in editor mode :

* Copy an existing cube : clic on a cube and a copy of it will appear on the face you were looking at
* Make multiple copies of a cube : look at a cube without clicking it and use the number keys from 1 to 9 to create (1 to 9) copies of the cube. It's the same as clicking on a cube, then on its copy, then on the copy of its copy and so on
* Delete an existing cube : right-clic a cube
* Make a rectangle : look at a cube and use the ``X`` key to create a rectangle from this cube to where you are (the camera)
* Make a room : look at a cube and use the ``Shift-X`` key to create a room (non-filled parallelepiped) from this cube to where you are (the camera)

Loading an existing level
-------------------------

You can edit an existing level by launching the editor on it: ::

    ppython main.py -e level1

Notes
-----

When saving the level, the camera position in the editor is saved as the ``origin`` position in the ``.lvl`` file so it will be the player's original position.
