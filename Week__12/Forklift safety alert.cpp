#define TRIG_PIN 9
#define ECHO_PIN 10
#define BUZZER_PIN 8
#define MOTOR_PIN 6

long duration;
float distance;

void setup() {

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(MOTOR_PIN, OUTPUT);

  Serial.begin(9600);
  Serial.println("Forklift Safety System Started");
}

void loop() {

  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  duration = pulseIn(ECHO_PIN, HIGH);

  distance = duration * 0.034 / 2;

  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  if(distance <= 200 && distance > 0)
  {
    digitalWrite(BUZZER_PIN, HIGH);
    digitalWrite(MOTOR_PIN, LOW);

    Serial.println("ALERT! Pedestrian Detected!");
    Serial.println("Motor STOPPED for safety!");
  }
  else
  {
    digitalWrite(BUZZER_PIN, LOW);
    digitalWrite(MOTOR_PIN, HIGH);

    Serial.println("All Clear - Motor Running");
  }

  delay(500);
}