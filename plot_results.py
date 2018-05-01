import json
import matplotlib.pyplot as plt


with open("results.json", "r") as input_file:
    results = json.load(input_file)

for term, result in results.items():
    plt.plot(result, label=term)

plt.ylabel("latency(s)")
leg = plt.legend(loc='best', ncol=2, mode="expand", shadow=True, fancybox=True)
leg.get_frame().set_alpha(0.5)
plt.show()