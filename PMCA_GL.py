import re
import math
from glglue.sample import *
from OpenGL.GL import *

DELEGATE_PATTERN=re.compile('^on[A-Z]')
VELOCITY=0.1


def to_radian(degree):
    return degree/180.0*math.pi


class Model:
    def __init__(self, vertices, uvs, indices, colors, paths, indexCounts):
        self.vertices=vertices
        self.indices=indices

    def draw(self):
        glEnableClientState(GL_VERTEX_ARRAY);
        glVertexPointer(3, GL_FLOAT, 0, self.vertices);
        #glEnableClientState(GL_COLOR_ARRAY);
        #glColorPointer(3, GL_FLOAT, 0, self.colors);
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, self.indices);
        #glDisableClientState(GL_COLOR_ARRAY);
        glDisableClientState(GL_VERTEX_ARRAY);


class Scene(object):
    def __init__(self):
        self.coord=coord.Coord(30.0)
        self.xrot=0
        self.yrot=0
        self.clear()

    def clear(self):
        self.drawable_map={}

    def add_item(self, key, method):
        self.drawable_map[key]=method

    def onUpdate(self, ms):
        self.yrot+=ms * VELOCITY
        while self.yrot>360.0:
            self.yrot-=360.0
        self.xrot+=ms * VELOCITY * 0.5
        while self.xrot>360.0:
            self.xrot-=360.0

    def draw(self):
        self.coord.draw()
        glRotate(math.sin(to_radian(self.yrot))*180, 0, 1, 0)
        glRotate(math.sin(to_radian(self.xrot))*180, 1, 0, 0)
        for drawable in self.drawable_map.values():
            drawable()


class GLController(object):
    def __init__(self, view=None, root=None):
        view=view or targetview.TargetView(40)
        self.view=view
        self.root=root or Scene()
        self.isInitialized=False
        self.delegate(view)
        self.delegate(root)

    def delegate(self, to):
        for name in dir(to):  
            if DELEGATE_PATTERN.match(name):
                method = getattr(to, name)  
                setattr(self, name, method)

    def onUpdate(self, ms):
        self.root.onUpdate(ms)

    def onKeyDown(self, key):
        #print("onKeyDown: %x" % key)
        if key==ord('\033'):
            # Escape
            sys.exit()
        if key==ord('q'):
            # q
            sys.exit()
        else:
            print(key)

    def onInitialize(*args):
        pass

    def initilaize(self):
        self.view.onResize()
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.6, 0.6, 0.4, 0.0)
        # 初期化時の呼び出し
        self.onInitialize()

    def draw(self):
        if not self.isInitialized:
            self.initilaize()
            self.isInitialized=True
        # OpenGLバッファのクリア
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # 投影行列のクリア
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        self.view.updateProjection()
        # モデルビュー行列のクリア
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.view.updateView()
        # 描画
        self.root.draw()

        glFlush()

