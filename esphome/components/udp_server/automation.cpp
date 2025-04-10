#include "automation.h"
#include "esphome/core/log.h"

namespace esphome 
{
    namespace udp_server 
    {
        static const char *const TAG = "udp_server.automation";

        OnReceiveTrigger::OnReceiveTrigger(UDPServerComponent *udp_server) 
        {
            udp_server->add_on_receive_callback([this](const std::vector<uint8_t> &data) 
            {
                this->trigger(data);
            });
        }

    }  // namespace udp_server
}  // namespace esphome