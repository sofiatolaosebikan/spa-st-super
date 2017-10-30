import matplotlib.pyplot as plt
import csv


# ================================ Only keep track of instances that admits a super-stable matching ================================
def get_soluble_instances(filename):
    is_super_stable = []
    with open(filename, 'r') as read_csvfile:
        I = list(csv.reader(read_csvfile, delimiter=' '))
        for row in I:
            if row[2] == 'Y':
                is_super_stable.append(int(row[3]))
    return is_super_stable
#  ---------------------------------------------------------------------------------------------------------------------------------
#  =================================================================================================================================

# ================================ Only keep track of instances that admits a super-stable matching ================================
def get_soluble_instances_with_time(filename):
    is_super_stable = []
    time_taken = 0
    with open(filename, 'r') as read_csvfile:
        I = list(csv.reader(read_csvfile, delimiter=' '))
        for row in I:
            if row[2] == 'Y':
                is_super_stable.append(int(row[3]))
                time_taken += float(row[1])  # we only care about the average time taken for soluble instances
    return is_super_stable, time_taken


# =================================== The proportion of these instances -- 1000 instances in all ===================================
def proportion(value):
    return round((value/1000)*100, 2)
#  ---------------------------------------------------------------------------------------------------------------------------------
#  =================================================================================================================================

#  with respect to an instance size
def get_all_proportion(size):
    all_proportion = []
    for i in range(0,11):
        temp = []
        for j in range(0, 11):
            filename = '../experiments/2/' + str(i) + '_' + str(j) + '/' + size +'/output3.csv'
            # experiments/2/0_0/100/output.csv
            is_super_stable = get_soluble_instances(filename)
            p = proportion(len(is_super_stable))
            temp.append(p)
        all_proportion.append(temp)
    return all_proportion


def write_statistics():
    for i in range(0,11):
        for j in range(0, 11):
            filename = '../experiments/2/' + str(i) + '_' + str(j) + '/'
            write_to = filename + 'analysis_new.csv'
            with open(write_to, 'w', newline='') as write_csvfile:
                O = csv.writer(write_csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                O.writerow(['n1', 'proportion', 'time_taken'])
                for k in range(100, 1100, 100):
                    write_from = filename + str(k) + '/output3.csv'
                    is_super_stable, time_taken = get_soluble_instances_with_time(write_from)
                    p = proportion(len(is_super_stable))
                    t = 0
                    if time_taken != 0:
                        t = time_taken/len(is_super_stable)
                    O.writerow([k, p, t])
                write_csvfile.close()
        
        
def subplot(size):
    prop = get_all_proportion(size)
    x = [0.005*j for j in range(0,11)]  # lecturer on the x-axis
    for i in range(0, 11):
        y = [0.005*i for _ in range(0,11)]  # student on the y-axis    
        plt.scatter(x, y, c=prop[i], marker='s', s=100, linewidths=0,  edgecolors=None, cmap='gist_heat_r', vmin=0, vmax=100)
        plt.ylim(-0.005, 0.055)
        plt.xlim(-0.005, 0.055)

write_statistics()

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
plt.savefig('../experiments/2/varying_tie_density_new.png')
