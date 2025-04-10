from esphome import automation
from esphome.automation import maybe_simple_id
import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.const import CONF_ID, CONF_TRIGGER_ID
from esphome.core import CORE
from esphome.coroutine import coroutine_with_priority

from esphome.components import network

DEPENDENCIES = ["network"]

CONF_PORT = "port"
CONF_ON_RECEIVE = "on_receive"

udp_server_ns = cg.esphome_ns.namespace("udp_server")

UDPServerComponent = udp_server_ns.class_("UDPServerComponent", cg.Component)

OnReceiveTrigger = udp_server_ns.class_(
    "OnReceiveTrigger", automation.Trigger.template(cg.std_vector.template(cg.uint8).operator("ref")),
)


CONFIG_SCHEMA = cv.Schema({
    cv.GenerateID(): cv.declare_id(UDPServerComponent),
    cv.Optional(CONF_PORT, default=54321): cv.port,
    cv.Optional(CONF_ON_RECEIVE): automation.validate_automation(
        {
            cv.GenerateID(CONF_TRIGGER_ID): cv.declare_id(OnReceiveTrigger),
        }
    )
}).extend(cv.COMPONENT_SCHEMA)


@coroutine_with_priority(100.0)
async def to_code(config):
    cg.add_global(udp_server_ns.using)
    cg.add_define("USE_UDP_SERVER")

    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)

    cg.add(var.set_port(config[CONF_PORT]))

    for conf in config[CONF_ON_RECEIVE]:
        trigger = cg.new_Pvariable(conf[CONF_TRIGGER_ID], var)
        await automation.build_automation(
            trigger,
            [(cg.std_vector.template(cg.uint8).operator("ref").operator("const"), "data")],
            conf
        )
        #cg.add(var.add_on_receive_callback(trigger))