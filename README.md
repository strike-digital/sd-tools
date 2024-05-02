# SD Tools for blender

This is an addon I use for testing features and fixing small papercuts that I have with Blender. Feel free to download and try it, but be prepared for not everything to work and for an addon that is focused on on my specific workflow rather than being as adaptable as possible.

Currently it contains:
* Operators for extracting node values into dedicated input nodes, and also for converting those input nodes into group inputs of their parent group.
* Operator for batch changing view settings across all workspaces
* Operator to play an animation for the start frame rather than the current frame
* Operator to make selecting all objects in a collection easier
* A panel to inspect the various properties of nodes and their inputs
* An Operator to toggle between the shader and geometry node editors
* An operator to open the asset browser at the bottom of the screen, like the content browser in Unreal Engine
* An operator for switching workspaces with ctrl+tab, like in other programs. Supports thumbnails of each editor.
* An operator to set the transparency blending mode of a material in Eevee to clip, regardless of the current render engine
* An extended node rename operator bound to F2, that lets you also change other settings such as node group inputs and outputs, without having to go inside and look in the N-Panel
* An operator to automatically set a reroute node to be active after it is added with shift right-click, cause by an unfixed bug in Blender
* An operator to swap the x and y render resolutions of the scene, available from the preset menu in the panel header.
* An update to the render operator on F12 to automatically render into a new render slot, rather than overwriting the old one.
* An operator to play the current timeline from the start, bound to shift space.
