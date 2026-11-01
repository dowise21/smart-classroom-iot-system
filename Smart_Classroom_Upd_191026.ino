#include <Arduino.h>
#include <DHT.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

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

#define TEMP_FAN_ON      34.0f
#define TEMP_FAN_OFF     33.5f
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

bool tempFanNeed = false; // Biến lưu yêu cầu bật quạt từ nhiệt độ
bool fanOn = false;       // Trạng thái quạt thực tế (Nhiệt độ HOẶC Khí Gas)
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

// Hàm in đúng 16 ký tự lên LCD (không cần lcd.clear để tránh loạn chữ)
void printLcdLine(uint8_t row, const char* text) {
  char buf[17];
  snprintf(buf, sizeof(buf), "%-16s", text);
  lcd.setCursor(0, row);
  lcd.print(buf);
}

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

  // Khởi tạo I2C chống nhiễu cho LCD
  Wire.begin(LCD_SDA_PIN, LCD_SCL_PIN);
  Wire.setClock(50000);
  delay(100);

  lcd.init();
  delay(100);
  lcd.backlight();
  printLcdLine(0, "Smart Classroom");
  printLcdLine(1, "Initializing...");

  // TEST OUTPUT 1 GIÂY
  Serial.println("\n=== KHOI DONG SMART CLASSROOM ===");
  setFanRelay(true);
  setLightRelay(true);
  digitalWrite(WARNING_LED_PIN, HIGH);
  digitalWrite(BUZZER_PIN, HIGH);
  delay(1000);

  setFanRelay(false);
  setLightRelay(false);
  digitalWrite(WARNING_LED_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);

  // Làm tươi lại LCD sau khi đóng ngắt Relay test
  delay(100);
  lcd.init();
  lcd.backlight();
  printLcdLine(0, "SYSTEM READY");
  printLcdLine(1, "Waiting data...");

  dht.begin();
  Serial.println("==> HE THONG SAN SANG!\n");
  delay(1000);
}

void loop() {
  unsigned long currentTime = millis();

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
  lightOn = (isDark && motionDetected);
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

      // Xét nhu cầu bật quạt theo nhiệt độ
      if (currentTemp >= TEMP_FAN_ON) {
        tempFanNeed = true;
      } else if (currentTemp <= TEMP_FAN_OFF) {
        tempFanNeed = false;
      }

      // Xét cảnh báo nhiệt độ cao
      if (currentTemp >= TEMP_ALARM_ON) {
        tempAlarm = true;
      } else if (currentTemp <= TEMP_ALARM_OFF) {
        tempAlarm = false;
      }
    }

    // --- 3.3 TỔNG HỢP ĐIỀU KHIỂN QUẠT (Bật khi Nóng HOẶC Có Khí Gas) ---
    fanOn = (tempFanNeed || gasAlarm);
    setFanRelay(fanOn);

    // --- 3.4 TỔNG HỢP CÒI & ĐÈN CẢNH BÁO ---
    alarmActive = (gasAlarm || tempAlarm);
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

    Serial.printf("PIR: %-5s | LDR: %-5s | MQ135: %-4d | ",
                  motionDetected ? "CO" : "KHONG",
                  isDark ? "TOI" : "SANG",
                  mq135Raw);

    if (dhtError) {
      Serial.print("DHT11: LOI! | ");
    } else {
      Serial.printf("Temp: %.1f*C Hum: %.0f%% | ", currentTemp, currentHum);
    }

    Serial.printf("Quat: %-3s | Den Hoc: %-3s | Trang thai: %s\n",
                  fanOn ? "BAT" : "TAT",
                  lightOn ? "BAT" : "TAT",
                  gasAlarm ? "CANH BAO KHI GAS!" : (tempAlarm ? "NHIET DO CAO!" : "Binh thuong"));
  }

  // 6. NHẤP NHÁY ĐÈN & CÒI KHI CÓ BÁO ĐỘNG
  if (alarmActive) {
    if (currentTime - lastBlinkMs >= ALARM_BLINK_INTERVAL) {
      lastBlinkMs = currentTime;
      blinkState = !blinkState;
      digitalWrite(WARNING_LED_PIN, blinkState ? HIGH : LOW);
      digitalWrite(BUZZER_PIN, blinkState ? HIGH : LOW);
    }
  }
}