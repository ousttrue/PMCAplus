import re
import math
import ctypes
from glglue.sample import *
from OpenGL.GL import *
from PIL import Image

DELEGATE_PATTERN=re.compile('^on[A-Z]')
VELOCITY=0.1


def to_radian(degree):
    return degree/180.0*math.pi


class Texture(object):

    def __init__(self, path):
        self.path=path
        self.image=None
        self.id=0
        self.isInitialized=False

    def onInitialize(self):
        self.isInitialized=False

    def createTexture(self):
        self.id=glGenTextures(1)
        if self.id==0:
            print("fail to glGenTextures")
            return False
        print("createTexture: %d" % self.id)

        channels=len(self.image.getbands())
        w, h=self.image.size
        glBindTexture(GL_TEXTURE_2D, self.id)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        if channels==4:
            print("RGBA")
            glPixelStorei(GL_UNPACK_ALIGNMENT, 4)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 
                    0, GL_RGBA, GL_UNSIGNED_BYTE, self.image.tobytes())
        elif channels==3:
            print("RGB")
            glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, w, h, 
                    0, GL_RGB, GL_UNSIGNED_BYTE, self.image.tobytes())

    def begin(self):
        if not self.isInitialized:
            try:
                # load image
                if not self.image:
                    self.image=Image.open(self.path)
                    if self.image:
                        print("load image:", self.path)
                    else:
                        print("failt to load image:", self.path)
                        return
                # createTexture
                if self.image:
                    self.createTexture()
            except Exception as e:
                print(e)
                return
            finally:
                self.isInitialized=True
        if self.id!=0:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.id)

    def end(self):
        glDisable(GL_TEXTURE_2D)


class Material:
    def __init__(self, color, texture_path, index_count):
        self.color=color
        self.texture=Texture(texture_path)
        self.index_count=index_count

    def begin(self):
        glColor4f(*self.color)
        self.texture.begin()

    def end(self):
        self.texture.end()


class Model:
    def __init__(self, vertices, uvs, indices, colors, paths, indexCounts):
        self.vertices=vertices
        self.indices=indices

    def draw(self):
        glEnableClientState(GL_VERTEX_ARRAY);
        glVertexPointer(3, GL_FLOAT, 0, self.vertices);
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, self.indices);
        glDisableClientState(GL_VERTEX_ARRAY);


class ModelVBO:
    def __init__(self, vertices, uvs, indices, colors, paths, indexCounts):
        self.is_initialized=False
        self.vertices=vertices
        self.uvs=uvs
        self.indices=indices
        self.colors=colors
        self.paths=paths
        self.indexCounts=indexCounts

    def initilaize(self):
        if(self.is_initialized):return
        self.is_initialized=True

        self.buffers = glGenBuffers(3)
        # vertices
        glBindBuffer(GL_ARRAY_BUFFER, self.buffers[0])
        glBufferData(GL_ARRAY_BUFFER, len(self.vertices)*4, (ctypes.c_float*len(self.vertices))(*self.vertices), GL_STATIC_DRAW)
        # uv
        glBindBuffer(GL_ARRAY_BUFFER, self.buffers[1])
        glBufferData(GL_ARRAY_BUFFER, len(self.uvs)*4, (ctypes.c_float*len(self.uvs))(*self.uvs), GL_STATIC_DRAW)
        # indices
        self.index_len=len(self.indices)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.buffers[2])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(self.indices)*4, (ctypes.c_uint*len(self.indices))(*self.indices), GL_STATIC_DRAW)

        self.materials=[Material(self.colors[i*4:i*4+4], path, self.indexCounts[i]) for i, path in enumerate(self.paths)]

    def draw(self):
        self.initilaize()

        try:
            # vertices
            glEnableClientState(GL_VERTEX_ARRAY);
            glBindBuffer(GL_ARRAY_BUFFER, self.buffers[0]);
            glVertexPointer(3, GL_FLOAT, 0, None);
            # uv
            glEnableClientState(GL_TEXTURE_COORD_ARRAY);
            glBindBuffer(GL_ARRAY_BUFFER, self.buffers[1]);
            glTexCoordPointer(2, GL_FLOAT, 0, None);

            # indices
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.buffers[2]);
            index_offset=0
            for i, m in enumerate(self.materials):
                # submesh
                m.begin()
                glDrawElements(GL_TRIANGLES, m.index_count, GL_UNSIGNED_INT, ctypes.c_void_p(index_offset));
                index_offset+=m.index_count * 4 # byte size
                m.end()

            # disable
            glDisableClientState(GL_TEXTURE_COORD_ARRAY);
            glDisableClientState(GL_VERTEX_ARRAY);
        except GLError:
            pass


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

