import time
import digitalio
import board
import busio
import terminalio
import rotaryio
import analogio
import adafruit_ssd1306
import usb_hid
from adafruit_hid.mouse import Mouse
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode

# -- protocol
i2c = busio.I2C(board.GP21, board.GP20)

# -- entities
consumer_control = ConsumerControl(usb_hid.devices)
encoder = rotaryio.IncrementalEncoder(board.GP17, board.GP16)
encoder_button = digitalio.DigitalInOut(board.GP28)
encoder_button.direction = digitalio.Direction.INPUT
encoder_button.pull = digitalio.Pull.UP
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
mouse = Mouse(usb_hid.devices)
joyY = analogio.AnalogIn(board.GP27)
joyX = analogio.AnalogIn(board.GP26)
joy_button = digitalio.DigitalInOut(board.GP22)
joy_button.direction = digitalio.Direction.INPUT
joy_button.pull = digitalio.Pull.UP
key_left = digitalio.DigitalInOut(board.GP3)
key_left.direction = digitalio.Direction.INPUT
key_left.pull = digitalio.Pull.UP
key_right = digitalio.DigitalInOut(board.GP2)
key_right.direction = digitalio.Direction.INPUT
key_right.pull = digitalio.Pull.UP

# -- variables
in_min, in_max, out_min, out_max = (256, 65000, -5, 5)
filter_joystick_deadzone = lambda x: int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min) if abs(x - 32768) > 500 else 0
last_rotary_pos = 0
# -- menu
menu_show = True
menu_items = ['MOUSE', 'VOLUME', 'BRIGHTNESS']
menu_index = [0, -1]
menu_button_state = False
menu_state = True
prev_menu_state = menu_state
# -- display
display_time = -1
# -- keys
key_left_state = True
key_right_state = True
joy_button_state = True

def draw_UI():
  oled.fill(0)
  oled.line(30, 0, 30, 64, 0xFFFFFF)
  oled.show()
#endef

def render_menu():
  oled.fill_rect(31, 0, 97, 64, 0x0)
  for i in range(len(menu_items)):
    oled.text(menu_items[i], 36, (i * 10) + 17, terminalio.FONT)
  #endfor
  oled.show()
#enddef

def render_menu_index():
  global menu_index, menu_state, prev_menu_state
  if menu_index[0] != menu_index[1] or menu_state != prev_menu_state:
    oled.fill_rect(0, 0, 30, 64, 0x0)
    miy = (menu_index[0] * 10) + 15
    
    oled.fill_rect(16, miy, 8, 8, 0xFFF)
    oled.line(16, miy + 4, 30, miy +4, 0xFFF)
    if menu_state:
      oled.fill_rect(18, miy + 2, 4, 4, 0x0)
    #endif
    oled.show()
    # -- states
    menu_index[1] = menu_index[0]
    prev_menu_state = menu_state
  #endif
#endef

def menu_move(move_index):
  global menu_index
  mi = menu_index[0] + move_index
  if mi < 0:
    mi = 0
  elif mi >= len(menu_items):
    mi = len(menu_items) - 1
  #endif
  menu_index[0] = mi
#endef

def rotary_tick(move_index):
  global menu_state, menu_index, consumer_control
  if menu_state:
    menu_move(move_index)
  else:
    if menu_index[0] == 0: # -- mouse
      mouse.move(0, 0, move_index * -1)
    elif menu_index[0] == 1: # -- volume
      if move_index > 0:
        consumer_control.send(ConsumerControlCode.VOLUME_INCREMENT)
      else:
        consumer_control.send(ConsumerControlCode.VOLUME_DECREMENT)
      #endif
    elif menu_index[0] == 2: # -- brightness
      if move_index > 0:
        consumer_control.send(ConsumerControlCode.BRIGHTNESS_INCREMENT)
      else:
        consumer_control.send(ConsumerControlCode.BRIGHTNESS_DECREMENT)
      #endif
    #endif
  #endif
#endef

def main():
  global last_rotary_pos, display_time, menu_button_state
  global menu_state, key_left_state, key_right_state, joy_button_state
  draw_UI()
  render_menu()
  while True:
    now_time = time.monotonic()
    # -- encoder
    position = encoder.position
    if last_rotary_pos is None or position != last_rotary_pos:
      index_move = position - last_rotary_pos
      last_rotary_pos = position
      rotary_tick(index_move)
    #endif
    if encoder_button.value != menu_button_state:
      menu_button_state = encoder_button.value
      if menu_button_state == False:
        menu_state = not menu_state
      #endif
    #endif
    # -- mouse
    mx = filter_joystick_deadzone(joyX.value) * -1 #Invert axis
    my = filter_joystick_deadzone(joyY.value)
    mouse.move(mx, my, 0)

    if key_left.value != key_left_state:
      key_left_state = key_left.value
      if not key_left_state:
        mouse.press(Mouse.LEFT_BUTTON)
      else:
        mouse.release(Mouse.LEFT_BUTTON)
      #endif
    #endif
    
    if key_right.value != key_right_state:
      key_right_state = key_right.value
      if not key_right_state:
        mouse.press(Mouse.RIGHT_BUTTON)
      else:
        mouse.release(Mouse.RIGHT_BUTTON)
      #endif
    #endif

    if joy_button_state != joy_button.value:
      joy_button_state = joy_button.value
      if not joy_button_state:
        mouse.press(Mouse.MIDDLE_BUTTON)
      else:
        mouse.release(Mouse.MIDDLE_BUTTON)
      #endif
    #endif

    # print('x: ', str(mx), 'y: ', str(my))
    # -- render
    if now_time > (display_time + 0.1):
      display_time = now_time
      render_menu_index()
    #endif
  #endwhile
#endef

main()
