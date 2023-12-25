# MQTT Topics Tibber Puls
MQTT_TOPIC_TIBBER_PULSE_CONSUMPTION = "/home/tibber/pulse/power/current/consumption"
MQTT_TOPIC_PRODUCTION = "/home/tibber/pulse/power/current/production"


# Power consumption as measured by EM24
MQTT_TOPIC_EM24_CONSUMPTION = "/home/victron/em24/consumption"

# Power controlled by Victron Multiplus II -> positiv: charging, negative: discharging
MQTT_TOPIC_MP_POWER = "/home/victron/mp/power/controlled"

# Battery state of charge
MQTT_TOPIC_MP_SOC = "/home/victron/mp/battery/soc"

# MPPT Charger power
MQTT_TOPIC_MPPT_SOLAR_POWER = "/home/victron/mppt/power"

# --- Results calculated ---
# House Solar System Production
MQTT_TOPIC_HOUSE_SOLAR_PROD = "/home/house/solar/house"
# House Solar System Production
# MQTT_TOPIC_HOUSE_SOLAR_VICTRON_PROD = "/home/house/solar/victron"
# Devices consuming energy (or producing e.g. balkony solar systems)
MQTT_TOPIC_HOUSE_CONSUMPTION = "/home/house/energy/consumption"
# tibber bilanz
# MQTT_TOPIC_HOUSE_TIBBER_CONSUMPTION = "/home/house/tibber/consumption"
# MQTT_TOPIC_HOUSE_TIBBER_PRODUCTION = "/home/house/tibber/production"
