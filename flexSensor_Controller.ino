/*********
  Author: Jitesh Saini
  This code is built upon the example code in pubsubclient library 
  Complete project details at https://helloworld.co.in
*********/

#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>

// Replace the SSID/Password details as per your wifi router
const char* ssid = " ";
const char* password = " ";

/*const char* ssid = "yen";
const char* password = "19951225";*/

// Replace your MQTT Broker IP address here:
//const char* mqtt_server = "172.20.10.2";
//const char* mqtt_server = "192.168.137.69";

WiFiClient espClient;
PubSubClient client(espClient);

long lastMsg = 0; //마지막으로 보낸 MQTT 메세지 시간 측정

/*플렉스센서 처리 코드 선언*/
const int flexPins[] = {32, 33, 34, 35};  // 센서와 연결된 아날로그 핀 배열
const int Max_Val = 3400;  // 임계값 (3200아래로가면)
const int Min_Count = 16;  // 임계값을 초과하는 값이 10개 중 4개 이상이면 '1' 반환
const int numReadings = 40;  // 플렉스센서를 읽는 횟수 10회

int flexVals[4][numReadings];  // 5개의 센서값을 저장할 2차원 배열
char flex_Send[4] = {'0', '0', '0', '0'};  // 5개의 센서 상태값 ('0' 또는 '1')
int Command_Send = 0; //보낼 명령 초기화
int command = 0; //배열에 있는 값을 비트로 변환하기위한 값 

void FlexRead() {
  for (int i = 0; i < 4; i++) {  // 5개의 센서를 순차적으로 처리
    int count = 0;
    
    // 각 센서에서 10개의 값을 읽음
    for (int j = 0; j < numReadings; j++) {
      flexVals[i][j] = analogRead(flexPins[i]);  // 센서 값 읽기
      //delay(10);  // 읽기 간격 조정 (필요 시 조정 가능)
      
      // 읽은 값이 임계값을 초과하는지 확인 3500아래인지?
      if (flexVals[i][j] < Max_Val) {
        count++;
      }
    }
    
    // 4개 이상의 값이 임계값을 넘으면 '1', 그렇지 않으면 '0'
    if (count >= Min_Count) {
      flex_Send[i] = '1';
    } else {
      flex_Send[i] = '0';
    }
  }
}

void determineCommand() {  
  //flex_send 배열값을 비트로 변환함
  command = 0;  // command를 초기화
  for (int i = 3; i>=0; i--) {
    command |= (flex_Send[i] - '0') << i;  // flex_Send[i]가 '1'이면 해당 비트를 1로 설정
  }
  
  switch(command) {
    case 0: //0000 아무상태도X
      //Serial.println("Command: 0");
      command = 0;
      break;

    case 1: //0001 검지
      //Serial.println("Command: 1");
      command = 1;
      break;

    case 2: //0010 중지
      //Serial.println("Command: 2");
      command = 2;
      break;

    case 3: //0011 검지 중지
      //Serial.println("Command: 3");
      command = 3;
      break;

    case 4: //0100 약지
      //Serial.println("Command: 4");
      command = 4;
      break;

    case 5: //0101 검지 약지
      //Serial.println("Command: 5");
      command = 5;
      break;

    case 6: //0110 중지 약지
      //Serial.println("Command: 6");
      command = 6;
      break;

    case 7: //0111 검지 중지 약지 
     // Serial.println("Command: 7");
      command = 7;
      break;

    case 8: //1000 새끼손가락
      //Serial.println("Command: 8");
      command = 8;
      break;

    case 12: //1100 약지 새끼  
      //Serial.println("Command: 12");
      command = 12;
      break;

    case 14: //1110 중지 약지 새끼 
      //Serial.println("Command: 12");
      command = 14;
      break;

    default:
      //Serial.println("Unknown Command");
      command = 0;
      break;
  }
}

void setup_wifi() { //wifi 연결 함수
  delay(50);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  int c=0;
  while (WiFi.status() != WL_CONNECTED) {
    //blink_led(2,200); //blink LED twice (for 200ms ON time) to indicate that wifi not connected
    delay(1000); //
    Serial.print(".");
    c=c+1;
    if(c>10){
        ESP.restart(); //restart ESP after 10 seconds
    }
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  
}

void connect_mqttServer() {
  // Loop until we're reconnected
  while (!client.connected()) {

        //first check if connected to wifi
        if(WiFi.status() != WL_CONNECTED){
          //if not connected, then first connect to wifi
          setup_wifi();
        }

        //now attemt to connect to MQTT server
        Serial.print("Attempting MQTT connection...");
        // Attempt to connect
        if (client.connect("esp32_client1")) { // Change the name of client here if multiple ESP32 are connected
          //attempt successful
          Serial.println("connected");
          // Subscribe to topics here
          client.subscribe("rpi/broadcast");
          //client.subscribe("rpi/xyz"); //subscribe more topics here
          
        } 
        else {
          //attempt not successful
          Serial.print("failed, rc=");
          Serial.print(client.state());
          Serial.println(" trying again in 2 seconds");
    
          //blink_led(3,200); //blink LED three times (200ms on duration) to show that MQTT server connection attempt failed
          // Wait 2 seconds before retrying
          delay(2000);
        }
  }
  
}

//this function will be executed whenever there is data available on subscribed topics
void callback(char* topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messageTemp;
  
  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    messageTemp += (char)message[i];
  }
  Serial.println();

  // Check if a message is received on the topic "rpi/broadcast"
  if (String(topic) == "rpi/broadcast") {
      if(messageTemp == "10"){
        Serial.println("Action: blink LED");
      }
  }

  //Similarly add more if statements to check for other subscribed topics 
}

void setup() {
  Serial.begin(115200);

  setup_wifi();
  client.setServer(mqtt_server,1883);//1883 is the default port for MQTT server
  client.setCallback(callback);
}

void loop() {
  
  if (!client.connected()) {
    connect_mqttServer();
  }

  client.loop();
  FlexRead();  // 센서 값을 읽고 상태 업데이트
  determineCommand(); //상태 판단 
  
  long now = millis();
  if (now - lastMsg > 20) {
    lastMsg = now;

    char commandStr[3]; 
    itoa(command, commandStr, 10);  // 정수 command 값을 문자열로 변환 (10진수)

    
    client.publish("esp32/sensor1", commandStr); //바꾼 command 문자열을 전송함
  }
}
