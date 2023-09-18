from pyMorpho import np
from pyMorpho.abstraction import erosion, dilation
from pyMorpho.concretization import RhythmicLattice, ChromaRoll, ChromaRollPattern

chroma_roll = ChromaRoll(RhythmicLattice.array_to_lattice(np.flip(np.array([
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
]), axis=0)), None, RhythmicLattice())

major_chord = ChromaRollPattern(RhythmicLattice.array_to_lattice(np.flip(np.array([
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
]), axis=0)))

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
