#include <Servo.h>
#include <Wire.h>

/**************************/
/* Ian J. Choi
 * 2024-09-29 12:31
 * 6-dof Robot_arm movement code
 * 
 * 10-02 10:27 수정
 * command grap 7 -> 95
 * 로봇 시작 state 7 -> 2
 */
#define sv1_pin 4   //D4
#define sv2_pin 7   //D7
#define sv3_pin 8   //D8
#define grab_pin 12 //D12
/*************************/
/******바꿔도 되는 값********/
const int vtc_maxIdx = 16;
const int hrz_maxIdx = 12;
const int Grab_maxangle = 180;
const int Drop_maxangle = 100;
/*      세팅해서 사용     */
char CMDs[8][3]=
{
  {'0','1','\0'}, //초기화 세팅
  {'0','5','\0'}, //flex센서에서 오는 값 0101검지약지
  {'0','6','\0'}, //flex센서에서 오는 값 0110중지약지
  {'0','9','\0'}, //flex센서에서 오는 값 1001검지중지약지
  {'0','8','\0'}, //flex센서에서 오는 값 1000소지
  {'1','2','\0'}, //flex센서에서 오는 값 1100약지소지
  {'1','4','\0'}, //flex센서에서 오는 값 1110중지약지소지
  {'0','0','\0'}
};

typedef class Robot_arm{
private:
  int vtc_idx;
  int hrz_idx;
  const int vtc_sv[3][vtc_maxIdx+1]= {
      {170, 160, 150, 145, 140, 130, 120, 110, 100, 90, 80, 70, 60, 50, 40, 40, 30},         //로봇의 위 아래 움직임 servo1의 값 //0~vtc_maxIdx
      {180, 175, 170, 160, 150, 135, 120, 110, 100, 90, 80, 70, 60, 50, 35, 25, 20},         //로봇의 위 아래 움직임 servo2의 값 //0~vtc_maxIdx
      {180, 180, 175, 175, 175, 175, 180, 175, 175, 175, 170, 170, 165, 160, 160, 160, 155}  //로봇의 위 아래 움직임 servo3의 값 //0~vtc_maxIdx
    };
  const int hrz_sv[3][hrz_maxIdx+1] = {
    {-60, -50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 60},                             //로봇의 앞, 뒤 움직임 servo1의 값 //0~hrz_maxIdx
    {0, 0, 0, 0, 0, 0, 0, 10, 20, 30, 40, 50, 60},                                         //로봇의 앞, 뒤 움직임 servo2의 값 //0~hrz_maxIdx
    {-60, -50, -40, -30, -20, -10, 0, 0, 0, 0, 0, 0, 0}                                    //로봇의 앞, 뒤 움직임 servo3의 값 //0~hrz_maxIdx
  };
  
public:
  bool vtcUP();
  bool vtcDOWN();
  bool hrzBACK();
  bool hrzFORWARD();
  bool angleValidate();
  int angles[3];
  int grab_angle = Grab_maxangle;
  Robot_arm();
  void angleCalculator(char cmd[]);
}Robot_arm;

Servo sv1;
Servo sv2;
Servo sv3;
Servo grabsv;
Robot_arm arm6dof;

char getCommand(){
  while(1)
  {
    if (Serial.available() > 0) {
      int incomingByte = Serial.read();  // 하나의 바이트 읽기
      static char utf8_char[4];  // UTF-8은 최대 4바이트까지 차지할 수 있음
      static int byteCount = 0;
      if (byteCount == 0) {
        if (incomingByte <= 0x7F) {  // 1바이트 문자
          return (char)incomingByte;
        } 
        else if (incomingByte >= 0xC0 && incomingByte <= 0xF7) {
          utf8_char[byteCount++] = incomingByte;  // 첫 바이트 저장
        }
      } 
      else 
      {  // 다바이트 문자 처리 (후속 바이트)
        utf8_char[byteCount++] = incomingByte;
        if (byteCount == 2 && utf8_char[0] >= 0xC0 && utf8_char[0] <= 0xDF) {
          //Serial.println("2byte");
          return '0';
        } 
        else if (byteCount == 3 && utf8_char[0] >= 0xE0 && utf8_char[0] <= 0xEF) {
          //Serial.println("3byte");
          return '0';
        } 
        else if (byteCount == 4 && utf8_char[0] >= 0xF0 && utf8_char[0] <= 0xF7) {
          //Serial.println("4byte");
          return '0';
        }
      }
    }
  }
  return '0';
}

void setup(){
  Serial.begin(115200);
  sv1.attach(sv1_pin);
  sv2.attach(sv2_pin);
  sv3.attach(sv3_pin);
  grabsv.attach(grab_pin);
  arm6dof.angleCalculator(CMDs[0]);
  sv1.write(arm6dof.angles[0]);
  sv2.write(arm6dof.angles[1]);
  sv3.write(arm6dof.angles[2]);
  grabsv.write(arm6dof.grab_angle);

  
  
}
void loop() {
  char command[3] = {'0','0','\0'};
  command[1] = getCommand();
  if(command[1] == '1'){
    char temp = '1';
    while(temp == '1') {
      temp = getCommand();
    }
    command[0] = command[1];
    command[1] = temp;
  } 
  if(command[1] != '0'){
    arm6dof.angleCalculator(command);
    sv1.write(arm6dof.angles[0]);
    sv2.write(arm6dof.angles[1]);
    sv3.write(arm6dof.angles[2]);
    grabsv.write(arm6dof.grab_angle);
    delay(150); 

  }
  
}

Robot_arm::Robot_arm()
{
  this->vtc_idx=2;
  this->hrz_idx=6;
  this->angles[0] = 0;
  this->angles[1] = 0;
  this->angles[2] = 0;
  this->grab_angle = 180;
}
bool Robot_arm::vtcUP()
{
  if(this->vtc_idx+1<=vtc_maxIdx) {  
    this->vtc_idx++;
    return true;
  }
  return false;
}
bool Robot_arm::vtcDOWN()
{
  if(this->vtc_idx-1 >= 0) {
    this->vtc_idx--;
    return true;
  }
  return false;
}
bool Robot_arm::hrzBACK()
{
  if(this->hrz_idx+1<=hrz_maxIdx) {
    this->hrz_idx++;
    return true;
  }
  return false;
}
bool Robot_arm::hrzFORWARD()
{
  if(this->hrz_idx-1 >= 0) {
    this->hrz_idx--;
    return true;
  }
  return false;
}

bool Robot_arm::angleValidate()
{
  for(int i = 0;i<3;i++){
    if(vtc_sv[i][this->vtc_idx]+hrz_sv[i][this->hrz_idx] > 180 || vtc_sv[i][this->vtc_idx]+hrz_sv[i][this->hrz_idx] <0)
    {return false;}  
  }
  return true;
}
void Robot_arm::angleCalculator(char cmd[])
{
  bool possible=false;
  if(cmd[0] == '0')
  {
    if     (cmd[1] == CMDs[0][1]) possible=true;
    else if(cmd[1] == CMDs[1][1]) possible=vtcUP();
    else if(cmd[1] == CMDs[2][1]) possible=vtcDOWN();
    else if(cmd[1] == CMDs[3][1]) {
      if(this->grab_angle+10 >= Grab_maxangle) { return; }
      else if(this->grab_angle < Grab_maxangle) { this->grab_angle+=10; }
      return;
    }
    else if(cmd[1] == CMDs[4][1]) {
      if(this->grab_angle-10 <= Drop_maxangle) { return; }
      else if(this->grab_angle > Drop_maxangle) { this->grab_angle-=10; }
      return;
    }
  }
  else if(cmd[0] == '1')
  {
    if(cmd[1] == CMDs[5][1])      possible=hrzFORWARD();
    else if(cmd[1] == CMDs[6][1]) possible=hrzBACK();
  }
  if(!possible){
    if(cmd[1] == CMDs[1][1])      this->vtc_idx--;
    else if(cmd[1] == CMDs[2][1]) this->vtc_idx++;
    else if(cmd[1] == CMDs[5][1]) this->hrz_idx++;
    else if(cmd[1] == CMDs[6][1]) this->hrz_idx--;
    return;
  }
  if(!angleValidate()) {
    if(cmd[1] == CMDs[1][1])      this->vtc_idx--;
    else if(cmd[1] == CMDs[2][1]) this->vtc_idx++;
    else if(cmd[1] == CMDs[5][1]) this->hrz_idx++;
    else if(cmd[1] == CMDs[6][1]) this->hrz_idx--;
    return;
  }
  this->angles[0] = vtc_sv[0][this->vtc_idx]+hrz_sv[0][this->hrz_idx];
  this->angles[1] = vtc_sv[1][this->vtc_idx]+hrz_sv[1][this->hrz_idx];
  this->angles[2] = vtc_sv[2][this->vtc_idx]+hrz_sv[2][this->hrz_idx];
}
