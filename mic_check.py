import pyaudio

p = pyaudio.PyAudio()

print("="*60)
print("Listing all available audio devices...")
print("="*60)

for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    device_name = info.get('name')
    is_input = info.get('maxInputChannels') > 0
    
    print(f"Device index: {i}")
    print(f"  Name: {device_name}")
    print(f"  Input device: {is_input}")
    print(f"  Max Input Channels: {info.get('maxInputChannels')}")
    print(f"  Default Sample Rate: {info.get('defaultSampleRate')}")
    print("-" * 30)

p.terminate()

print("Look for the device that corresponds to your microphone.")
print("Note its 'Device index'.")
