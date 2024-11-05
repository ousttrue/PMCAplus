pub extern fn getInfo(
    index: u32,
    name: *[*:0]const u8,
    name_eng: *[*:0]const u8,
    comment: *[*:0]const u8,
    comment_eng: *[*:0]const u8,
    vertex_count: *c_int,
    face_count: *c_int,
    material_count: *c_int,
    bone_count: *c_int,
    ik_count: *c_int,
    skin_count: *c_int,
    bone_grup_count: *c_int,
    bone_disp_count: *c_int,
    eng_support: *c_int,
    rb_count: *c_int,
    joint_count: *c_int,
    skin_disp: *[*]u16,
) void;

pub extern fn MODEL_LOCK(level: u32) void;
pub extern fn Create_PMD(index: u32) void;
pub extern fn Load_PMD(index: u32, [*:0]const u8) void;
pub extern fn Copy_PMD(src: c_int, dst: u32) void;
pub extern fn Update_Skin(index: u32) void;
pub extern fn Adjust_Joints(index: u32) void;
pub extern fn PMD_view_set(index: u32, [*:0]const u8) void;
pub extern fn Add_PMD(num: c_int, add: c_int) void;
pub extern fn Marge_PMD(num: c_int) void;
pub extern fn Get_PMD(num: c_int) *anyopaque;
