import time
import digitalio
import board
import busio
import terminalio
import rotaryio
import analogio
import adafruit_ssd1306
# import asyncio
import usb_hid
from adafruit_hid.mouse import Mouse
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

# -- protocol
i2c = busio.I2C(board.GP21, board.GP20)

# -- entities
encoder = rotaryio.IncrementalEncoder(board.GP17, board.GP16)
encoder_button = digitalio.DigitalInOut(board.GP28)
encoder_button.direction = digitalio.Direction.INPUT
encoder_button.pull = digitalio.Pull.UP
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
mouse = Mouse(usb_hid.devices)
joyY = analogio.AnalogIn(board.GP26)
joyX = analogio.AnalogIn(board.GP27)

# -- variables
in_min, in_max, out_min, out_max = (256, 65000, -5, 5)
filter_joystick_deadzone = lambda x: int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min) if abs(x - 32768) > 500 else 0
last_rotary_pos = 0
# -- menu
menu_show = True
menu_items = ['MOUSE', 'VOLUME', 'BRIGHTNESS', 'MAKRO']
menu_index = [0, -1]
menu_button_state = False
prev_menu_button_state = menu_button_state
# -- display
display_time = -1

def draw_UI():
  oled.fill(0)
  oled.line(30, 0, 30, 64, 0xFFFFFF)
  oled.show()
#endef

def render_menu():
  oled.fill_rect(31, 0, 97, 64, 0x0)
  for i in range(len(menu_items)):
    oled.text(menu_items[i], 36, (i * 10) + 2, terminalio.FONT)
  #endfor
  oled.show()
#enddef

def render_menu_index():
  global menu_index
  # print('render_menu_index', menu_index)
  if menu_index[0] != menu_index[1]:
    oled.fill_rect(0, 0, 30, 64, 0x000000)
    miy = (menu_index[0] * 10) + 1
    oled.fill_rect(16, miy, 8, 8, 0xFFF)
    oled.line(16, miy + 4, 30, miy +4, 0xFFF)
    oled.show()
    menu_index[1] = menu_index[0]
  #endif
#endef

def menu_move(move_index):
  global menu_index
  mi = menu_index[0] + move_index
  if mi < 0:
    mi = 0
  elif mi >= len(menu_items):
    mi = len(menu_items) - 1
  menu_index[0] = mi
#endef

def main():
  global last_rotary_pos, display_time
  draw_UI()
  render_menu()
  while True:
    now_time = time.monotonic()
    # -- encoder
    position = encoder.position
    if last_rotary_pos is None or position != last_rotary_pos:
      index_move = position - last_rotary_pos
      menu_move(index_move)
      last_rotary_pos = position
    # -- mouse
    mx = filter_joystick_deadzone(joyX.value) * -1 #Invert axis
    my = filter_joystick_deadzone(joyY.value)
    # mouse.move(mx, my, 0)
    # print('x: ', str(mx), 'y: ', str(my))
    # -- render
    if now_time > (display_time + 0.1):
      display_time = now_time
      render_menu_index()
    #endif
#endwhile

main()


# import time
# import digitalio
# import board
# import busio
# import terminalio
# import rotaryio
# import analogio
# import adafruit_ssd1306
# import asyncio
# import usb_hid
# from adafruit_hid.mouse import Mouse

# # -- protocol
# i2c = busio.I2C(board.GP21, board.GP20)

# # -- entities
# encoder = rotaryio.IncrementalEncoder(board.GP17, board.GP16)
# board_led = digitalio.DigitalInOut(board.LED)
# board_led.direction = digitalio.Direction.OUTPUT
# oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
# mouse = Mouse(usb_hid.devices)

# # -- variables
# in_min,in_max,out_min,out_max = (256, 65000, -5, 5)
# filter_joystick_deadzone = lambda x: int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min) if abs(x - 32768) > 500 else 0
# last_rotary_pos = None
# ay = analogio.AnalogIn(board.GP26)
# ax = analogio.AnalogIn(board.GP27)

# # def range_map(x, in_min, in_max, out_min, out_max):
# #     return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

# # async def blinkFn():
# #   global board_led
# #   while True:
# #     board_led.value = not board_led.value
# #     await asyncio.sleep_ms(1000)
# # #enddef

# async def renderFn():
#   global board_led
#   global last_rotary_pos
#   while True:
#     oled.fill(0)
#     oled.text('LED STATE:', 0, 0, terminalio.FONT)
#     if board_led.value:
#       oled.text('ON', 0, 10, terminalio.FONT)
#     else:
#       oled.text('OFF', 0, 10, terminalio.FONT)
#     oled.text(str(last_rotary_pos), 0, 20, terminalio.FONT)
#     oled.show()
#     await asyncio.sleep_ms(33)
# #enddef

# async def rotaryFn():
#   global last_rotary_pos, ax, ay, mouse
#   while True:
#     position = encoder.position
#     if last_rotary_pos is None or position != last_rotary_pos:
#       print(position)
#     last_rotary_pos = position

#     # x=range_map(ax.value, 256, 65535, -10, 10),
#     # y=range_map(ay.value, 0, 65535, -10, 10),
#     x = filter_joystick_deadzone(ax.value) * -1 #Invert axis
#     y = filter_joystick_deadzone(ay.value) * -1
#     mouse.move(x, y, 0)

#     # print('x: ', str(x), 'y: ', str(y))
#     # print('x: ', str(ax.value), 'y: ', str(ay.value))
#     # await asyncio.sleep_ms(0)
# #enddef

# async def main():
#   display_task = asyncio.create_task(renderFn())
#   led_task = asyncio.create_task(blinkFn())
#   encoder_task = asyncio.create_task(rotaryFn())

#   await asyncio.gather(display_task, led_task, encoder_task)
#   # await asyncio.gather(display_task, led_task)
# #enddef

# async def main1():
#   encoder_task = asyncio.create_task(rotaryFn())
#   await asyncio.gather(encoder_task)

# # loop = asyncio.get_event_loop()
# # try: 
# #     loop.create_task(rotaryFn())
# #     asyncio.ensure_future(listen())
# #     loop.run_forever()
# # except KeyboardInterrupt:
# #     pass
# # finally:
# #     print("Closing Loop")
# #     loop.close()
# # loop.run_until_complete(rotaryFn())

# asyncio.run(main())
# # asyncio.run_forever(main1())


# # import time
# # import digitalio
# # import board
# # import busio
# # import terminalio
# # import rotaryio
# # import analogio
# # import adafruit_ssd1306
# # import asyncio
# # import usb_hid
# # from adafruit_hid.mouse import Mouse

# # # -- protocol
# # i2c = busio.I2C(board.GP21, board.GP20)

# # # -- entities
# # encoder = rotaryio.IncrementalEncoder(board.GP17, board.GP16)
# # board_led = digitalio.DigitalInOut(board.LED)
# # board_led.direction = digitalio.Direction.OUTPUT
# # oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
# # mouse = Mouse(usb_hid.devices)

# # # -- variables
# # in_min,in_max,out_min,out_max = (256, 65000, -5, 5)
# # filter_joystick_deadzone = lambda x: int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min) if abs(x - 32768) > 500 else 0
# # last_rotary_pos = None
# # ay = analogio.AnalogIn(board.GP26)
# # ax = analogio.AnalogIn(board.GP27)

# # def range_map(x, in_min, in_max, out_min, out_max):
# #     return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

# # async def blinkFn():
# #   global board_led
# #   while True:
# #     board_led.value = not board_led.value
# #     await asyncio.sleep_ms(1000)
# # #enddef

# # async def renderFn():
# #   global board_led
# #   global last_rotary_pos
# #   while True:
# #     oled.fill(0)
# #     oled.text('LED STATE:', 0, 0, terminalio.FONT)
# #     if board_led.value:
# #       oled.text('ON', 0, 10, terminalio.FONT)
# #     else:
# #       oled.text('OFF', 0, 10, terminalio.FONT)
# #     oled.text(str(last_rotary_pos), 0, 20, terminalio.FONT)
# #     oled.show()
# #     await asyncio.sleep_ms(33)
# # #enddef

# # async def rotaryFn():
# #   global last_rotary_pos, ax, ay, mouse
# #   while True:
# #     position = encoder.position
# #     if last_rotary_pos is None or position != last_rotary_pos:
# #       print(position)
# #     last_rotary_pos = position

# #     # x=range_map(ax.value, 256, 65535, -10, 10),
# #     # y=range_map(ay.value, 0, 65535, -10, 10),
# #     x = filter_joystick_deadzone(ax.value) * -1 #Invert axis
# #     y = filter_joystick_deadzone(ay.value) * -1
# #     mouse.move(x, y, 0)

# #     # print('x: ', str(x), 'y: ', str(y))
# #     # print('x: ', str(ax.value), 'y: ', str(ay.value))
# #     # await asyncio.sleep_ms(0)
# # #enddef

# # async def main():
# #   display_task = asyncio.create_task(renderFn())
# #   led_task = asyncio.create_task(blinkFn())
# #   encoder_task = asyncio.create_task(rotaryFn())

# #   await asyncio.gather(display_task, led_task, encoder_task)
# #   # await asyncio.gather(display_task, led_task)
# # #enddef

# # async def main1():
# #   encoder_task = asyncio.create_task(rotaryFn())
# #   await asyncio.gather(encoder_task)

# # # loop = asyncio.get_event_loop()
# # # try: 
# # #     loop.create_task(rotaryFn())
# # #     asyncio.ensure_future(listen())
# # #     loop.run_forever()
# # # except KeyboardInterrupt:
# # #     pass
# # # finally:
# # #     print("Closing Loop")
# # #     loop.close()
# # # loop.run_until_complete(rotaryFn())

# # asyncio.run(main())
# # # asyncio.run_forever(main1())






# # # # # import time
# # # # # import digitalio
# # # # # import board
# # # # # import busio
# # # # # import terminalio
# # # # # import rotaryio
# # # # # import adafruit_ssd1306
# # # # # import asyncio

# # # # # # -- protocol
# # # # # i2c = busio.I2C(board.GP21, board.GP20)

# # # # # # -- entities
# # # # # encoder = rotaryio.IncrementalEncoder(board.GP17, board.GP16)
# # # # # board_led = digitalio.DigitalInOut(board.LED)
# # # # # board_led.direction = digitalio.Direction.OUTPUT
# # # # # oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

# # # # # # -- variables
# # # # # last_rotary_pos = None
# # # # # last_board_led_value = board_led.value

# # # # # # -- start setting
# # # # # oled.fill(0)
# # # # # oled.show()

# # # # # async def led_blink():
# # # # #   while True:
# # # # #     board_led.value = not board_led.value
# # # # #     await asyncio.sleep_ms(1000)

# # # # # asyncio.create_task(led_blink)

# # # # # while True:
# # # # #   # -- rotary encoder 
# # # # #   position = encoder.position
# # # # #   if last_rotary_pos is None or position != last_rotary_pos:
# # # # #     print(position)
# # # # #   # last_rotary_pos = position

# # # # #   if last_rotary_pos != position:
# # # # #     oled.fill(0)

# # # # #     # board_led.value = not board_led.value
# # # # #     # last_board_led_value = board_led.value;

# # # # #     oled.text('LED STATE:', 0, 0, terminalio.FONT)
# # # # #     # if board_led.value:
# # # # #     #   oled.text('ON', 0, 10, terminalio.FONT)
# # # # #     # else:
# # # # #     #   oled.text('OFF', 0, 10, terminalio.FONT)

# # # # #     oled.text(str(position), 0, 20, terminalio.FONT)
# # # # #     oled.show()

# # # # #   last_rotary_pos = position
# # # # #   # # -- ssd1306 display
# # # # #   # oled.fill(0)
# # # # #   # board_led.value = not board_led.value
# # # # #   # oled.text('LED STATE:', 0, 0, terminalio.FONT)
# # # # #   # if board_led.value:
# # # # #   #   oled.text('ON', 0, 10, terminalio.FONT)
# # # # #   # else:
# # # # #   #   oled.text('OFF', 0, 10, terminalio.FONT)

# # # # #   # oled.text(str(position), 0, 20, terminalio.FONT)
# # # # #   # oled.show()
# # # # #   # time.sleep(1)

# # # # # # led = digitalio.DigitalInOut(board.LED)
# # # # # # led.direction = digitalio.Direction.OUTPUT

# # # # # # while True:
# # # # # #   led.value = True
# # # # # #   # led.value(not led.value())
# # # # # #   time.sleep(1)
# # # # # #   led.value = False
# # # # # #   time.sleep(1)
