from microbit import uart, sleep, temperature
import radio

name = b'uBit'

def execute_command(payload):
    global name
    try:
        cmd, data = payload.split(b' ', 1)
    except ValueError:
        print('FAIL Invalid command 1: ' + repr(payload))
        return
    cmd = cmd.upper()
    if cmd == b'NAME':
        name = data
        print('OK Name set to:' + repr(data))
    elif cmd == b'SEND':
        print('OK Sending.')
        radio.send(name + b':' + data)
    elif cmd == b'TEMP':
        print('OK Temperature is %d' % temperature())
    else:
        print('FAIL Invalid command 2: ' + repr(payload))
        return

# coroutine
def stdin_routine():
    buffer = b''
    while True:
        data = (yield)
        buffer = buffer + data
        if b'\r' in data:
            # print(b"STDIN:" + data)
            line, buffer = buffer.split(b'\r')
            execute_command(line)

# coroutine
def radio_receive():
    while True:
        data = (yield)
        print("RADIO IN:" + repr(data))

# coroutine
def radio_send():
    while True:
        data = (yield)
        radio.send(data)

def init():
    uart.init(baudrate=115200)
    radio.on()
    
    stdin = stdin_routine()
    stdin.send(None)
    receiver = radio_receive()
    receiver.send(None)
    sender = radio_send()
    sender.send(None)
    
    print('OK uBit online.')
    
    while True:
        data = uart.readall()
        if data:
            stdin.send(data)
        rdata = radio.receive()
        if rdata:
            receiver.send(rdata)
        sleep(10)

# start OS
init()
