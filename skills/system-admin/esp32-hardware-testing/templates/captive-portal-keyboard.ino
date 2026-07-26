/*
 * ESP32 Captive Portal Keyboard Configurator — TEMPLATE
 * 
 * ESP32 creates WiFi AP, hosts a web-based keyboard configurator.
 * Connect phone to AP → captive portal auto-opens the config page.
 * 
 * Tested on: ESP32-D0WD-V3, Arduino ESP32 core 3.3.10
 * Partition: huge_app (compile with --fqbn esp32:esp32:esp32:PartitionScheme=huge_app)
 * 
 * Flash with:
 *   BDIR=$(ls -td ~/.cache/arduino/sketches/*/ | head -1)
 *   sudo esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash \
 *     0x1000 "$BDIR/sketch.ino.bootloader.bin" \
 *     0x8000 "$BDIR/sketch.ino.partitions.bin" \
 *     0xe000 "$BDIR/boot_app0.bin" \
 *     0x10000 "$BDIR/sketch.ino.bin"
 */

#include <WiFi.h>
#include <WiFiUdp.h>
#include <WebServer.h>
#include <Preferences.h>

// ===== CONFIG =====
const char* AP_SSID = "ESP32 Keyboard";
const char* AP_PASS = "";  // Open network
const byte DNS_PORT = 53;

// ===== GLOBALS =====
WebServer server(80);
Preferences prefs;
WiFiUDP dnsUdp;
IPAddress apIP(192, 168, 4, 1);
IPAddress apGateway(192, 168, 4, 1);
IPAddress apSubnet(255, 255, 255, 0);

// ===== HTML PAGE =====
const char PAGE_HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ESP32 Config</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui;background:#0a0a0f;color:#e8e8f0;min-height:100vh;display:flex;align-items:center;justify-content:center}
.card{background:#12121a;border:1px solid #252535;border-radius:14px;padding:32px;max-width:400px;width:90%;text-align:center}
h1{font-size:20px;margin-bottom:8px}
p{color:#6b6b80;font-size:14px;margin-bottom:20px}
.status{display:inline-flex;align-items:center;gap:8px;padding:8px 16px;border-radius:8px;background:#1a1a25;font-size:13px;color:#4ade80}
.dot{width:6px;height:6px;border-radius:50%;background:#4ade80;box-shadow:0 0 8px rgba(74,222,128,.4)}
</style>
</head>
<body>
<div class="card">
  <h1>ESP32 Keyboard</h1>
  <p>Captive portal is working!</p>
  <div class="status"><span class="dot"></span>Connected</div>
</div>
</body>
</html>
)rawliteral";

// ===== HANDLERS =====
void handleRoot() {
  server.send_P(200, "text/html", PAGE_HTML);
}

void handleNotFound() {
  String host = server.hostHeader();
  
  // Captive portal detection — respond with 200 + meta refresh
  if (host.indexOf("captive.apple.com") >= 0 ||
      host.indexOf("connectivitycheck") >= 0 ||
      host.indexOf("google") >= 0 ||
      host.indexOf("msftconnecttest") >= 0 ||
      host.indexOf("msftncsi") >= 0 ||
      host.indexOf("android") >= 0 ||
      host.indexOf("detectportal") >= 0 ||
      host.indexOf("example.com") >= 0) {
    server.send(200, "text/html",
      "<!DOCTYPE html><html><head>"
      "<meta http-equiv='refresh' content='0;url=http://" + apIP.toString() + "/'>"
      "</head><body><p>Redirecting...</p></body></html>");
    return;
  }
  
  // Everything else → redirect to main page
  server.sendHeader("Location", "http://" + apIP.toString() + "/", true);
  server.send(302, "text/plain", "");
}

// ===== CUSTOM DNS HANDLER =====
// Responds to ALL DNS queries with our AP IP — captive portal magic
void handleDNS() {
  int packetSize = dnsUdp.parsePacket();
  if (!packetSize) return;
  
  byte buffer[512];
  int len = dnsUdp.read(buffer, sizeof(buffer));
  if (len < 12) return;
  
  byte response[512];
  memcpy(response, buffer, len);
  response[2] = 0x81;  // QR=1, Opcode=0, AA=1
  response[3] = 0x80;  // RA=1, RCODE=0
  response[6] = 0x00; response[7] = 0x01;  // Answer count = 1
  
  int off = len;
  response[off++]=0xC0; response[off++]=0x0C;  // Name pointer to question
  response[off++]=0x00; response[off++]=0x01;  // Type A
  response[off++]=0x00; response[off++]=0x01;  // Class IN
  response[off++]=0x00; response[off++]=0x00;
  response[off++]=0x00; response[off++]=0x3C;  // TTL = 60s
  response[off++]=0x00; response[off++]=0x04;  // Data length = 4
  response[off++]=apIP[0]; response[off++]=apIP[1];
  response[off++]=apIP[2]; response[off++]=apIP[3];
  
  dnsUdp.beginPacket(dnsUdp.remoteIP(), dnsUdp.remotePort());
  dnsUdp.write(response, off);
  dnsUdp.endPacket();
}

// ===== SETUP =====
void setup() {
  Serial.begin(115200);
  delay(100);
  
  Serial.println("\n=== ESP32 Captive Portal ===");
  
  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(apIP, apGateway, apSubnet);  // MUST be before softAP
  WiFi.softAP(AP_SSID, AP_PASS);
  delay(100);
  
  Serial.println("[AP] SSID: " + String(AP_SSID));
  Serial.println("[AP] IP: " + WiFi.softAPIP().toString());
  
  dnsUdp.begin(DNS_PORT);
  
  server.on("/", HTTP_GET, handleRoot);
  server.onNotFound(handleNotFound);
  server.begin();
  
  Serial.println("[READY] Connect to WiFi: " + String(AP_SSID));
}

void loop() {
  handleDNS();
  server.handleClient();
}
