#include <stdio.h>
#include "esp_log.h"
#include "driver/i2c.h"

static const char *TAG = "i2c-simple-example";

#define I2C_MASTER_SCL_IO           18      /*!< GPIO number used for I2C master clock */
#define I2C_MASTER_SDA_IO           19      /*!< GPIO number used for I2C master data  */
#define I2C_MASTER_NUM              0                          /*!< I2C master i2c port number, the number of i2c peripheral interfaces available will depend on the chip */
#define I2C_MASTER_FREQ_HZ          50000                     /*!< I2C master clock frequency */
#define I2C_MASTER_TX_BUF_DISABLE   0                          /*!< I2C master doesn't need buffer */
#define I2C_MASTER_RX_BUF_DISABLE   0                          /*!< I2C master doesn't need buffer */
#define I2C_MASTER_TIMEOUT_MS       1000

#define TC74_SENSOR_ADDR                 0x4D        /*!< Slave address of the MPU9250 sensor */


/**
 * @brief Read a sequence of bytes from a MPU9250 sensor registers
 */
// static esp_err_t mpu9250_register_read(uint8_t reg_addr, uint8_t *data, size_t len)
// {
//     return i2c_master_write_read_device(I2C_MASTER_NUM, MPU9250_SENSOR_ADDR, &reg_addr, 1, data, len, I2C_MASTER_TIMEOUT_MS / portTICK_PERIOD_MS);
// }

/**
 * @brief Write a byte to a MPU9250 sensor register
 */
/**
 * Passar no data o valor do 0x5A
*/
// static esp_err_t mpu9250_register_write_byte(uint8_t reg_addr, uint8_t data)
// {
//     int ret;
//     uint8_t write_buf[2] = {reg_addr, data};

//     ret = i2c_master_write_to_device(I2C_MASTER_NUM, MPU9250_SENSOR_ADDR, write_buf, sizeof(write_buf), I2C_MASTER_TIMEOUT_MS / portTICK_PERIOD_MS);

//     return ret;
// }

/**
 * @brief i2c master initialization
 */
static esp_err_t i2c_master_init(void)
{
    int i2c_master_port = I2C_MASTER_NUM;

    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = I2C_MASTER_SDA_IO,
        .scl_io_num = I2C_MASTER_SCL_IO,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = I2C_MASTER_FREQ_HZ,
    };

    i2c_param_config(i2c_master_port, &conf);

    return i2c_driver_install(i2c_master_port, conf.mode, I2C_MASTER_RX_BUF_DISABLE, I2C_MASTER_TX_BUF_DISABLE, 0);
}


void app_main(void)
{
    uint8_t data = 0x5A;
    ESP_ERROR_CHECK(i2c_master_init());
    ESP_LOGI(TAG, "I2C initialized successfully");

    while(1){
        i2c_master_write_to_device(I2C_MASTER_NUM, TC74_SENSOR_ADDR, &data, 1, I2C_MASTER_TIMEOUT_MS/ portTICK_PERIOD_MS);
        vTaskDelay(100/portTICK_PERIOD_MS);
    }
    ESP_ERROR_CHECK(i2c_driver_delete(I2C_MASTER_NUM));
    ESP_LOGI(TAG, "I2C de-initialized successfully");
}
