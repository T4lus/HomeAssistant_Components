#pragma once

#include "esphome.h"
#include "esphome/core/component.h"
#include "esphome/core/helpers.h"
#include "esphome/core/log.h"
#include <WiFiUdp.h>
#include <vector>

namespace esphome {
    namespace udp_server {

        class UDPServerComponent : public Component 
        {
            public:
                void setup() override
                {
                    udp_.begin(port_);
                    ESP_LOGI("udp_server", "Listening on UDP port %d", port_);
                }

                void loop() override 
                {
                    int packet_size = udp_.parsePacket();
                    if (packet_size > 0) 
                    {
                        size_t len = udp_.read(reinterpret_cast<uint8_t *>(buffer_), sizeof(buffer_));

                        std::vector<uint8_t> vec(buffer_, buffer_ + len);

                        this->on_receive_callbacks_.call(vec);

                        /*
                        for (auto *cb : on_packet_callbacks_) 
                        {
                            cb->trigger(vec);
                        }
                        */
                    }
                }

                void set_port(uint16_t port)
                { 
                    this->port_ = port; 
                }

                void add_on_receive_callback(std::function<void(const std::vector<uint8_t> &)> &&callback)
                {
                    this->on_receive_callbacks_.add(std::move(callback));
                }

            protected:
                WiFiUDP udp_;
                uint16_t port_{54321};
                uint8_t buffer_[8192];

                CallbackManager<void(const std::vector<uint8_t> &)> on_receive_callbacks_{};
        };
    }  // namespace udp_server
}