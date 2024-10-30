//! PMCA sample1
//! PMCAv0.0.6 sample1
//!
//!
//! PARTS
//! [Name] セーラー服上半身01(スカート,半袖)
//! [Path] ./parts/ub_mt_slr001_s_sk.pmd
//! [Child]
//! [Name] 顔f01
//! [Path] ./parts/head_mt001_1.pmd
//! [Child]
//! [Name] 前髪01
//! [Path] ./parts/hair_mf1_mt001.pmd
//! [Child]
//! [Name] 後髪02
//! [Path] ./parts/hair_mr1_mt002.pmd
//! [Child]
//! None
//! [Parent]
//! [Parent]
//! None
//! None
//! [Parent]
//! [Name] 腕01b
//! [Path] ./parts/arm1_mt001b.pmd
//! [Child]
//! None
//! [Parent]
//! [Name] スカート下半身01(スカート)
//! [Path] ./parts/lb_sk_mt001.pmd
//! [Child]
//! [Name] 靴_ローポリ
//! [Path] ./parts/shoes1_mt01.pmd
//! [Child]
//! None
//! [Parent]
//! [Parent]
//! None
//! [Parent]
//!
//! MATERIAL
//! [Name] mt_shoes1
//! [Sel] 外履き
//! NEXT
//! [Name] mt_sock1
//! [Sel] 白
//!
//! TRANSFORM
//! [Scale] 1.000000
//! [Pos] 0.000000 0.000000 0.000000
//! [Rot] 0.000000 0.000000 0.000000
//! BONES
//! [Name]
//! [Length] 1.000000
//! [Thick] 1.000000
//! [Pos] 0.000000 0.000000 0.000000
//! [Rot] 0.000000 0.000000 0.000000
//! NEXT
//! [Name]
//! [Length] 1.000000
//! [Thick] 1.000000
//! [Pos] 0.000000 0.000000 0.000000
//! [Rot] 0.000000 0.000000 0.000000
//! NEXT
//! [Name] 上半身
//! [Length] 0.905785
//! [Thick] 1.000000
//! [Pos] 0.000000 0.000000 0.000000
//! [Rot] 0.000000 0.000000 0.000000
const std = @import("std");

const bom = [3]u8{
    0xEF, 0xBB, 0xBF,
};

pub const PartsNode = struct {
    name: []const u8,
    path: []const u8 = "",
    children: std.ArrayList(?usize),

    fn init(
        allocator: std.mem.Allocator,
        name: []const u8,
    ) !@This() {
        return .{
            .name = try allocator.dupe(u8, name),
            .children = std.ArrayList(?usize).init(allocator),
        };
    }

    fn deinit(self: *@This()) void {
        self.children.deinit();
    }
};

pub const Assembler = struct {
    allocator: std.mem.Allocator,
    nodes: std.ArrayList(PartsNode),
    node_stack: std.ArrayList(usize),
    fn init(allocator: std.mem.Allocator) !@This() {
        var assembler = Assembler{
            .allocator = allocator,
            .nodes = std.ArrayList(PartsNode).init(allocator),
            .node_stack = std.ArrayList(usize).init(allocator),
        };
        try assembler.nodes.append(try PartsNode.init(allocator, "__root__"));
        try assembler.node_stack.append(0);
        return assembler;
    }

    fn deinit(self: *@This()) void {
        self.nodes.deinit();
        self.node_stack.deinit();
    }

    fn newNode(self: *@This(), name: []const u8) !void {
        const index = self.nodes.items.len;
        try self.nodes.append(try PartsNode.init(self.allocator, name));

        const stack_top = self.node_stack.items[self.node_stack.items.len - 1];
        const parent = &self.nodes.items[stack_top];
        try parent.children.append(index);
        try self.node_stack.append(index);
    }

    fn setPath(self: *@This(), path: []const u8) !void {
        const stack_top = self.node_stack.items[self.node_stack.items.len - 1];
        const parent = &self.nodes.items[stack_top];
        parent.path = try self.allocator.dupe(u8, path);
    }

    fn none(self: *@This()) !void {
        const stack_top = self.node_stack.items[self.node_stack.items.len - 1];
        const parent = &self.nodes.items[stack_top];
        try parent.children.append(null);
    }

    fn pop(self: *@This()) !void {
        _ = self.node_stack.pop();
    }

    fn debug_print_recursive(self: @This(), _index: ?usize, indent: usize) void {
        for (0..indent) |_| {
            std.debug.print("  ", .{});
        }
        if (_index) |index| {
            const node = self.nodes.items[index];
            std.debug.print("{s}\n", .{node.name});
            for (node.children.items) |child| {
                self.debug_print_recursive(child, indent + 1);
            }
        } else {
            std.debug.print("None\n", .{});
        }
    }

    pub fn debug_print(self: @This()) void {
        self.debug_print_recursive(0, 0);
    }
};

var line_buf: [1024]u8 = undefined;
fn getLine(r: anytype) ?[]const u8 {
    while (r.readUntilDelimiterOrEof(&line_buf, '\n')) |_line| {
        if (_line) |line| {
            const trimed = std.mem.trim(u8, line, &std.ascii.whitespace);
            if (trimed.len > 0) {
                return trimed;
            }
        } else {
            return null;
        }
    } else |_| {
        @panic("error");
    }
}

const KeyValue = struct {
    key: []const u8,
    value: []const u8,
};

fn matchKeyValue(line: []const u8) ?KeyValue {
    if (line[0] == '[') {
        if (std.mem.indexOf(u8, line, "]")) |close| {
            const key = line[1..close];
            const value = std.mem.trim(u8, line[close + 1 ..], &std.ascii.whitespace);
            return .{ .key = key, .value = value };
        }
    }
    return null;
}

pub fn parse(allocator: std.mem.Allocator, _data: []const u8) !Assembler {
    var data = _data;

    if (std.mem.startsWith(u8, data, &bom)) {
        data = data[bom.len..];
    }

    var s = std.io.fixedBufferStream(data);
    const r = s.reader();
    // skip until PARTS
    while (getLine(r)) |line| {
        if (std.mem.eql(u8, line, "PARTS")) {
            break;
        }
    }

    var assembler = try Assembler.init(allocator);

    // PARTS
    {
        while (getLine(r)) |line| {
            if (std.mem.eql(u8, line, "MATERIAL")) {
                break;
            } else if (matchKeyValue(line)) |kv| {
                if (std.mem.eql(u8, kv.key, "Name")) {
                    try assembler.newNode(kv.value);
                } else if (std.mem.eql(u8, kv.key, "Path")) {
                    try assembler.setPath(kv.value);
                } else if (std.mem.eql(u8, kv.key, "Child")) {
                    // try assembler.newNode();
                } else if (std.mem.eql(u8, kv.key, "Parent")) {
                    try assembler.pop();
                } else {
                    std.debug.print("unkonwn PARTS key: {s}\n", .{kv.key});
                    @panic("unknown PARTS property");
                }
            } else if (std.mem.eql(u8, line, "None")) {
                try assembler.none();
            } else {
                std.debug.print("{s}\n", .{line});
                unreachable;
            }
        }
    }

    // MATERIAL
    {
        while (getLine(r)) |line| {
            if (std.mem.eql(u8, line, "TRANSFORM")) {
                break;
            }
            // std.debug.print("{s}\n", .{line});
        }
    }

    // TRANSFORM
    {
        while (getLine(r)) |line| {
            _ = line;
            // std.debug.print("{s}\n", .{line});
        }
    }

    return assembler;
}
