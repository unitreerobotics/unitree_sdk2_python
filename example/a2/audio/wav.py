import struct
import time

def read_wav(filename):
    try:
        with open(filename, 'rb') as f:
            def read(fmt):
                return struct.unpack(fmt, f.read(struct.calcsize(fmt)))

            # === Chunk Header ===
            chunk_id, = read('<I')
            if chunk_id != 0x46464952:  # "RIFF"
                print(f"[ERROR] chunk_id != 'RIFF': {hex(chunk_id)}")
                return [], -1, -1, False

            _chunk_size, = read('<I')
            format_tag, = read('<I')
            if format_tag != 0x45564157:  # "WAVE"
                print(f"[ERROR] format != 'WAVE': {hex(format_tag)}")
                return [], -1, -1, False

            # === Subchunk1: fmt ===
            subchunk1_id, = read('<I')
            subchunk1_size, = read('<I')

            if subchunk1_id == 0x4B4E554A:  # JUNK
                f.seek(subchunk1_size, 1)
                subchunk1_id, = read('<I')
                subchunk1_size, = read('<I')

            if subchunk1_id != 0x20746D66:  # "fmt "
                print(f"[ERROR] subchunk1_id != 'fmt ': {hex(subchunk1_id)}")
                return [], -1, -1, False

            if subchunk1_size not in [16, 18]:
                print(f"[ERROR] subchunk1_size != 16 or 18: {subchunk1_size}")
                return [], -1, -1, False

            audio_format, = read('<H')
            if audio_format != 1:
                print(f"[ERROR] audio_format != PCM (1): {audio_format}")
                return [], -1, -1, False

            num_channels, = read('<H')
            sample_rate, = read('<I')
            byte_rate, = read('<I')
            block_align, = read('<H')
            bits_per_sample, = read('<H')

            expected_byte_rate = sample_rate * num_channels * bits_per_sample // 8
            if byte_rate != expected_byte_rate:
                print(f"[ERROR] byte_rate mismatch: got {byte_rate}, expected {expected_byte_rate}")
                return [], -1, -1, False

            expected_align = num_channels * bits_per_sample // 8
            if block_align != expected_align:
                print(f"[ERROR] block_align mismatch: got {block_align}, expected {expected_align}")
                return [], -1, -1, False

            if bits_per_sample != 16:
                print(f"[ERROR] Only 16-bit samples supported, got {bits_per_sample}")
                return [], -1, -1, False

            if subchunk1_size == 18:
                extra_size, = read('<H')
                if extra_size != 0:
                    print(f"[ERROR] extra_size != 0: {extra_size}")
                    return [], -1, -1, False

            # === Subchunk2: data ===
            while True:
                subchunk2_id, subchunk2_size = read('<II')
                if subchunk2_id == 0x61746164:  # "data"
                    break
                f.seek(subchunk2_size, 1)

            raw_pcm = f.read(subchunk2_size)
            if len(raw_pcm) != subchunk2_size:
                print("[ERROR] Failed to read full PCM data")
                return [], -1, -1, False

            return list(raw_pcm), sample_rate, num_channels, True

    except Exception as e:
        print(f"[ERROR] read_wave() failed: {e}")
        return [], -1, -1, False


def write_wave(filename, sample_rate, samples, num_channels=1):
    try:
        import array
        if isinstance(samples[0], int):
            samples = array.array('h', samples)

        subchunk2_size = len(samples) * 2
        chunk_size = 36 + subchunk2_size

        with open(filename, 'wb') as f:
            # RIFF chunk
            f.write(struct.pack('<I', 0x46464952))  # "RIFF"
            f.write(struct.pack('<I', chunk_size))
            f.write(struct.pack('<I', 0x45564157))  # "WAVE"

            # fmt subchunk
            f.write(struct.pack('<I', 0x20746D66))  # "fmt "
            f.write(struct.pack('<I', 16))          # PCM
            f.write(struct.pack('<H', 1))           # PCM format
            f.write(struct.pack('<H', num_channels))
            f.write(struct.pack('<I', sample_rate))
            f.write(struct.pack('<I', sample_rate * num_channels * 2))  # byte_rate
            f.write(struct.pack('<H', num_channels * 2))                # block_align
            f.write(struct.pack('<H', 16))                              # bits per sample

            # data subchunk
            f.write(struct.pack('<I', 0x61746164))  # "data"
            f.write(struct.pack('<I', subchunk2_size))
            f.write(samples.tobytes())

        return True
    except Exception as e:
        print(f"[ERROR] write_wave() failed: {e}")
        return False


def play_pcm_stream(client, pcm_list, stream_name="example", chunk_size=96000, sleep_time=1.0, verbose=False):
    """
    Play PCM audio stream (16-bit little-endian format), sending data in chunks.

    Parameters:
        client: An object with a PlayStream method
        pcm_list: list[int], PCM audio data in int16 format
        stream_name: Stream name, default is "example"
        chunk_size: Number of bytes to send per chunk, default is 96000 (3 seconds at 16kHz)
        sleep_time: Delay between chunks in seconds
    """
    pcm_data = bytes(pcm_list)
    stream_id = str(int(time.time() * 1000))  # Unique stream ID based on current timestamp
    offset = 0
    chunk_index = 0
    total_size = len(pcm_data)

    while offset < total_size:
        remaining = total_size - offset
        current_chunk_size = min(chunk_size, remaining)
        chunk = pcm_data[offset:offset + current_chunk_size]

        if verbose:
            # Print info about the current chunk
            print(f"[CHUNK {chunk_index}] offset = {offset}, size = {current_chunk_size} bytes")
            print("  First 10 samples (int16): ", end="")
            for i in range(0, min(20, len(chunk) - 1), 2):
                sample = struct.unpack_from('<h', chunk, i)[0]
                print(sample, end=" ")
            print()

        # Send the chunk
        ret_code, _ = client.PlayStream(stream_name, stream_id, chunk)
        if ret_code != 0:
            print(f"[ERROR] Failed to send chunk {chunk_index}, return code: {ret_code}")
            break
        else:
            print(f"[INFO] Chunk {chunk_index} sent successfully")

        offset += current_chunk_size
        chunk_index += 1
        time.sleep(sleep_time)