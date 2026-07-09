# Implementing low-level bitwise operations to extract hardware states from a single telemetry byte

def parse_device_status_register(status_byte):
    """
    Decodes an 8-bit integer status register using bitmask matching flags.
    Demonstrates resource-optimized telemetry tracking for constrained IoT nodes.
    """
    print("--- IoT Embedded Systems: Bitmask Status Analyzer ---")
    print(f"Incoming Status Register Byte : Int={status_byte} | Binary={bin(status_byte)[2:]:>08}\n")
    
    # 1. Define hexadecimal bitmasks representing hardware status positions
    # Each flag targets a completely unique bit position in the byte architecture
    MASK_POWER_ON       = 0x01  # Binary: 00000001 (Bit 0)
    MASK_SENSOR_READY   = 0x02  # Binary: 00000010 (Bit 1)
    MASK_BATTERY_LOW    = 0x04  # Binary: 00000100 (Bit 2)
    MASK_NETWORK_ERROR  = 0x08  # Binary: 00001000 (Bit 3)
    
    # 2. Extract specific bits using the Bitwise AND (&) operator matrix
    is_powered       = (status_byte & MASK_POWER_ON) != 0
    is_sensor_ready  = (status_byte & MASK_SENSOR_READY) != 0
    is_battery_low   = (status_byte & MASK_BATTERY_LOW) != 0
    has_network_err  = (status_byte & MASK_NETWORK_ERROR) != 0
    
    print("Decoded Hardware Telemetry Report:")
    print(f"  🔹 System Core Power Status : {'ONLINE' if is_powered else 'OFFLINE'}")
    print(f"  🔹 Sensor Calibration State : {'INITIALIZED' if is_sensor_ready else ' WAITING'}")
    print(f"  🔹 Power Cell Health Check  : {'WARNING: LOW VOLTAGE' if is_battery_low else ' VOLTAGE STABLE'}")
    print(f"  🔹 Network Link Integrity   : {'ERROR: PACKET DROPS' if has_network_err else ' LINK STABLE'}")
    
    # 3. Decision Maker Router for Project Management Layer
    if has_network_err or is_battery_low:
        return " MAINTENANCE ALERT: Hardware flag anomaly intercepted. Dispatch updates to remote node."
    return " RUNTIME STATUS SAFE: Core firmware operating within nominal limits."

if __name__ == "__main__":
    # Case A: Simulated register containing 5 (Binary: 00000101)
    # Power is ON (Bit 0=1), Sensor not ready (Bit 1=0), Battery is LOW (Bit 2=1), Network stable (Bit 3=0)
    anomalous_register = 5
    verdict_A = parse_device_status_register(anomalous_register)
    print(f"System Action: {verdict_A}")
    
    print("\n" + "="*55 + "\n")
    
    # Case B: Simulated register containing 3 (Binary: 00000011)
    # Power is ON (Bit 0=1), Sensor is READY (Bit 1=1), Battery stable (Bit 2=0), Network stable (Bit 3=0)
    healthy_register = 3
    verdict_B = parse_device_status_register(healthy_register)
    print(f"System Action: {verdict_B}")