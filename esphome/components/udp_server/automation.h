#pragma once

#include "esphome/core/automation.h"
#include "udp_server.h"

#include <vector>

namespace esphome {
    namespace udp_server {

        class UDPServerComponent; 

        class OnReceiveTrigger : public Trigger<const std::vector<uint8_t> &> 
        {
            public:
                explicit OnReceiveTrigger(UDPServerComponent *udp_server);
        };
        
    }  // namespace udp_server
}  // namespace esphome