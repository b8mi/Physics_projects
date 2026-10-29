Azam = "Mirrors Project TKInter || Made by: عزام البقمي || Class 12-2"
import math, sys, traceback, tkinter as tk
fps = 1 #less is better 

DO_MIN_CONCAVE = 1
DO_MAX_CONCAVE = 12.0
DO_MIN_PLANE   = 1
DO_MAX_PLANE   = 7.0

EXTRA_MIN_CONCAVE = 0
EXTRA_MAX_CONCAVE = 6
EXTRA_MIN_PLANE = 0
EXTRA_MAX_PLANE = 6

HEIGHT_SLIDER_MIN = 2
HEIGHT_SLIDER_MAX = 12.0

SCALE = 60.0
MIRROR_R_HARDCODED = 6.0
DASH_SOLIDISH = (8,4)
CANVAS_W=920; CANVAS_H=684

def add(a,b): return (a[0]+b[0], a[1]+b[1])
def sub(a,b): return (a[0]-b[0], a[1]-b[1])
def mul(a,s): return (a[0]*s, a[1]*s)
def dot(a,b): return a[0]*b[0]+a[1]*b[1]
def norm(a): return math.hypot(a[0],a[1])
def normalize(a):
    n = norm(a); return (a[0]/n, a[1]/n) if n!=0 else (0.0,0.0)
def reflect(v,n):
    nd = dot(v,n); nn = dot(n,n)
    if nn==0: return v
    return sub(v, mul(n, 2*nd/nn))
def line_circle_intersection(p0,v,center,R):
    ox,oy = p0[0]-center[0], p0[1]-center[1]
    a = dot(v,v); b = 2*(ox*v[0]+oy*v[1]); c = ox*ox+oy*oy-R*R
    disc = b*b-4*a*c
    if disc<0: return None
    sd = math.sqrt(disc)
    t1 = (-b-sd)/(2*a); t2 = (-b+sd)/(2*a)
    ts = [t for t in (t1,t2) if t>1e-6]
    return min(ts) if ts else None
def line_xplane_intersection(p0,v,xplane):
    if abs(v[0])<1e-9: return None
    t = (xplane-p0[0])/v[0]
    return t if t>1e-6 else None
def intersect_lines(p1,d1,p2,d2):
    a,b,c,d = d1[0], -d2[0], d1[1], -d2[1]
    det = a*d - b*c
    if abs(det) < 1e-9: return None
    dx = p2[0]-p1[0]; dy = p2[1]-p1[1]
    t = (dx*d - b*dy)/det
    return (p1[0]+d1[0]*t, p1[1]+d1[1]*t)

class Mirror:
    def __init__(self, kind='concave', R=6.0, height=4.0, vertex_x=0.0):
        self.kind=kind; self.R=max(0.5,R); self.height=max(0.2,height); self.vertex_x=vertex_x
        self.update()
    def update(self):
        R=self.R
        if self.kind=='concave':
            self.center = (-R,0.0); self.f = R/2.0; self.focal = (-self.f,0.0)
        else:
            self.center=None; self.f=float('inf'); self.focal=None
    def surface_x(self,y):
        if self.kind=='plane': return self.vertex_x
        cx = self.center[0]; disc = self.R*self.R - y*y
        if disc<0: return None
        xp = cx + math.sqrt(disc); xn = cx - math.sqrt(disc)
        return xp if abs(xp-self.vertex_x)<abs(xn-self.vertex_x) else xn
    def intersect(self,p0,v):
        if self.kind=='plane':
            t=line_xplane_intersection(p0,v,self.vertex_x)
            if t is None: return (None,None)
            P = add(p0,mul(v,t))
            if abs(P[1])>self.height/2+1e-6: return (None,None)
            return (P, (1.0,0.0))
        t = line_circle_intersection(p0,v,self.center,self.R)
        if t is None: return (None,None)
        P = add(p0,mul(v,t))
        if abs(P[1])>self.height/2+1e-6: return (None,None)
        normal = sub(P,self.center)
        return (P, normal)

class App:
    def __init__(self, root):
        self.root=root
        self.root.title(Azam)
        self.root.config(bg='black') 
        
        self.canvas_w=CANVAS_W; self.canvas_h=CANVAS_H
        self.preview_w=220; self.preview_h=220
        self.left_margin_px = 31
        self.vertex_margin_px = 30
        self.center_px = self.canvas_w // 2
        self.vertex_px = 0
        self.SCALE = SCALE
        
        self.left_frame = tk.Frame(root, bg='black'); 
        self.left_frame.pack(side='left', padx=(6, 0), pady=0, fill='y') 
        
        self.canvas = tk.Canvas(self.left_frame, width=self.canvas_w, height=self.canvas_h, bg='black', highlightthickness=0); 
        self.canvas.pack(padx=0, pady=0) 
        
        self.separator = tk.Frame(root, width=5, bg='white')
        self.separator.pack(side='left', fill='y')
        
        self.right_frame = tk.Frame(root, bg='black'); 
        self.right_frame.pack(side='left', padx=(0, 6), pady=0, fill='y') 
        
        self.preview = tk.Canvas(self.right_frame, width=self.preview_w, height=self.preview_h, bg='black', highlightthickness=1, highlightbackground='#333'); 
        self.preview.pack(pady=6)
        
        self.controls = tk.Frame(self.right_frame, bg='black'); 
        self.controls.pack(pady=6)
        
        self.mirror_var = tk.StringVar(root); self.mirror_var.set('concave')
        self.opt = tk.OptionMenu(self.controls, self.mirror_var, 'concave','plane', command=lambda e: self.on_mode_change()); self.opt.config(bg='#222', fg='white', highlightthickness=0); self.opt.pack(pady=4)
        
        self.mode_state = {
            'concave': {'do': 5.0, 'height': 4.0, 'extra': 0},
            'plane':   {'do': 3.0, 'height': 4.0, 'extra': 0}
        }

        self.s_do = tk.Scale(self.controls, from_=DO_MIN_CONCAVE, to=DO_MAX_CONCAVE, resolution=0.1, orient=tk.HORIZONTAL, length=260, label='Do', command=lambda v: self.on_slider_changed('do', v), bg='black', fg='white', troughcolor='#333'); 
        self.s_do.set(self.mode_state['concave']['do']); self.s_do.pack(pady=4)

        self.s_h = tk.Scale(self.controls, from_=HEIGHT_SLIDER_MIN, to=HEIGHT_SLIDER_MAX, resolution=0.1, orient=tk.HORIZONTAL, length=260, label='Height', command=lambda v: self.on_slider_changed('height', v), bg='black', fg='white', troughcolor='#333'); 
        self.s_h.set(self.mode_state['concave']['height']); self.s_h.pack(pady=4)

        self.s_extra = tk.Scale(self.controls, from_=EXTRA_MIN_CONCAVE, to=EXTRA_MAX_CONCAVE, resolution=1, orient=tk.HORIZONTAL, length=260, label='Extra rays', command=lambda v: self.on_slider_changed('extra', v), bg='black', fg='white', troughcolor='#333'); 
        self.s_extra.set(self.mode_state['concave']['extra']); self.s_extra.pack(pady=4)
        
        self.formula_frame = tk.Frame(self.controls, bg='black'); self.formula_frame.pack(pady=(5,0))
        self.m_label = tk.Label(self.formula_frame, text="m =", bg='black', fg='white', font=('Arial', 10)); 
        self.left_num_label = tk.Label(self.formula_frame, text="1", bg='black', fg='white', font=('Arial', 10)); self.left_num_label.grid(row=0, column=1, padx=2)
        self.left_den_line = tk.Frame(self.formula_frame, width=20, height=1, bg='white'); self.left_den_line.grid(row=1, column=1, padx=2)
        self.left_den_label = tk.Label(self.formula_frame, text="f", bg='black', fg='white', font=('Arial', 10)); self.left_den_label.grid(row=2, column=1, padx=2)
        self.eq_label = tk.Label(self.formula_frame, text="=", bg='black', fg='white', font=('Arial', 10)); self.eq_label.grid(row=1, column=2, padx=2)
        self.right_num_label = tk.Label(self.formula_frame, text="1", bg='black', fg='white', font=('Arial', 10)); self.right_num_label.grid(row=0, column=3, padx=2)
        self.right_den_line = tk.Frame(self.formula_frame, width=20, height=1, bg='white'); self.right_den_line.grid(row=1, column=3, padx=2)
        self.right_den_label = tk.Label(self.formula_frame, text="Do", bg='black', fg='white', font=('Arial', 10)); self.right_den_label.grid(row=2, column=3, padx=2)
        self.plus_label = tk.Label(self.formula_frame, text="+", bg='black', fg='white', font=('Arial', 10)); self.plus_label.grid(row=1, column=4, padx=2)
        self.di_num_label = tk.Label(self.formula_frame, text="1", bg='black', fg='white', font=('Arial', 10)); self.di_num_label.grid(row=0, column=5, padx=2)
        self.di_den_line = tk.Frame(self.formula_frame, width=20, height=1, bg='white'); self.di_den_line.grid(row=1, column=5, padx=2)
        self.di_den_label = tk.Label(self.formula_frame, text="Di", bg='black', fg='white', font=('Arial', 10)); self.di_den_label.grid(row=2, column=5, padx=2)
        
        self.values_frame = tk.Frame(self.controls, bg='black'); self.values_frame.pack(pady=(5,0))
        self.val_f_label = tk.Label(self.values_frame, text="f: ", bg='black', fg='white', font=('Arial', 10)); self.val_f_label.grid(row=0, column=0, padx=(5,0))
        self.val_do_label = tk.Label(self.values_frame, text="Do: ", bg='black', fg='white', font=('Arial', 10)); self.val_do_label.grid(row=0, column=1, padx=5)
        self.val_di_label = tk.Label(self.values_frame, text="Di: ", bg='black', fg='white', font=('Arial', 10)); self.val_di_label.grid(row=0, column=2, padx=5)

        self.error_label = tk.Label(self.controls, text="", bg='black', fg='#ff0000', font=('Arial', 9)); self.error_label.pack(pady=(5,0))
        self.empty_space1 = tk.Frame(self.controls, width=260, height=10, bg='black'); self.empty_space1.pack(pady=6)
        self.empty_space2 = tk.Frame(self.controls, width=260, height=10, bg='black'); self.empty_space2.pack(pady=6)
        
        self.mirror = Mirror()
        self.mirror.R = MIRROR_R_HARDCODED
        self.mirror.update()
        self.obj_h = 1.0; self.max_ray = 80.0
        self.redraw_ids=[]; self._after_id = None
        self.bring_to_front()
        self.schedule_update()

    def on_mode_change(self):
        mode = self.mirror_var.get()
        if mode == 'concave':
            self.s_do.config(from_=DO_MIN_CONCAVE, to=DO_MAX_CONCAVE, resolution=0.1)
            self.s_extra.config(from_=EXTRA_MIN_CONCAVE, to=EXTRA_MAX_CONCAVE, resolution=1)
        else:
            self.s_do.config(from_=DO_MIN_PLANE, to=DO_MAX_PLANE, resolution=0.1)
            self.s_extra.config(from_=EXTRA_MIN_PLANE, to=EXTRA_MAX_PLANE, resolution=1)
        st = self.mode_state.get(mode, None)
        if st:
            self.s_do.set(st['do'])
            self.s_h.set(st['height'])
            self.s_extra.set(st['extra'])
        self.schedule_update()

    def on_slider_changed(self, which, value):
        mode = self.mirror_var.get()
        try:
            if which == 'extra':
                v = int(float(value))
            else:
                v = float(value)
        except:
            v = value
        if mode not in self.mode_state:
            self.mode_state[mode] = {'do':5.0,'height':4.0,'extra':0}
        if which == 'do':
            self.mode_state[mode]['do'] = v
        elif which == 'height':
            self.mode_state[mode]['height'] = v
        elif which == 'extra':
            self.mode_state[mode]['extra'] = int(v)
        self.schedule_update()

    def bring_to_front(self):
        try:
            self.root.update_idletasks(); self.root.lift(); self.root.attributes('-topmost', True)
            self.root.after(150, lambda: self.root.attributes('-topmost', False))
        except Exception:
            pass

    def world_to_canvas(self, x, y):
        px = self.vertex_px + (x - 0.0) * self.SCALE
        py = self.canvas_h/2 - y * self.SCALE
        return px, py

    def generate_rays(self, P_obj, mirror_kind, num_extra, Do):
        rays=[]
        if mirror_kind == 'plane':
            P_img = (Do, self.obj_h)
            P_hit_target = (0.0, 0.75 * self.obj_h)
            dir_in = normalize(sub(P_hit_target, P_obj))
            R = reflect(dir_in, (1.0, 0.0))
            rays.append({'p0':P_obj,'dir':dir_in,'color':'#ff3b3b','main':True, 'P_hit_target': P_hit_target, 'R_dir': R})
            rays.append({'p0':P_obj,'dir':(1.0,0.0),'color':'#3ba6ff','main':True})
        else:
            rays.append({'p0':P_obj,'dir':(1.0,0.0),'color':'#ff3b3b','main':True})
            if mirror_kind=='concave' and Do <= self.mirror.f:
                center = self.mirror.center
                dirv = normalize(sub(P_obj, center))
                rays.append({'p0':P_obj,'dir':dirv,'color':'#3ba6ff','main':True})
            else:
                focal = self.mirror.focal
                dir_to_f = normalize(sub(focal, P_obj))
                rays.append({'p0':P_obj,'dir':dir_to_f,'color':'#3ba6ff','main':True})

        n_extra = int(round(num_extra))
        if n_extra>0:
            for i in range(n_extra):
                if n_extra==1: a=0
                else: a = -0.25 + i*(0.5/(n_extra-1))
                ca,sa = math.cos(a), math.sin(a)
                base = (1.0,0.0); dirv = normalize((base[0]*ca - base[1]*sa, base[0]*sa + base[1]*ca))
                rays.append({'p0':P_obj,'dir':dirv,'color':'#888888','main':False})
        return rays

    def trace_ray(self, ray, max_len):
        p0=ray['p0']; v=normalize(ray['dir'])
        
        perp_x = getattr(self, 'perp_x_world', None)
        t_perp = None
        t_p = None
        if perp_x is not None:
            t_p = line_xplane_intersection(p0, v, perp_x)
            if t_p is not None:
                Pp = add(p0, mul(v, t_p))
                t_perp = t_p

        t_mirror = None
        if self.mirror.kind == 'plane':
            t_m = line_xplane_intersection(p0, v, self.mirror.vertex_x)
            if t_m is not None:
                Pm = add(p0, mul(v, t_m))
                if abs(Pm[1]) <= self.mirror.height / 2.0 + 1e-6:
                    t_mirror = t_m
        else:
            t_c = line_circle_intersection(p0, v, self.mirror.center, self.mirror.R)
            if t_c is not None:
                Pm = add(p0, mul(v, t_c))
                if abs(Pm[1]) <= self.mirror.height / 2.0 + 1e-6:
                    t_mirror = t_c

        if t_perp is not None and self.mirror.kind == 'concave':
            P_hit = add(p0, mul(v, t_perp))
            normal = (1.0, 0.0)
            r = reflect(v, normal)
            segs = [(p0, P_hit, True)]
            segs.append((P_hit, add(P_hit, mul(r, max_len)), False))
            return segs, P_hit, r

        if self.mirror.kind == 'plane' and ray.get('P_hit_target'):
            P = ray['P_hit_target']
            normal = (1.0, 0.0)
            r = ray['R_dir']
            segs = [(p0, P, True)]
            return segs, P, r

        P, normal = self.mirror.intersect(p0,v)
        segs=[]
        if P is None:
            segs.append((p0, add(p0,mul(v,max_len)), False)); return segs, None, None

        segs.append((p0,P,True)); r = reflect(v, normal); segs.append((P, add(P,mul(r,max_len)), False))
        return segs, P, r

    def compute_image_formula(self, do):
        if self.mirror.kind=='plane': return -do, 1.0
        f = self.mirror.f
        if abs(do-f) < 1e-9: return None, None
        if abs(1.0/f - 1.0/do) < 1e-9: return None, None
        di = 1.0/(1.0/f - 1.0/do); m = -di/do; return di, m

    def snap_01(self, x): return math.floor(x*10+0.5)/10.0

    def schedule_update(self):
        if self._after_id: self.root.after_cancel(self._after_id)
        self._after_id = self.root.after(fps, self.update_scene) #fps

    def update_scene(self):
        for idd in list(self.redraw_ids):
            try: self.canvas.delete(idd)
            except: pass
        self.redraw_ids=[]

        Do_raw = float(self.s_do.get())
        H = max(HEIGHT_SLIDER_MIN, float(self.s_h.get()))
        extra = int(self.s_extra.get())
        mk = self.mirror_var.get()

        if mk not in self.mode_state:
            self.mode_state[mk] = {'do':Do_raw, 'height':H, 'extra':extra}
        else:
            self.mode_state[mk]['do'] = Do_raw
            self.mode_state[mk]['height'] = H
            self.mode_state[mk]['extra'] = extra

        self.mirror.kind=mk; self.mirror.height=H; self.mirror.R = MIRROR_R_HARDCODED; self.mirror.update()

        if mk == 'plane':
            self.vertex_px = self.center_px
        else:
            self.vertex_px = self.canvas_w - self.vertex_margin_px
        self.mirror.vertex_x = 0.0

        vx = self.vertex_px
        left_px = self.left_margin_px
        
        Do_min_world = 35.0 / self.SCALE
        Do_max_world_canvas = (vx - left_px) / self.SCALE
        
        if mk == 'plane':
            mode_min = DO_MIN_PLANE; mode_max = DO_MAX_PLANE
        else:
            mode_min = DO_MIN_CONCAVE; mode_max = DO_MAX_CONCAVE

        Do_max_world = min(Do_max_world_canvas, mode_max)
        Do_min_world = max(Do_min_world, mode_min)

        if Do_max_world <= Do_min_world + 1e-9:
            Do_max_world = Do_min_world + 0.1

        Do = Do_raw
        if Do < Do_min_world: Do = Do_min_world
        if Do > Do_max_world: Do = Do_max_world
        Do = self.snap_01(Do)

        try:
            if mk == 'plane':
                self.s_do.config(from_=DO_MIN_PLANE, to=DO_MAX_PLANE, resolution=0.1)
                self.s_extra.config(from_=EXTRA_MIN_PLANE, to=EXTRA_MAX_PLANE, resolution=1)
            else:
                self.s_do.config(from_=DO_MIN_CONCAVE, to=DO_MAX_CONCAVE, resolution=0.1)
                self.s_extra.config(from_=EXTRA_MIN_CONCAVE, to=EXTRA_MAX_CONCAVE, resolution=1)

            self.s_h.config(from_=HEIGHT_SLIDER_MIN, to=HEIGHT_SLIDER_MAX, resolution=0.1)
            self.s_do.set(Do)
            self.s_h.set(H)
            self.s_extra.set(extra)
        except: pass

        self.canvas.create_rectangle(0,0,self.canvas_w,self.canvas_h,fill='black',outline='black')
        ys = [ -H/2 + i*(H/199) for i in range(200) ]
        pts_canvas = []
        for y in ys:
            sx = self.mirror.surface_x(y)
            if sx is None: continue
            px,py = self.world_to_canvas(sx, y)
            pts_canvas.append((px, py))
        for i in range(len(pts_canvas)-1):
            idd = self.canvas.create_line(pts_canvas[i][0], pts_canvas[i][1], pts_canvas[i+1][0], pts_canvas[i+1][1], fill='#ffffff', width=3)
            self.redraw_ids.append(idd)

        mirror_surface_x = self.mirror.surface_x(0.0) if self.mirror.surface_x(0.0) is not None else self.mirror.vertex_x
        
        left_world = (left_px - vx)/self.SCALE
        right_world = (self.canvas_w - left_px - vx)/self.SCALE
        mx1,my1 = self.world_to_canvas(mirror_surface_x, 0.0)
        mx2,my2 = self.world_to_canvas(right_world, 0.0)
        idd_main = self.canvas.create_line(self.world_to_canvas(left_world, 0.0), mx2, my2, fill='#AAAAAA', width=2)
        self.redraw_ids.append(idd_main)

        if mk == 'concave':
            self.perp_x_world = right_world
            self.perp_height = H
            p_top_x, p_top_y = self.world_to_canvas(self.perp_x_world, H/2.0)
            p_bot_x, p_bot_y = self.world_to_canvas(self.perp_x_world, -H/2.0)
            idd_perp = self.canvas.create_line(p_top_x, p_top_y, p_bot_x, p_bot_y, fill='#ffffff', width=3)
            self.redraw_ids.append(idd_perp)
        else:
            self.perp_x_world = None
            self.perp_height = None

        vx_px, vy_px = self.world_to_canvas(0.0, 0.0)

        P_obj = (-Do, self.obj_h)
        ox1,oy1 = self.world_to_canvas(P_obj[0], 0)
        ox2,oy2 = self.world_to_canvas(P_obj[0], P_obj[1])
        self.redraw_ids.append(self.canvas.create_line(ox1,oy1,ox2,oy2,fill="#9900ff",width=2))

        rays = self.generate_rays(P_obj, mk, extra, Do)
        reflected=[]
        di_m = self.compute_image_formula(Do)
        di = None; m = 0.0
        if di_m[0] is not None:
            di, m = di_m
        else:
            di = None; m = 0.0

        image_point = None
        if di is not None:
            image_point = (-di, m * self.obj_h)

        f_val = self.mirror.f
        do_val = Do
        
        f_str = f"{f_val:.2f}"
        do_str = f"{do_val:.2f}"
        di_str = ""
        err_text = ""

        if mk == 'plane':
            f_str = "∞"
            self.m_label.grid(row=1, column=0, padx=2)
            self.left_num_label.grid(row=0, column=1, padx=2)
            self.left_num_label.config(text="hi")
            self.left_den_line.grid(row=1, column=1, padx=2)
            self.left_den_label.grid(row=2, column=1, padx=2)
            self.left_den_label.config(text="ho")
            self.eq_label.grid(row=1, column=2, padx=2)
            self.right_num_label.grid(row=0, column=3, padx=2)
            self.right_num_label.config(text="-di")
            self.right_den_line.grid(row=1, column=3, padx=2)
            self.right_den_label.grid(row=2, column=3, padx=2)
            self.right_den_label.config(text="do")
            self.plus_label.grid_forget()
            self.di_num_label.grid_forget(); self.di_den_line.grid_forget(); self.di_den_label.grid_forget()
            self.val_f_label.config(text=f"f: ∞")
            self.val_do_label.config(text=f"Do: {do_val:.2f}")
            self.val_di_label.config(text=f"Di: {di:.2f}")
        elif di is None:
            self.m_label.grid_forget()
            di_str = "∞" 
            self.left_num_label.grid(row=0, column=1, padx=2)
            self.left_num_label.config(text="1")
            self.left_den_line.grid(row=1, column=1, padx=2)
            self.left_den_label.grid(row=2, column=1, padx=2)
            self.left_den_label.config(text=f_str)
            self.eq_label.grid(row=1, column=2, padx=2)
            self.right_num_label.grid(row=0, column=3, padx=2)
            self.right_num_label.config(text="1")
            self.right_den_line.grid(row=1, column=3, padx=2)
            self.right_den_label.grid(row=2, column=3, padx=2)
            self.right_den_label.config(text=do_str)
            self.plus_label.grid(row=1, column=4, padx=2)
            self.di_num_label.grid(row=0, column=5, padx=2)
            self.di_num_label.config(text="1")
            self.di_den_line.grid(row=1, column=5, padx=2)
            self.di_den_label.grid(row=2, column=5, padx=2)
            self.di_den_label.config(text=di_str)
            self.val_f_label.config(text=f"f: {f_val:.2f}")
            self.val_do_label.config(text=f"Do: {do_val:.2f}")
            self.val_di_label.config(text=f"Di: ∞")
            self.error_label.config(text=err_text)
        else:
            self.m_label.grid_forget()
            di_str = f"{di:.2f}"
            self.left_num_label.grid(row=0, column=1, padx=2)
            self.left_num_label.config(text="1")
            self.left_den_line.grid(row=1, column=1, padx=2)
            self.left_den_label.grid(row=2, column=1, padx=2)
            self.left_den_label.config(text=f_str)
            self.eq_label.grid(row=1, column=2, padx=2)
            self.right_num_label.grid(row=0, column=3, padx=2)
            self.right_num_label.config(text="1")
            self.right_den_line.grid(row=1, column=3, padx=2)
            self.right_den_label.grid(row=2, column=3, padx=2)
            self.right_den_label.config(text=do_str)
            self.plus_label.grid(row=1, column=4, padx=2)
            self.di_num_label.grid(row=0, column=5, padx=2)
            self.di_num_label.config(text="1")
            self.di_den_line.grid(row=1, column=5, padx=2)
            self.di_den_label.grid(row=2, column=5, padx=2)
            self.di_den_label.config(text=di_str)
            self.val_f_label.config(text=f"f: {f_val:.2f}")
            self.val_do_label.config(text=f"Do: {do_val:.2f}")
            self.val_di_label.config(text=f"Di: {di:.2f}")
            self.error_label.config(text="")
        
        f_width = max(20, len(self.left_den_label.cget("text")) * 8)
        do_width = max(20, len(self.right_den_label.cget("text")) * 8)
        di_width = max(20, len(self.di_den_label.cget("text")) * 8)
        
        if mk == 'plane':
            f_width = max(20, len(self.left_den_label.cget("text")) * 8)
            do_width = max(20, len(self.right_den_label.cget("text")) * 8)

        self.left_den_line.config(width=f_width)
        self.right_den_line.config(width=do_width)
        self.di_den_line.config(width=di_width)

        P_img = (-di, m * self.obj_h) if di is not None else None

        for ri,ray in enumerate(rays):
            current_max_ray = self.max_ray
            if ri == 1 and mk == 'concave' and Do <= self.mirror.f:
                current_max_ray = self.max_ray * 3.0 
            
            segs,P_hit,r = self.trace_ray(ray, current_max_ray)
            color = ray['color']
            
            if mk == 'plane' and ray.get('main', False):
                pstart, P_hit, _ = segs[0]
                p1x,p1y = self.world_to_canvas(pstart[0], pstart[1])
                p2x,p2y = self.world_to_canvas(P_hit[0], P_hit[1])
                self.redraw_ids.append(self.canvas.create_line(p1x,p1y,p2x,p2y,fill=color,width=2))
                
                r_dir = r 
                reflected.append((P_hit, r_dir))
                p_far = add(P_hit, mul(r_dir, current_max_ray))
                p3x, p3y = self.world_to_canvas(p_far[0], p_far[1])
                self.redraw_ids.append(self.canvas.create_line(p2x,p2y, p3x,p3y, fill=color, width=2))
                
                if P_img is not None:
                    ix_canvas, iy_canvas = self.world_to_canvas(P_img[0], P_img[1])
                    if ri == 0:
                        self.redraw_ids.append(self.canvas.create_line(p2x,p2y, ix_canvas, iy_canvas, fill=color, width=1, dash=DASH_SOLIDISH))
                    elif ri == 1:
                        self.redraw_ids.append(self.canvas.create_line(p2x,p2y, ix_canvas, iy_canvas, fill=color, width=1, dash=DASH_SOLIDISH))
                
            else:
                if ray.get('main', False) and P_hit is not None:
                    pstart, phit, _ = segs[0]
                    p1x,p1y = self.world_to_canvas(pstart[0], pstart[1])
                    p2x,p2y = self.world_to_canvas(phit[0], phit[1])
                    self.redraw_ids.append(self.canvas.create_line(p1x,p1y,p2x,p2y,fill=color,width=2))

                    is_virtual = (di is not None and di < 0) or (mk == 'plane')
                    
                    if P_img is not None:
                        refl_dir_to_img = normalize(sub(P_img, phit))
                        ix_canvas, iy_canvas = self.world_to_canvas(P_img[0], P_img[1])
                        
                        if is_virtual:
                            refl_dir = r 
                            if refl_dir is None: refl_dir = (0,0)
                            reflected.append((phit, refl_dir))
                            
                            p_far = add(phit, mul(refl_dir, current_max_ray))
                            p3x, p3y = self.world_to_canvas(p_far[0], p_far[1])
                            
                            dash_opt = None
                            if ri == 1 and mk == 'concave' and Do <= self.mirror.f: 
                                dash_opt = DASH_SOLIDISH 
                                
                                center = self.mirror.center
                                v_back = normalize(sub(center, pstart)) 
                                p_past_c = add(pstart, mul(v_back, current_max_ray)) 
                                
                                pstart_cx, pstart_cy = self.world_to_canvas(pstart[0], pstart[1])
                                p_past_c_x, p_past_c_y = self.world_to_canvas(p_past_c[0], p_past_c[1])
                                
                                self.redraw_ids.append(self.canvas.create_line(pstart_cx, pstart_cy, p_past_c_x, p_past_c_y, fill=color, width=1, dash=DASH_SOLIDISH))
                            
                            self.redraw_ids.append(self.canvas.create_line(p2x,p2y, p3x,p3y, fill=color, width=2, dash=dash_opt))
                            self.redraw_ids.append(self.canvas.create_line(p2x,p2y, ix_canvas, iy_canvas, fill=color, width=1, dash=DASH_SOLIDISH))
                        
                        else:
                            refl_dir = refl_dir_to_img
                            reflected.append((phit, refl_dir))
                            
                            self.redraw_ids.append(self.canvas.create_line(p2x,p2y, ix_canvas, iy_canvas, fill=color, width=2))
                            
                            ext_p = add(P_img, mul(refl_dir, current_max_ray * 0.5))
                            ext_px, ext_py = self.world_to_canvas(ext_p[0], ext_p[1])
                            self.redraw_ids.append(self.canvas.create_line(ix_canvas, iy_canvas, ext_px, ext_py, fill=color, width=1, dash=DASH_SOLIDISH))
                    
                    elif di is None:
                        refl_dir = r 
                        if refl_dir is None: refl_dir = (0,0)
                        reflected.append((phit, refl_dir))
                        p_far = add(phit, mul(refl_dir, current_max_ray))
                        p3x, p3y = self.world_to_canvas(p_far[0], p_far[1])
                        self.redraw_ids.append(self.canvas.create_line(p2x,p2y, p3x,p3y, fill=color, width=2))
                    
                    else:
                        if r is not None:
                            refl_dir = r
                            reflected.append((phit, r))
                            p_ref_far = add(phit, mul(r, current_max_ray))
                            p3x,p3y = self.world_to_canvas(p_ref_far[0], p_ref_far[1])
                            self.redraw_ids.append(self.canvas.create_line(p2x,p2y, p3x,p3y, fill=color, width=2))
                    
                    continue
                
                for (pstart,pend,solid) in segs:
                    p1x,p1y = self.world_to_canvas(pstart[0], pstart[1])
                    p2x,p2y = self.world_to_canvas(pend[0], pend[1])
                    if solid:
                        idd = self.canvas.create_line(p1x,p1y,p2x,p2y,fill=color,width=2)
                    else:
                        idd = self.canvas.create_line(p1x,p1y,p2x,p2y,fill=color,width=1,dash=(6,6))
                    self.redraw_ids.append(idd)
                if P_hit is not None and r is not None and not ray.get('main', False):
                    reflected.append((P_hit,r))

        main_ref=[]
        for i,ray in enumerate(rays):
            if ray['main'] and i < len(reflected):
                main_ref.append(reflected[i])

        img_point_intersect=None
        if len(main_ref)>=2:
            inter = intersect_lines(main_ref[0][0],main_ref[0][1], main_ref[1][0],main_ref[1][1])
            if inter: img_point_intersect = inter

        final_image_point = img_point_intersect if img_point_intersect is not None else P_img
        
        if final_image_point is not None:
            ix_canvas, iy_canvas = self.world_to_canvas(final_image_point[0], final_image_point[1])
            self.redraw_ids.append(self.canvas.create_oval(ix_canvas-4, iy_canvas-4, ix_canvas+4, iy_canvas+4, fill="#FFA600", outline=''))
            self.redraw_ids.append(self.canvas.create_text(ix_canvas, iy_canvas+12, text='Image', fill="#FFA600"))
            proj_x_canvas, proj_y_canvas = self.world_to_canvas(final_image_point[0], 0.0)
            self.redraw_ids.append(self.canvas.create_line(ix_canvas, iy_canvas, proj_x_canvas, proj_y_canvas, fill='#FFA600', width=2))

        if mk!='plane' and self.mirror.focal:
            fx,fy = self.world_to_canvas(self.mirror.focal[0],0)
            self.redraw_ids.append(self.canvas.create_text(fx,fy-10, text='F', fill="#00FF4C"))
            cx,cy = self.world_to_canvas(self.mirror.center[0],0)
            self.redraw_ids.append(self.canvas.create_text(cx,cy-10, text='C', fill="#00FF4C"))

        self.preview.delete('all')
        self.preview.create_rectangle(0,0,self.preview_w,self.preview_h,fill='black',outline='#333')
        
        if di is None and mk == 'concave':
            self.preview.create_text(self.preview_w/2, self.preview_h/2, 
                                     text="No image forms\n(forms at infinity)", 
                                     fill='white', font=('Arial', 10), justify=tk.CENTER)
            self.preview.create_text(5, self.preview_h-10, anchor='w', text="m = undefined", fill='white', font=('Arial',9))
        else:
            preview_mag = m
            if final_image_point is not None:
                 preview_mag = final_image_point[1] / self.obj_h
            
            cxp, cyp = self.preview_w//2, self.preview_h//2
            arr_h_world = abs(preview_mag * self.obj_h)
            arr_h = int(0.35*self.preview_h*(1+arr_h_world)) 
            
            if arr_h > self.preview_h - 10: arr_h = self.preview_h - 10
            if arr_h < 5: arr_h = 5
            
            if preview_mag>=0:
                self.preview.create_line(cxp, cyp+arr_h//2, cxp, cyp-arr_h//2, fill='#FFA600', width=4)
                self.preview.create_polygon(cxp-8, cyp-arr_h//2+8, cxp, cyp-arr_h//2, cxp+8, cyp-arr_h//2+8, fill='#FFA600')
            else:
                self.preview.create_line(cxp, cyp-arr_h//2, cxp, cyp+arr_h//2, fill='#FFA600', width=4)
                self.preview.create_polygon(cxp-8, cyp+arr_h//2-8, cxp, cyp+arr_h//2, cxp+8, cyp+arr_h//2-8, fill="#FFA600")
            self.preview.create_text(5, self.preview_h-10, anchor='w', text=f"m={preview_mag:.2f}", fill='white', font=('Arial',9))

if __name__=='__main__':
    try:
        root = tk.Tk()
        app = App(root)
        root.mainloop()
    except Exception:
        print("Error launching GUI:")
        traceback.print_exc()
