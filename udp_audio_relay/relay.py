import asyncio
import logging
import wave
import os
from collections import deque
from datetime import datetime, timedelta

from .const import DOMAIN
from homeassistant.const import EVENT_HOMEASSISTANT_STOP

_LOGGER = logging.getLogger(__name__)

class UDPAudioRelay:
    def __init__(self, hass, 
                 host, 
                 port, 
                 discovery_port,
                 discovery_keyword,
                 save_path,
                ):

        self.hass = hass
        self.host = host
        self.port = port
        self.discovery_port = discovery_port
        self.discovery_keyword = discovery_keyword
        self.save_path = save_path

        self.buffer = deque()
        self.timeout_handle = None

        self.auto_discovered = set()
        self.active_devices = {}
        self.forward_targets = []

        self.discovery_transport = None
        self.forward_transport = None



    async def start(self):
        loop = asyncio.get_running_loop()

        # Listen for audo discovery
        self.discovery_transport, _ = await loop.create_datagram_endpoint(
            lambda: DiscoveryProtocol(self),
            local_addr=(self.host, self.discovery_port)
        )
        _LOGGER.info(f"Autodiscovery enabled on port {self.discovery_port}")

        # Listen for incoming audio
        self.transport, _ = await loop.create_datagram_endpoint(
            lambda: UDPProtocol(self),
            local_addr=(self.host, self.port)
        )

        # UDP sender socket (for forwarding)
        self.forward_transport, _ = await loop.create_datagram_endpoint(
            asyncio.DatagramProtocol,
            remote_addr=None  # We send manually to each target
        )

        _LOGGER.info(f"UDP Audio Relay started on {self.host}:{self.port}")

        self.hass.loop.create_task(self.cleanup_loop())
        self.hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, self.stop)

    async def stop(self, event=None):
        self.transport.close()

        if self.autodiscovery:
            self.discovery_transport.close()
            self.forward_targets.clear()
            self.auto_discovered.clear()

        if self.forward_transport:
            self.forward_transport.close()

        _LOGGER.info("UDP Audio Relay stopped")
        self.save_as_wav()

    async def cleanup_loop(self):
        while True:
            await asyncio.sleep(30)
            now = datetime.now()
            for key in list(self.active_devices):
                if now - self.active_devices[key] > timedelta(seconds=30):
                    _LOGGER.info(f"ESP Audio Receiver {key} timed out, removing.")
                    self.forward_targets.remove(key)
                    self.auto_discovered.remove(key)
                    del self.active_devices[key]

    def handle_audio_packet(self, data):
        self.buffer.append(data)

        # Schedule save after inactivity
        if self.timeout_handle:
            self.timeout_handle.cancel()
        self.timeout_handle = asyncio.get_event_loop().call_later(10, self.save_as_wav)

        # Forward to targets
        for ip, port in self.forward_targets:
            try:
                self.forward_transport.sendto(data, (ip, port))
            except Exception as e:
                _LOGGER.warning(f"Error forwarding to {ip}:{port} - {e}")

    def save_as_wav(self):
        if self.buffer:
            timestamp = datetime.now().strftime("%H.%M")
            file_path = os.path.join(self.save_path, f"audio-{timestamp}.wav")
            _LOGGER.info("Saving audio data to %s", file_path)
            with wave.open(file_path, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(44100)
                while self.buffer:
                    wav_file.writeframes(self.buffer.popleft())
        else:
            _LOGGER.info("No audio data to save.")

class UDPProtocol(asyncio.DatagramProtocol):
    def __init__(self, udp_audio_relay):
        self.udp_audio_relay = udp_audio_relay

    def datagram_received(self, data, addr):
        _LOGGER.debug(f"Data received from {addr}")
        self.udp_audio_relay.handle_audio_packet(data)

class DiscoveryProtocol(asyncio.DatagramProtocol):
    def __init__(self, udp_audio_relay):
        self.udp_audio_relay = udp_audio_relay

    def datagram_received(self, data, addr):
        message = data.decode(errors="ignore")

        ip, _ = addr

        if self.receiver.discovery_keyword in message and (ip, port) not in self.udp_audio_relay.auto_discovered:
            try:
                port = int(message.split(":")[1])  # e.g., "HELLO_UDP_AUDIO_RELAY:4567"
            except (IndexError, ValueError):
                port = 4567

            key = (ip, port)
            self.receiver.auto_discovered.add(key)
            self.receiver.forward_targets.append(key)
            self.receiver.active_devices[key] = datetime.now()

            _LOGGER.info(f"Discovered ESP Audio Receiver at {ip}:{port}")