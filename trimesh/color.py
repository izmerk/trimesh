import numpy as np
from colorsys import hsv_to_rgb
from .constants import TOL_ZERO, log

COLORS = {'red'    : [205,59,34],
          'purple' : [150,111,214],
          'blue'   : [119,158,203],
          'brown'  : [160,85,45]}
COLOR_DTYPE = np.uint8
DEFAULT_COLOR = COLORS['purple']

def random_color(dtype=COLOR_DTYPE):
    '''
    Return a random RGB color using datatype specified.
    '''
    hue  = np.random.random() + .61803
    hue %= 1.0
    color = np.array(hsv_to_rgb(hue, .99, .99))
    if np.dtype(dtype).kind in 'iu':
        max_value = (2**(np.dtype(dtype).itemsize * 8)) - 1
        color    *= max_value
    color     = color.astype(dtype)
    return color

def distinct_colors(dtype=COLOR_DTYPE, expected_length=50):
    '''
    Generator for colors 
    '''
    while True:
        yield random_color(dtype)

def average_color(a, b):
    result = (np.array(a) + b) / 2
    return result

def face_to_vertex_color(mesh, face_colors, dtype=COLOR_DTYPE):
    '''
    Convert a set of face colors into a set of vertex colors.
    '''
    vertex_colors = np.zeros((len(mesh.vertices),3,3))
    population    = np.zeros((len(mesh.vertices),3), dtype=np.bool)

    vertex_colors[[mesh.faces[:,0],0]] = face_colors
    vertex_colors[[mesh.faces[:,1],1]] = face_colors
    vertex_colors[[mesh.faces[:,2],2]] = face_colors

    population[[mesh.faces[:,0], 0]] = True
    population[[mesh.faces[:,1], 1]] = True
    population[[mesh.faces[:,2], 2]] = True

    # clip the population sum to 1, to avoid a division error in edge cases
    populated     = np.clip(population.sum(axis=1), 1, 3)
    vertex_colors = vertex_colors.sum(axis=1) / populated.reshape((-1,1))
    return vertex_colors.astype(dtype)

class VisualAttributes(object):
    '''
    Hold the visual attributes (usually colors) for a mesh. 
    '''
    def __init__(self, mesh):
        self.mesh = mesh

        self._vertex_colors = None
        self._face_colors   = None

    @property
    def face_colors(self):
        if self._face_colors is None:
            self._face_colors = np.tile(DEFAULT_COLOR,
                                        (len(self.mesh.faces), 1))
        return self._face_colors

    @face_colors.setter
    def face_colors(self, values):
        if np.shape(values) == np.shape(self.mesh.faces):
            self._face_colors = values
        elif np.shape(values) == (3,):
            # case where a single RGB color has been passed to the setter
            # here we apply this color to all faces 
            self.face_colors = np.tile(values, 
                                       (len(self.mesh.faces), 1))
        else: 
            raise ValueError('Face colors are the wrong shape!')

    @property
    def vertex_colors(self):
        if self._vertex_colors is None:
            vertex_colors = face_to_vertex_color(self.mesh, 
                                                 self.face_colors)
            return vertex_colors
        return self._vertex_colors

    @vertex_colors.setter
    def vertex_colors(self, values):
        if np.shape(values) == np.shape(self.mesh.vertices):
            self._vertex_colors = values
        else: 
            raise ValueError('Vertex colors are the wrong shape!')

    def update_faces(self, mask):
        if not (self._face_colors is None):
            self._face_colors = self._face_colors[mask]

    def update_vertices(self, mask):
        if not (self._vertex_colors is None):
            self._vertex_colors = self._vertex_colors[mask]
