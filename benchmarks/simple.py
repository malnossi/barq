import timeit
import matplotlib.pyplot as plt
import numpy as np


from barq import *
from pydantic import BaseModel, Field

# Define the objects and serializers
obj = dict(a="a", b=1, c=2.3, d=False)

class BarqSerializer(Serializer):
    a = StrField()
    b = IntField()
    c = FloatField()
    e = BoolField(attr="d")

class PydanticSerializer(BaseModel):
    a: str
    b: int
    c: float
    d: bool = Field(..., serialization_alias='e')

# Define test functions
def test_barq(n):
    for _ in range(n):
        BarqSerializer(obj).data

def test_pydantic(n):
    for _ in range(n):
        PydanticSerializer(**obj).model_dump()

n_values = [100, 1000, 10000, 100000, 1000000]
barq_times = []
pydantic_times = []

for n in n_values:
    barq_time = timeit.timeit(lambda: test_barq(n), number=1)
    pydantic_time = timeit.timeit(lambda: test_pydantic(n), number=1)
    barq_times.append(barq_time)
    pydantic_times.append(pydantic_time)

# Plotting the results as a bar chart
bar_width = 0.35
indices = np.arange(len(n_values))

plt.figure(figsize=(12, 6))
plt.bar(indices - bar_width/2, barq_times, bar_width, label="Barq Serializer")
plt.bar(indices + bar_width/2, pydantic_times, bar_width, label="Pydantic Serializer")
plt.xlabel("Number of Iterations (n)")
plt.ylabel("Execution Time (seconds)")
plt.title("Benchmarking Barq vs Pydantic Serialization")
plt.yscale("linear")
plt.xticks(indices, n_values)
plt.legend()

# Create directory and save the plot
output_path = './benchmarks/simple.png'
plt.savefig(output_path)
