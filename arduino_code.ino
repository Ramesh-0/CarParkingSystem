#include <Servo.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 20, 4);
Servo myservo;

// ---- IR Sensor Pins ----
#define ir_enter 2
#define ir_back 4
#define ir_car1 5
#define ir_car2 6
#define ir_car3 7
#define ir_car4 8

// ---- Variables ----
int S1 = 0, S2 = 0, S3 = 0, S4 = 0;
int slot = 4;               // total parking slots
bool gateOpen = false;
String gateDir = "";
unsigned long lastToggle = 0;
bool showSlots = true;

// ---- Helpers ----
// Print a centered line on `row` (0..3). This always writes 20 characters
void printCentered(int row, const String &text) {
  int len = text.length();
  if (len >= 20) {
    lcd.setCursor(0, row);
    lcd.print(text.substring(0, 20));
    return;
  }
  int left = (20 - len) / 2;
  int right = 20 - len - left;
  String line = "";
  for (int i = 0; i < left; ++i) line += ' ';
  line += text;
  for (int i = 0; i < right; ++i) line += ' ';
  lcd.setCursor(0, row);
  lcd.print(line);
}

// Print a left aligned pair of labels in two columns
void printTwoCols(int row, int startCol1, const String &col1, int startCol2, const String &col2) {
  String line = "";
  for (int i = 0; i < 20; ++i) line += ' ';
  for (unsigned int i = 0; i < col1.length() && (startCol1 + (int)i) < 20; ++i)
    line.setCharAt(startCol1 + i, col1[i]);
  for (unsigned int i = 0; i < col2.length() && (startCol2 + (int)i) < 20; ++i)
    line.setCharAt(startCol2 + i, col2[i]);
  lcd.setCursor(0, row);
  lcd.print(line);
}

// ---- Setup ----
void setup() {
  Serial.begin(9600);

  pinMode(ir_enter, INPUT);
  pinMode(ir_back, INPUT);
  pinMode(ir_car1, INPUT);
  pinMode(ir_car2, INPUT);
  pinMode(ir_car3, INPUT);
  pinMode(ir_car4, INPUT);

  myservo.attach(3);
  myservo.write(90);  // Closed gate

  lcd.init();
  lcd.backlight();

  lcd.clear();
  printCentered(1, "CAR PARKING SYSTEM");
  printCentered(2, "INITIALIZING...");
  delay(1800);
  lcd.clear();
}

// ---- Main Loop ----
void loop() {
  Read_Sensor();

  // Toggle between two LCD screens every 3 seconds
  if (millis() - lastToggle > 3000) {
    showSlots = !showSlots;
    lastToggle = millis();
    lcd.clear();
  }

  // ----- Display Section -----
  if (showSlots) {
    Display_Slots();
  } else {
    printCentered(1, "CAR PARKING SYSTEM");
    printCentered(2, String("SLOTS LEFT: ") + slot);
  }

  // ----- Entry from Outside -----
  if (digitalRead(ir_enter) == LOW && !gateOpen) {
    if (slot > 0) {
      myservo.write(180);  // Open gate
      gateOpen = true;
      gateDir = "in";
      lcd.clear();
      printCentered(1, "CAR ENTERING...");
      Serial.println("ENTRY"); // 🔹 Send entry signal to laptop
    } else {
      lcd.clear();
      printCentered(1, "PARKING FULL!");
      delay(1600);
      lcd.clear();
    }
  }

  // ----- Exit from Inside -----
  if (digitalRead(ir_back) == LOW && !gateOpen) {
    myservo.write(180);  // Open gate
    gateOpen = true;
    gateDir = "out";
    lcd.clear();
    printCentered(1, "CAR EXITING...");
    Serial.println("EXIT"); // 🔹 Send exit signal to laptop
  }

  // ----- Close gate once car passes -----
  if (gateOpen) {
    if (gateDir == "in" && digitalRead(ir_back) == LOW) {
      myservo.write(90);
      gateOpen = false;
      slot--;
      if (slot < 0) slot = 0;

      lcd.clear();
      printCentered(1, "GATE CLOSED");
      delay(900);
      lcd.clear();
      printCentered(1, "WELCOME!");
      printCentered(2, "ENJOY YOUR PARKING");
      delay(1600);
      lcd.clear();
    } 
    else if (gateDir == "out" && digitalRead(ir_enter) == LOW) {
      myservo.write(90);
      gateOpen = false;
      slot++;
      if (slot > 4) slot = 4;

      lcd.clear();
      printCentered(1, "GATE CLOSED");
      delay(900);
      lcd.clear();
      printCentered(1, "THANK YOU!");
      printCentered(2, "VISIT AGAIN SOON");
      delay(1600);
      lcd.clear();
    }
  }

  delay(100);
}

// ---- Read Slot Sensors ----
void Read_Sensor() {
  // Assume LOW means detected (sensor output active LOW)
  S1 = (digitalRead(ir_car1) == LOW) ? 1 : 0;
  S2 = (digitalRead(ir_car2) == LOW) ? 1 : 0;
  S3 = (digitalRead(ir_car3) == LOW) ? 1 : 0;
  S4 = (digitalRead(ir_car4) == LOW) ? 1 : 0;

  int filled = S1 + S2 + S3 + S4;
  slot = 4 - filled;
  if (slot < 0) slot = 0;
  if (slot > 4) slot = 4;
}

// ---- Display Slot Info (centered) ----
void Display_Slots() {
  printCentered(0, "PARKING SLOT STATUS");
  printCentered(1, String("AVAILABLE: ") + slot);
  printTwoCols(2, 0, String("S1: ") + (S1 ? "FULL" : "EMPTY"), 10, String("S2: ") + (S2 ? "FULL" : "EMPTY"));
  printTwoCols(3, 0, String("S3: ") + (S3 ? "FULL" : "EMPTY"), 10, String("S4: ") + (S4 ? "FULL" : "EMPTY"));
}
