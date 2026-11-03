# Sofle

- [Chinese](README.md)
- [English](README_EN.md)

## Update List

- 2026/11/02
  1. Encoder rotation is now remappable in standard ZMK Studio. Two virtual keys appear below the left thumb keys: counterclockwise on the left, clockwise on the right. The base defaults are volume down/up; other layers inherit these until remapped.
  2. This follows the virtual-key approach in [gmk70_firmware](https://github.com/skyser2003/gmk70_firmware): each encoder step becomes an ordinary key press/release. Flash the updated left-half firmware, reconnect Studio, select a layer, edit either virtual key, and save. Existing physical key positions are preserved.

- 2026/10/29
  1. Removed the Q/S/Z soft-off combo to avoid delaying these keys during simultaneous input, such as Korean Semo-e. Flash the updated left-half firmware for this change.
  2. To power off, hold the layer-2 thumb key and hold the physical `.` key for 2 seconds. Press the reset switch to wake the keyboard.

- 2024/12/21
  1. Added support for zmk-studio (just refresh the left hand to use).
- 2024/10/24
  1. Modified power supply mode to reduce power consumption.
  2. Fixed the automatic shut-off feature for RGB power supply.
- 2025/8/22
  1. Added soft off for transport. The original Q/S/Z shortcut was removed on 2026/10/29; use the layer-2 shortcut described above. Press the reset switch to wake the keyboard.
  2. This month, I also updated the ultra-thin versions of the corne and sofle cases. The frame and base plate have been thickened, and the opening of the reset switch has been adjusted, so that the reset switch can be easily pressed. At present, we are still conceptualizing how to design the shell with an inclined bracket.If you have carefully examined a PCB, you will notice that there are reserved interfaces for expansion IO. I wonder if anyone has been able to utilize them,I will try it！
  3. The GIF animations on the right-hand keyboard screen have been removed, which will significantly reduce the power consumption of the right-hand keyboard.
 
-2026/6/22
The keyboard now supports key remapping via DYA STUDIO. Chinese users should contact the seller to obtain the Chinese version of the DYA STUDIO installer. This PC software offers better key remapping functionality than ZMK Studio. Website: https://studio.dya.cormoran.works/ https://studio.dya.cormoran.works/

> If your  sofle was updated before 2025/8/22, please update to the latest firmware.
>

## Contact Me

For 3D printed model files or any issues and malfunctions with the keyboard, please contact [380465425@qq.com](mailto:380465425@qq.com)

## Sofle Keymap

Encoder direction bindings use the normal Studio keymap and persist like other
keys. The existing encoder push button is a separate physical key. The firmware
uses ZMK's existing sensor rotation handling for detent counting and 5 ms taps.

Host-side checks for the virtual-key bridge can be run with `bash tests/run.sh`.
Full firmware builds also validate the matrix transform and Studio layout.

![Sofle键位图](keymap-drawer/eyelash_sofle.svg)
