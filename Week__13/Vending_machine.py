// Vending Machine

//Step01: Enum for all states
enum {Idle, Payment, Insuff, Item1Drop, Item2Drop, ReturnMoney, Unlocking, Collect, Quit, Locking};

//Step02: Define all inputs and outputs

#define M1 11   
#define M2 10
#define M3 9
#define M4 8


#define InsuffLED 6
#define LockedLED 5
#define UnlockedLED 4
#define CollectLED 3
#define ChangeLED 2


#define C100 A0
#define C50 A1
#define I1 A2
#define I2 A3 
#define cancel A4



float item1Price = 1;
float item2Price = 0.5;

float Total=0;  
float Change=0; 

int current=Idle;

void setup()
{
Serial.begin(9600);
pinMode(M1,OUTPUT); //Item1Drop
pinMode(M2,OUTPUT); //Item2Drop
pinMode(M3,OUTPUT); //Unlock
pinMode(M4,OUTPUT); //Return change

pinMode(InsuffLED,OUTPUT); //Red LED
pinMode(LockedLED,OUTPUT); //Blue LED
pinMode(UnlockedLED,OUTPUT); //Brown LED
pinMode(CollectLED,OUTPUT); //Green LED
pinMode(ChangeLED,OUTPUT); //White LED

pinMode(C100,INPUT_PULLUP); // One dirham(100 cents) button
pinMode(C50,INPUT_PULLUP); // half dirham(50 cents) button
pinMode(I1,INPUT_PULLUP); //Item 1 button
pinMode(I2,INPUT_PULLUP); // Item 2 button
pinMode(cancel,INPUT_PULLUP);// cancel button
}
 void loop()
{
switch(current)
{
case Idle:
Serial.println("Insert coin");
digitalWrite(M1, LOW);
digitalWrite(M2, LOW);
digitalWrite(M3, LOW);
digitalWrite(M4, LOW);
digitalWrite(InsuffLED, LOW);
digitalWrite(LockedLED, HIGH);
digitalWrite(UnlockedLED, LOW);
digitalWrite(CollectLED, LOW);
digitalWrite(ChangeLED, LOW);

if (digitalRead(C50)==0){
Total += 0.5;
Serial.println(Total);
delay(500);
current = Payment;
}
  
if (digitalRead(C100)==0){
Total += 1;
Serial.println(Total);
delay(500);
current = Payment;
}
  break;
  
case Payment:
Serial.println("Choose item/Add coin/Press A4 to cancel");
digitalWrite(M1, LOW);
digitalWrite(M2, LOW);
digitalWrite(M3, LOW);
digitalWrite(M4, LOW);
digitalWrite(InsuffLED, LOW);
digitalWrite(LockedLED, HIGH);
digitalWrite(UnlockedLED, LOW);
digitalWrite(CollectLED, LOW);
digitalWrite(ChangeLED, LOW);

if(digitalRead(cancel) == 0) {
Change = Total;
current = Quit;
}

if(digitalRead(C50) == 0) {
delay(500);
Total+=0.5;
Serial.println(Total);
}

if(digitalRead(C100) == 0){
delay(500);
Total+=1;
Serial.println(Total);
}

if (digitalRead(I1)==0 && (Total>=item1Price)) {
Change = Total - item1Price;

current =Item1Drop;

}
if (digitalRead(I2)==0 && (Total>=item2Price)) {
Change = Total - item2Price;
current =Item2Drop;

}

if (((digitalRead(I1) == 0) && (Total<item1Price)) || ((digitalRead(I2) == 0) && (Total<item2Price))) {

  current = Insuff;

}

break;

case Insuff:
Serial.println("Not enough money");
digitalWrite(M1, LOW);
digitalWrite(M2, LOW);
digitalWrite(M3, LOW);
digitalWrite(M4, LOW);
digitalWrite(InsuffLED, HIGH);
digitalWrite(LockedLED, HIGH);
digitalWrite(UnlockedLED, LOW);
digitalWrite(CollectLED, LOW);
digitalWrite(ChangeLED, LOW);
delay(3000);
current= Payment;
break;

case Item1Drop:
Serial.println("Item 1 chosen");
digitalWrite(M1, HIGH);
digitalWrite(M2, LOW);
digitalWrite(M3, LOW);
digitalWrite(M4, LOW);
digitalWrite(InsuffLED, LOW);
digitalWrite(LockedLED, HIGH);
digitalWrite(UnlockedLED, LOW);
digitalWrite(CollectLED, LOW);
digitalWrite(ChangeLED, LOW);

if(Change>0)
  {
    delay(2000);
    current= ReturnMoney;
  }
  
if(Change==0)
  {
    delay(2000);
    current= Unlocking;
  }
break;

case Item2Drop:
Serial.println("Item 2 chosen");
digitalWrite(M1, LOW);
digitalWrite(M2, HIGH);
digitalWrite(M3, LOW);
digitalWrite(M4, LOW);
digitalWrite(InsuffLED, LOW);
digitalWrite(LockedLED, HIGH);
digitalWrite(UnlockedLED, LOW);
digitalWrite(CollectLED, LOW);
digitalWrite(ChangeLED, LOW);


if(Change>0)
{
delay(2000);
current= ReturnMoney;
}
if(Change==0)
{
delay(2000);
current= Unlocking;
}
break;

case ReturnMoney:
Serial.println("Take the change");
digitalWrite(M1, LOW);
digitalWrite(M2, LOW);
digitalWrite(M3, LOW);
digitalWrite(M4, HIGH);
digitalWrite(InsuffLED, LOW);
digitalWrite(LockedLED, HIGH);
digitalWrite(UnlockedLED, LOW);
digitalWrite(CollectLED, LOW);
digitalWrite(ChangeLED, HIGH);

delay(1500);
while(Change>0)
{
Change-=0.5;
current= ReturnMoney;
}
if (Change==0)
{
current= Unlocking;
}
break;

case Unlocking:
Serial.println("Unlocking...");
digitalWrite(M1, LOW);
digitalWrite(M2, LOW);
digitalWrite(M3, HIGH);
digitalWrite(M4, LOW);
digitalWrite(InsuffLED, LOW);
digitalWrite(LockedLED, LOW);
digitalWrite(UnlockedLED, HIGH);
digitalWrite(CollectLED, LOW);
digitalWrite(ChangeLED, LOW);
delay(2000);
current= Collect;
break;

case Collect:
Serial.println("Pick your item, have a nice day :)");
digitalWrite(M1, LOW);
digitalWrite(M2, LOW);
digitalWrite(M3, LOW);
digitalWrite(M4, LOW);
digitalWrite(InsuffLED, LOW);
digitalWrite(LockedLED, LOW);
digitalWrite(UnlockedLED, HIGH);
digitalWrite(CollectLED, HIGH);
digitalWrite(ChangeLED, LOW);
delay(10000);
current= Locking;
break;

case Locking:
Serial.println("Locking...");
digitalWrite(M1, LOW);
digitalWrite(M2, LOW);
digitalWrite(M3, HIGH);
digitalWrite(M4, LOW);
digitalWrite(InsuffLED, LOW);
digitalWrite(LockedLED, HIGH);
digitalWrite(UnlockedLED, LOW);
digitalWrite(CollectLED, LOW);
digitalWrite(ChangeLED, LOW);
delay(2000);
current = Idle;
break;

case Quit:
Serial.println("Purchase cancelled");
digitalWrite(M1, LOW);
digitalWrite(M2, LOW);
digitalWrite(M3, LOW);
digitalWrite(M4, HIGH);
digitalWrite(InsuffLED, LOW);
digitalWrite(LockedLED, HIGH);
digitalWrite(UnlockedLED, LOW);
digitalWrite(CollectLED, LOW);
digitalWrite(ChangeLED, HIGH);

delay(1500);
while(Change>0)
{
Change = Change-0.5;
current= Quit;
}
if (Change==0)
{
current= Idle;
}
break;
}
 }
 