import numpy as np
import math
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as Axes3D
import matplotlib.animation as animation
import sys

class GUI():
    # 'quad_list' is a dictionary of format: quad_list = {'quad_1_name':{'position':quad_1_position,'orientation':quad_1_orientation,'arm_span':quad_1_arm_span}, ...}
    def __init__(self, quads, get_data, get_time):
        self.quads = quads
        self.get_data = get_data
        self.get_time = get_time
        self.fig = plt.figure()
        self.ax = Axes3D.Axes3D(self.fig, auto_add_to_figure=False)
        self.fig.add_axes(self.ax)
        self.ax.set_xlim3d([-2.0, 2.0])
        self.ax.set_xlabel('X')
        self.ax.set_ylim3d([-2.0, 2.0])
        self.ax.set_ylabel('Y')
        self.ax.set_zlim3d([0, 5.0])
        self.ax.set_zlabel('Z')
        self.ax.set_title('Quadcopter Simulation')
        self.init_plot()
        self.fig.canvas.mpl_connect('key_press_event', self.key_press_routine)
        self.fig.canvas.mpl_connect('close_event', self.close_routine)

    def rotation_matrix(self,angles):
        ct = math.cos(angles[0])
        cp = math.cos(angles[1])
        cg = math.cos(angles[2])
        st = math.sin(angles[0])
        sp = math.sin(angles[1])
        sg = math.sin(angles[2])
        R_x = np.array([[1,0,0],[0,ct,-st],[0,st,ct]])
        R_y = np.array([[cp,0,sp],[0,1,0],[-sp,0,cp]])
        R_z = np.array([[cg,-sg,0],[sg,cg,0],[0,0,1]])
        R = np.dot(R_z, np.dot( R_y, R_x ))
        return R

    def init_plot(self):
        blit_artists = []
        for key in self.quads:
            self.quads[key]['l1'], = self.ax.plot([],[],[],color='blue',linewidth=3,antialiased=False)
            self.quads[key]['l2'], = self.ax.plot([],[],[],color='red',linewidth=3,antialiased=False)
            self.quads[key]['hub'], = self.ax.plot([],[],[],marker='o',color='green', markersize=6,antialiased=False)
            blit_artists.append(self.quads[key]['l1'])
            blit_artists.append(self.quads[key]['l2'])
            blit_artists.append(self.quads[key]['hub'])
        return tuple(blit_artists)
    
    def update(self, i=0):
        blit_artists = []
        for key in self.quads:
            self.quads[key]['position'] = self.get_data[0](key)
            self.quads[key]['orientation'] = self.get_data[1](key)
            R = self.rotation_matrix(self.quads[key]['orientation'])
            L = self.quads[key]['L']
            points = np.array([ [-L,0,0], [L,0,0], [0,-L,0], [0,L,0], [0,0,0], [0,0,0] ]).T
            points = np.dot(R,points)
            points[0,:] += self.quads[key]['position'][0]
            points[1,:] += self.quads[key]['position'][1]
            points[2,:] += self.quads[key]['position'][2]
            self.quads[key]['l1'].set_data(points[0,0:2],points[1,0:2])
            self.quads[key]['l1'].set_3d_properties(points[2,0:2])
            self.quads[key]['l2'].set_data(points[0,2:4],points[1,2:4])
            self.quads[key]['l2'].set_3d_properties(points[2,2:4])
            self.quads[key]['hub'].set_data(points[0,5],points[1,5])
            self.quads[key]['hub'].set_3d_properties(points[2,5])
            blit_artists.append(self.quads[key]['l1'])
            blit_artists.append(self.quads[key]['l2'])
            blit_artists.append(self.quads[key]['hub'])
        return tuple(blit_artists)
    
    def frame_iter(self):
        while self.get_time() < self.anim_duration:
            yield
        self.run = False
    
    def animate(self, duration, pause_sim, frame_rate=30):
        self.run = True
        self.pause = False
        self.pause_sim = pause_sim
        self.anim_duration = duration
        frame_delta = 1/frame_rate
        self.anim = animation.FuncAnimation(self.fig, self.update, init_func=self.init_plot,
                                       frames=self.frame_iter, interval=1000*frame_delta,
                                       blit=True)
        while self.run == True:
            plt.pause(frame_delta)
        self.init_plot()
        self.update()
    
    def toggle_pause(self):
        
        self.pause = not self.pause
        self.pause_sim(self.pause)
        if self.pause == True:
            self.anim.pause()
            self.init_plot()
        else:
            self.anim.resume()
            self.init_plot()

    def key_press_routine(self,event):
        sys.stdout.flush()
        if event.key == 'p':
            self.toggle_pause()
        if event.key == 'x':
            y = list(self.ax.get_ylim3d())
            y[0] += 0.2
            y[1] += 0.2
            self.ax.set_ylim3d(y)
        elif event.key == 'w':
            y = list(self.ax.get_ylim3d())
            y[0] -= 0.2
            y[1] -= 0.2
            self.ax.set_ylim3d(y)
        elif event.key == 'd':
            x = list(self.ax.get_xlim3d())
            x[0] += 0.2
            x[1] += 0.2
            self.ax.set_xlim3d(x)
        elif event.key == 'a':
            x = list(self.ax.get_xlim3d())
            x[0] -= 0.2
            x[1] -= 0.2
            self.ax.set_xlim3d(x)
    
    def close_routine(self,event):
        self.run = False