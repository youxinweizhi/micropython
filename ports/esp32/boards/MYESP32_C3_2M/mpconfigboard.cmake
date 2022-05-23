set(IDF_TARGET esp32c3)

set(SDKCONFIG_DEFAULTS
    boards/MYESP32_C3_2M/sdkconfig.base
    boards/sdkconfig.ble
)

if(NOT MICROPY_FROZEN_MANIFEST)
	set(MICROPY_FROZEN_MANIFEST ${MICROPY_PORT_DIR}/boards/MYESP32_C3_2M/manifest.py)
endif()
