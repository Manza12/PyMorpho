from pyMorpho import np
from pyMorpho.abstraction import Image, StructuringElement, erosion, dilation
from pyMorpho.concretization import Line, Circle, Z, T, RhythmicLattice

rhythmic_lattice = RhythmicLattice()
chroma_roll = Image(rhythmic_lattice.array_to_lattice(np.flip(np.array([
    [0, 0, 0, 0, 2, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [2, 1, 1, 1, 2, 1, 2, 1],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 2, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 2, 1],
    [2, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 2, 1, 2, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [2, 1, 0, 0, 0, 0, 2, 1],
]), axis=0)), Circle(12) * Line(8), rhythmic_lattice)

major_chord = StructuringElement(rhythmic_lattice.array_to_lattice(np.flip(np.array([
    [0, 0],
    [0, 0],
    [0, 0],
    [0, 0],
    [2, 1],
    [0, 0],
    [0, 0],
    [2, 1],
    [0, 0],
    [0, 0],
    [0, 0],
    [2, 1],
]), axis=0)), T(12) * Z(2), rhythmic_lattice)

activations = erosion(chroma_roll, major_chord)

for i in range(12):
    for j in range(8):
        print(np.flip(activations.array, 0)[i, j], end=' ')
    print()

print()

opening = dilation(activations, major_chord)

for i in range(12):
    for j in range(8):
        print(np.flip(opening.array, 0)[i, j], end=' ')
    print()
