#Functions for calculating the energy consumption per fix
import xlwt
def calculate_energy_consumption():
    fix_period=[1,10,60,1800,3600,14399,14400,15551700,15552000]
    t= [60,3600,86400,2592000,31536000]
    supply = 3.3
    i_sleep, T_sleep, i_wake,T_wake,i_acq, T_acq, i_track, T_track = 3.2*1E-3,0,101*1E-3,5,80*1E-3,0,72*1E-3,1
    v_sleep = supply - i_sleep
    v_wake  = supply - i_wake
    v_acq   = supply - i_acq
    v_track = supply - i_track

    P_sleep = v_sleep*i_sleep
    P_wake  = v_wake*i_wake
    P_acq   = v_acq*i_acq
    P_track = v_track*i_track
    
    print(P_sleep)
    print(P_wake)
    print(P_acq)
    print(P_track)

    columns,rows= len(fix_period),len(t)
    Energy_consumption = [[0 for x in range(columns)] for y in range(rows)]
    print(Energy_consumption)


    i_iterator= 0
    j_iterator= 0

    for i in t:
        for j in fix_period:
            if(j_iterator>columns-1):
                j_iterator = 0   
            if((j<2) or (j>i) ):
                print("i=",i)
                print("j=",j)
                if((j<5) and (j<i)):
                    Energy_consumption[i_iterator][j_iterator] = P_track*i
                else:
                    print(i_iterator,j_iterator)
                    Energy_consumption[i_iterator][j_iterator]= -1
                print("Energy Consumption: ", Energy_consumption[i_iterator][j_iterator])
                j_iterator = j_iterator +1
                continue
            elif(j<14400):
                T_acq   = 1
            elif (j>14399 and j<15552000):
                T_acq   = 30      
            elif(j == 15552000):
                T_acq   = 35
            print("i",i)
            print("j=",j)
            print("T_acq=",T_acq)
            print("T_wake=",T_wake)
            print("T_track= ", T_track)
            T_sleep     = j - T_wake - T_acq - T_track 
            print("T_sleep=", T_sleep)
            Energy_consumption[i_iterator][j_iterator] = (P_sleep*T_sleep + P_wake*T_wake + P_acq*T_acq + P_track*T_track)*i/j
            print("E_Init: ",(P_wake*T_wake)*i/j)
            print("E_acq: ",(P_acq*T_acq)*i/j)
            print("E_track: ",(P_track*T_track)*i/j)
            print("E_sleep: ",P_sleep*T_sleep)
            #print("plot of temp",P_sleep*T_sleep + P_wake*T_wake + P_acq*T_acq + P_track*T_track )
            print("Energy_consumption:",Energy_consumption[i_iterator][j_iterator])
            j_iterator = j_iterator +1

        i_iterator = i_iterator +1
        if(i_iterator>rows-1):
            i_iterator = 0  
    print (Energy_consumption)
    book = xlwt.Workbook()
    sh = book.add_sheet("Sheet 1")
    style = xlwt.XFStyle()
    # font
    font = xlwt.Font()
    font.bold = True
    style.font = font
    
    for i in range(columns):
        for j in range(rows):
            sh.write(i,j,Energy_consumption[j][i])
    book.save('ny.xls')

    optimal   =   Energy_consumption[4][5]
    temp     =   Energy_consumption[4][6]
    fix_o = 14400

    while(optimal<temp):  
        T_sleep = fix_o - T_wake - 30 - T_track
        optimal = (P_sleep*T_sleep + P_wake*T_wake + P_acq*30 + P_track*T_track)*t[4]/fix_o
        fix_o = fix_o + 1
    print("fix_o",fix_o)

        
calculate_energy_consumption()