#part 2
B = getRotationQuaternion('B') 
BRef = getRotationQuaternion('BRef')
diffQ = B * BRef.inverse()
print(diffQ)

step = 360/20
for i in range(20+1):
    mc.setAttr('B.rx', 0)
    mc.setAttr('B.ry', 0)
    mc.setAttr('B.rz', 0)
    mc.setAttr('x.tx', 0)
    mc.setAttr('y.ty', 0)
    mc.setAttr('z.tz', 0)
    
    count = step * float(i)
    
    if (i >= 10):
        count = 180 - count
            
    mc.setAttr('B.rx', count)
    #mc.setAttr('B.ry', count)
    
    B = getRotationQuaternion('B')
    BRef = getRotationQuaternion('BRef')
    diffQ = B * BRef.inverse()
    
    if(diffQ.w < 0.0):
        diffQ.negateIt()
        
    abs_x = abs(diffQ.x)
    abs_y = abs(diffQ.y)
    abs_z = abs(diffQ.z)
    
    if(diffQ.x>0.0):
        mc.setAttr('x.tx', abs_x)
    
    if(diffQ.x<0.0):
        mc.setAttr('x.tx', abs_x * -2)
    if(diffQ.y>0.0):
        mc.setAttr('y.ty', abs_y)
    
    if(diffQ.y<0.0):
        mc.setAttr('y.ty', abs_y * -2)
        
    if (diffQ.z > 0.0):
        mc.setAttr('z.tz', abs_z)
            
    if (diffQ.z < 0.0):
        mc.setAttr('z.tz', abs_z * -2)
        
    result_x = pow(abs_x, 1.5)
    
    print('B = [{0}, {1}, {2}, {3}, {4}, {5}]'.format(count, 
                                        round(diffQ.x, 2), 
                                        round(diffQ.y, 2),
                                        round(diffQ.z, 2),
                                        round(diffQ.w, 2),
                                        result_x))
    mc.refresh()
    time.sleep(0.25)                                        
    
    
    
    
    


 
   