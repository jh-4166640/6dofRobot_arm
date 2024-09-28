#include <Servo.h>
#include <Wire.h>
Servo test_servo1;
Servo test_servo2;
Servo test_servo3;
/**************************/
/* Ian J. Choi
 * 2024-09-29 12:31
 * 6-dof Robot_arm movement code
 */
/******바꿔도 되는 값********/
#define vtc_maxIdx 16
#define hrz_maxIdx 12
/*      세팅해서 사용     */
#define UP      0x00 //flex센서에서 오는 값
#define DOWN    0x00 //flex센서에서 오는 값
#define FORWARD 0x00 //flex센서에서 오는 값
#define BACK    0x00 //flex센서에서 오는 값
/*************************/
typedef class Robot_arm{
private:
  int vtc_idx = 7;
  int hrz_idx = 6;
  const int vtc_sv[3][vtc_maxIdx+1]= {
    {170, 160, 150, 145, 140, 130, 120, 110, 100, 90, 80, 70, 60, 50, 40, 40, 30},         //로봇의 위 아래 움직임 servo1의 값 //0~vtc_maxIdx
    {180, 175, 170, 160, 150, 135, 120, 110, 100, 90, 80, 70, 60, 50, 35, 25, 20},         //로봇의 위 아래 움직임 servo2의 값 //0~vtc_maxIdx
    {180, 180, 175, 175, 175, 175, 180, 175, 175, 175, 170, 170, 165, 160, 160, 160, 155}  //로봇의 위 아래 움직임 servo3의 값 //0~vtc_maxIdx
  };
  const int hrz_sv[3][hrz_maxIdx+1] = {
    {-60, -50, -40, -30, -20, -10, 0, 10, 20, 30, 40, 50, 60},                             //로봇의 앞, 뒤 움직임 servo1의 값 //0~hrz_maxIdx
    {0, 0, 0, 0, 0, 0, 0, 10, 20, 30, 40, 50, 60},                                         //로봇의 앞, 뒤 움직임 servo2의 값 //0~hrz_maxIdx
    {-60, -50, -40, -30, -20, -10, 0, 0, 0, 0, 0, 0, 0}                                   //로봇의 앞, 뒤 움직임 servo3의 값 //0~hrz_maxIdx
  };
  bool vtcUP()
  {
    if(vtc_idx+1<=vtc_maxIdx) {
      this->vtc_idx++;
      return true;
    }
    return false;
  }
  bool vtcDOWN()
  {
    if(vtc_idx-1 >= 0) {
      this->vtc_idx--;
      return true;
    }
    return false;
  }
  bool hrzBACK()
  {
    if(hrz_idx+1<=hrz_maxIdx) {
      this->hrz_idx++;
      return true;
    }
    return false;
  }
  bool hrzFORWARD()
  {
    if(hrz_idx-1 >= 0) {
      this->hrz_idx--;
      return true;
    }
    return false;
  }
  bool angleValidate()
  {
    for(int i = 0;i<3;i++){
      if(vtc_sv[i][vtc_idx]+hrz_sv[i][hrz_idx] > 180 || vtc_sv[i][vtc_idx]+hrz_sv[i][hrz_idx] <0)
      {return false;}  
    }
    return true;
  }
public:
  int angle[3] = {0,};
  void angleCalculator(uint8_t cmd)
  {
    bool possible=false;
    if     (cmd&UP)      possible=vtcUP();
    else if(cmd&DOWN)    possible=vtcDOWN();
    else if(cmd&FORWARD) possible=hrzFORWARD();
    else if(cmd&BACK)    possible=hrzBACK();
    
    if(!possible && !angleValidate()) return;
    this->angle[0] = abs(vtc_sv[0][vtc_idx]+hrz_sv[0][hrz_idx]-180);
    this->angle[1] = vtc_sv[1][vtc_idx]+hrz_sv[1][hrz_idx]-90;
    this->angle[2] = vtc_sv[2][vtc_idx]+hrz_sv[2][hrz_idx]-90;
  }
}Robot_arm;
void setup(){
  Serial.begin(9600);
  
}
void loop() {
  /* 사용 예시 */
  /* 통신 코드 맨위에 Robot_arm class와 
   *  #define 값 세팅해서 사용하면돼
   */
  uint8_t command;
  command = Serial.read();
  Robot_arm arm;
  arm.angleCalculator(command);
  test_servo1.write(arm.angle[0]);
  test_servo2.write(arm.angle[1]);
  test_servo3.write(arm.angle[2]);
}
