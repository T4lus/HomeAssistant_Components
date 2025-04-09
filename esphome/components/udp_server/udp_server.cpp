#include "udp_server.h"

namespace udp_server {
    void UDPServerComponent::setup() 
    {
        udp_.begin(port_);
        ESP_LOGI("udp_server", "Listening on UDP port %d", port_);
    }

    void UDPServerComponent::loop() 
    {
        int packet_size = udp_.parsePacket();
        if (packet_size > 0) 
        {
            size_t len = udp_.read(reinterpret_cast<uint8_t *>(buffer_), sizeof(buffer_));

            std::vector<uint8_t> vec(buffer_, buffer_ + len);
            for (auto *cb : callbacks_) 
            {
                cb->trigger(vec);
            }
        }
    }

    void UDPServerComponent::set_port(uint16_t port) 
    { 
        this->port_ = port; 
    }

    void UDPServerComponent::add_on_packet_callback(OnPacketTrigger *trigger) 
    {
        callbacks_.push_back(trigger);
    }
}  // namespace udp_server