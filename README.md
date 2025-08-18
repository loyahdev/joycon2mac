# Nintendo Switch 2 JoyCon as Keyboard

This is a tool to use your Joycon 2 on Mac as keyboard controller. I intend to make it a fully customizable, but for now, all you can do is connect a maximum of 2 Joycons and have all button and joystick functions mapped to the keyboard.

When both Joycon 2's are connected they work in vertical mode with the L/R buttons facing
up. While for each single Joycon 2 they work horizontal with the SL/SR buttons facing up. Mapping for single and dual Joycon 2's change automatically.

# How to use this?

1. Download the latest release from the releases tab
2. Follow instructions in app
___
5. Hold the sync button on any Joycon 2 to pair with the app
6. Enjoy

It's not the best tool ever but its worth using if you really want to. There is still numerous bugs and some button mapping might be messed up per orientation.

>[!NOTE]
>When Apple accepts my entitlement request for Driver Kit I will make this tool into a fully working HID emulator to have the Joycon 2's work as a fully functional bluetooth controller.

---
## Special Thanks! 
I was only able to do this because of [the original joycon2py by  TheFrano](https://github.com/TheFrano/joycon2py/)

Some more mac based info I used was provided in [moutella's joycon2mouse for Mac](https://github.com/moutella/joycon2mouse)


# Building
macOS: python3 setup.py py2app
(make sure to install correct requirements)
Built app is in the dist folder.
