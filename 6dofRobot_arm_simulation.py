import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import math
import numpy as np

# zaxis rotate motor를 제외한 sv1, sv2, sv3의 각도 값 저장
Org_sv1 = [170, 160, 150, 145, 140, 130, 120, 110, 100, 90, 80, 70, 60, 50, 40, 40, 30] 
Org_sv2 = [180, 175, 170, 160, 150, 135, 120, 110, 100, 90, 80, 70, 60, 50, 35, 25, 20] 
Org_sv3=  [180, 180, 175, 175, 175, 175, 180, 175, 175, 175, 170, 170, 165, 160, 160, 160, 155]
Hrz_sv1 = [-60,	-50, -40, -30, -20, -10, 0, 10, 20, 30 , 40, 50, 60]
Hrz_sv2 = [0, 0, 0, 0, 0, 0, 0,	10, 20, 30,	40, 50, 60]
Hrz_sv3 = [-60,	-50, -40, -30, -20, -10, 0, 0, 0, 0,0, 0, 0]


global ch_sv, d
global x_idx, y_idx
x_idx = 6
y_idx = 7
ch_sv = []
d=[8.4, 7.7, 13]


#figure = plt.figure()

def robot_test():  #하나씩 plot
    global y_idx, x_idx
    print(y_idx, " ", "Sv1 ",Org_sv1[y_idx]," Sv2 ", Org_sv2[y_idx], " Sv3 ", Org_sv3[y_idx])
    print(x_idx, " ", "Sv1 ",Hrz_sv1[x_idx]," Sv2 ", Hrz_sv2[x_idx], " Sv3 ", Hrz_sv3[x_idx])
    angle1 = abs(Org_sv1[y_idx]+Hrz_sv1[x_idx]-180)
    angle2 = angle1 + Org_sv2[y_idx]+Hrz_sv2[x_idx]-90
    angle3 = angle2 + Org_sv3[y_idx]+Hrz_sv3[x_idx]-90
    if angle1 > 180 or angle1 <0 or angle2 > 180 or angle2 <0 or angle3 > 180 or angle3 <0: return
    print(angle1 , " ", angle2, " ",  angle3 )

    plt.cla()
    x1 = d[0]*math.cos(angle1*math.pi/180)
    x2 = x1+d[1]*math.cos(angle2*math.pi/180)
    x3 = x2+d[2]*math.cos(angle3*math.pi/180)
    y1 = d[0]*math.sin(angle1*math.pi/180)
    y2 = y1+d[1]*math.sin(angle2*math.pi/180)
    y3 = y2+d[2]*math.sin(angle3*math.pi/180)
    
    plt.xlim([-35,35])
    plt.ylim([0,30])
    plt.plot([0, x1, x2, x3], [0, y1, y2, y3])
    plt.pause(0.6)
    
def over_under_chk():
    angle1 = abs(Org_sv1[y_idx]+Hrz_sv1[x_idx]-180)
    angle2 = angle1 + Org_sv2[y_idx]+Hrz_sv2[x_idx]-90
    angle3 = angle2 + Org_sv3[y_idx]+Hrz_sv3[x_idx]-90
    if angle1 > 180 or angle1 <0 or angle2 > 180 or angle2 <0 or angle3 > 180 or angle3 <0: return False
    return True
def robot_command(cmd):
    global y_idx, x_idx
    if cmd == 'w' :
        if y_idx+1 <= 16 :
            y_idx=y_idx+1
            if(not over_under_chk()) : y_idx = y_idx -1
    elif cmd == 's':
        if y_idx-1 >= 0:
            y_idx = y_idx -1
            if(not over_under_chk()) : y_idx = y_idx +1
    elif cmd == 'a':
        if x_idx - 1 >= 0:
            x_idx = x_idx -1
            if(not over_under_chk()) : x_idx = x_idx +1 
    elif cmd == 'd':
        if x_idx + 1 <= 12:
            x_idx = x_idx + 1
            if(not over_under_chk()) : x_idx = x_idx -1
            
def robot_test2(row, col ,n): #all plot
    
    print(n,"row",row, " ", "Sv1 ",Org_sv1[row]," Sv2 ", Org_sv2[row], " Sv3 ", Org_sv3[row])
    print(n,"col",col, " ", "Sv1 ",Hrz_sv1[col]," Sv2 ", Hrz_sv2[col], " Sv3 ", Hrz_sv3[col])
    if (Org_sv1[row]+Hrz_sv1[col] > 180 or Org_sv1[row]+Hrz_sv1[col] <0 
        or Org_sv2[row]+Hrz_sv2[col] > 180 or Org_sv2[row]+Hrz_sv2[col] <0 
        or Org_sv3[row]+Hrz_sv3[col] > 180 or Org_sv3[row]+Hrz_sv3[col] <0): 
        plt.xlim([-35,35])
        plt.ylim([0,30])
        plt.subplot(17,13, n) # i max , j max , nums
        plt.plot(0, 0)
        return
    angle1 = abs(Org_sv1[row]+Hrz_sv1[col]-180)
    angle2 =Org_sv2[row]+Hrz_sv2[col]-90
    angle3 = Org_sv3[row]+Hrz_sv3[col]-90
    
    print(angle1 , " ", angle2, " ",  angle3 )

    x1 = d[0]*math.cos(angle1*math.pi/180)
    x2 = x1+d[1]*math.cos((angle1+angle2)*math.pi/180)
    x3 = x2+d[2]*math.cos((angle1+angle2+angle3)*math.pi/180)
    y1 = d[0]*math.sin(angle1*math.pi/180)
    y2 = y1+d[1]*math.sin((angle1+angle2)*math.pi/180)
    y3 = y2+d[2]*math.sin((angle1+angle2+angle3)*math.pi/180)
    
    plt.xlim([-35,35])
    plt.ylim([0,30])
    plt.subplot(17,13, n) # i max , j max , nums
    plt.plot([0, x1, x2, x3], [0, y1, y2, y3])
    
    

# while True: controll func
#    c = input(":")
#    if c != 's' and c != 'w' and c != 'a' and c != 'd': break
#    else :
#       robot_command(c)
#       robot_test()

plt.xlim([-35,35])
plt.ylim([0,30])
nums = 0
for i in range(0,17,1):
    for j in range(0,13,1):
        nums = nums + 1
        robot_test2(i,j,nums)
plt.xlabel("Front<------->Back")
plt.ylabel("Up<------->Down")
plt.show()    
