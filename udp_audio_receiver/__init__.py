import asyncio
import logging
import wave
import os
from collections import deque
from datetime import datetime
from homeassistant.const import EVENT_HOMEASSISTANT_STOP

DOMAIN = "audio_receiver"

_logger = logging.getLogger(__name__)

class UDPAudioReceiver:
    def __init__(self, hass, host, port, save_path):
        self.hass = hass
        self.host = host
        self.port = port
        self.save_path = save_path
        self.buffer = deque()
        self.timeout_handle = None

    async def start(self):
        loop = asyncio.get_running_loop()
        self.transport, _ = await loop.create_datagram_endpoint(
            lambda: UDPProtocol(self),
            local_addr=(self.host, self.port)
        )
        _logger.info(f"UDP audio receiver started on {self.host}:{self.port}")
        self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, self.stop)

    async def stop(self, event):
        self.transport.close()
        _logger.info("UDP audio receiver stopped")
        self.save_as_wav()

    def save_as_wav(self):
        if self.buffer:
            timestamp = datetime.now().strftime("%H.%M")
            file_path = os.path.join(self.save_path, f"audio-{timestamp}.wav")
            _logger.info("Timeout reached, saving data...")
            with wave.open(file_path, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(44100)
                while self.buffer:
                    wav_file.writeframes(self.buffer.popleft())
            _logger.info(f"Audio data saved to {file_path}")
        else:
            _logger.info("Timeout reached, but no data to save.")

class UDPProtocol(asyncio.DatagramProtocol):
    def __init__(self, receiver):
        self.receiver = receiver

    def datagram_received(self, data, addr):
        _logger.info(f"Data received from {addr}")
        self.receiver.buffer.append(data)
        if self.receiver.timeout_handle:
            self.receiver.timeout_handle.cancel()
        self.receiver.timeout_handle = asyncio.get_event_loop().call_later(10, self.receiver.save_as_wav)

async def async_setup(hass, config):
    host = config[DOMAIN].get('host', '0.0.0.0')
    port = config[DOMAIN].get('port', 12345)
    save_path = config[DOMAIN].get('save_path', '/media/audio')
    receiver = UDPAudioReceiver(hass, host, port, save_path)
    hass.loop.create_task(receiver.start())
    return True