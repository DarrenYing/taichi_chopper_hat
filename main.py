import taichi as ti
from taichi.math import *
from scene import Scene

scene = Scene(voxel_edges=0, exposure=1)  # 创建场景，指定体素描边宽度和曝光值
scene.set_floor(0, (1.0, 1.0, 1.0))  # 地面高度
scene.set_background_color((0.204, 0.596, 0.859))  # 天空颜色 #3498db
scene.set_directional_light((0.1, 0.2, -0.3), 0, (0.1, 0.1, 0.1))  # 光线方向和颜色


@ti.func
def create_hat_top(pos, radius, height, offset, color):
    for I in ti.grouped(ti.ndrange((-radius, radius), (0, height), (-radius, radius))):
        d = vec2(I[0], I[2]).norm()
        if d < (radius - I[1] * offset / height + 1 - I[1] / height):
            scene.set_voxel(pos + I, 2, color)


@ti.func
def create_cross(pos, w, h, color):
    for I in ti.grouped(ti.ndrange((-w / 2, w / 2), (-h / 2, h / 2), 2)):
        org_x, org_z = I[0], I[1]
        theta = pi / 4
        I[0] = ti.cos(theta) * org_x - ti.sin(theta) * org_z
        I[1] = ti.sin(theta) * org_x + ti.cos(theta) * org_z
        scene.set_voxel(pos + I, 2, color)
        theta = -pi / 4
        I[0] = ti.cos(theta) * org_x - ti.sin(theta) * org_z
        I[1] = ti.sin(theta) * org_x + ti.cos(theta) * org_z
        scene.set_voxel(pos + I, 2, color)


@ti.func
def create_antler(org_pos, color):
    pos = org_pos
    for x in range(0, 4):
        I = [x, x * x / 4, 0]
        scene.set_voxel(pos + I, 2, color)
    pos[0] += 4
    pos[1] += 4
    for x in range(-4, 5):
        for y in range(-5, 5):
            if y % 3 == 0:
                I = [x, x * x / 4, y]
                scene.set_voxel(pos + I, 2, color)
    pos = org_pos
    pos[0] -= 2 * org_pos[0]
    for x in range(-4, 0):
        I = [x, x * x / 4, 0]
        scene.set_voxel(pos + I, 2, color)
    pos[0] -= 4
    pos[1] += 4
    for x in range(-4, 5):
        for y in range(-5, 5):
            if y % 3 == 0:
                I = [x, x * x / 4, y]
                scene.set_voxel(pos + I, 2, color)


@ti.func
def create_hat_bottom(pos, radius, height, color):
    for I in ti.grouped(ti.ndrange((-radius, radius), (0, height), (-radius, radius))):
        d = vec2(I[0], I[2]).norm()  # 到圆柱中轴线的距离
        if d <= radius:
            scene.set_voxel(pos + I, 2, color)


@ti.kernel
def initialize_voxels():
    bottom_radius = 20
    bottom_height = 2
    top_height = bottom_radius * 1.2
    top_radius = bottom_radius * 3 / 4
    offset = bottom_radius / 5

    create_hat_bottom(
        pos=ivec3(0, 0, 0), radius=bottom_radius,
        height=bottom_height, color=vec3(0.95, 0.1, 0.1)
    )

    create_hat_top(
        pos=ivec3(0, bottom_height, 0), radius=top_radius,
        height=top_height, offset=offset, color=vec3(0.90, 0.12, 0.12)
    )

    create_cross(
        pos=ivec3(0, bottom_height + top_height / 2, top_radius),
        w=1, h=12, color=vec3(1, 1, 1)
    )

    create_antler(
        org_pos=vec3(top_radius, bottom_height + top_height / 3, 0),
        color=vec3(0.6, 0.3, 0.2)
    )


initialize_voxels()
scene.finish()
