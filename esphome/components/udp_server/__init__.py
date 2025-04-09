import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import automation
from esphome.const import CONF_ID, CONF_TRIGGER_ID
from esphome.components import network

DEPENDENCIES = ["network"]

udp_server_ns = cg.global_ns.namespace("udp_server")
UDPServerComponent = udp_server_ns.class_("UDPServerComponent", cg.Component)

OnPacketTrigger = udp_server_ns.class_(
    "OnPacketTrigger",
    automation.Trigger.template(cg.std_vector.template(cg.uint8).operator("ref")),
)

CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(UDPServerComponent),
    cv.Optional("port", default=54321): cv.port,
    cv.Optional("on_packet"): automation.validate_automation(
        {
            cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(OnPacketTrigger),
        }
    )
}).extend(cv.COMPONENT_SCHEMA)

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    cg.add(var.set_port(config["port"]))

    if "on_packet" in config:
        for conf in config["on_packet"]:
            trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], OnPacketTrigger())
            await automation.build_automation(
                trigger,
                [(cg.std_vector.template(cg.uint8).operator("ref").operator("const"), "data")],
                conf
            )
            cg.add(var.add_on_packet_callback(trigger))