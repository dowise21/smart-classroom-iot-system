#include <Arduino.h>
#include <DHT.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>

// =====================================================
// 0. CẤU HÌNH WIFI & GOOGLE SCRIPT WEBHOOK
// =====================================================
const char* WIFI_SSID     = "pengon";  
const char* WIFI_PASSWORD = "ngoanlv6";    

const char* AP_SSID       = "SmartClassroom_WiFi";
const char* AP_PASS       = "12345678";

// Dán đường dẫn Web App URL của Google Apps Script vào đây:
const char* GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwqhls0hb2drMwGw814XrDK-JxXPHil40b2adFl8XtYK-oC5IMo5byE8DOU8kQ2yy-4eQ/exec";

// Biến chống spam mail (Chỉ gửi 1 mail, sau 5 phút mới được gửi tiếp nếu sự cố vẫn còn)
unsigned long lastEmailSendTime = 0;
const unsigned long EMAIL_COOLDOWN = 300000; // 300.000 ms = 5 phút

// THÊM: 2 biến cờ để ghi nhớ sự kiện đã gửi (Phục vụ Logic Leo Thang)
bool tempEmailSent = false;
bool gasEmailSent = false;

ESP8266WebServer server(80);
String localIpStr = "Offline";

uint8_t fanMode   = 0; 
uint8_t lightMode = 0;

// =====================================================
// 1. KHAI BÁO CHÂN ESP8266
// =====================================================
#define PIR_PIN         14  // D5 - GPIO14
#define LDR_DO_PIN      12  // D6 - GPIO12
#define DHT_PIN          0  // D3 - GPIO0
#define MQ135_AO_PIN    A0  // A0 - MQ135 Analog Output

#define RELAY_FAN_PIN   16  // D0 - GPIO16
#define RELAY_LIGHT_PIN  2  // D4 - GPIO2
#define WARNING_LED_PIN 13  // D7 - GPIO13
#define BUZZER_PIN      15  // D8 - GPIO15

#define LCD_SDA_PIN      4  // D2 - GPIO4
#define LCD_SCL_PIN      5  // D1 - GPIO5
#define LCD_ADDR      0x27

// =====================================================
// 2. CẤU HÌNH THỜI GIAN
// =====================================================
const unsigned long PIR_HOLD_TIME        = 15000;
const unsigned long PRINT_INTERVAL       = 1000;
const unsigned long SENSOR_INTERVAL      = 2000;
const unsigned long LCD_INTERVAL         = 2000;
const unsigned long ALARM_BLINK_INTERVAL = 300;

// =====================================================
// 3. DHT11 + LCD
// =====================================================
#define DHTTYPE DHT11
DHT dht(DHT_PIN, DHTTYPE);
LiquidCrystal_I2C lcd(LCD_ADDR, 16, 2);

// =====================================================
// 4. CẤU HÌNH RELAY / ĐÈN & NGƯỠNG DEMO
// =====================================================
#define FAN_ACTIVE_HIGH  true
#define LIGHT_ACTIVE_LOW false

#define TEMP_FAN_ON      35.0f
#define TEMP_FAN_OFF     34.5f
#define TEMP_ALARM_ON    35.0f
#define TEMP_ALARM_OFF   34.5f

#define MQ135_ALARM_ON   500
#define MQ135_ALARM_OFF  450

// =====================================================
// 5. BIẾN TRẠNG THÁI
// =====================================================
volatile bool pirInterruptTriggered = false;
bool motionDetected = false;
unsigned long lastMotionTime = 0;

float currentTemp = NAN;
float currentHum = NAN;
bool dhtError = true;
int mq135Raw = 0;
bool isDark = false;

bool tempFanNeed = false; 
bool fanOn = false;       
bool lightOn = false;

bool tempAlarm = false;
bool gasAlarm = false;
bool alarmActive = false;
bool blinkState = false;

unsigned long lastSensorReadMs = 0;
unsigned long lastPrintTime = 0;
unsigned long lastBlinkMs = 0;
unsigned long lastLcdUpdateMs = 0;

uint8_t lcdPage = 0;
uint8_t lcdResetCounter = 0;

void IRAM_ATTR onPirRisingEdge() {
  pirInterruptTriggered = true;
}

void setFanRelay(bool turnOn) {
  if (FAN_ACTIVE_HIGH) {
    digitalWrite(RELAY_FAN_PIN, turnOn ? HIGH : LOW);
  } else {
    digitalWrite(RELAY_FAN_PIN, turnOn ? LOW : HIGH);
  }
}

void setLightRelay(bool turnOn) {
  if (LIGHT_ACTIVE_LOW) {
    digitalWrite(RELAY_LIGHT_PIN, turnOn ? LOW : HIGH);
  } else {
    digitalWrite(RELAY_LIGHT_PIN, turnOn ? HIGH : LOW);
  }
}

void printLcdLine(uint8_t row, const char* text) {
  char buf[17];
  snprintf(buf, sizeof(buf), "%-16s", text);
  lcd.setCursor(0, row);
  lcd.print(buf);
}

// =====================================================
// 6. HÀM GỬI EMAIL CHUYÊN NGHIỆP TỚI GOOGLE SCRIPT
// =====================================================
void sendAlertEmail(String temp, String gas) {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClientSecure client;
    client.setInsecure(); // Bỏ qua chứng chỉ SSL
    
    HTTPClient http;
    // URL thông minh: Chỉ ghép những chỉ số thực sự đang có sự cố
    String url = String(GOOGLE_SCRIPT_URL) + "?";
    
    if (temp != "") url += "temp=" + temp + "&";
    if (gas != "") url += "gas=" + gas;
    
    Serial.println(">>> Đang gọi Webhook gửi Email HTML...");
    http.begin(client, url);
    
    // LỆNH ÉP ĐI THEO CHUYỂN HƯỚNG CỦA GOOGLE (BẮT BUỘC)
    http.setFollowRedirects(HTTPC_STRICT_FOLLOW_REDIRECTS);
    
    int httpCode = http.GET();
    
    if (httpCode > 0) {
      Serial.println("==> HTTP Code: " + String(httpCode));
      if (httpCode == HTTP_CODE_OK || httpCode == 302) {
        Serial.println("==> GỬI MAIL HTML THÀNH CÔNG!");
      }
    } else {
      Serial.println("==> Lỗi kết nối, mã lỗi: " + http.errorToString(httpCode));
    }
    http.end();
  }
}

// =====================================================
// 7. WEB SERVER DASHBOARD
// =====================================================
void handleRoot() {
  String html = R"rawliteral(
<!DOCTYPE html><html><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Smart Classroom Dashboard</title>
<style>
  body{font-family:Arial,sans-serif;background:#f0f4f8;margin:0;padding:15px;text-align:center;color:#333;}
  h2{color:#1a73e8;margin-bottom:10px;}
  .status-bar{padding:12px;border-radius:8px;font-weight:bold;color:#fff;margin-bottom:15px;font-size:18px;}
  .safe{background:#28a745;} .danger{background:#dc3545;animation:blink 0.8s infinite;}
  @keyframes blink{50%{opacity:0.4;}}
  .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:12px;max-width:650px;margin:auto;}
  .card{background:#fff;padding:15px;border-radius:10px;box-shadow:0 2px 6px rgba(0,0,0,0.08);}
  .val{font-size:24px;font-weight:bold;color:#1a73e8;margin-top:6px;}
  .ctrl{max-width:650px;margin:15px auto;background:#fff;padding:15px;border-radius:10px;box-shadow:0 2px 6px rgba(0,0,0,0.08);}
  button{padding:8px 14px;margin:4px;border:none;border-radius:6px;font-weight:bold;cursor:pointer;color:#fff;}
  .btn-auto{background:#6c757d;} .btn-on{background:#28a745;} .btn-off{background:#dc3545;}
</style></head><body>
  <h2>SMART CLASSROOM IoT</h2>
  <div id="alarmBox" class="status-bar safe">HE THONG AN TOAN</div>
  <div class="grid">
    <div class="card">Nhiệt độ<div class="val" id="temp">-- °C</div></div>
    <div class="card">Độ ẩm<div class="val" id="hum">-- %</div></div>
    <div class="card">Khí Gas (MQ135)<div class="val" id="gas">--</div></div>
    <div class="card">Ánh sáng<div class="val" id="ldr">--</div></div>
    <div class="card">Chuyển động PIR<div class="val" id="pir">--</div></div>
    <div class="card">Thiết bị<div class="val" style="font-size:16px" id="dev">--</div></div>
  </div>
  <div class="ctrl">
    <div><b>Điều khiển Quạt:</b> (<span id="fMode">AUTO</span>)<br>
      <button class="btn-auto" onclick="setMode('fan',0)">AUTO</button>
      <button class="btn-on" onclick="setMode('fan',1)">BẬT</button>
      <button class="btn-off" onclick="setMode('fan',2)">TẮT</button>
    </div><hr style="border:0;border-top:1px solid #eee;margin:12px 0;">
    <div><b>Điều khiển Đèn học:</b> (<span id="lMode">AUTO</span>)<br>
      <button class="btn-auto" onclick="setMode('light',0)">AUTO</button>
      <button class="btn-on" onclick="setMode('light',1)">BẬT</button>
      <button class="btn-off" onclick="setMode('light',2)">TẮT</button>
    </div>
  </div>
<script>
  function setMode(dev,m){fetch('/control?dev='+dev+'&mode='+m).then(()=>loadData());}
  function loadData(){
    fetch('/data').then(r=>r.json()).then(d=>{
      document.getElementById('temp').innerText = d.dhtErr ? 'LỖI!' : d.temp.toFixed(1)+' °C';
      document.getElementById('hum').innerText  = d.dhtErr ? '--' : d.hum.toFixed(0)+' %';
      document.getElementById('gas').innerText  = d.gas;
      document.getElementById('ldr').innerText  = d.dark ? 'TỐI' : 'SÁNG';
      document.getElementById('pir').innerText  = d.pir ? 'CÓ NGƯỜI' : 'VẮNG';
      document.getElementById('dev').innerText  = 'Quạt: '+(d.fan?'ON':'OFF')+' | Đèn: '+(d.light?'ON':'OFF');
      const mNames = ['AUTO','BẬT TAY','TẮT TAY'];
      document.getElementById('fMode').innerText = mNames[d.fMode];
      document.getElementById('lMode').innerText = mNames[d.lMode];
      const ab = document.getElementById('alarmBox');
      if(d.gasAlarm){ab.className='status-bar danger';ab.innerText='! CẢNH BÁO RÒ RỈ KHÍ GAS !';}
      else if(d.tempAlarm){ab.className='status-bar danger';ab.innerText='! CẢNH BÁO NHIỆT ĐỘ CAO !';}
      else{ab.className='status-bar safe';ab.innerText='HỆ THỐNG BÌNH THƯỜNG';}
    });
  }
  setInterval(loadData, 1500); loadData();
</script></body></html>
)rawliteral";
  server.send(200, "text/html", html);
}

void handleData() {
  String json = "{";
  json += "\"temp\":" + String(isnan(currentTemp) ? 0 : currentTemp, 1) + ",";
  json += "\"hum\":" + String(isnan(currentHum) ? 0 : currentHum, 0) + ",";
  json += "\"dhtErr\":" + String(dhtError ? "true" : "false") + ",";
  json += "\"gas\":" + String(mq135Raw) + ",";
  json += "\"dark\":" + String(isDark ? "true" : "false") + ",";
  json += "\"pir\":" + String(motionDetected ? "true" : "false") + ",";
  json += "\"fan\":" + String(fanOn ? "true" : "false") + ",";
  json += "\"light\":" + String(lightOn ? "true" : "false") + ",";
  json += "\"fMode\":" + String(fanMode) + ",";
  json += "\"lMode\":" + String(lightMode) + ",";
  json += "\"gasAlarm\":" + String(gasAlarm ? "true" : "false") + ",";
  json += "\"tempAlarm\":" + String(tempAlarm ? "true" : "false");
  json += "}";
  server.send(200, "application/json", json);
}

void handleControl() {
  if (server.hasArg("dev") && server.hasArg("mode")) {
    String dev = server.arg("dev");
    uint8_t m = server.arg("mode").toInt();
    if (m <= 2) {
      if (dev == "fan") fanMode = m;
      else if (dev == "light") lightMode = m;
    }
  }
  server.send(200, "text/plain", "OK");
}

// =====================================================
// 8. SETUP
// =====================================================
void setup() {
  Serial.begin(115200);
  delay(500);

  pinMode(PIR_PIN, INPUT);
  pinMode(LDR_DO_PIN, INPUT);
  pinMode(RELAY_FAN_PIN, OUTPUT);
  pinMode(RELAY_LIGHT_PIN, OUTPUT);
  pinMode(WARNING_LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  attachInterrupt(digitalPinToInterrupt(PIR_PIN), onPirRisingEdge, RISING);

  Wire.begin(LCD_SDA_PIN, LCD_SCL_PIN);
  Wire.setClock(50000);
  delay(100);
  lcd.init();
  lcd.backlight();
  printLcdLine(0, "Smart Classroom");
  printLcdLine(1, "Testing H/W...");

  // Test phần cứng 1 giây
  setFanRelay(true);
  setLightRelay(true);
  digitalWrite(WARNING_LED_PIN, HIGH);
  digitalWrite(BUZZER_PIN, HIGH);
  delay(1000);

  setFanRelay(false);
  setLightRelay(false);
  digitalWrite(WARNING_LED_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);

  // Kết nối WiFi (Tối đa 15 giây để chống lỗi Hotspot)
  delay(100);
  lcd.init();
  lcd.backlight();
  printLcdLine(0, "Connecting WiFi");
  printLcdLine(1, WIFI_SSID);

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  unsigned long startWifiMs = millis();
  while (WiFi.status() != WL_CONNECTED && (millis() - startWifiMs < 15000)) {
    delay(400);
  }

  if (WiFi.status() == WL_CONNECTED) {
    localIpStr = WiFi.localIP().toString();
    printLcdLine(0, "WiFi Connected!");
    printLcdLine(1, localIpStr.c_str());
  } else {
    WiFi.mode(WIFI_AP);
    WiFi.softAP(AP_SSID, AP_PASS);
    localIpStr = WiFi.softAPIP().toString();
    printLcdLine(0, "AP Mode Active");
    printLcdLine(1, localIpStr.c_str());
  }

  server.on("/", handleRoot);
  server.on("/data", handleData);
  server.on("/control", handleControl);
  server.begin();

  dht.begin();
  delay(2500);
}

// =====================================================
// 9. LOOP
// =====================================================
void loop() {
  unsigned long currentTime = millis();
  server.handleClient();

  // 1. XỬ LÝ PIR
  bool currentPirHigh = (digitalRead(PIR_PIN) == HIGH);
  if (pirInterruptTriggered || currentPirHigh) {
    motionDetected = true;
    lastMotionTime = currentTime;
    pirInterruptTriggered = false;
  }
  if (motionDetected && (currentTime - lastMotionTime >= PIR_HOLD_TIME)) {
    motionDetected = false;
  }

  // 2. ĐỌC LDR & ĐIỀU KHIỂN ĐÈN HỌC
  isDark = (digitalRead(LDR_DO_PIN) == HIGH);
  if (lightMode == 0) lightOn = (isDark && motionDetected);
  else if (lightMode == 1) lightOn = true;
  else lightOn = false;
  setLightRelay(lightOn);

  // 3. ĐỌC DHT11 + MQ135 (Mỗi 2 giây)
  if (currentTime - lastSensorReadMs >= SENSOR_INTERVAL) {
    lastSensorReadMs = currentTime;

    // --- 3.1 Đọc MQ135 ---
    mq135Raw = analogRead(MQ135_AO_PIN);
    if (mq135Raw >= MQ135_ALARM_ON) {
      gasAlarm = true;
    } else if (mq135Raw <= MQ135_ALARM_OFF) {
      gasAlarm = false;
    }

    // --- 3.2 Đọc DHT11 ---
    float t = dht.readTemperature();
    float h = dht.readHumidity();

    if (isnan(t) || isnan(h)) {
      dhtError = true;
      tempFanNeed = false;
      tempAlarm = false;
    } else {
      dhtError = false;
      currentTemp = t;
      currentHum = h;

      if (currentTemp >= TEMP_FAN_ON) {
        tempFanNeed = true;
      } else if (currentTemp <= TEMP_FAN_OFF) {
        tempFanNeed = false;
      }

      if (currentTemp >= TEMP_ALARM_ON) {
        tempAlarm = true;
      } else if (currentTemp <= TEMP_ALARM_OFF) {
        tempAlarm = false;
      }
    }

    // Tổng hợp điều khiển Quạt
    if (gasAlarm) {
      fanOn = true;
    } else if (fanMode == 0) {
      fanOn = tempFanNeed;
    } else if (fanMode == 1) {
      fanOn = true;
    } else {
      fanOn = false;
    }
    setFanRelay(fanOn);

    // Tổng hợp cảnh báo
    alarmActive = (gasAlarm || tempAlarm);
    
    // --- 3.3 THUẬT TOÁN GỬI EMAIL LEO THANG (ESCALATION ALERT) ---
    bool needToSendEmail = false;

    // Kiểm tra xem có sự cố MỚI nào vừa xuất hiện mà chưa báo cáo không?
    if (gasAlarm && !gasEmailSent) {
      needToSendEmail = true; // Xé rào nếu có Khí Gas rò rỉ mới
    }
    if (tempAlarm && !tempEmailSent) {
      needToSendEmail = true; // Xé rào nếu có Nhiệt độ cao mới
    }

    // Kiểm tra xem đã hết 5 phút để gửi mail nhắc nhở chưa?
    if (alarmActive && lastEmailSendTime != 0 && (currentTime - lastEmailSendTime >= EMAIL_COOLDOWN)) {
      needToSendEmail = true; 
    }

    // Thực hiện gửi mail
    if (needToSendEmail) {
      lastEmailSendTime = currentTime; 
      tempEmailSent = tempAlarm;       // Ghi nhớ lại trạng thái đã báo cáo     
      gasEmailSent = gasAlarm;         
      
      String tempToPush = "";
      String gasToPush = "";

      // Chỉ đóng gói dữ liệu của sự kiện đang vượt ngưỡng
      if (tempAlarm) {
        tempToPush = String(currentTemp, 1);
      }
      if (gasAlarm) {
        gasToPush = String(mq135Raw);
      }
      
      // Gọi hàm gửi Email
      sendAlertEmail(tempToPush, gasToPush);
    }

    // Khi an toàn, Reset bộ nhớ (Chỉ reset sau 5 phút để tránh chập chờn)
    if (!alarmActive) {
      if (currentTime - lastEmailSendTime >= EMAIL_COOLDOWN) {
        lastEmailSendTime = 0; 
        tempEmailSent = false;
        gasEmailSent = false;
      }
    }

    if (!alarmActive) {
      blinkState = false;
      digitalWrite(WARNING_LED_PIN, LOW);
      digitalWrite(BUZZER_PIN, LOW);
    }
  }

  // 4. HIỂN THỊ LCD (Mỗi 2 giây)
  if (currentTime - lastLcdUpdateMs >= LCD_INTERVAL) {
    lastLcdUpdateMs = currentTime;

    lcdResetCounter++;
    if (lcdResetCounter >= 10) {
      lcdResetCounter = 0;
      lcd.init();
      lcd.backlight();
    }

    char line0[17];
    char line1[17];

    if (gasAlarm) {
      snprintf(line0, sizeof(line0), "! CANH BAO KHI !");
      snprintf(line1, sizeof(line1), "Gas:%d Fan:ON", mq135Raw);
    } else if (tempAlarm) {
      snprintf(line0, sizeof(line0), "! NHIET DO CAO !");
      snprintf(line1, sizeof(line1), "T:%.1fC Fan:ON", currentTemp);
    } else {
      if (lcdPage == 0) {
        if (dhtError) {
          snprintf(line0, sizeof(line0), "DHT: LOI DOC!");
        } else {
          snprintf(line0, sizeof(line0), "T:%.1fC H:%.0f%%", currentTemp, currentHum);
        }
        snprintf(line1, sizeof(line1), "Gas:%d %s", mq135Raw, isDark ? "TOI" : "SANG");
      } else {
        snprintf(line0, sizeof(line0), "PIR:%s", motionDetected ? "CO NGUOI" : "VANG");
        snprintf(line1, sizeof(line1), "Fan:%s Den:%s", fanOn ? "ON " : "OFF", lightOn ? "ON" : "OFF");
      }
      lcdPage = (lcdPage + 1) % 2;
    }

    printLcdLine(0, line0);
    printLcdLine(1, line1);
  }

  // 5. IN RA SERIAL MONITOR (Mỗi 1 giây)
  if (currentTime - lastPrintTime >= PRINT_INTERVAL) {
    lastPrintTime = currentTime;

    Serial.printf("[IP: %s] PIR:%-5s | LDR:%-4s | MQ135:%-4d | ",
                  localIpStr.c_str(),
                  motionDetected ? "CO" : "KHONG",
                  isDark ? "TOI" : "SANG",
                  mq135Raw);

    if (dhtError) {
      Serial.print("DHT:LOI! | ");
    } else {
      Serial.printf("T:%.1f*C H:%.0f%% | ", currentTemp, currentHum);
    }

    Serial.printf("Quat:%-3s | Den:%-3s | %s\n",
                  fanOn ? "BAT" : "TAT",
                  lightOn ? "BAT" : "TAT",
                  gasAlarm ? "CANH BAO KHI GAS!" : (tempAlarm ? "NHIET DO CAO!" : "An toan"));
  }

  // 6. NHẤP NHÁY ĐÈN & CÒI (CHỈ HÚ KHI CÓ GAS)
  if (alarmActive) {
    if (currentTime - lastBlinkMs >= ALARM_BLINK_INTERVAL) {
      lastBlinkMs = currentTime;
      blinkState = !blinkState;
      
      // Đèn luôn chớp báo hiệu có sự kiện
      digitalWrite(WARNING_LED_PIN, blinkState ? HIGH : LOW);
      
      // Còi chỉ kích hoạt nếu có rò rỉ khí Gas
      if (gasAlarm) {
        digitalWrite(BUZZER_PIN, blinkState ? HIGH : LOW);
      } else {
        digitalWrite(BUZZER_PIN, LOW); // Ép tắt còi nếu chỉ là báo nhiệt độ
      }
    }
  }
}