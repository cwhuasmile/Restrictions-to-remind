from machine import Pin
import utime
import DS1302

# p2 = Pin(2,Pin.OUT)

# for i in range(30):
#     if i%2 == 0:
#         p2.value(0)
#     else:
#         p2.value(1)
#     utime.sleep(0.1)

#蜂鸣器循环发声
def push(num):
    for i in range(num):
        p3.on()
        utime.sleep(0.3)
        p3.off()
        utime.sleep(0.2)

#播报完成后快速滴滴两声
def didi():
    utime.sleep(1)
    for i in range(2):
        p3.on()
        utime.sleep(0.1)
        p3.off()
        utime.sleep(0.1)

#播报当前星期、时间
def m_and_t():
    date_time = ds.DateTime()
    #按键播报当前周几
    push(date_time[3])
    utime.sleep(2)
    #播报小时，如果是夜里0点，则播放一个长声
    if date_time[4] == 0:
        p3.on()
        utime.sleep(1)
        p3.off()
        utime.sleep(1)
    else:
        push(date_time[4])
    utime.sleep(2)
    #播报分钟,小于10直接播报，大于10先播报十位再播报个位
    if date_time[5] <= 10:
        push(date_time[5])
    else:
        m = str(date_time[5])
        push(int(m[0]))
        utime.sleep(2)
        #个位是0播报长声
        if m[1] == "0":
            p3.on()
            utime.sleep(1)
            p3.off()
            utime.sleep(1)
        else:
            push(int(m[1]))

#读取规则文件内容
def read_rule():
    f = open("rule.txt","r")
    i = int(f.read())
    f.close()
    return i

#写入规则到文件
def update_rule():
    i = read_rule()
    if i >= 7:
        i = 0
    f = open("rule.txt","w")
    f.write(str(i+1))
    f.close()

#播报当前限行规则
def rule():
    i = read_rule()
    push(i)

p3 = Pin(5,Pin.OUT) #蜂鸣器
p3.off()
p4 = Pin(4,mode=Pin.IN,pull=Pin.PULL_UP)    #按键
p2 = Pin(2,Pin.OUT) #LED

ds = DS1302.DS1302(Pin(14),Pin(12),Pin(13))
utime.sleep(0.5)
date_time = ds.DateTime()
utime.sleep(0.5)

#判断限行
def xianxing():
    i = read_rule()
    if i >= 6:
        #对于单双号限行,号牌和日期不同则触发警报
        if i%2 != date_time[2]%2:
            p3.on()
            #按键清楚警报
            while 1:
                if p4.value() == 0:
                    p3.off()
                    #p4.off()
                    didi()
                    break
                p2.value(not p2.value())
                utime.sleep(0.1)
    else:
        #对于星期限行
        if i == date_time[3]:
            p3.on()
            #按键清楚警报
            while 1:
                if p4.value() == 0:
                    p3.off()
                    #p4.off()
                    didi()
                    break
                p2.value(not p2.value())
                utime.sleep(0.1)
    return

#诊断时间是否清零重置
while 1:
    if date_time[0] < 2021:
        p3.on()
        utime.sleep(0.5)
        p3.off()
        utime.sleep(0.2)
        p3.on()
        utime.sleep(1)
        p3.off()
        utime.sleep(0.2)
    else:
        break

#限行判断
xianxing()

#点亮待机指示灯
p2.off()
#短按播报星期和时间，2秒内松开播报限行规则，6秒后松开更新限行规则
#限行规则：1-5为周一至周五，6为双号禁行，7为单号禁行
while 1:
    utime.sleep(0.1)
    if p4.value() == 0:
        flag = utime.ticks_ms()
        while 1:
            utime.sleep(0.1)
            if p4.value() == 1:
                if (utime.ticks_ms() - flag)/1000 <= 2:
                    m_and_t()
                    didi()
                elif 2 < (utime.ticks_ms() - flag)/1000 < 6:
                    rule()
                    didi()
                elif (utime.ticks_ms() - flag)/1000 >= 6:
                    update_rule()
                    rule()
                    didi()
                else:
                    p3.on()
                    utime.sleep(2)
                    p3.off()
                break