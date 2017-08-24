import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import AxesGrid
import csv


# ================================ Only keep track of instances that admits a super-stable matching ================================
def get_soluble_instances(filename):
    is_super_stable = []
    with open(filename, 'r') as read_csvfile:
        I = list(csv.reader(read_csvfile, delimiter=' '))
        for row in I:
            if row[1] == 'Y':
                is_super_stable.append(int(row[2]))
    return is_super_stable
#  ---------------------------------------------------------------------------------------------------------------------------------
#  =================================================================================================================================


# =================================== The proportion of these instances -- 1000 instances in all ===================================
def proportion(value):
    return round((value/1000)*100, 2)
#  ---------------------------------------------------------------------------------------------------------------------------------
#  =================================================================================================================================
    
def get_all_proportion(size):
    all_proportion = []
    for i in range(0,7):
        temp = []
        for j in range(0, 11):
            filename = 'experiments/2/' + str(i) + '_' + str(j) +  '/' + size +'/output.csv'
            # experiments/2/0_0/100/output.csv
            is_super_stable = get_soluble_instances(filename)
            p = proportion(len(is_super_stable))
            temp.append(p)
        all_proportion.append(temp)
    return all_proportion
    
def subplot(size):
    prop = get_all_proportion(size)
    #print(prop)
    #plt.figure()
    x = [0.005*j for j in range(0,11)]  # lecturer on the x-axis
    for i in range(0, 7):
        y = [0.005*i for _ in range(0,11)]  # student on the y-axis    
        plt.scatter(x, y, c=prop[i], marker='s', s=100, linewidths=0,  edgecolors=None, cmap='gist_heat_r', vmin=0, vmax=100)
        plt.ylim(-0.005)
        plt.xlim(-0.005, 0.055)
        
    
    
    

    plt.suptitle('Proportion of instances that admits super-stable matching as tie density varies', fontsize=15)



plt.figure(figsize=(15, 15))
ax1 = plt.subplot(331)
ax1.title.set_text('instance size 100')
subplot('100')
plt.ylabel('tie density for students')

plt.setp(ax1.get_xticklabels(), visible=False)

ax2 = plt.subplot(332, sharey = ax1)
ax2.title.set_text('instance size 200')
subplot('200')
plt.setp(ax2.get_xticklabels(), visible=False)
plt.setp(ax2.get_yticklabels(), visible=False)


ax3 = plt.subplot(333, sharey = ax1)
ax3.title.set_text('instance size 300')
subplot('300')
plt.setp(ax3.get_xticklabels(), visible=False)
plt.setp(ax3.get_yticklabels(), visible=False)


ax4 = plt.subplot(334, sharey = ax1)
ax4.title.set_text('instance size 400')
subplot('400')
plt.ylabel('tie density for students')
plt.setp(ax4.get_xticklabels(), visible=False)

ax5 = plt.subplot(335, sharey = ax1)
ax5.title.set_text('instance size 500')
subplot('500')
plt.setp(ax5.get_xticklabels(), visible=False)
plt.setp(ax5.get_yticklabels(), visible=False)


ax6 = plt.subplot(336, sharey=ax1)
ax6.title.set_text('instance size 600')
subplot('600')
plt.setp(ax6.get_xticklabels(), visible=False)
plt.setp(ax6.get_yticklabels(), visible=False)

ax7 = plt.subplot(337, sharey = ax1)
ax7.title.set_text('instance size 700')
subplot('700')
plt.ylabel('tie density for students')
plt.xlabel('tie density for lecturers')

ax8 = plt.subplot(338, sharey = ax1, sharex=ax7)
ax8.title.set_text('instance size 800')
subplot('800')
plt.setp(ax8.get_yticklabels(), visible=False)
plt.xlabel('tie density for lecturers')

ax9 = plt.subplot(339, sharey = ax1, sharex=ax7)
ax9.title.set_text('instance size 900')
subplot('900')
plt.setp(ax9.get_yticklabels(), visible=False)
plt.xlabel('tie density for lecturers')



plt.subplots_adjust(bottom=0.1, right=0.82, top=0.9)
cax = plt.axes([0.85, 0.1, 0.03, 0.8])
plt.colorbar(cax=cax)
plt.show()


    

#plt.figure(figsize=(5, 13))
#ax1 = plt.subplot(521)
#subplot('100')
#plt.ylim((-0.005))
#plt.ylabel('tie density for students')
#plt.setp(ax1.get_xticklabels(), visible=False)
#
#ax2 = plt.subplot(522)
#subplot('200')
#plt.setp(ax2.get_xticklabels(), visible=False)
#plt.setp(ax2.get_yticklabels(), visible=False)
#
#ax3 = plt.subplot(523, sharey=ax1)
#subplot('300')
#plt.setp(ax3.get_xticklabels(), visible=False)
#
#ax4 = plt.subplot(524)
#subplot('400')
#plt.setp(ax4.get_xticklabels(), visible=False)
#plt.setp(ax4.get_yticklabels(), visible=False)
#
#ax5 = plt.subplot(525, sharey=ax1)
#subplot('500')
#plt.setp(ax5.get_xticklabels(), visible=False)
#
#ax6 = plt.subplot(526)
#subplot('600')
#plt.setp(ax6.get_xticklabels(), visible=False)
#plt.setp(ax6.get_yticklabels(), visible=False)
#
#ax7 = plt.subplot(527, sharey=ax1)
#subplot('700')
#plt.setp(ax7.get_xticklabels(), visible=False)
#
#ax8 = plt.subplot(528, sharex=ax6)
#subplot('800')
#plt.setp(ax8.get_xticklabels(), visible=False)
#plt.setp(ax8.get_yticklabels(), visible=False)
#
#ax9 = plt.subplot(529, sharey=ax1)
#subplot('900')
#plt.xlim((-0.005, 0.055))
#plt.xlabel('tie density for lecturers')
#
#ax10 = plt.subplot(5,2,10, sharex=ax9)
#subplot('1000')
#plt.setp(ax10.get_yticklabels(), visible=False)
#
##plt.colorbar()
#plt.show()














#plt.figure(figsize=(20, 8))
#ax1 = plt.subplot(251)
#ax1.title.set_text('instance size 100')
#subplot('100')
#plt.ylabel('tie density for students')
#
#plt.setp(ax1.get_xticklabels(), visible=False)
#
#ax2 = plt.subplot(252, sharey = ax1)
#ax2.title.set_text('instance size 200')
#subplot('200')
#plt.setp(ax2.get_xticklabels(), visible=False)
#plt.setp(ax2.get_yticklabels(), visible=False)
#
#
#ax3 = plt.subplot(253, sharey = ax1)
#ax3.title.set_text('instance size 300')
#subplot('300')
#plt.setp(ax3.get_xticklabels(), visible=False)
#plt.setp(ax3.get_yticklabels(), visible=False)
#
#
#ax4 = plt.subplot(254, sharey = ax1)
#ax4.title.set_text('instance size 400')
#subplot('400')
#plt.setp(ax4.get_xticklabels(), visible=False)
#plt.setp(ax4.get_yticklabels(), visible=False)
#
#
#ax5 = plt.subplot(255, sharey = ax1)
#ax5.title.set_text('instance size 500')
#subplot('500')
#plt.setp(ax5.get_xticklabels(), visible=False)
#plt.setp(ax5.get_yticklabels(), visible=False)
#
#
#ax6 = plt.subplot(256, sharey=ax1)
#ax6.title.set_text('instance size 600')
#subplot('600')
#plt.ylabel('tie density for students')
#plt.xlabel('tie density for lecturers')
#
#ax7 = plt.subplot(257, sharey = ax1, sharex=ax6)
#ax7.title.set_text('instance size 700')
#subplot('700')
#plt.setp(ax7.get_yticklabels(), visible=False)
#plt.xlabel('tie density for lecturers')
#
#ax8 = plt.subplot(258, sharey = ax1, sharex=ax6)
#ax8.title.set_text('instance size 800')
#subplot('800')
#plt.setp(ax8.get_yticklabels(), visible=False)
#plt.xlabel('tie density for lecturers')
#
#ax9 = plt.subplot(259, sharey = ax1, sharex=ax6)
#ax9.title.set_text('instance size 900')
#subplot('900')
#plt.setp(ax9.get_yticklabels(), visible=False)
#plt.xlabel('tie density for lecturers')
#
#ax10 = plt.subplot(2,5,10, sharey = ax1, sharex=ax6)
#ax10.title.set_text('instance size 1000')
#subplot('1000')
#plt.setp(ax10.get_yticklabels(), visible=False)
#plt.xlabel('tie density for lecturers')
#
#
#
#
#
#
#plt.subplots_adjust(bottom=0.1, right=0.82, top=0.9)
#cax = plt.axes([0.85, 0.1, 0.03, 0.8])
#plt.colorbar(cax=cax)
#plt.show()