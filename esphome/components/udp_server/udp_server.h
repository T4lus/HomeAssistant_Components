#pragma once

#include "esphome.h"
#include "esphome/core/component.h"
#include "esphome/core/log.h"
#include <WiFiUdp.h>
#include <vector>

namespace udp_server {

    class OnPacketTrigger : public esphome::Trigger<std::vector<uint8_t>> {
        public:
            void trigger(const std::vector<uint8_t> &data) { this->trigger_(data); }
    };

    class UDPServerComponent : public esphome::Component {
        public:
            void setup() override;
            void loop() override;

            void set_port(uint16_t port);
            void add_on_packet_callback(OnPacketTrigger *trigger);

        protected:
            WiFiUDP udp_;
            uint16_t port_{54321};
            uint8_t buffer_[8192];
            std::vector<OnPacketTrigger *> callbacks_;
    };

}  // namespace udp_server