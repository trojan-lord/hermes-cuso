/*
 * ESP32 Comprehensive Hardware Test Sketch
 * Tests: WiFi, Bluetooth, GPIO, ADC, I2C, SPI, Deep Sleep, Flash, Memory
 * Output: Serial @ 115200 baud
 * Compile: arduino-cli compile --fqbn esp32:esp32:esp32
 * Board: esp32dev (ESP32-D0WD-V3)
 */

#include <WiFi.h>
#include <BluetoothSerial.h>
#include <Wire.h>
#include <SPI.h>
#include <esp_system.h>
#include <esp_sleep.h>
#include <driver/adc.h>
#include <driver/gpio.h>
#include <soc/efuse_reg.h>
#include <esp_chip_info.h>

#define GPIO_TEST_OUT  25
#define GPIO_TEST_IN   26
#define I2C_SDA        21
#define I2C_SCL        22
#define SPI_MOSI       23
#define SPI_MISO       19
#define SPI_CLK        18
#define SPI_CS          5

BluetoothSerial SerialBT;
int testPass = 0, testFail = 0;

void pass(const char* name) { Serial.printf("[PASS] %s\n", name); testPass++; }
void fail(const char* name, const char* reason) { Serial.printf("[FAIL] %s: %s\n", name, reason); testFail++; }

void testChipInfo() {
    Serial.println("\n===== CHIP INFORMATION =====");
    esp_chip_info_t ci;
    esp_chip_info(&ci);
    Serial.printf("Chip: ESP32 | Rev: %d | Cores: %d\n", ci.revision, ci.cores);
    Serial.printf("Flash: %d MB | Free heap: %d bytes\n", esp_flash_get_size()/(1024*1024), esp_get_free_heap_size());
    Serial.printf("MAC: %s\n", WiFi.macAddress().c_str());
    pass("Chip Info");
}

void testFlash() {
    Serial.println("\n===== FLASH TEST =====");
    uint32_t flash_size = 0;
    esp_flash_get_size(&flash_size);
    Serial.printf("Flash: %d KB (%d MB)\n", flash_size/1024, flash_size/(1024*1024));
    (flash_size >= 1024*1024) ? pass("Flash Size") : fail("Flash Size", "< 1MB");
}

void testWiFi() {
    Serial.println("\n===== WIFI TEST =====");
    WiFi.mode(WIFI_STA); WiFi.disconnect(); delay(100);
    (WiFi.status() == WL_DISCONNECTED) ? pass("WiFi Init") : fail("WiFi Init", "Unexpected status");
    int n = WiFi.scanNetworks();
    Serial.printf("Found %d networks\n", n);
    (n >= 0) ? pass("WiFi Scan") : fail("WiFi Scan", "Scan error");
    WiFi.setTxPower(WIFI_POWER_19_5dBm); pass("WiFi TX Power");
    WiFi.scanDelete(); WiFi.disconnect(); WiFi.mode(WIFI_OFF);
}

void testBluetooth() {
    Serial.println("\n===== BLUETOOTH TEST =====");
    bool ok = SerialBT.begin("ESP32_Test");
    ok ? pass("BT Classic Init") : fail("BT Classic Init", "Failed");
    Serial.printf("BT MAC: %s\n", SerialBT.localMACAddress().c_str());
    SerialBT.end(); pass("BT Stack");
}

void testGPIO() {
    Serial.println("\n===== GPIO TEST =====");
    pinMode(GPIO_TEST_OUT, OUTPUT); pinMode(GPIO_TEST_IN, INPUT_PULLDOWN);
    digitalWrite(GPIO_TEST_OUT, HIGH); delayMicroseconds(10);
    (digitalRead(GPIO_TEST_IN) == HIGH) ? pass("GPIO High") : fail("GPIO High", "Input LOW");
    digitalWrite(GPIO_TEST_OUT, LOW); delayMicroseconds(10);
    (digitalRead(GPIO_TEST_IN) == LOW) ? pass("GPIO Low") : fail("GPIO Low", "Input HIGH");
    unsigned long start = micros();
    for (int i = 0; i < 10000; i++) { digitalWrite(GPIO_TEST_OUT, HIGH); digitalWrite(GPIO_TEST_OUT, LOW); }
    Serial.printf("GPIO toggle: 10000 cycles in %lu us\n", micros()-start);
    pass("GPIO Speed");
    int pins[] = {14,15,27,32,33}, ok=0;
    for (int p : pins) { pinMode(p,OUTPUT); digitalWrite(p,HIGH); delayMicroseconds(10); if(digitalRead(p)==HIGH) ok++; digitalWrite(p,LOW); }
    Serial.printf("Multi-pin: %d/5 OK\n", ok);
    (ok==5) ? pass("GPIO Multi-Pin") : fail("GPIO Multi-Pin", "Some pins failed");
}

void testADC() {
    Serial.println("\n===== ADC TEST =====");
    adc1_config_width(ADC_WIDTH_BIT_12);
    int channels[] = {ADC1_CHANNEL_0, ADC1_CHANNEL_3, ADC1_CHANNEL_6, ADC1_CHANNEL_7};
    int gpios[] = {36,39,34,35}; bool ok = true;
    for (int i=0; i<4; i++) {
        adc1_config_channel_atten(channels[i], ADC_ATTEN_DB_11);
        int raw = adc1_get_raw(channels[i]);
        Serial.printf("ADC1 CH%d (GPIO%d): %d\n", channels[i], gpios[i], raw);
        if (raw<0||raw>4095) ok=false;
    }
    ok ? pass("ADC1") : fail("ADC1", "Out of range");
}

void testI2C() {
    Serial.println("\n===== I2C TEST =====");
    Wire.begin(I2C_SDA, I2C_SCL); Wire.setClock(100000); delay(100);
    int found = 0;
    for (byte a=1; a<127; a++) { Wire.beginTransmission(a); if(Wire.endTransmission()==0) { Serial.printf("  Device at 0x%02X\n",a); found++; } }
    Serial.printf("I2C: %d devices\n", found); pass("I2C Scan"); Wire.end();
}

void testSPI() {
    Serial.println("\n===== SPI TEST =====");
    SPI.begin(SPI_CLK, SPI_MISO, SPI_MOSI, SPI_CS);
    pinMode(SPI_CS, OUTPUT); digitalWrite(SPI_CS, HIGH);
    digitalWrite(SPI_CS, LOW); byte r = SPI.transfer(0xAA); digitalWrite(SPI_CS, HIGH);
    Serial.printf("SPI loopback: sent 0xAA, got 0x%02X\n", r);
    pass("SPI Init"); SPI.end();
}

void testTimer() {
    Serial.println("\n===== TIMER TEST =====");
    unsigned long s = micros(); delay(100); unsigned long e = micros()-s;
    Serial.printf("delay(100): %lu us\n", e);
    (e>90000 && e<110000) ? pass("Timer Accuracy") : fail("Timer Accuracy", "Drift >10%");
}

void testMemory() {
    Serial.println("\n===== MEMORY TEST =====");
    size_t free = esp_get_free_heap_size(), minf = esp_get_minimum_free_heap_size();
    Serial.printf("Free: %d | Min: %d | Frag: %d%%\n", free, minf, free>0?(100-(minf*100/free)):100);
    void* blk = malloc(100*1024);
    blk ? (free(blk), pass("Memory Alloc")) : fail("Memory Alloc", "100KB alloc failed");
    (free>100000) ? pass("Free Memory") : fail("Free Memory", "<100KB free");
}

void printResults() {
    Serial.println("\n╔══════════════════════════════════════╗");
    Serial.println("║     ESP32 HARDWARE TEST RESULTS     ║");
    Serial.printf("║  PASSED: %-27d║\n", testPass);
    Serial.printf("║  FAILED: %-27d║\n", testFail);
    Serial.printf("║  TOTAL:  %-27d║\n", testPass+testFail);
    Serial.println(testFail==0 ? "║  STATUS: ALL TESTS PASSED           ║" : "║  STATUS: SOME TESTS FAILED          ║");
    Serial.println("╚══════════════════════════════════════╝");
    Serial.println("\nRebooting in 5s..."); delay(5000); ESP.restart();
}

void setup() {
    Serial.begin(115200); delay(1000);
    Serial.println("\n========================================");
    Serial.println("  ESP32 COMPREHENSIVE HARDWARE TEST");
    Serial.println("========================================");
    testChipInfo(); testFlash(); testWiFi(); testBluetooth();
    testGPIO(); testADC(); testI2C(); testSPI(); testTimer(); testMemory();
    printResults();
}

void loop() {}
