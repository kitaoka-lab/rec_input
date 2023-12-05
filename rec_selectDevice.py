import os
os.environ['PYAUDIO_IGNORE_ALSA_PLUGHW'] = '1'

import pyaudio
import wave
import time
import sys

# パラメータ #######################################################################
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
CHUNK = 1024
RECORD_SECONDS = 5
OUTPUT_FILENAME = "output.wav"
INPUT_DEVICE = "MacBook Proのマイク"

# pyaudio #########################################################################
audio = pyaudio.PyAudio()

# 利用可能な録音デバイスをリストアップ #############################################
print("\n### 利用可能な録音デバイスの一覧 ###")
device_count = audio.get_device_count()
devices = []
for i in range(device_count):
    device_info = audio.get_device_info_by_index(i)
    devices.append((i, device_info['name']))
    if device_info['maxInputChannels'] > 0:  # 録音デバイスのみをリストアップ
        print(f"{i}: {device_info['name']}")


# ユーザーにデバイスを選択させる
device_id = None
while device_id is None:
    try:
        choice = int(input("選択したいデバイスの番号を入力してください: "))
        selected_device = next((d for d in devices if d[0] == choice), None)
        if selected_device is not None:
            device_id = selected_device[0]
        else:
            print("無効な選択です。もう一度入力してください。")
    except ValueError:
        print("数値を入力してください。")

print(f"選択したデバイス: {devices[choice][1]}")
INPUT_DEVICE = devices[choice][1]

# # 録音デバイスの のデバイスIDを探す #######################################
# device_id = None
# for i in range(audio.get_device_count()):
#     info = audio.get_device_info_by_index(i)
#     if INPUT_DEVICE in info['name']:
#         device_id = info['index']
#         break

# 指定の録音デバイス が見つからなかったら終了
if device_id is None:
    print(f"{INPUT_DEVICE} が見つかりませんでした。")
    exit()

print(f"[{INPUT_DEVICE}] index:{device_id}")

# 見つかったデバイスIDを使用して、ストリームを開く ###############################
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index=device_id)

# 録音開始 ########################################################################
print("録音中...", end='')
frames = []
start_time = time.time()

try:
    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

        elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        sys.stdout.write(f"\r録音中... {elapsed_time:.0f} ms/ {RECORD_SECONDS*1000} ms")
        sys.stdout.flush()


except KeyboardInterrupt:
    pass  # Allow manual interruption with Ctrl+C

print(f"\n録音終了 {OUTPUT_FILENAME} に保存しました。")

# 録音の停止とストリームのクローズ ############################################
stream.stop_stream()
stream.close()
audio.terminate()

# 音声データをファイルに保存 ###################################################
with wave.open(OUTPUT_FILENAME, 'wb') as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
