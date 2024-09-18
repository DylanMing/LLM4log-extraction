import matplotlib.pyplot as plt
import numpy as np

# IP precision by chunk size
# x: chunk size
labels = ["128k-extraction","Regular expresion"]

url_recall = [0.593,0.971]
url_recall_correct = [0.963-0.593,0]



x = np.arange(len(labels)) # the label locations
width = 0.4  # the width of the bars

fig, ax = plt.subplots()


rects1 = ax.bar(x , url_recall, width, label='url recall')
rects2 = ax.bar(x , url_recall_correct, width, url_recall, label='Correction')


# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('url_recall')
ax.set_xlabel('extraction method')
ax.set_title('url_recall by extraction method')
ax.set_xticks(x,labels)
ax.legend(loc = "lower right")



ax.bar_label(rects1, padding=-15)
ax.bar_label(rects2, padding=4)



fig.tight_layout()
plt.ylim(ymin=0.7,ymax=1)
plt.show()