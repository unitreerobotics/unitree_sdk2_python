import time
import sys
import wave
import os
from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
from unitree_sdk2py.g1.audio.g1_audio_client import AudioClient
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient

def ReadWave(file_path):
    """Read a wave file and return PCM data along with metadata"""
    try:
        with wave.open(file_path, 'rb') as wf:
            sample_rate = wf.getframerate()
            num_channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            n_frames = wf.getnframes()
            
            # Read all frames
            pcm_data = wf.readframes(n_frames)
            
            # Convert bytes to list of integers
            pcm_list = list(pcm_data)
            
            return pcm_list, sample_rate, num_channels, n_frames, True
    except Exception as e:
        print(f"Error reading wave file: {e}")
        return [], -1, 0, 0, False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} networkInterface")
        sys.exit(-1)

    ChannelFactoryInitialize(0, sys.argv[1])

    audio_client = AudioClient()  
    audio_client.SetTimeout(10.0)
    audio_client.Init()

    sport_client = LocoClient()  
    sport_client.SetTimeout(10.0)
    sport_client.Init()

    ret = audio_client.GetVolume()
    print("debug GetVolume: ",ret)

    audio_client.SetVolume(85)

    ret = audio_client.GetVolume()
    print("debug GetVolume: ",ret)

    AUDIO_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.wav")
    
    pcm, sample_rate, num_channels, n_frames, filestate = ReadWave(AUDIO_FILE_PATH)
    
    print(f"wav file sample_rate = {sample_rate} num_channels = {num_channels} filestate = {filestate}")
    
    if filestate and sample_rate == 16000 and num_channels == 1:
        # Calculate the actual duration of the audio file
        audio_duration = n_frames / sample_rate
        print(f"Audio duration: {audio_duration:.2f} seconds")
        
        current_time_ms = int(time.time() * 1000)
        audio_client.PlayStream("example", str(current_time_ms), pcm)
        print("start play stream")
        
        # Wait for the actual duration of the audio plus a small buffer time
        buffer_time = 0.2  # Additional buffer time to ensure complete playback
        time.sleep(audio_duration + buffer_time)
        
        print("stop play stream")
        ret = audio_client.PlayStop("example")
    else:
        print("audio file format error, please check!")

    sport_client.WaveHand()

    audio_client.TtsMaker("大家好!我是宇树科技人形机器人。语音开发测试例程运行成功！ 很高兴认识你！",0)
    time.sleep(8)
    audio_client.TtsMaker("接下来测试灯带开发例程！",0)
    time.sleep(1)
    audio_client.LedControl(255,0,0)
    time.sleep(1)
    audio_client.LedControl(0,255,0)
    time.sleep(1)
    audio_client.LedControl(0,0,255)

    time.sleep(3)
    audio_client.TtsMaker("测试完毕，谢谢大家！",0)
    
