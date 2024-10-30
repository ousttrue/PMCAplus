//! PMCA Parts list v2.0
//!
//! SETDIR ./parts/
//!
//! [name] セーラー服上半身01(スカート,長袖)
//! [comment] 普通の長袖セーラー服、縦リボン
//! [type] root
//! [path] ub_mt_slr001_l_sk.pmd
//! [joint] head,hand,lb_sk,body_acce
//! [pic] ub_mt_slr001_l_sk.png
//!
//! NEXT
const std = @import("std");

const header = "PMCA Parts list v2.0";
const setdir = "SETDIR ";
const bom = [3]u8{
    0xEF, 0xBB, 0xBF,
};

pub const Parts = struct {
    dir: []const u8,
    name: []const u8,
    comment: []const u8,
    path: []const u8,
    pic: []const u8,
    parent_joints: []const []const u8,
    child_joints: []const []const u8,
    pre_scripts: []const []const u8,
    post_scripts: []const []const u8,

    pub fn deinit(self: *@This(), allocator: std.mem.Allocator) void {
        allocator.free(self.parent_joints);
        allocator.free(self.child_joints);
        allocator.free(self.pre_scripts);
        allocator.free(self.post_scripts);
    }
};

const Builder = struct {
    parent_joints: std.ArrayList([]const u8),
    child_joints: std.ArrayList([]const u8),
    pre_scripts: std.ArrayList([]const u8),
    post_scripts: std.ArrayList([]const u8),
    dir: []const u8 = "",
    name: []const u8 = "",
    comment: []const u8 = "",
    path: []const u8 = "",
    pic: []const u8 = "",

    fn init(allocator: std.mem.Allocator) @This() {
        return .{
            .parent_joints = std.ArrayList([]const u8).init(allocator),
            .child_joints = std.ArrayList([]const u8).init(allocator),
            .pre_scripts = std.ArrayList([]const u8).init(allocator),
            .post_scripts = std.ArrayList([]const u8).init(allocator),
        };
    }

    fn deinit(self: *@This()) void {
        self.parent_joints.deinit();
        self.child_joints.deinit();
        self.pre_scripts.deinit();
        self.post_scripts.deinit();
    }

    fn clear(self: *@This()) void {
        self.name = "";
        self.comment = "";
        self.path = "";
        self.pic = "";
    }

    fn commit(self: *@This()) !Parts {
        std.debug.assert(self.parent_joints.items.len > 0);
        defer self.clear();
        return .{
            .dir = self.dir,
            .name = self.name,
            .comment = self.comment,
            .path = self.path,
            .pic = self.pic,
            .parent_joints = try self.parent_joints.toOwnedSlice(),
            .child_joints = try self.child_joints.toOwnedSlice(),
            .pre_scripts = try self.pre_scripts.toOwnedSlice(),
            .post_scripts = try self.post_scripts.toOwnedSlice(),
        };
    }

    fn isMatch(comptime prop: anytype, key: []const u8, value: []const u8) ?[]const u8 {
        if (std.mem.eql(u8, prop, key)) {
            return std.mem.trim(u8, value, &std.ascii.whitespace);
        } else {
            return null;
        }
    }

    pub fn set(self: *@This(), key: []const u8, _value: []const u8) !void {
        if (isMatch("name", key, _value)) |value| {
            self.name = value;
        } else if (isMatch("type", key, _value)) |value| {
            try self.parent_joints.append(value);
        } else if (isMatch("joint", key, _value)) |value| {
            try self.child_joints.append(value);
        } else if (isMatch("script_pre", key, _value)) |value| {
            try self.pre_scripts.append(value);
        } else if (isMatch("script_post", key, _value)) |value| {
            try self.post_scripts.append(value);
        } else if (isMatch("path", key, _value)) |value| {
            self.path = value;
        } else if (isMatch("pic", key, _value)) |value| {
            self.pic = value;
        } else if (isMatch("comment", key, _value)) |value| {
            self.comment = value;
        } else {
            std.debug.print("unkonwn key: {s}\n", .{key});
            @panic("unknown property");
        }
    }
};

const Parser = struct {};

pub fn parse(allocator: std.mem.Allocator, _data: []const u8) ![]Parts {
    var data = _data;

    if (std.mem.startsWith(u8, data, &bom)) {
        data = data[bom.len..];
    }

    if (!std.mem.startsWith(u8, data, header)) {
        return error.no_header;
    }
    data = data[header.len..];

    while (data[0] == '\r' or data[0] == '\n') : (data = data[1..]) {
        // skip crlf
    }

    var s = std.io.fixedBufferStream(data);
    const r = s.reader();

    var list = std.ArrayList(Parts).init(allocator);
    var line_buf: [1024]u8 = undefined;
    var builder = Builder.init(allocator);
    defer builder.deinit();
    while (r.readUntilDelimiterOrEof(&line_buf, '\n')) |_line| {
        const line = _line orelse {
            // last
            if (builder.parent_joints.items.len > 0) {
                try list.append(try builder.commit());
            }
            return list.toOwnedSlice();
        };

        const trimed = std.mem.trim(u8, line, &std.ascii.whitespace);
        if (trimed.len == 0) {
            continue;
        }

        if (std.mem.startsWith(u8, trimed, setdir)) {
            builder.dir = trimed[setdir.len..];
        } else if (std.mem.eql(u8, trimed, "NEXT")) {
            // commit
            try list.append(try builder.commit());
        } else if (trimed[0] == '[') {
            if (std.mem.indexOf(u8, trimed, "]")) |close| {
                try builder.set(trimed[1..close], trimed[close + 1 ..]);
            }
        } else {
            unreachable;
        }
    } else |_| {
        @panic("error");
    }
}
