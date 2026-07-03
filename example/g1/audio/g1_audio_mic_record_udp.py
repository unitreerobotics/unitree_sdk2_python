import sys
from wav import record_pcm_multicast_to_wav

def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <network_interface_ip_on_192.168.123.x> [seconds] [output_wav]")
        print("Example: python g1_audio_mic_record_udp.py 192.168.123.99 5 /tmp/g1_record.wav")
        sys.exit(1)

    iface_ip = sys.argv[1]
    seconds = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
    out_wav = sys.argv[3] if len(sys.argv) > 3 else "/tmp/g1_record.wav"

    record_pcm_multicast_to_wav(
        output_wav=out_wav,
        group_ip="239.168.123.161", # your robot PC1 IP
        port=5555,
        iface_ip=iface_ip,
        record_seconds=seconds,
        sample_rate=16000,
        num_channels=1,
    )

if __name__ == "__main__":
    main()
