const std = @import("std");

const header = "PMCA Materials list v2.0";
const setdir = "SETDIR ";
const bom = [3]u8{
    0xEF, 0xBB, 0xBF,
};

// SETDIR ./parts/
//
// [name] mt_hair
// [comment] 髪の色
//
// [ENTRY] 青色01
// [tex]	mt_hair_bl01.png
// [toon] 6 toon_mt_hair_bl01.bmp
// [diff_rgb] 0.80 0.80 0.80
// [spec_rgb] 0.08 0.22 0.37
// [mirr_rgb] 0.37 0.65 0.63
// [author] mato
//
// [ENTRY] グレー01
//
// NEXT

pub const ToonTexture = struct {
    index: usize,
    toon_texture: []const u8,
};

pub const Entry = struct {
    name: []const u8,
    tex: ?[]const u8 = null,
    toon: ?ToonTexture = null,
    diff_rgb: ?struct { f32, f32, f32 } = null,
    spec_rgb: ?struct { f32, f32, f32 } = null,
    mirr_rgb: ?struct { f32, f32, f32 } = null,
    author: ?[]const u8 = null,
};

pub const Material = struct {
    name: []const u8,
    comment: []const u8,
    entries: []Entry,
};

const Builder = struct {
    entries: std.ArrayList(Entry),
    name: []const u8 = "",
    comment: []const u8 = "",
    current_entry: ?Entry = null,

    fn init(allocator: std.mem.Allocator) @This() {
        return .{
            .entries = std.ArrayList(Entry).init(allocator),
        };
    }

    fn deinit(self: @This()) void {
        self.entries.deinit();
    }

    fn commit(self: *@This()) !Material {
        defer self.current_entry = null;
        defer self.name = "";
        defer self.comment = "";
        return Material{
            .name = self.name,
            .comment = self.comment,
            .entries = try self.entries.toOwnedSlice(),
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
        if (self.current_entry) |*entry| {
            if (isMatch("tex", key, _value)) |value| {
                entry.tex = value;
            } else if (isMatch("toon", key, _value)) |value| {
                _ = value;
            } else if (isMatch("diff_rgb", key, _value)) |value| {
                _ = value;
            } else if (isMatch("spec_rgb", key, _value)) |value| {
                _ = value;
            } else if (isMatch("mirr_rgb", key, _value)) |value| {
                _ = value;
            } else if (isMatch("author", key, _value)) |value| {
                _ = value;
            } else if (isMatch("ENTRY", key, _value)) |value| {
                self.current_entry = Entry{
                    .name = value,
                };
            } else {
                std.debug.print("unkonwn entry key: {s}\n", .{key});
                @panic("unknown entry property");
            }
        } else {
            if (isMatch("name", key, _value)) |value| {
                self.name = value;
            } else if (isMatch("comment", key, _value)) |value| {
                self.comment = value;
            } else if (isMatch("ENTRY", key, _value)) |value| {
                self.current_entry = Entry{
                    .name = value,
                };
            } else {
                std.debug.print("unkonwn material key: {s}\n", .{key});
                @panic("unknown material property");
            }
        }
    }
};

pub fn parse(allocator: std.mem.Allocator, _data: []const u8) ![]Material {
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

    var list = std.ArrayList(Material).init(allocator);
    var line_buf: [1024]u8 = undefined;
    var builder = Builder.init(allocator);
    defer builder.deinit();
    while (r.readUntilDelimiterOrEof(&line_buf, '\n')) |_line| {
        const line = _line orelse {
            // last
            if (builder.entries.items.len > 0) {
                try list.append(try builder.commit());
            }
            return list.toOwnedSlice();
        };
        // std.debug.print("{s}\n", .{line});

        const trimed = std.mem.trim(u8, line, &std.ascii.whitespace);
        if (trimed.len == 0) {
            continue;
        }

        if (std.mem.startsWith(u8, trimed, setdir)) {
            // builder.dir = trimed[setdir.len..];
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

    return try list.toOwnedSlice();
}
